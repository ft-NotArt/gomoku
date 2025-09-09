# Game
BOARD_SIZE = 19  # Traditional Go board is 19x19
WIN_LINE = 5

NOT_SELECTED = 0
BLACK = 1
WHITE = 2

DIRECTIONS = [
	(1, 0),		# Horizontal	#|/
	(0, 1),		# Vertical		#*-
	(1, 1),		# Diagonal		##\
	(1, -1),	# Anti-diagonal
]

FREE_THREES = [
	[0, 0, 1, 1, 1, 0],
	[0, 1, 1, 1, 0, 0],
	[0, 1, 0, 1, 1, 0],
	[0, 1, 1, 0, 1, 0],
]


# Window display
BOARD_WIDTH = BOARD_SIZE * 40  # Total board width/height
BOARD_PADDING = 30
LINE_SPACING = BOARD_WIDTH / (BOARD_SIZE - 1)
WINDOW_SIZE = BOARD_WIDTH + BOARD_PADDING * 2