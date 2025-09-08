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
	def __init__(self, x, y, batch, board):
		super().__init__(x, y, pressed=black_img, unpressed=empty_img, hover=black_img, batch=batch)
		self.state = NOT_SELECTED
		self.board = board
	
	def on_press(self, button):
		super().on_press(self)
		if self.state != NOT_SELECTED:
			return
		
		if self.board.turn == BLACK:
			self._unpressed_img = black_img
			self._pressed_img = black_img
			self._hover_img = black_img
		else:
			self._unpressed_img = white_img
			self._pressed_img = white_img
			self._hover_img = white_img
		
		self.state = self.board.turn
		self.board.change_turn()
	
	def change_turn_img(self):
		if self.state != NOT_SELECTED:
			return

		if self.board.turn == BLACK:
			self._hover_img = black_img
			self._pressed_img = black_img
		else:
			self._hover_img = white_img
			self._pressed_img = white_img