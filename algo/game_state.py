import numpy as np
from const import *

class FastGameState:
    """État du jeu optimisé avec NumPy pour calculs rapides"""
    
    def __init__(self, board=None):
        if board is None:
            self.grid = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
            self.turn = BLACK
            self.black_captures = 0
            self.white_captures = 0
        else:
            self.sync_from_board(board)
    
    def sync_from_board(self, board):
        """Synchronise avec l'objet Board existant"""
        self.grid = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                self.grid[y, x] = board.buttons[y][x].state
        
        self.turn = board.turn
        self.black_captures = board.black_pairs_captured
        self.white_captures = board.white_pairs_captured
    
    def get_empty_positions(self):
        """Retourne les positions vides comme array NumPy"""
        empty = np.where(self.grid == NOT_SELECTED)
        return np.column_stack((empty[1], empty[0]))  # (x, y)
    
    def get_occupied_positions(self, player=None):
        """Retourne les positions occupées par un joueur"""
        if player is None:
            occupied = np.where(self.grid != NOT_SELECTED)
        else:
            occupied = np.where(self.grid == player)
        return np.column_stack((occupied[1], occupied[0]))  # (x, y)
    
    def is_valid_position(self, x, y):
        """Vérifie si une position est valide"""
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE
    
    def make_move(self, x, y, player):
        """Effectue un coup (temporaire)"""
        old_state = self.grid[y, x]
        self.grid[y, x] = player
        return old_state
    
    def undo_move(self, x, y, old_state):
        """Annule un coup"""
        self.grid[y, x] = old_state
    
    def count_consecutive(self, x, y, dx, dy, player, max_length=5):
        """Compte les pierres consécutives dans une direction avec NumPy"""
        count = 0
        for i in range(max_length):
            nx, ny = x + i * dx, y + i * dy
            if not self.is_valid_position(nx, ny):
                break
            if self.grid[ny, nx] == player:
                count += 1
            else:
                break
        return count
    
    def evaluate_direction_fast(self, x, y, dx, dy, player):
        """Évaluation rapide d'une direction avec slicing NumPy"""
        positions = []
        
        # Génère les positions dans la direction
        for i in range(-4, 5):  # Fenêtre de 9 cases
            nx, ny = x + i * dx, y + i * dy
            if self.is_valid_position(nx, ny):
                positions.append((nx, ny, self.grid[ny, nx]))
        
        if len(positions) < 5:
            return 0
        
        # Analyse des patterns avec NumPy
        values = np.array([p[2] for p in positions])
        score = 0
        
        # Cherche les alignements
        for start in range(len(values) - 4):
            window = values[start:start + 5]
            player_count = np.sum(window == player)
            empty_count = np.sum(window == NOT_SELECTED)
            
            if player_count + empty_count == 5:  # Pas d'adversaire dans la fenêtre
                if player_count == 5:
                    score += 100000  # Victoire
                elif player_count == 4:
                    score += 50000   # Menace critique
                elif player_count == 3:
                    score += 2000    # Forte menace
                elif player_count == 2:
                    score += 100     # Début prometteur
        
        return score
    
    def find_nearby_moves_vectorized(self, radius=2):
        """Trouve les coups candidats avec NumPy vectorisé"""
        occupied = self.get_occupied_positions()
        if len(occupied) == 0:
            return np.array([[BOARD_SIZE // 2, BOARD_SIZE // 2]])
        
        candidates = set()
        
        # Pour chaque position occupée, ajoute les voisins
        for x, y in occupied:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if (self.is_valid_position(nx, ny) and 
                        self.grid[ny, nx] == NOT_SELECTED):
                        candidates.add((nx, ny))
        
        return np.array(list(candidates))
    
