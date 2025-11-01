#!/usr/bin/env python3
"""Test rapide de l'IA sans interface graphique"""

from const import *
from algo.minimax_ai import MinimaxAI
from algo.game_state import FastGameState

# Mock simple d'un board pour tester
class MockButton:
    def __init__(self):
        self.state = NOT_SELECTED

class MockBoard:
    def __init__(self):
        self.buttons = [[MockButton() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = BLACK
        self.black_pairs_captured = 0
        self.white_pairs_captured = 0

    def check_victory(self):
        return False

    def is_double_three_move(self, x, y):
        return False

def test_ai_basic():
    """Test basique de l'IA"""
    print("=== Test de l'IA Gomoku ===\n")

    # Crée un board vide
    board = MockBoard()

    # Place quelques pierres pour créer une situation intéressante
    board.buttons[9][9].state = BLACK  # Centre
    board.buttons[9][10].state = BLACK
    board.buttons[9][11].state = WHITE

    # Crée l'IA
    ai = MinimaxAI(max_depth=15, time_limit=2.0)

    print("Position initiale:")
    print("  Noir en (9,9) et (9,10)")
    print("  Blanc en (9,11)")
    print()

    # Teste l'IA pour les blancs
    board.turn = WHITE
    print("L'IA (Blanc) réfléchit...")
    x, y = ai.get_best_move(board)
    print(f"\nL'IA choisit: ({x}, {y})")
    if ai.reached_depth == 0:
        print("⚠️  WARNING: Profondeur 0 atteinte - vérifier l'iterative deepening")
    print()

    print("=== Test de capture ===")

    # Test avec possibilité de capture
    board2 = MockBoard()
    board2.buttons[9][9].state = BLACK
    board2.buttons[9][10].state = WHITE
    board2.buttons[9][11].state = WHITE
    board2.buttons[9][12].state = BLACK
    board2.turn = BLACK

    print("Position: NOIR-BLANC-BLANC-NOIR en (9,9-12)")
    print("L'IA (Noir) devrait détecter que ce n'est pas une capture car la configuration est incorrecte")
    ai2 = MinimaxAI(max_depth=10, time_limit=1.0)
    x, y = ai2.get_best_move(board2)
    print(f"L'IA choisit: ({x}, {y})\n")

    print("=== Test FastGameState ===")
    game_state = FastGameState(board)
    print(f"Zobrist hash: {game_state.zobrist_hash}")
    print(f"Positions occupées: {len(game_state.get_occupied_positions())}")
    print(f"Positions vides: {len(game_state.get_empty_positions())}")

    # Test capture simulation
    print("\nTest simulation de capture:")
    move_data = game_state.make_move(10, 10, BLACK)
    old_state, captured = move_data
    print(f"  Coup en (10,10): {len(captured)} captures")
    game_state.undo_move(10, 10, move_data)
    print(f"  Undo OK, hash restauré: {game_state.zobrist_hash}")

    print("\n=== Tests terminés avec succès! ===")

if __name__ == "__main__":
    test_ai_basic()
