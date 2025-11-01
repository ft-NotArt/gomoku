import numpy as np
from const import *
from .game_state import FastGameState

class GameEvaluator:
    """Module d'évaluation séparé pour plus de lisibilité"""
    
    def __init__(self):
        self.pattern_scores = {
            5: 100000,   # Cinq alignés - victoire
            4: 50000,    # Quatre alignés - menace critique
            3: 1000,     # Trois alignés - forte menace  
            2: 50,       # Deux alignés - début d'attaque
        }
    
    def evaluate_position(self, board) -> float:
        """Évaluation principale"""
        game_state = FastGameState(board)
        
        player = board.turn
        opponent = WHITE if player == BLACK else BLACK
        
        # Évaluation vectorisée agressive
        player_score = self._evaluate_player_numpy(game_state, player)
        opponent_score = self._evaluate_player_numpy(game_state, opponent)
        
        # Bonus captures
        capture_bonus = self._get_capture_bonus(board, player)
        
        # DÉFENSE PRIORITAIRE : Si l'adversaire a une menace critique, la bloquer est vital
        opponent_threats = self._detect_critical_threats(game_state, opponent)
        defense_bonus = opponent_threats * 25000  # Très important
        
        # ATTAQUE AGRESSIVE : Favorise les formations offensives
        attack_bonus = self._calculate_attack_potential(game_state, player)
        
        return player_score - (opponent_score * 1.2) + capture_bonus + defense_bonus + attack_bonus
    
    
    def _get_capture_bonus(self, board, player: int) -> float:
        """Calcule le bonus des captures avec NumPy"""
        black_bonus = board.black_pairs_captured * 50
        white_bonus = board.white_pairs_captured * 50
        return black_bonus if player == BLACK else white_bonus
    
    
    def _evaluate_player_numpy(self, game_state: FastGameState, player: int) -> float:
        """Évaluation rapide d'un joueur avec NumPy"""
        score = 0
        
        # Récupère toutes les positions du joueur
        positions = game_state.get_occupied_positions(player)
        
        # Évalue chaque position avec toutes les directions
        directions = np.array(DIRECTIONS)
        
        for x, y in positions:
            for dx, dy in directions:
                score += game_state.evaluate_direction_fast(x, y, dx, dy, player)
        
        return score / 2  # Divise par 2 car chaque ligne est comptée dans les deux sens
    
    def quick_move_score_numpy(self, board, x: int, y: int) -> float:
        """Évaluation rapide optimisée avec NumPy"""
        game_state = FastGameState(board)
        player = board.turn

        # Simule le coup avec captures
        move_data = game_state.make_move(x, y, player)

        # Évalue seulement autour de la position jouée (optimisation)
        score = 0
        directions = np.array(DIRECTIONS)

        for dx, dy in directions:
            score += game_state.evaluate_direction_fast(x, y, dx, dy, player)

        # Bonus pour les captures
        _, captured = move_data
        if len(captured) > 0:
            score += len(captured) * 400  # Bonus important pour les captures

        # Restaure l'état
        game_state.undo_move(x, y, move_data)

        return score
    
    def _detect_critical_threats(self, game_state: FastGameState, player: int) -> int:
        """Détecte les menaces critiques (3+ alignés) de l'adversaire"""
        threats = 0
        positions = game_state.get_occupied_positions(player)
        
        for x, y in positions:
            for dx, dy in np.array(DIRECTIONS):
                # Compte les alignements de 3+ dans chaque direction
                consecutive = game_state.count_consecutive(x, y, dx, dy, player)
                if consecutive >= 3:
                    threats += consecutive - 2  # 3=1 threat, 4=2 threats, etc.
        
        return threats
    
    def _calculate_attack_potential(self, game_state: FastGameState, player: int) -> float:
        """Calcule le potentiel d'attaque offensif"""
        attack_score = 0
        positions = game_state.get_occupied_positions(player)
        
        # Bonus pour formations ouvertes (pas bloquées)
        for x, y in positions:
            for dx, dy in np.array(DIRECTIONS):
                consecutive = game_state.count_consecutive(x, y, dx, dy, player)
                
                # Vérifie si l'extrémité est libre (formation ouverte)
                end_x, end_y = x + consecutive * dx, y + consecutive * dy
                if (game_state.is_valid_position(end_x, end_y) and 
                    game_state.grid[end_y, end_x] == NOT_SELECTED):
                    attack_score += consecutive * consecutive * 10  # Formations ouvertes = bonus
        
        return attack_score