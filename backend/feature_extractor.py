# import chess
# import chess.engine

# STOCKFISH_PATH = r"D:\Projects\Chess_Gpt\backend\stockfish-windows-x86-64-avx2"

# engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

# def extract_features(fen: str, time=0.1):
#     board = chess.Board(fen)
#     info = engine.analyse(board, chess.engine.Limit(time=time))

#     features = {}

#     # Material balance
#     piece_values = {chess.PAWN:1, chess.KNIGHT:3, chess.BISHOP:3, chess.ROOK:5, chess.QUEEN:9}
#     white_material = sum(piece_values.get(p.piece_type,0) for p in board.piece_map().values() if p.color == chess.WHITE)
#     black_material = sum(piece_values.get(p.piece_type,0) for p in board.piece_map().values() if p.color == chess.BLACK)
#     features["material_balance"] = white_material - black_material

#     # King safety
#     features["white_king_safety"] = len(board.attacks(board.king(chess.WHITE)))
#     features["black_king_safety"] = len(board.attacks(board.king(chess.BLACK)))

#     # Center control
#     center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
#     white_center = sum(len(board.attackers(chess.WHITE, sq)) for sq in center_squares)
#     black_center = sum(len(board.attackers(chess.BLACK, sq)) for sq in center_squares)
#     features["center_control"] = white_center - black_center

#     # Mobility
#     features["white_mobility"] = len(list(board.legal_moves)) if board.turn == chess.WHITE else None
#     features["black_mobility"] = len(list(board.legal_moves)) if board.turn == chess.BLACK else None

#     # Stockfish eval
#     if "score" in info:
#         features["engine_eval"] = info["score"].white().score(mate_score=10000)

#     return features
