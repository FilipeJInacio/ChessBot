from Client.client import Client

class Client_minmax(Client):

    def minimax(self, depth, maximizing_player):
        # Terminal condition
        if depth == 0 or self.game.is_game_over():
            return self.game.position_evaluation()

        if maximizing_player:
            max_value = float("-inf")
            for move in self.game.get_possible_moves():
                # Simulate the move
                self.game.make_move(move)
                value = self.minimax(depth - 1, False)
                self.game.undo_move()
                max_value = max(max_value, value)
            return max_value
        else:
            min_value = float("inf")
            for move in self.game.get_possible_moves():
                self.game.make_move(move)
                value = self.minimax(depth - 1, True)
                self.game.undo_move()
                min_value = min(min_value, value)
            return min_value


    def select_move(self):
        depth = 3
        best_value = float("-inf")
        best_move = None

        for move in self.game.get_possible_moves():
            self.game.make_move(move)
            value = self.minimax(depth - 1, False)
            self.game.undo_move()
            if value > best_value:
                best_value = value
                best_move = move

        return best_move


