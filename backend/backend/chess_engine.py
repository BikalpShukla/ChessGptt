# import chess
# import chess.engine

# # Initialize Stockfish (download from https://stockfishchess.org/download/)

# engine = chess.engine.SimpleEngine.popen_uci(
#     r"D:\Projects\Chess_Gpt\backend\stockfish-windows-x86-64-avx2.exe"
# )

# def get_best_move(fen, time=0.1):
#     """
#     Returns the best move for a given FEN position using Stockfish
#     """
#     board = chess.Board(fen)
#     result = engine.play(board, chess.engine.Limit(time=time))
#     return str(result.move), board
