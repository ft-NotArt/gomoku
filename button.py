import pyglet
from pyglet.gui import PushButton
from const import *


def resize_image(img, size):
	new_img = img.get_texture()
	new_img.width = size
	new_img.height = size
	return new_img

# Load images from files
black_white_img = pyglet.image.load("img/black_white_stone.png")
black_white_img = resize_image(black_white_img, int(LINE_SPACING))
black_img = pyglet.image.load("img/black_stone.png")
black_img = resize_image(black_img, int(LINE_SPACING))
white_img = pyglet.image.load("img/white_stone.png")
white_img = resize_image(white_img, int(LINE_SPACING))

class CustomButton(PushButton):
	def __init__(self, x, y, batch):
		super().__init__(x, y, pressed=black_img, unpressed=white_img, hover=black_white_img, batch=batch)
	def on_press(self, button):
		super().on_press(self)
		print("Button was clicked!")
		self._unpressed_img = black_img
		self._hover_img = black_img
