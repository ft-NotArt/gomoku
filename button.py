import pyglet
from pyglet.gui import PushButton
from const import *


def resize_image(img, size):
	new_img = img.get_texture()
	new_img.width = size
	new_img.height = size
	return new_img

def get_button_size_img(img_path):
	img = pyglet.image.load(img_path)
	return resize_image(img, int(LINE_SPACING))

# Load images from files
empty_img = get_button_size_img("img/empty.png")
black_img = get_button_size_img("img/black_stone.png")
white_img = get_button_size_img("img/white_stone.png")

class CustomButton(PushButton):
	def __init__(self, screen_x, screen_y, grid_x, grid_y, batch, board):
		super().__init__(screen_x, screen_y, pressed=black_img, unpressed=empty_img, hover=black_img, batch=batch)
		self.grid_x = grid_x
		self.grid_y = grid_y
		self.state = NOT_SELECTED
		self.board = board
	
	def on_press(self, button):
		super().on_press(self)
		if self.state != NOT_SELECTED:
			return
		
		if self.board.turn == BLACK:
			self._pressed_img = black_img
			self._unpressed_img = black_img
			self._hover_img = black_img
		else:
			self._pressed_img = white_img
			self._unpressed_img = white_img
			self._hover_img = white_img
		
		self.state = self.board.turn
		self.board.capture(self.grid_x, self.grid_y)
		self.board.change_turn()
	
	def change_turn_img(self):
		if self.state != NOT_SELECTED:
			return

		if self.board.turn == BLACK:
			self._pressed_img = black_img
			self._hover_img = black_img
		else:
			self._pressed_img = white_img
			self._hover_img = white_img
	
	def reset(self):
		self.state = NOT_SELECTED
		self._unpressed_img = empty_img
		self.change_turn_img() # Should already be called by board's change_turn_img loop, but why not
		self._sprite.image = empty_img # Forces the img update