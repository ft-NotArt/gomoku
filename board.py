import pyglet
from const import *
from button import CustomButton

class Board():
	def __init__(self):
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
				self.buttons[row][col] = CustomButton(x, y, self.batch)
