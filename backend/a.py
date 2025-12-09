from stockfish import Stockfish

    # Initialize Stockfish (you need to provide the path to the Stockfish executable)
stockfish = Stockfish(path="/path/to/stockfish_executable")

    # Set the FEN of the board
stockfish.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    # Get the best move
best_move = stockfish.get_best_move()
print(f"Best move: {best_move}")

    # Get the evaluation
evaluation = stockfish.get_evaluation()
print(f"Evaluation: {evaluation}")