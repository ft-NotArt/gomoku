from const import *
import random

def ai_move(board):
	posX = random.randint(0, 18)
	posY = random.randint(0, 18)
	while board.buttons[posY][posX].state != NOT_SELECTED or board.is_double_three_move(posX, posY) :
		posX = random.randint(0, 18)
		posY = random.randint(0, 18)
	return posX, posY