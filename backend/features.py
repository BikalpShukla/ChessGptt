import chess

# ==============================================================
# Chess Feature Extractor (FEN → Feature Vector)
# --------------------------------------------------------------
# This script extracts multiple abstract chess features from a 
# given FEN (Forsyth-Edwards Notation). These features represent 
# board evaluation factors like material, king safety, pawn structure, 
# development, rook activity, threats, coordination, etc.
#
# Output: A dictionary of features (White + Black) → useful for ML 
# models, evaluation functions, or building a ChessGPT-style system.
# ==============================================================

# === Yahan apna FEN dalna hai ===
fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
board = chess.Board(fen)

# --- Standard Material values ---
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0   # king has no material value (infinite importance)
}

# -------------------------------
# MATERIAL COUNT
# -------------------------------
def get_material(board):
    """
    Calculates total material score for both White and Black.
    Uses standard piece values.
    """
    white_material = black_material = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            val = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                white_material += val
            else:
                black_material += val
    return white_material, black_material


# -------------------------------
# MOBILITY
# -------------------------------
def get_mobility(board):
    """Counts total number of legal moves (both sides combined)."""
    return len(list(board.legal_moves))


# -------------------------------
# KING SAFETY
# -------------------------------
def get_king_safety(board, color):
    """
    Evaluates king safety based on:
    - Castling rights (castled or not)
    - Enemy attacks near king
    """
    king_sq = board.king(color)
    castled = board.has_castling_rights(color) is False
    unsafe = 0
    for sq in chess.SquareSet(chess.BB_KING_ATTACKS[king_sq]):
        if board.is_attacked_by(not color, sq):
            unsafe += 1
    return "Safe" if unsafe <= 2 and castled else "Exposed"


# -------------------------------
# PAWN STRUCTURE
# -------------------------------
def get_pawn_structure(board, color):
    """
    Detects pawn-related features:
    - doubled pawns
    - isolated pawns
    - passed pawns
    """
    pawns = board.pieces(chess.PAWN, color)
    files = [chess.square_file(sq) for sq in pawns]

    # Count doubled pawns (same file >1)
    doubled = sum(files.count(f) > 1 for f in set(files))

    # Count isolated pawns (no pawns in adjacent files)
    isolated = sum(
        all(abs(f - other) > 1 for other in set(files) if other != f)
        for f in set(files)
    )

    # Count passed pawns (no enemy pawns ahead on same file)
    passed = 0
    for sq in pawns:
        rank = chess.square_rank(sq)
        file = chess.square_file(sq)
        blocked = False
        for ahead in range(rank+1, 8):
            front = chess.square(file, ahead)
            if board.piece_at(front) and board.piece_at(front).color != color:
                blocked = True
        if not blocked:
            passed += 1

    return {"doubled": doubled, "isolated": isolated, "passed": passed}


# -------------------------------
# CENTER CONTROL
# -------------------------------
def get_center_control(board, color):
    """Counts how many central squares (d4,d5,e4,e5) are controlled."""
    center = [chess.D4, chess.D5, chess.E4, chess.E5]
    return sum(board.is_attacked_by(color, sq) for sq in center)


# -------------------------------
# DEVELOPMENT
# -------------------------------
def get_development(board, color):
    """Counts developed minor pieces (knights + bishops)."""
    developed = 0
    minors = board.pieces(chess.KNIGHT, color) | board.pieces(chess.BISHOP, color)
    for sq in minors:
        rank = chess.square_rank(sq)
        if (color == chess.WHITE and rank > 0) or (color == chess.BLACK and rank < 7):
            developed += 1
    return developed


# -------------------------------
# ROOK ACTIVITY
# -------------------------------
def get_rook_activity(board, color):
    """Counts active rooks (on open files without pawns)."""
    rooks = board.pieces(chess.ROOK, color)
    active = 0
    for r in rooks:
        file = chess.square_file(r)
        has_pawn = any(board.piece_at(chess.square(file, rank)) 
                       and board.piece_at(chess.square(file, rank)).piece_type == chess.PAWN
                       for rank in range(8))
        if not has_pawn:
            active += 1
    return active


# -------------------------------
# HANGING PIECES
# -------------------------------
def get_hanging_pieces(board, color):
    """Counts undefended pieces attacked by opponent."""
    hanging = 0
    for sq, piece in board.piece_map().items():
        if piece.color == color:
            if not board.is_attacked_by(color, sq) and board.is_attacked_by(not color, sq):
                hanging += 1
    return hanging


# -------------------------------
# PIECE ACTIVITY
# -------------------------------
def get_piece_activity(board, color):
    """Counts number of legal moves by this color."""
    return sum(1 for move in board.legal_moves if board.color_at(move.from_square) == color)


# -------------------------------
# PIECE COORDINATION
# -------------------------------
def get_piece_coordination(board, color):
    """Counts defended pieces (pieces protected by same side)."""
    defended = 0
    for sq, piece in board.piece_map().items():
        if piece.color == color and board.is_attacked_by(color, sq):
            defended += 1
    return defended


# -------------------------------
# BISHOP PAIR BONUS
# -------------------------------
def get_bishop_pair_bonus(board, color):
    """Returns 1 if player has both bishops, else 0."""
    return 1 if len(board.pieces(chess.BISHOP, color)) >= 2 else 0


# -------------------------------
# OPEN FILE CONTROL
# -------------------------------
def get_open_file_control(board, color):
    """Counts rooks/queens on open files (no pawns present)."""
    controlled = 0
    for piece_type in [chess.ROOK, chess.QUEEN]:
        for sq in board.pieces(piece_type, color):
            file = chess.square_file(sq)
            pawns_in_file = any(
                board.piece_at(chess.square(file, rank)) and 
                board.piece_at(chess.square(file, rank)).piece_type == chess.PAWN
                for rank in range(8)
            )
            if not pawns_in_file:
                controlled += 1
    return controlled


# -------------------------------
# SPACE ADVANTAGE
# -------------------------------
def get_space_advantage(board, color):
    """Counts how many squares in opponent’s half are controlled."""
    half_ranks = range(4,8) if color == chess.WHITE else range(0,4)
    control = 0
    for rank in half_ranks:
        for file in range(8):
            sq = chess.square(file, rank)
            if board.is_attacked_by(color, sq):
                control += 1
    return control


# -------------------------------
# WEAK SQUARES
# -------------------------------
def get_weak_squares(board, color):
    """Counts central weak squares not controlled by player."""
    weak = 0
    center = [chess.D4, chess.D5, chess.E4, chess.E5]
    for sq in center:
        if not board.is_attacked_by(color, sq) and not board.piece_at(sq):
            weak += 1
    return weak


# -------------------------------
# OUTPOSTS
# -------------------------------
def get_outposts(board, color):
    """Counts knight outposts (safe squares in enemy territory)."""
    outposts = 0
    knights = board.pieces(chess.KNIGHT, color)
    for n in knights:
        for sq in chess.SquareSet(chess.BB_KNIGHT_ATTACKS[n]):
            if not board.is_attacked_by(not color, sq):
                outposts += 1
    return outposts


# -------------------------------
# PINNED PIECES
# -------------------------------
def get_pinned_pieces(board, color):
    """Counts how many pieces of this color are pinned."""
    return sum(1 for sq in board.pieces(chess.PAWN, color) | board.pieces(chess.KNIGHT, color) |
               board.pieces(chess.BISHOP, color) | board.pieces(chess.ROOK, color) |
               board.pieces(chess.QUEEN, color)
               if board.is_pinned(color, sq))


# -------------------------------
# ATTACKED vs DEFENDED
# -------------------------------
def get_attacked_vs_defended_balance(board, color):
    """Counts how many squares are attacked vs defended."""
    attacked = defended = 0
    for sq, piece in board.piece_map().items():
        if board.is_attacked_by(not color, sq):
            attacked += 1
        if board.is_attacked_by(color, sq):
            defended += 1
    return {"attacked": attacked, "defended": defended}


# -------------------------------
# CASTLING STATUS
# -------------------------------
def get_castling_status(board, color):
    """Returns True if castling rights available."""
    return board.has_castling_rights(color)


# -------------------------------
# KING ZONE CONTROL
# -------------------------------
def get_king_zone_control(board, color):
    """Counts controlled squares in king’s immediate zone."""
    king_sq = board.king(color)
    zone = chess.SquareSet(chess.BB_KING_ATTACKS[king_sq])
    control = sum(board.is_attacked_by(color, sq) for sq in zone)
    return control


# -------------------------------
# ROOK ON 7TH RANK
# -------------------------------
def get_rook_on_7th_rank(board, color):
    """Counts rooks on 7th rank (very strong attacking position)."""
    rank = 6 if color == chess.WHITE else 1
    return sum(1 for sq in board.pieces(chess.ROOK, color) if chess.square_rank(sq) == rank)


# -------------------------------
# CONNECTED ROOKS
# -------------------------------
def get_connected_rooks(board, color):
    """Checks if rooks are connected (support each other)."""
    rooks = list(board.pieces(chess.ROOK, color))
    return 1 if len(rooks) == 2 and board.is_attacked_by(color, rooks[0]) and board.is_attacked_by(color, rooks[1]) else 0


# -------------------------------
# PASSED PAWN ADVANCEMENT
# -------------------------------
def get_passed_pawn_advancement(board, color):
    """Measures how far passed pawns have advanced."""
    pawns = board.pieces(chess.PAWN, color)
    advancement = 0
    for sq in pawns:
        if not any(board.piece_at(chess.square(chess.square_file(sq), r))
                   and board.piece_at(chess.square(chess.square_file(sq), r)).color != color
                   for r in range(chess.square_rank(sq)+1, 8)):
            advancement += chess.square_rank(sq)
    return advancement


# -------------------------------
# PAWN SHIELD
# -------------------------------
def get_pawn_shield(board, color):
    """Counts pawns protecting the king (pawn shield)."""
    king_sq = board.king(color)
    rank = chess.square_rank(king_sq)
    file = chess.square_file(king_sq)
    front_rank = rank+1 if color == chess.WHITE else rank-1
    files = [file-1, file, file+1]
    shield = 0
    for f in files:
        if 0 <= f < 8 and 0 <= front_rank < 8:
            sq = chess.square(f, front_rank)
            piece = board.piece_at(sq)
            if piece and piece.color == color and piece.piece_type == chess.PAWN:
                shield += 1
    return shield


# -------------------------------
# BACKWARD PAWNS
# -------------------------------
def get_backward_pawns(board, color):
    """Counts backward pawns (no supporting pawns behind)."""
    pawns = board.pieces(chess.PAWN, color)
    backward = 0
    for p in pawns:
        file = chess.square_file(p)
        rank = chess.square_rank(p)
        supporters = [chess.square(file-1, rank-1), chess.square(file+1, rank-1)]
        if color == chess.BLACK:
            supporters = [chess.square(file-1, rank+1), chess.square(file+1, rank+1)]
        if all((s < 0 or s >= 64 or not board.piece_at(s) or board.piece_at(s).piece_type != chess.PAWN) for s in supporters):
            backward += 1
    return backward


# -------------------------------
# ISOLATED WEAKNESS CLUSTERS
# -------------------------------
def get_isolated_weakness_clusters(board, color):
    """Counts clusters of isolated pawns (weak pawn groups)."""
    pawns = list(board.pieces(chess.PAWN, color))
    files = [chess.square_file(p) for p in pawns]
    clusters = 0
    for f in set(files):
        if all(abs(f - other) > 1 for other in set(files) if other != f):
            clusters += 1
    return clusters


# ==============================================================
# MAIN FEATURE COLLECTION
# ==============================================================
white_material, black_material = get_material(board)
white_king_safety = get_king_safety(board, chess.WHITE)
black_king_safety = get_king_safety(board, chess.BLACK)

features = {
    "material": {"white": white_material, "black": black_material},
    "mobility": get_mobility(board),
    "king_safety": {"white": white_king_safety, "black": black_king_safety},
    "pawn_structure": {
        "white": get_pawn_structure(board, chess.WHITE),
        "black": get_pawn_structure(board, chess.BLACK)
    },
    "center_control": {
        "white": get_center_control(board, chess.WHITE),
        "black": get_center_control(board, chess.BLACK)
    },
    "development": {
        "white": get_development(board, chess.WHITE),
        "black": get_development(board, chess.BLACK)
    },
    "rook_activity": {
        "white": get_rook_activity(board, chess.WHITE),
        "black": get_rook_activity(board, chess.BLACK)
    },
    "threats": {
        "white": get_hanging_pieces(board, chess.WHITE),
        "black": get_hanging_pieces(board, chess.BLACK)
    },
    "piece_activity": {
        "white": get_piece_activity(board, chess.WHITE),
        "black": get_piece_activity(board, chess.BLACK)
    },
    "piece_coordination": {
        "white": get_piece_coordination(board, chess.WHITE),
        "black": get_piece_coordination(board, chess.BLACK)
    },
    "bishop_pair_bonus": {
        "white": get_bishop_pair_bonus(board, chess.WHITE),
        "black": get_bishop_pair_bonus(board, chess.BLACK)
    },
    "open_file_control": {
        "white": get_open_file_control(board, chess.WHITE),
        "black": get_open_file_control(board, chess.BLACK)
    },
    "space_advantage": {
        "white": get_space_advantage(board, chess.WHITE),
        "black": get_space_advantage(board, chess.BLACK)
    },
    "weak_squares": {
        "white": get_weak_squares(board, chess.WHITE),
        "black": get_weak_squares(board, chess.BLACK)
    },
    "outposts": {
        "white": get_outposts(board, chess.WHITE),
        "black": get_outposts(board, chess.BLACK)
    },
    "pinned_pieces": {
        "white": get_pinned_pieces(board, chess.WHITE),
        "black": get_pinned_pieces(board, chess.BLACK)
    },
    "attacked_vs_defended": {
        "white": get_attacked_vs_defended_balance(board, chess.WHITE),
        "black": get_attacked_vs_defended_balance(board, chess.BLACK)
    },
    "castling_status": {
        "white": get_castling_status(board, chess.WHITE),
        "black": get_castling_status(board, chess.BLACK)
    },
    "king_zone_control": {
        "white": get_king_zone_control(board, chess.WHITE),
        "black": get_king_zone_control(board, chess.BLACK)
    },
    "rook_on_7th_rank": {
        "white": get_rook_on_7th_rank(board, chess.WHITE),
        "black": get_rook_on_7th_rank(board, chess.BLACK)
    },
    "connected_rooks": {
        "white": get_connected_rooks(board, chess.WHITE),
        "black": get_connected_rooks(board, chess.BLACK)
    },
    "passed_pawn_advancement": {
        "white": get_passed_pawn_advancement(board, chess.WHITE),
        "black": get_passed_pawn_advancement(board, chess.BLACK)
    },
    "pawn_shield": {
        "white": get_pawn_shield(board, chess.WHITE),
        "black": get_pawn_shield(board, chess.BLACK)
    },
    "backward_pawns": {
        "white": get_backward_pawns(board, chess.WHITE),
        "black": get_backward_pawns(board, chess.BLACK)
    },
    "isolated_weakness_clusters": {
        "white": get_isolated_weakness_clusters(board, chess.WHITE),
        "black": get_isolated_weakness_clusters(board, chess.BLACK)
    }
}

# --- Print All Features ---
print("Abstract Features:")
for k, v in features.items():
    print(f"- {k}: {v}")








































# import chess

# # === Yahan apna FEN dalna hai ===
# fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
# board = chess.Board(fen)

# # --- Material values ---
# piece_values = {
#     chess.PAWN: 1,
#     chess.KNIGHT: 3,
#     chess.BISHOP: 3,
#     chess.ROOK: 5,
#     chess.QUEEN: 9,
#     chess.KING: 0
# }

# def get_material(board):
#     white_material = black_material = 0
#     for square in chess.SQUARES:
#         piece = board.piece_at(square)
#         if piece:
#             val = piece_values[piece.piece_type]
#             if piece.color == chess.WHITE:
#                 white_material += val
#             else:
#                 black_material += val
#     return white_material, black_material

# def get_mobility(board):
#     return len(list(board.legal_moves))

# def get_king_safety(board, color):
#     king_sq = board.king(color)
#     castled = board.has_castling_rights(color) is False
#     unsafe = 0
#     for sq in chess.SquareSet(chess.BB_KING_ATTACKS[king_sq]):
#         if board.is_attacked_by(not color, sq):
#             unsafe += 1
#     return "Safe" if unsafe <= 2 and castled else "Exposed"

# def get_pawn_structure(board, color):
#     pawns = board.pieces(chess.PAWN, color)
#     files = [chess.square_file(sq) for sq in pawns]
#     doubled = sum(files.count(f) > 1 for f in set(files))
#     isolated = sum(
#         all(abs(f - other) > 1 for other in set(files) if other != f)
#         for f in set(files)
#     )
#     passed = 0
#     for sq in pawns:
#         rank = chess.square_rank(sq)
#         file = chess.square_file(sq)
#         blocked = False
#         for ahead in range(rank+1, 8):
#             front = chess.square(file, ahead)
#             if board.piece_at(front) and board.piece_at(front).color != color:
#                 blocked = True
#         if not blocked:
#             passed += 1
#     return {"doubled": doubled, "isolated": isolated, "passed": passed}

# def get_center_control(board, color):
#     center = [chess.D4, chess.D5, chess.E4, chess.E5]
#     return sum(board.is_attacked_by(color, sq) for sq in center)

# def get_development(board, color):
#     developed = 0
#     minors = board.pieces(chess.KNIGHT, color) | board.pieces(chess.BISHOP, color)
#     for sq in minors:
#         rank = chess.square_rank(sq)
#         if (color == chess.WHITE and rank > 0) or (color == chess.BLACK and rank < 7):
#             developed += 1
#     return developed

# def get_rook_activity(board, color):
#     rooks = board.pieces(chess.ROOK, color)
#     active = 0
#     for r in rooks:
#         file = chess.square_file(r)
#         has_pawn = any(board.piece_at(chess.square(file, rank)) 
#                        and board.piece_at(chess.square(file, rank)).piece_type == chess.PAWN
#                        for rank in range(8))
#         if not has_pawn:
#             active += 1
#     return active

# def get_hanging_pieces(board, color):
#     hanging = 0
#     for sq, piece in board.piece_map().items():
#         if piece.color == color:
#             if not board.is_attacked_by(color, sq) and board.is_attacked_by(not color, sq):
#                 hanging += 1
#     return hanging

# def get_piece_activity(board, color):
#     return sum(1 for move in board.legal_moves if board.color_at(move.from_square) == color)

# def get_piece_coordination(board, color):
#     defended = 0
#     for sq, piece in board.piece_map().items():
#         if piece.color == color and board.is_attacked_by(color, sq):
#             defended += 1
#     return defended

# def get_bishop_pair_bonus(board, color):
#     return 1 if len(board.pieces(chess.BISHOP, color)) >= 2 else 0

# def get_open_file_control(board, color):
#     controlled = 0
#     for piece_type in [chess.ROOK, chess.QUEEN]:
#         for sq in board.pieces(piece_type, color):
#             file = chess.square_file(sq)
#             pawns_in_file = any(
#                 board.piece_at(chess.square(file, rank)) and 
#                 board.piece_at(chess.square(file, rank)).piece_type == chess.PAWN
#                 for rank in range(8)
#             )
#             if not pawns_in_file:
#                 controlled += 1
#     return controlled

# def get_space_advantage(board, color):
#     half_ranks = range(4,8) if color == chess.WHITE else range(0,4)
#     control = 0
#     for rank in half_ranks:
#         for file in range(8):
#             sq = chess.square(file, rank)
#             if board.is_attacked_by(color, sq):
#                 control += 1
#     return control

# def get_weak_squares(board, color):
#     weak = 0
#     center = [chess.D4, chess.D5, chess.E4, chess.E5]
#     for sq in center:
#         if not board.is_attacked_by(color, sq) and not board.piece_at(sq):
#             weak += 1
#     return weak

# def get_outposts(board, color):
#     outposts = 0
#     knights = board.pieces(chess.KNIGHT, color)
#     for n in knights:
#         for sq in chess.SquareSet(chess.BB_KNIGHT_ATTACKS[n]):
#             if not board.is_attacked_by(not color, sq):
#                 outposts += 1
#     return outposts

# def get_pinned_pieces(board, color):
#     return sum(1 for sq in board.pieces(chess.PAWN, color) | board.pieces(chess.KNIGHT, color) |
#                board.pieces(chess.BISHOP, color) | board.pieces(chess.ROOK, color) |
#                board.pieces(chess.QUEEN, color)
#                if board.is_pinned(color, sq))

# def get_attacked_vs_defended_balance(board, color):
#     attacked = defended = 0
#     for sq, piece in board.piece_map().items():
#         if board.is_attacked_by(not color, sq):
#             attacked += 1
#         if board.is_attacked_by(color, sq):
#             defended += 1
#     return {"attacked": attacked, "defended": defended}

# def get_castling_status(board, color):
#     return board.has_castling_rights(color)

# def get_king_zone_control(board, color):
#     king_sq = board.king(color)
#     zone = chess.SquareSet(chess.BB_KING_ATTACKS[king_sq])
#     control = sum(board.is_attacked_by(color, sq) for sq in zone)
#     return control

# def get_rook_on_7th_rank(board, color):
#     rank = 6 if color == chess.WHITE else 1
#     return sum(1 for sq in board.pieces(chess.ROOK, color) if chess.square_rank(sq) == rank)

# def get_connected_rooks(board, color):
#     rooks = list(board.pieces(chess.ROOK, color))
#     return 1 if len(rooks) == 2 and board.is_attacked_by(color, rooks[0]) and board.is_attacked_by(color, rooks[1]) else 0

# def get_passed_pawn_advancement(board, color):
#     pawns = board.pieces(chess.PAWN, color)
#     advancement = 0
#     for sq in pawns:
#         if not any(board.piece_at(chess.square(chess.square_file(sq), r))
#                    and board.piece_at(chess.square(chess.square_file(sq), r)).color != color
#                    for r in range(chess.square_rank(sq)+1, 8)):
#             advancement += chess.square_rank(sq)
#     return advancement

# def get_pawn_shield(board, color):
#     king_sq = board.king(color)
#     rank = chess.square_rank(king_sq)
#     file = chess.square_file(king_sq)
#     front_rank = rank+1 if color == chess.WHITE else rank-1
#     files = [file-1, file, file+1]
#     shield = 0
#     for f in files:
#         if 0 <= f < 8 and 0 <= front_rank < 8:
#             sq = chess.square(f, front_rank)
#             piece = board.piece_at(sq)
#             if piece and piece.color == color and piece.piece_type == chess.PAWN:
#                 shield += 1
#     return shield

# def get_backward_pawns(board, color):
#     pawns = board.pieces(chess.PAWN, color)
#     backward = 0
#     for p in pawns:
#         file = chess.square_file(p)
#         rank = chess.square_rank(p)
#         supporters = [chess.square(file-1, rank-1), chess.square(file+1, rank-1)]
#         if color == chess.BLACK:
#             supporters = [chess.square(file-1, rank+1), chess.square(file+1, rank+1)]
#         if all((s < 0 or s >= 64 or not board.piece_at(s) or board.piece_at(s).piece_type != chess.PAWN) for s in supporters):
#             backward += 1
#     return backward

# def get_isolated_weakness_clusters(board, color):
#     pawns = list(board.pieces(chess.PAWN, color))
#     files = [chess.square_file(p) for p in pawns]
#     clusters = 0
#     for f in set(files):
#         if all(abs(f - other) > 1 for other in set(files) if other != f):
#             clusters += 1
#     return clusters

# white_material, black_material = get_material(board)
# white_king_safety = get_king_safety(board, chess.WHITE)
# black_king_safety = get_king_safety(board, chess.BLACK)

# features = {
#     "material": {"white": white_material, "black": black_material},
#     "mobility": get_mobility(board),
#     "king_safety": {"white": white_king_safety, "black": black_king_safety},
#     "pawn_structure": {
#         "white": get_pawn_structure(board, chess.WHITE),
#         "black": get_pawn_structure(board, chess.BLACK)
#     },
#     "center_control": {
#         "white": get_center_control(board, chess.WHITE),
#         "black": get_center_control(board, chess.BLACK)
#     },
#     "development": {
#         "white": get_development(board, chess.WHITE),
#         "black": get_development(board, chess.BLACK)
#     },
#     "rook_activity": {
#         "white": get_rook_activity(board, chess.WHITE),
#         "black": get_rook_activity(board, chess.BLACK)
#     },
#     "threats": {
#         "white": get_hanging_pieces(board, chess.WHITE),
#         "black": get_hanging_pieces(board, chess.BLACK)
#     },
#     "piece_activity": {
#         "white": get_piece_activity(board, chess.WHITE),
#         "black": get_piece_activity(board, chess.BLACK)
#     },
#     "piece_coordination": {
#         "white": get_piece_coordination(board, chess.WHITE),
#         "black": get_piece_coordination(board, chess.BLACK)
#     },
#     "bishop_pair_bonus": {
#         "white": get_bishop_pair_bonus(board, chess.WHITE),
#         "black": get_bishop_pair_bonus(board, chess.BLACK)
#     },
#     "open_file_control": {
#         "white": get_open_file_control(board, chess.WHITE),
#         "black": get_open_file_control(board, chess.BLACK)
#     },
#     "space_advantage": {
#         "white": get_space_advantage(board, chess.WHITE),
#         "black": get_space_advantage(board, chess.BLACK)
#     },
#     "weak_squares": {
#         "white": get_weak_squares(board, chess.WHITE),
#         "black": get_weak_squares(board, chess.BLACK)
#     },
#     "outposts": {
#         "white": get_outposts(board, chess.WHITE),
#         "black": get_outposts(board, chess.BLACK)
#     },
#     "pinned_pieces": {
#         "white": get_pinned_pieces(board, chess.WHITE),
#         "black": get_pinned_pieces(board, chess.BLACK)
#     },
#     "attacked_vs_defended": {
#         "white": get_attacked_vs_defended_balance(board, chess.WHITE),
#         "black": get_attacked_vs_defended_balance(board, chess.BLACK)
#     },
#     "castling_status": {
#         "white": get_castling_status(board, chess.WHITE),
#         "black": get_castling_status(board, chess.BLACK)
#     },
#     "king_zone_control": {
#         "white": get_king_zone_control(board, chess.WHITE),
#         "black": get_king_zone_control(board, chess.BLACK)
#     },
#     "rook_on_7th_rank": {
#         "white": get_rook_on_7th_rank(board, chess.WHITE),
#         "black": get_rook_on_7th_rank(board, chess.BLACK)
#     },
#     "connected_rooks": {
#         "white": get_connected_rooks(board, chess.WHITE),
#         "black": get_connected_rooks(board, chess.BLACK)
#     },
#     "passed_pawn_advancement": {
#         "white": get_passed_pawn_advancement(board, chess.WHITE),
#         "black": get_passed_pawn_advancement(board, chess.BLACK)
#     },
#     "pawn_shield": {
#         "white": get_pawn_shield(board, chess.WHITE),
#         "black": get_pawn_shield(board, chess.BLACK)
#     },
#     "backward_pawns": {
#         "white": get_backward_pawns(board, chess.WHITE),
#         "black": get_backward_pawns(board, chess.BLACK)
#     },
#     "isolated_weakness_clusters": {
#         "white": get_isolated_weakness_clusters(board, chess.WHITE),
#         "black": get_isolated_weakness_clusters(board, chess.BLACK)
#     }
# }

# # --- Print All Features ---
# print("Abstract Features:")
# for k, v in features.items():
#     print(f"- {k}: {v}")
