import pyglet
from pyglet.gui import PushButton
from const import *


def resize_image(img, width, heigth):
	new_img = img.get_texture()
	new_img.width = width
	new_img.height = heigth
	return new_img

def get_gomoku_piece_sized_img(img_path):
	img = pyglet.image.load(img_path)
	return resize_image(img, int(LINE_SPACING), int(LINE_SPACING))

def get_settings_button_sized_img(img_path):
	img = pyglet.image.load(img_path)
	return resize_image(img, int(SET_BUT_W), int(SET_BUT_H))

# Load images from files
start_img = get_settings_button_sized_img("img/start.png")
j1_vs_ai_img = get_settings_button_sized_img("img/j1_vs_ai.png")
j1_vs_j2_img = get_settings_button_sized_img("img/j1_vs_j2.png")
empty_img = get_gomoku_piece_sized_img("img/empty.png")
black_img = get_gomoku_piece_sized_img("img/black_stone.png")
white_img = get_gomoku_piece_sized_img("img/white_stone.png")

class GomokuPieceButton(PushButton):
	def __init__(self, screen_x, screen_y, grid_x, grid_y, batch, board):
		super().__init__(screen_x, screen_y, pressed=black_img, unpressed=empty_img, hover=black_img, batch=batch)
		self.grid_x = grid_x
		self.grid_y = grid_y
		self.state = NOT_SELECTED
		self.board = board
	
	def on_press(self, widget):
		super().on_press(widget)
		if self.state != NOT_SELECTED:
			return
		
		self.state = self.board.turn # Need to change the button to clicked before checking for double-three
		if self.board.is_double_three_move(self.grid_x, self.grid_y):
			self.state = NOT_SELECTED
			print("Invalid move: double-three")
			return
		
		if self.board.turn == BLACK:
			self._pressed_img = black_img
			self._unpressed_img = black_img
			self._hover_img = black_img
		else:
			self._pressed_img = white_img
			self._unpressed_img = white_img
			self._hover_img = white_img
		
		# Force la mise à jour visuelle
		self._sprite.image = self._unpressed_img
		
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


class StartGameButton(PushButton):
	def __init__(self, screen_x, screen_y, batch, board):
		super().__init__(screen_x, screen_y, pressed=start_img, unpressed=start_img, hover=start_img, batch=batch)
		self.board = board

	def on_press(self, widget):
		super().on_press(widget)
		self.board.start_game()


class SetOpponentButton(PushButton):
	def __init__(self, ai_opp, screen_x, screen_y, batch, board):
		self.ai_opp = ai_opp
		self.board = board
		
		img = j1_vs_ai_img if (self.ai_opp) else j1_vs_j2_img
		super().__init__(screen_x, screen_y, pressed=img, unpressed=img, hover=img, batch=batch)

	def on_press(self, widget):
		super().on_press(widget)
		# TODO: adapt this to first player preference when button is created
		self.board.ai_turn = WHITE if (self.ai_opp) else NOT_SELECTED
		print(f"AI mode {'enabled' if (self.ai_opp) else 'disabled'}")