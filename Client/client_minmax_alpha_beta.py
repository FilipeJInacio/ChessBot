from Client.client import Client

class Client_minmax_alpha_beta(Client):

    def minimax(self, depth, alpha, beta, maximizing_player):
        # Terminal condition
        if depth == 0 or self.game.is_game_over():
            return self.game.position_evaluation()

        if maximizing_player:
            value = float("-inf")
            for move in self.game.get_possible_moves():
                # Simulate the move
                self.game.make_move(move)
                value = max(value, self.minimax(depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                self.game.undo_move()
                if beta <= alpha:
                    break 
            return value
        else:
            value = float("inf")
            for move in self.game.get_possible_moves():
                self.game.make_move(move)
                value = min(value, self.minimax(depth - 1, alpha, beta, True))
                beta = min(beta, value)
                self.game.undo_move()
                if beta <= alpha:
                    break
            return value


    def select_move(self):
        depth = 3
        best_value = float("-inf")
        best_move = None

        for move in self.game.get_possible_moves():
            self.game.make_move(move)
            value = self.minimax(depth - 1, float("-inf"), float("inf"), False)
            self.game.undo_move()
            if value > best_value:
                best_value = value
                best_move = move

        return best_move


