# To implement
# State representation for chess -> FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# Build board from FEN
# class algorithm has a board attribute

# f1(x, a) -> next state                Function, f(FEN, action) -> new FEN 
# f2(x) -> possible actions
# f3(x, a) -> reward/cost

example_state_fen = "7k/3N2qp/b5r1/2p1Q1N1/Pp4PK/7P/!P3p2/6r1 w - - 7 4"


from game.game import Game

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()