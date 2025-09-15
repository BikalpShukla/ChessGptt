import chess
import chess.engine
import numpy as np

class ChessFeatureExtractor:
    def __init__(self, stockfish_path=None):
        self.stockfish_path = stockfish_path
        self.engine = None
        if stockfish_path:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
            except Exception as e:
                print(f"⚠️ Could not load Stockfish: {e}")

    def board_pattern_features(self, board: chess.Board):
        """
        Convert board into 8x8x12 tensor → flatten → feature vector
        """
        piece_to_idx = {
            chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 2,
            chess.ROOK: 3, chess.QUEEN: 4, chess.KING: 5
        }
        tensor = np.zeros((8, 8, 12), dtype=np.int8)

        for square, piece in board.piece_map().items():
            row, col = divmod(square, 8)
            offset = 0 if piece.color == chess.WHITE else 6
            tensor[row, col, piece_to_idx[piece.piece_type] + offset] = 1

        return tensor.flatten()

    def move_sequence_features(self, move_list, max_len=10):
        """
        Encode last N moves as integers (UCI notation hashed).
        """
        features = np.zeros(max_len)
        for i, move in enumerate(move_list[-max_len:]):
            features[i] = hash(move.uci()) % 1000 / 1000.0  # normalize
        return features

    def stockfish_eval(self, board: chess.Board, time_limit=0.1):
        """
        Get evaluation score from Stockfish (if available).
        """
        if not self.engine:
            return 0.0
        info = self.engine.analyse(board, chess.engine.Limit(time=time_limit))
        score = info["score"].white().score(mate_score=10000)
        return score / 100.0  # normalize

    def extract_features(self, fen: str, move_list=[]):
        board = chess.Board(fen)

        # Core features
        board_feats = self.board_pattern_features(board)
        move_feats = self.move_sequence_features(move_list)

        # Higher-level heuristic scores (dummy placeholders for now)
        risk_score = np.random.rand()
        tactical_score = np.random.rand()
        endgame_score = np.random.rand()

        # Stockfish score (optional)
        stockfish_score = self.stockfish_eval(board)

        feature_vector = {
            "featureVector": {
                "boardPatternFeatures": board_feats.tolist(),
                "moveSequenceFeatures": move_feats.tolist(),
                "styleCluster": "aggressive",  # Placeholder
                "riskTakingScore": float(risk_score),
                "tacticalAwarenessScore": float(tactical_score),
                "endgameSkillScore": float(endgame_score),
                "stockfishEval": stockfish_score
            }
        }
        return feature_vector

    def close(self):
        if self.engine:
            self.engine.quit()


# ----------------- Example Usage -----------------
if __name__ == "__main__":
    fen = "r1bqkbnr/pppppppp/n7/8/8/N7/PPPPPPPP/R1BQKBNR w KQkq - 0 1"

    extractor = ChessFeatureExtractor(stockfish_path=r"F:\D_drive\ChessGptt\backend\stockfish-windows-x86-64-avx2.exe")  # update path
    features = extractor.extract_features(fen, [])
    extractor.close()

    print(features)
