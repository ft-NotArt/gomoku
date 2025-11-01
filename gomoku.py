import pyglet
from pyglet import gl
from board import Board
from const import *


window = pyglet.window.Window(WINDOW_SIZE + 500, WINDOW_SIZE)

# Set background color to camel
gl.glClearColor(0.757, 0.604, 0.420, 1.0)

board = Board()

# Modes de jeu (décommente ce que tu veux) :
# board.enable_ai(WHITE)          # Humain vs IA (IA = blancs)
board.enable_ai(BLACK)          # IA vs Humain (IA = noirs)
# board.enable_ai_vs_ai(4, 4)     # IA vs IA équilibrée
# board.enable_ai_vs_ai(8, 8)     # IA vs IA déséquilibrée



@window.event
def on_draw():
	window.clear()
	board.batch.draw() # Draw everything in the batch (lines + button)

# Handle mouse events for button interaction
@window.event
def on_mouse_press(x, y, button_pressed, modifiers):
	if board.turn == board.ai_turn: # prevent the player from playing during AI reflexion time
		return
	for row in board.buttons:
		for button in row:
			button.on_mouse_press(x, y, button_pressed, modifiers)

@window.event
def on_mouse_release(x, y, button_pressed, modifiers):
	for row in board.buttons:
		for button in row:
			button.on_mouse_release(x, y, button_pressed, modifiers)

@window.event
def on_mouse_motion(x, y, dx, dy):
	for row in board.buttons:
		for button in row:
				button.on_mouse_motion(x, y, dx, dy)

@window.event
def on_key_press(symbol, modifiers):
	# Contrôles IA avec le clavier
	if symbol == pyglet.window.key.A:  # IA blancs
		board.enable_ai(WHITE)
	elif symbol == pyglet.window.key.B:  # IA noirs
		board.enable_ai(BLACK)
	elif symbol == pyglet.window.key.V:  # IA vs IA équilibrée
		board.enable_ai_vs_ai(4, 4)
	elif symbol == pyglet.window.key.W:  # IA vs IA déséquilibrée (blanc plus fort)
		board.enable_ai_vs_ai(3, 5)
	elif symbol == pyglet.window.key.D:  # Désactiver IA
		board.disable_ai()
		board.ai_vs_ai = False
	elif symbol == pyglet.window.key.R:  # Restart
		board.__init__()

pyglet.app.run()