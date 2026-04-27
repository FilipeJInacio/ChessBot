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

    model = ChessResNet()

    model.load_state_dict(torch.load("005_model.pt"))

    board = chess.Board()

    while True:

        features = board_to_features(board)
        features_tensor = torch.tensor(features).unsqueeze(0)  # Add batch dimension
        with torch.no_grad():
            output = model(features_tensor)
            print(f"{output}")

        move_uci = input("Enter your move in UCI format (e.g., e2e4): ")
        try:
            move = chess.Move.from_uci(move_uci)
            if move in board.legal_moves:
                board.push(move)
                print(board)
                print("\n" + "-"*30 + "\n")
            else:
                print("Illegal move. Try again.")
        except ValueError:
            print("Invalid UCI format. Try again.")        
    

