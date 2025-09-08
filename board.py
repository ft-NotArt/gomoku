import pyglet
from const import *
from button import CustomButton

class Board():
	def __init__(self):
		self.turn = BLACK
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
				self.buttons[row][col] = CustomButton(x, y, self.batch, self)


	def change_turn(self):
		if self.check_victory():
			print(f'{"White" if (self.turn == WHITE) else "Black"} player wins !')
			pyglet.app.exit()
			return
		
		self.turn = WHITE if (self.turn == BLACK) else BLACK # Alternate between black and white turns
		
		for row in self.buttons:
			for button in row:
				button.change_turn_img()

	def check_victory(self):
		for x in range(BOARD_SIZE):
			for y in range(BOARD_SIZE):
				if (self.buttons[x][y].state == self.turn):
					if (self.check_horizontal_line(x, y)
					or	self.check_vertical_line(x, y)
					or	self.check_diagonal_line1(x, y)
					or	self.check_diagonal_line2(x, y)):
						return True
		return False

	def check_horizontal_line(self, x, y):
		if (BOARD_SIZE - x < 5):
			return False
	
		for i in range(5):
			if (self.buttons[x + i][y].state != self.turn):
				return False
		return True

	def check_vertical_line(self, x, y):
		if (BOARD_SIZE - y < 5):
			return False
	
		for i in range(5):
			if (self.buttons[x][y + i].state != self.turn):
				return False
		return True

	def check_diagonal_line1(self, x, y):
		if (BOARD_SIZE - x < 5 or BOARD_SIZE - y < 5):
			return False
	
		for i in range(5):
			if (self.buttons[x + i][y + i].state != self.turn):
				return False
		return True

	def check_diagonal_line2(self, x, y):
		if (BOARD_SIZE - x < 5 or BOARD_SIZE + y < 5):
			return False
	
		for i in range(5):
			if (self.buttons[x + i][y - i].state != self.turn):
				return False
		return True