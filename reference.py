import chess
import time



def perft(board, depth):
    if depth == 0:
        return 1

    nodes = 0
    for move in board.legal_moves:
        board.push(move)
        nodes += perft(board, depth - 1)
        board.pop()
    return nodes

def timed_perft(max_depth=5):
    board = chess.Board()
    results = {}

    for depth in range(1, max_depth + 1):
        start = time.perf_counter()
        nodes = perft(board, depth)
        elapsed = time.perf_counter() - start

        results[depth] = {
            "nodes": nodes,
            "time_sec": elapsed,
            "time_per_node_us": (elapsed / nodes) * 1e6
        }

        print(
            f"Depth {depth}: "
            f"{nodes:,} nodes | "
            f"{elapsed:.4f} s | "
            f"{results[depth]['time_per_node_us']:.2f} µs/node"
        )

    return results



timed_perft(5)
