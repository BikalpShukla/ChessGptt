# import chess

# def apply_move(fen, move_san):
#     """
#     Applies a SAN move to the board and returns updated FEN
#     """
#     board = chess.Board(fen)
#     try:
#         board.push_san(move_san)
#         return board.fen()
#     except:
#         return fen  # if invalid move, return original FEN
