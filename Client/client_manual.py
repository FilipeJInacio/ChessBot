from Client.client import Client

class Client_manual(Client):
    def select_move(self):
        legal_moves = self.game.get_possible_moves()
        move_uci = None
        while move_uci not in legal_moves:
            move_uci = input(f"Enter your move ({', '.join(legal_moves)}): ").strip()

            if not move_uci:
                print("Invalid input: move cannot be empty.")
                continue

            if move_uci not in legal_moves:
                print("Invalid move: not a legal move.")

        return move_uci


    