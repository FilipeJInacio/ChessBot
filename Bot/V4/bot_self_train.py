import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, random_split, TensorDataset
import chess
import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import shared_memory, cpu_count
import ctypes
from model import ChessResNet
import copy
import random
from collections import deque



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

    val_split = 0.05
    batch_size = 2048
    lr = 25e-5
    epochs = 30



    print("Training complete!")


# ── game generation ───────────────────────────────────────────────────────────

def play_game(current_model: torch.nn.Module, opponent_model: torch.nn.Module, engine, max_moves: int = 300, device: torch.device = None,) -> list[tuple[np.ndarray, int]]:
    board  = chess.Board()
    positions: list[np.ndarray] = []   # features at each step

    current_model.eval()
    opponent_model.eval()

    with torch.no_grad():
        for move_num in range(max_moves):
            if board.is_game_over():
                break

            model = current_model if board.turn == chess.WHITE else opponent_model

            engine.board = board
            engine.model = model
            move = engine.best_move()  # your existing alpha-beta entry point

            positions.append(board_to_features(board))
            board.push(move)

        if board.is_checkmate():
            label = 0 if board.turn == chess.WHITE else 2  # loser is to move
        elif move_num >= max_moves - 1:
            label = 1
        else:
            label = 1

    return [(feat, label) for feat in positions]


# ── replay buffer ─────────────────────────────────────────────────────────────

class ReplayBuffer:
    def __init__(self, max_positions: int = 500_000):
        self.buffer = deque(maxlen=max_positions)

    def add_game(self, samples: list[tuple[np.ndarray, int]]):
        self.buffer.extend(samples)

    def sample(self, n: int) -> tuple[np.ndarray, np.ndarray]:
        batch   = random.sample(self.buffer, min(n, len(self.buffer)))
        features = np.stack([f for f, _ in batch])
        labels   = np.array([l for _, l in batch], dtype=np.int64)
        return features, labels

    def __len__(self):
        return len(self.buffer)


# ── evaluation ────────────────────────────────────────────────────────────────

def evaluate(current_model: torch.nn.Module, opponent_model: torch.nn.Module, engine, n_games: int = 50, max_moves: int = 200, device: torch.device = None,) -> float:
    """Returns win rate of current_model against frozen opponent."""
    wins = 0
    for i in range(n_games):
        # alternate colours every game
        if i % 2 == 0:
            samples = play_game(current_model, opponent_model, engine, max_moves, device)
            won = samples[-1][1] == 2   # white (current) won
        else:
            samples = play_game(opponent_model, current_model, engine, max_moves, device)
            won = samples[-1][1] == 0   # black (current) won
        wins += int(won)
    return wins / n_games


# ── training step ─────────────────────────────────────────────────────────────

def train_step(model: torch.nn.Module, optimizer: torch.optim.Optimizer, replay_buffer: ReplayBuffer, supervised_dataset, batch_size: int = 512, supervised_ratio: float = 0.2, device: torch.device = None,) -> float:
    model.train()

    n_supervised  = int(batch_size * supervised_ratio)
    n_selfplay    = batch_size - n_supervised

    # ── self-play batch ───────────────────────────────────────────────────
    sp_features, sp_labels = replay_buffer.sample(n_selfplay)
    sp_features = torch.tensor(sp_features, dtype=torch.float32).to(device)
    sp_labels   = torch.tensor(sp_labels,   dtype=torch.long).to(device)

    # ── supervised batch (catastrophic forgetting prevention) ────────────
    indices      = random.sample(range(len(supervised_dataset)), n_supervised)
    sup_features = torch.stack([supervised_dataset[i][0] for i in indices]).to(device)
    sup_labels   = torch.stack([supervised_dataset[i][1] for i in indices]).to(device)

    # ── combine and train ─────────────────────────────────────────────────
    features = torch.cat([sp_features, sup_features], dim=0)
    labels   = torch.cat([sp_labels,   sup_labels],   dim=0)

    optimizer.zero_grad()
    logits = model(features)
    loss   = F.cross_entropy(logits, labels)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()

    return loss.item()


# ── main self-play loop ───────────────────────────────────────────────────────

def self_play_train(
    model: torch.nn.Module,
    engine,
    supervised_dataset,
    # self-play hyperparams
    n_iterations: int     = 200,   # outer loop iterations
    games_per_iter: int   = 50,    # games to play before each update
    updates_per_iter: int = 100,   # gradient steps per iteration
    batch_size: int       = 512,
    max_moves: int        = 200,
    # replay buffer
    buffer_size: int      = 500_000,
    min_buffer: int       = 10_000, # don't train until buffer has this many
    # opponent update
    eval_every: int       = 10,    # evaluate every N iterations
    eval_games: int       = 50,
    promote_threshold: float = 0.55,  # win rate needed to update opponent
    # optimiser
    lr: float             = 1e-4,
    supervised_ratio: float = 0.2,
    device: torch.device  = None,
    checkpoint_path: str  = "selfplay_best.pt",
):
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optimizer      = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    replay_buffer  = ReplayBuffer(max_positions=buffer_size)
    frozen_opponent = copy.deepcopy(model)   # start frozen = current model
    frozen_opponent.eval()

    for iteration in range(1, n_iterations + 1):
        print(f"\n── Iteration {iteration}/{n_iterations} ──────────────────")

        # ── 1. generate games ─────────────────────────────────────────────
        game_lengths = []
        for g in range(games_per_iter):
            samples = play_game(model, frozen_opponent, engine, max_moves, device)
            replay_buffer.add_game(samples)
            game_lengths.append(len(samples))

        avg_len = sum(game_lengths) / len(game_lengths)
        print(f"  games played : {games_per_iter} | "
              f"avg length : {avg_len:.1f} | "
              f"buffer size: {len(replay_buffer):,}")

        # ── 2. train ──────────────────────────────────────────────────────
        if len(replay_buffer) < min_buffer:
            print(f"  buffer too small ({len(replay_buffer)} < {min_buffer}), skipping update")
            continue

        losses = []
        for _ in range(updates_per_iter):
            loss = train_step(model, optimizer, replay_buffer,
                              supervised_dataset, batch_size,
                              supervised_ratio, device)
            losses.append(loss)

        avg_loss = sum(losses) / len(losses)
        print(f"  avg loss     : {avg_loss:.4f}")

        # ── 3. evaluate and maybe promote ────────────────────────────────
        if iteration % eval_every == 0:
            print(f"  evaluating vs frozen opponent ({eval_games} games)...")
            win_rate = evaluate(model, frozen_opponent, engine,
                                eval_games, max_moves, device)
            print(f"  win rate     : {win_rate:.2f} "
                  f"(threshold={promote_threshold})")

            if win_rate >= promote_threshold:
                print(f"  → promoting current model to opponent")
                frozen_opponent = copy.deepcopy(model)
                frozen_opponent.eval()
                torch.save(model.state_dict(), checkpoint_path)
                print(f"  → checkpoint saved to {checkpoint_path}")
            else:
                print(f"  → opponent unchanged")