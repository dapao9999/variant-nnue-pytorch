RANKS = 10
FILES = 9
SQUARES = RANKS * FILES
KING_SQUARES = 9
PIECE_TYPES = 7
PIECES = 2 * PIECE_TYPES
USE_POCKETS = False
POCKETS = 2 * FILES if USE_POCKETS else 0

PIECE_VALUES = {
  1: 1276,
  2: 420,
  3: 800,
  4: 200,
  5: 520,
  6: 300,
}