import pyglet
from pyglet import gl
from button import CustomButton
from board import Board
from const import *


window = pyglet.window.Window(WINDOW_SIZE + 500, WINDOW_SIZE)

# Set background color to camel
gl.glClearColor(0.757, 0.604, 0.420, 1.0)

board = Board()



@window.event
def on_draw():
	window.clear()
	board.batch.draw() # Draw everything in the batch (lines + button)

# Handle mouse events for button interaction
@window.event
def on_mouse_press(x, y, button_pressed, modifiers):
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

pyglet.app.run()