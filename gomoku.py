import pyglet
from pyglet import gl
from pyglet.gui import PushButton

# Go board configuration
BOARD_SIZE = 19  # Traditional Go board is 19x19
BOARD_WIDTH = BOARD_SIZE * 40  # Total board width/height
BOARD_PADDING = 30
LINE_SPACING = BOARD_WIDTH / (BOARD_SIZE - 1)

class CustomButton(PushButton):
	def on_press(self, button):
		super().on_press(self)
		print("Button was clicked!")
		# To permanently change the unpressed image, you need to update both the image and the sprite
		self._unpressed_img = black_img
		self._hover_img = black_img
		# self._sprite.image = black_img

WINDOW_SIZE = BOARD_WIDTH + BOARD_PADDING * 2
window = pyglet.window.Window(WINDOW_SIZE + 500, WINDOW_SIZE)

# Set background color to camel #C19A6B
gl.glClearColor(0.757, 0.604, 0.420, 1.0)  # Camel background


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

# Create a batch for GUI elements
batch = pyglet.graphics.Batch()

board_buttons = []

# Create the button and add it to the batch
for x in range(BOARD_SIZE):
	for y in range(BOARD_SIZE):
		button = CustomButton(x=BOARD_PADDING - (LINE_SPACING / 2) + (x * LINE_SPACING), y=BOARD_PADDING - (LINE_SPACING / 2) + (y * LINE_SPACING),
						pressed=black_img, unpressed=white_img, hover=black_white_img, batch=batch)
		board_buttons.append(button)

# Create board lines once and store them
board_lines = []

# Draw vertical lines
for i in range(BOARD_SIZE):
	x = BOARD_PADDING + i * LINE_SPACING
	line = pyglet.shapes.Line(x, BOARD_PADDING, x, BOARD_PADDING + BOARD_WIDTH, color=(51, 25, 0), batch=batch)
	board_lines.append(line)

# Draw horizontal lines  
for i in range(BOARD_SIZE):
	y = BOARD_PADDING + i * LINE_SPACING
	line = pyglet.shapes.Line(BOARD_PADDING, y, BOARD_PADDING + BOARD_WIDTH, y, color=(51, 25, 0), batch=batch)
	board_lines.append(line)

@window.event
def on_draw():
	window.clear()
	batch.draw()  # Draw everything in the batch (lines + button)

# Handle mouse events for button interaction
@window.event
def on_mouse_press(x, y, button_pressed, modifiers):
	print(f"Screen was clicked at {x, y}!")
	for button in board_buttons:
		button.on_mouse_press(x, y, button_pressed, modifiers)

@window.event
def on_mouse_release(x, y, button_pressed, modifiers):
	for button in board_buttons:
		button.on_mouse_release(x, y, button_pressed, modifiers)

@window.event
def on_mouse_motion(x, y, dx, dy):
	for button in board_buttons:
		button.on_mouse_motion(x, y, dx, dy)

pyglet.app.run()