import pyglet
from const import *
from button import CustomButton

def check_bounds(x, y, dx, dy, length):
	return (x + dx * (length - 1) < BOARD_SIZE
		and y + dy * (length - 1) < BOARD_SIZE
		and x + dx * (length - 1) >= 0
		and y + dy * (length - 1) >= 0)

class Board():
	def __init__(self):
		self.turn = BLACK
		self.black_pairs_captured = 0
		self.white_pairs_captured = 0

		self.batch = pyglet.graphics.Batch()

		self.board_lines = [] # This is needed to keep every line in memory
		for i in range(BOARD_SIZE):
			xy = BOARD_PADDING + i * LINE_SPACING
			line = pyglet.shapes.Line(xy, BOARD_PADDING, xy, BOARD_PADDING + BOARD_WIDTH, color=(51, 25, 0), batch=self.batch)
			self.board_lines.append(line)
			line = pyglet.shapes.Line(BOARD_PADDING, xy, BOARD_PADDING + BOARD_WIDTH, xy, color=(51, 25, 0), batch=self.batch)
			self.board_lines.append(line)

		# Buttons need to be added to the batch after the lines so that they're on top of them
		self.buttons = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)] # This is also needed to keep every button in memory
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				x = BOARD_PADDING - (LINE_SPACING / 2) + (col * LINE_SPACING)
				y = BOARD_PADDING - (LINE_SPACING / 2) + (row * LINE_SPACING)
				self.buttons[row][col] = CustomButton(x, y, col, row, self.batch, self)


	def change_turn(self):
		# Checks for victory before changing turn (player)
		winner = self.check_victory()
		if winner is not False :
			print(f'{"White" if (winner == WHITE) else "Black"} player wins !')
			pyglet.app.exit()
			return
		
		self.turn = WHITE if (self.turn == BLACK) else BLACK # Alternate between black and white turns
		
		for row in self.buttons:
			for button in row:
				button.change_turn_img()


	def check_victory(self):
		if self.black_pairs_captured >= 5 :
			return BLACK
		if self.white_pairs_captured >= 5 :
			return WHITE
		
		prev_color = WHITE if (self.turn == BLACK) else BLACK # This is needed to keep win order, in case both players make a line of five
		for player in [prev_color, self.turn]:
			for x in range(BOARD_SIZE):
				for y in range(BOARD_SIZE):
					for dx, dy in DIRECTIONS:
						if self.check_line(x, y, dx, dy, player):
							if player != self.turn : # As the winning player is about to play, there's no way for him to lose his five in a row.
								return player

							# Check if the winning line can be broken by a capture
							for i in range(WIN_LINE):
								if (self.is_capturable(x + (dx * i), y + (dy * i))):
									self.buttons[y + (dy * i)][x + (dx * i)].state = NOT_SELECTED
									ineluctable_win = self.check_victory()
									self.buttons[y + (dy * i)][x + (dx * i)].state = player
									if not ineluctable_win :
										return False

							return player
		return False


	def check_line(self, x, y, dx, dy, player):
		if not check_bounds(x, y, dx, dy, WIN_LINE):
			return False

		for i in range(WIN_LINE):
			if self.buttons[y + i * dy][x + i * dx].state != player :
				return False
		return True


	def is_capturable(self, x, y):
		color = self.buttons[y][x].state
		opp_color = WHITE if (color == BLACK) else BLACK
		if color == NOT_SELECTED :
			return False
		
		for dx, dy in DIRECTIONS:
			for dir in [1, -1]: # Double the directions, to have every possible one
				if (not check_bounds(x, y, (dx * dir), (dy * dir), 3) or not check_bounds(x, y, (dx * -dir), (dy * -dir), 2)):
					continue

				if (self.buttons[y + (dy * dir)][x + (dx * dir)].state == color):
					color_behind = self.buttons[y + (dy * -dir)][x + (dx * -dir)].state
					color_ahead = self.buttons[y + (dy * dir * 2)][x + (dx * dir * 2)].state

					if ((color_behind == opp_color and color_ahead == NOT_SELECTED)
					or	(color_behind == NOT_SELECTED and color_ahead == opp_color)): # Could've went for a full one line if but chose clarity
						return True
		return False
	
	def is_capture_move(self, x, y, dx, dy):
		color = self.buttons[y][x].state
		opp_color = WHITE if (color == BLACK) else BLACK
		if color == NOT_SELECTED :
			return False
		
		if not check_bounds(x, y, dx, dy, 4):
			return False
		
		if (self.buttons[y + dy * 1][x + dx * 1].state == opp_color
		and self.buttons[y + dy * 2][x + dx * 2].state == opp_color
		and self.buttons[y + dy * 3][x + dx * 3].state == color):
			return True
		
		return False
	
	def capture(self, x, y):
		for dx, dy in DIRECTIONS:
			for dir in [1, -1]: # Double the directions, to have every possible one
				if self.is_capture_move(x, y, (dx * dir), (dy * dir)):
					self.buttons[y + (dy * dir * 1)][x + (dx * dir * 1)].reset()
					self.buttons[y + (dy * dir * 2)][x + (dx * dir * 2)].reset()
	
					if self.turn == BLACK :
						self.black_pairs_captured += 1
					else:
						self.white_pairs_captured += 1
