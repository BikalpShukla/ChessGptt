# from fastapi import FastAPI
# from pydantic import BaseModel
# from chess_engine import get_best_move
# from feature_extractor import extract_features
# from gpt_explainer import explain_move
# from utils import apply_move


# app = FastAPI()

# class MoveRequest(BaseModel):
#     fen: str       # current board FEN
#     move: str = "" # optional: move user played

# @app.post("/analyze")
# def analyze_move(req: MoveRequest):
#     # Apply user's move if provided
#     fen_after_move = apply_move(req.fen, req.move) if req.move else req.fen

#     # Get Stockfish best move
#     best_move, board = get_best_move(fen_after_move)
    
#     features = extract_features(fen_after_move)

#     # Get GPT explanation
#     explanation = explain_move(best_move, fen_after_move)

#     return {
#         "current_fen": fen_after_move,
#         "best_move": best_move,
#         "features": features,
#         "explanation": explanation
#     }

# # Run server: uvicorn app:app --reload



import chess
# from IPython.display import display, SVG
# === Yahan apna FEN dalna hai ===
fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"


board = chess.Board(fen)
print(board)
# --- Material values ---
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

white_material = 0
black_material = 0

for square in chess.SQUARES:
    piece = board.piece_at(square)
    if piece:
        value = piece_values[piece.piece_type]
        if piece.color == chess.WHITE:
            white_material += value
        else:
            black_material += value

# --- Mobility ---
white_mobility = len(list(board.legal_moves))
# For simplicity, consider total legal moves as mobility
# Could be split by color if needed

# --- King Safety (simplified) ---
white_king_safety = "Safe"  # You can improve later
black_king_safety = "Safe"

# --- Print Abstract Features ---
print("Abstract Features:")
print(f"- Material: White {white_material}, Black {black_material}")
print(f"- Mobility: {white_mobility} moves")
print(f"- King Safety: White King: {white_king_safety}, Black King: {black_king_safety}")
