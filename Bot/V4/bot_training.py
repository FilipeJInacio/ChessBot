import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split
import chess
import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import shared_memory, cpu_count
import ctypes
from model import ChessResNet


# ── helpers ──────────────────────────────────────────────────────────────────

def moves_to_boards(moves: list[str], sample_every: int) -> list[chess.Board]:
    board = chess.Board()
    boards = []
    for i, move in enumerate(moves):
        try:
            board.push_uci(move)
        except Exception:
            break
        if i % sample_every == 0:
            boards.append(board.copy())
    return boards

def board_to_features(board: chess.Board) -> np.ndarray:
    features = np.zeros(787, dtype=np.float32)

    piece_order = [
        (chess.KING,   chess.WHITE),
        (chess.QUEEN,  chess.WHITE),
        (chess.ROOK,   chess.WHITE),
        (chess.BISHOP, chess.WHITE),
        (chess.KNIGHT, chess.WHITE),
        (chess.PAWN,   chess.WHITE),
        (chess.KING,   chess.BLACK),
        (chess.QUEEN,  chess.BLACK),
        (chess.ROOK,   chess.BLACK),
        (chess.BISHOP, chess.BLACK),
        (chess.KNIGHT, chess.BLACK),
        (chess.PAWN,   chess.BLACK),
    ]
    for i, (piece_type, color) in enumerate(piece_order):
        for square in board.pieces(piece_type, color):
            features[i * 64 + square] = 1.0

    features[768] = float(board.has_kingside_castling_rights(chess.WHITE))
    features[769] = float(board.has_queenside_castling_rights(chess.WHITE))
    features[770] = float(board.has_kingside_castling_rights(chess.BLACK))
    features[771] = float(board.has_queenside_castling_rights(chess.BLACK))

    if board.ep_square is not None:
        features[772 + chess.square_file(board.ep_square)] = 1.0

    features[780] = float(board.turn == chess.WHITE)

    halfmove = min(board.halfmove_clock, 15)
    for bit in range(4):
        features[781 + bit] = float((halfmove >> bit) & 1)

    features[785] = float(board.is_repetition(2))
    features[786] = float(board.is_repetition(3))

    return features

# ── worker ───────────────────────────────────────────────────────────────────

def process_chunk(args: tuple) -> tuple[np.ndarray, np.ndarray]:
    """
    Runs in a worker process.
    Receives a chunk of rows, returns (features, labels) as numpy arrays.
    No shared memory complexity — just return the arrays directly.
    """
    rows, sample_every = args  # rows: list of (moves, winner)

    local_features = []
    local_labels   = []

    for moves, winner in rows:
        label = 0 if winner == "black" else 2 if winner == "white" else 1
        for board in moves_to_boards(moves, sample_every):
            local_features.append(board_to_features(board))
            local_labels.append(label)

    if not local_features:
        return np.empty((0, 787), dtype=np.float32), np.empty((0,), dtype=np.int64)

    return (np.stack(local_features), np.array(local_labels, dtype=np.int64))


# ── dataset ──────────────────────────────────────────────────────────────────

class ChessDataset(Dataset):
    def __init__(self, df: pd.DataFrame, sample_every: int = 3, num_workers: int = cpu_count(), chunk_size: int = 2048):

        n_games = len(df)
        rows    = list(zip(df["moves_uci"], df["winner"]))

        # ── 1. divide into chunks ─────────────────────────────────────────
        chunks = [(rows[i : i + chunk_size], sample_every) for i in range(0, n_games, chunk_size)]
        n_chunks = len(chunks)
        print(f"→ {n_games} games | {n_chunks} chunks | {num_workers} workers")

        # ── 2. dispatch chunks across cores ──────────────────────────────
        all_features: list[np.ndarray] = [None] * n_chunks
        all_labels:   list[np.ndarray] = [None] * n_chunks

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(process_chunk, chunk): i for i, chunk in enumerate(chunks)}

            completed = 0
            for future in as_completed(futures):
                i = futures[future]
                all_features[i], all_labels[i] = future.result()
                completed += 1
                if completed % 50 == 0 or completed == n_chunks:
                    print(f"  {completed}/{n_chunks} chunks done", flush=True)

        # ── 3. merge results efficiently ──────────────────────────────────
        print("→ Merging results...")
        self.features = np.concatenate(all_features, axis=0)
        self.labels   = np.concatenate(all_labels,   axis=0)

        print(f"→ Done. {len(self.labels):,} positions | ", f"{self.features.nbytes / 1e9:.1f} GB", f" | {self.features.shape, self.labels.shape}")

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return (torch.tensor(self.features[idx]),
                torch.tensor(self.labels[idx], dtype=torch.long))










if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # # Web download dataset from Hugging Face Hub
    # file_path = hf_hub_download(repo_id="angeluriot/chess_games", filename="dataset.parquet", repo_type="dataset")

    # # Load dataset
    # df = pd.read_parquet(file_path, columns=["moves_uci", "winner", "end_type"])

    # # Shuffle (recommended so splits are not biased)
    # df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # # Split into 20 parts
    # splits = np.array_split(df, 20)

    # # Save each split
    # for i, split_df in enumerate(splits):
    #     output_path = f"data/chess_dataset_part_{i}.parquet"
    #     split_df.to_parquet(output_path, index=False)
    #     print(f"Saved {output_path} with {len(split_df)} rows")

    # del file_path, df, splits, split_df, output_path

    # Load data
    df = pd.read_parquet("data/chess_dataset_part_6.parquet")

    dataset = ChessDataset(df, sample_every=1)
    model = ChessResNet()

    model.load_state_dict(torch.load("007_model.pt", map_location=device))

    val_split = 0.05
    batch_size = 2048
    lr = 5e-5
    epochs = 30

    val_size   = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    model.to(device)

    for epoch in range(epochs):
        # --- Train ---
        model.train()
        train_loss = 0.0
        with tqdm(total=len(train_loader), desc=f"Train {epoch+1}/{epochs}", leave=False, unit="batch") as train_bar:
            for features, labels in train_loader:
                features, labels = features.to(device), labels.to(device)
                optimizer.zero_grad()
                logits = model(features)
                loss   = torch.nn.functional.cross_entropy(logits, labels)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                train_loss += loss.item()
                train_bar.update(1)

        # --- Validate ---
        model.eval()
        val_loss = 0.0
        correct  = 0
        total    = 0
        with tqdm(total=len(val_loader), desc=f"Val {epoch+1}/{epochs}", leave=False, unit="batch") as val_bar:
            with torch.no_grad():
                for features, labels in val_loader:
                    features, labels = features.to(device), labels.to(device)
                    logits = model(features)
                    val_loss += torch.nn.functional.cross_entropy(logits, labels).item()
                    correct  += (logits.argmax(dim=1) == labels).sum().item()
                    total    += labels.size(0)
                    val_bar.update(1)

        train_loss /= len(train_loader)
        val_loss   /= len(val_loader)
        accuracy    = correct / total
        print(f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, Val Accuracy: {accuracy:.3f}")

        scheduler.step()

        # --- Checkpoint ---
        # Always save in folder models the iterative model as XXX_model.pt
        torch.save(model.state_dict(), f"models/{epoch:03d}_model.pt")

    print("Training complete!")