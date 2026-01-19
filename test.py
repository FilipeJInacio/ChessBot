from game import ChessGame


game = ChessGame()

for move in ['d2d3', 'e7e5', 'a2a3', 'e5e4', 'c2c3', 'e4d3', 'g2g3', 'd3e2', 'c1f4', 'e2d1q', 'e1d1', 'g8f6', 'b1d2', 'f8c5', 'g1e2', 'e8g8']:
    print(f"Making move: {move}")
    if move not in game.get_possible_moves():
        print(game.get_possible_moves())
        print("Illegal move attempted!")
    game.make_move(move)
    game.print_board()