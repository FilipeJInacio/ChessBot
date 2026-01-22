import time
import zmq
import time
import threading
import signal
from game import ChessGame
import chess


class Server:
    def __init__(self):
        self.game = ChessGame() # Everything game-related
        self.turn_counter = 0 # To track turns
        self.players = {} # color mapping -> identity
        self.dataset = [] # To store game data

        self.context = zmq.Context.instance() # For communication of the 2 threads
        self.running = True # For shutdown
        self.pub_port = 5556 # For state updates
        self.router_port = 5557 # For move requests
        self.fps = 15 # UI update rate

        # Threads
        self.pub_thread = threading.Thread(target=self._publisher, daemon=True)
        self.router_thread = threading.Thread(target=self._router, daemon=True)
        self.state_lock = threading.Lock() # To protect shared state

        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def _publisher(self):
        pub = self.context.socket(zmq.PUB)
        pub.bind(f"tcp://*:{self.pub_port}")

        period = 1.0 / self.fps

        try:
            while self.running:
                with self.state_lock:
                    message = {"fen": self.game.get_board_fen(), "last_move": self.game.get_last_move().uci() if self.game.get_last_move() else None}
                pub.send_json(message)
                time.sleep(period)
        finally:
            pub.close()
            print("Publisher stopped")

    def dataset_append(self):
        # φ(s) = [
        #     material_counts,              // length 5
        #     pawn_square_counts,            // length 64
        #     knight_square_counts,          // length 64
        #     bishop_square_counts,          // length 64
        #     rook_square_counts,            // length 64
        #     queen_square_counts,           // length 64
        #     king_square_counts,            // length 64
        #     tempo,                         // length 1
        #     pawn_structure_features,       // length 2
        #     enemy_pawn_structure_features, // length 2
        #     king_distance                  // length 1
        #     piece importance to phase      // length 10
        # ]

        list_of_pawns = [0]*64
        list_of_knights = [0]*64
        list_of_bishops = [0]*64
        list_of_rooks = [0]*64
        list_of_queens = [0]*64
        list_of_kings = [0]*64


        for square in self.game.board.pieces(chess.PAWN, chess.WHITE):
            list_of_pawns[square^56] += 1/8
        for square in self.game.board.pieces(chess.PAWN, chess.BLACK):
            list_of_pawns[square] -= 1/8

        for square in self.game.board.pieces(chess.KNIGHT, chess.WHITE):
            list_of_knights[square^56] += 1/2
        for square in self.game.board.pieces(chess.KNIGHT, chess.BLACK):
            list_of_knights[square] -= 1/2

        for square in self.game.board.pieces(chess.BISHOP, chess.WHITE):
            list_of_bishops[square^56] += 1/2
        for square in self.game.board.pieces(chess.BISHOP, chess.BLACK):
            list_of_bishops[square] -= 1/2

        for square in self.game.board.pieces(chess.ROOK, chess.WHITE):
            list_of_rooks[square^56] += 1/2
        for square in self.game.board.pieces(chess.ROOK, chess.BLACK):
            list_of_rooks[square] -= 1/2

        for square in self.game.board.pieces(chess.QUEEN, chess.WHITE):
            list_of_queens[square^56] += 1
        for square in self.game.board.pieces(chess.QUEEN, chess.BLACK):
            list_of_queens[square] -= 1

        for square in self.game.board.pieces(chess.KING, chess.WHITE): # NERF KING IMPORTANCE
            list_of_kings[square^56] += 1*0.2
        for square in self.game.board.pieces(chess.KING, chess.BLACK):
            list_of_kings[square] -= 1*0.2
        
        list_of_side_to_move = ([1] if self.game.board.turn == chess.WHITE else [-1])*0.05

        # count passing pawns
        passing_pawns_white = 0
        passing_pawns_black = 0
        for square in self.game.board.pieces(chess.PAWN, chess.WHITE):
            file = chess.square_file(square)
            is_passing = True
            for enemy_square in self.game.board.pieces(chess.PAWN, chess.BLACK):
                enemy_file = chess.square_file(enemy_square)
                if abs(file - enemy_file) <= 1 and chess.square_rank(enemy_square) > chess.square_rank(square):
                    is_passing = False
                    break
            if is_passing:
                passing_pawns_white += 1

        for square in self.game.board.pieces(chess.PAWN, chess.BLACK):
            file = chess.square_file(square)
            is_passing = True
            for enemy_square in self.game.board.pieces(chess.PAWN, chess.WHITE):
                enemy_file = chess.square_file(enemy_square)
                if abs(file - enemy_file) <= 1 and chess.square_rank(enemy_square) < chess.square_rank(square):
                    is_passing = False
                    break
            if is_passing:
                passing_pawns_black += 1

        # count stacked pawns
        # basically, if 2 stacked +2 if 3 stacked +3 etc, if 2 stacked in 2 different files +4
        stacked_pawns_white = 0
        stacked_pawns_black = 0
        for file in range(8):
            count_white = 0
            count_black = 0
            for rank in range(8):
                square = chess.square(file, rank)
                if self.game.board.piece_at(square) == chess.Piece(chess.PAWN, chess.WHITE):
                    count_white += 1
                elif self.game.board.piece_at(square) == chess.Piece(chess.PAWN, chess.BLACK):
                    count_black += 1
            if count_white > 1:
                stacked_pawns_white += count_white
            if count_black > 1:
                stacked_pawns_black += count_black
        list_of_pawns_features = [(passing_pawns_white - passing_pawns_black)/8, (stacked_pawns_white - stacked_pawns_black)/8]

        list_piece_importance = [len(self.game.board.pieces(chess.PAWN, chess.WHITE)) + len(self.game.board.pieces(chess.PAWN, chess.BLACK)),
                                 len(self.game.board.pieces(chess.KNIGHT, chess.WHITE)) + len(self.game.board.pieces(chess.KNIGHT, chess.BLACK)),
                                 len(self.game.board.pieces(chess.BISHOP, chess.WHITE)) + len(self.game.board.pieces(chess.BISHOP, chess.BLACK)),
                                 len(self.game.board.pieces(chess.ROOK, chess.WHITE)) + len(self.game.board.pieces(chess.ROOK, chess.BLACK)),
                                 len(self.game.board.pieces(chess.QUEEN, chess.WHITE)) + len(self.game.board.pieces(chess.QUEEN, chess.BLACK)),
                                 0,0,0,0,0] # filler for 10 length

        # hamilton distance
        white_king_square = list(self.game.board.pieces(chess.KING, chess.WHITE))[0]
        black_king_square = list(self.game.board.pieces(chess.KING, chess.BLACK))[0]
        white_king_file = chess.square_file(white_king_square)
        white_king_rank = chess.square_rank(white_king_square)
        black_king_file = chess.square_file(black_king_square)
        black_king_rank = chess.square_rank(black_king_square)
        king_distance = (14 - (abs(white_king_file - black_king_file) + abs(white_king_rank - black_king_rank)))/14

        self.dataset.extend([(self.game.board.pawns(chess.WHITE).count() - self.game.board.pawns(chess.BLACK).count())/8, 
                             (self.game.board.knights(chess.WHITE).count() - self.game.board.knights(chess.BLACK).count())/2,
                             (self.game.board.bishops(chess.WHITE).count() - self.game.board.bishops(chess.BLACK).count())/2,
                             (self.game.board.rooks(chess.WHITE).count() - self.game.board.rooks(chess.BLACK).count())/2,
                             (self.game.board.queens(chess.WHITE).count() - self.game.board.queens(chess.BLACK).count())])
        self.dataset.extend(list_of_pawns)
        self.dataset.extend(list_of_knights)
        self.dataset.extend(list_of_bishops)
        self.dataset.extend(list_of_rooks)
        self.dataset.extend(list_of_queens)
        self.dataset.extend(list_of_kings)
        self.dataset.extend(list_of_side_to_move)
        self.dataset.extend(list_of_pawns_features)
        self.dataset.append(king_distance*0.1)




    def _router(self):
        state = "waiting_for_players"
        socket = self.context.socket(zmq.ROUTER)
        socket.setsockopt(zmq.RCVTIMEO, 200)
        socket.bind(f"tcp://*:{self.router_port}")

        #self.dataset_append()

        while self.running:
            try:
                time.sleep(0.3)
                msg = socket.recv_multipart()
                identity = msg[0]
                msg_type = msg[1]
                payload = msg[2] if len(msg) > 2 else b""
            except zmq.Again:
                continue

            # STATE 1   
            if state == "waiting_for_players":
                if msg_type == b"join":
                    if len(self.players) == 2:
                        socket.send_multipart([identity, b"join_nack", b""])
                        continue

                    color = "White" if "White" not in self.players else "Black"
                    self.players[color] = identity
                    print(f"Player joined as {color}")
                    socket.send_multipart([identity, b"join_ack", color.encode()])

                    if len(self.players) == 2:
                        self.game.reset()
                        print("Game started")
                        state = "active_game"
                else:
                    print("Unexpected Message")


            # STATE 3
            if state == "waiting_for_move":
                if msg_type == b"move":
                    if identity != current_player_identity:
                        continue
                    move = chess.Move.from_uci(payload.decode("utf-8"))
                    if move in legal_moves:
                        with self.state_lock:
                            self.game.make_move(move)
                        socket.send_multipart([identity, b"move_ack", b""])
                        state = "active_game"
                    else:
                        socket.send_multipart([identity, b"move_nack", b""])


                else:
                    print("Unexpected Message")
                    continue

            # STATE 2
            if state == "active_game":
                if self.game.is_game_over():
                    print(f"Game over detected by {self.game.game_over_reason()}")
                    winner = self.game.get_winner()
                    if winner == chess.WHITE:
                        winner = "White"
                    elif winner == chess.BLACK:
                        winner = "Black"
                    elif winner is None:
                        winner = "Draw"
                    for color, identity in self.players.items():
                        socket.send_multipart([identity, b"game_over", winner.encode("utf-8")])
                    state = "waiting_for_players"
                    self.turn_counter = 0
                    self.players = {}
                    print("Game over announced, waiting for new players")
                    continue
                self.turn_counter += 1
                current_player_identity = self.players[self.game.turn()]
                last_move = self.game.get_last_move()
                socket.send_multipart([current_player_identity, b"your_turn", last_move.uci().encode("utf-8") if last_move else b""])

                legal_moves = self.game.get_possible_moves()
                state = "waiting_for_move"
                continue


        # Send shutdown to all clients
        for color, identity in self.players.items():
            socket.send_multipart([identity, b"server_shutdown", b""])

        socket.close()
        return

    def start(self):
        print("Starting server...")
        self.pub_thread.start()
        self.router_thread.start()

        try:
            while self.running:
                time.sleep(1)
        finally:
            print("Server shutting down...")
            self.pub_thread.join()
            self.router_thread.join()
            self.context.term()
            print("Server terminated")



if __name__ == "__main__":
    server = Server()
    server.start()