import numpy as np
from typing import List, Tuple
from const import *
from .game_state import FastGameState

class MoveGenerator:
    """Générateur de coups candidats optimisé"""
    
    def __init__(self):
        self.max_candidates = 20
    
    def get_candidate_moves(self, board, evaluator) -> List[Tuple[int, int]]:
        """Génère et trie les meilleurs coups candidats avec NumPy"""
        game_state = FastGameState(board)
        candidates = game_state.find_nearby_moves_vectorized()
        
        if len(candidates) == 0:
            return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
        
        return self._sort_and_limit_moves_numpy(board, candidates, evaluator)
    
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        """Vérifie si la position est dans les limites"""
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE
    
    def _is_valid_move(self, board, x: int, y: int) -> bool:
        """Vérifie si le coup est valide (pas de double-trois)"""
        board.buttons[y][x].state = board.turn
        is_valid = not board.is_double_three_move(x, y)
        board.buttons[y][x].state = NOT_SELECTED
        return is_valid
    
    def _sort_and_limit_moves_numpy(self, board, candidates, evaluator) -> List[Tuple[int, int]]:
        """Trie les candidats avec NumPy vectorisé"""
        valid_moves = []
        scores = []
        
        # Filtre et évalue les coups valides avec NumPy seulement
        for x, y in candidates:
            if self._is_valid_move(board, x, y):
                score = evaluator.quick_move_score_numpy(board, x, y)
                valid_moves.append((x, y))
                scores.append(score)
        
        if not valid_moves:
            return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
        
        # Trie avec NumPy (plus rapide)
        scores_array = np.array(scores)
        indices = np.argsort(scores_array)[::-1]  # Tri décroissant
        
        # Retourne les meilleurs coups
        best_moves = [valid_moves[i] for i in indices[:self.max_candidates]]
        return best_moves
    
    def get_priority_moves_numpy(self, board) -> List[Tuple[int, int]]:
        """Génère les coups prioritaires AGRESSIFS avec NumPy"""
        game_state = FastGameState(board)
        
        # 1. VICTOIRE IMMÉDIATE (priorité absolue)
        winning_moves = self._find_winning_moves(game_state, board.turn)
        if len(winning_moves) > 0:
            return winning_moves.tolist()
        
        # 2. DÉFENSE CRITIQUE - bloquer l'adversaire
        opponent = WHITE if board.turn == BLACK else BLACK
        blocking_moves = self._find_winning_moves(game_state, opponent)
        if len(blocking_moves) > 0:
            return blocking_moves.tolist()
        
        # 3. MENACES DE 4 - créer des lignes de 4
        threat_moves = self._find_threat_moves(game_state, board.turn, 4)
        if len(threat_moves) > 0:
            return threat_moves.tolist()
        
        # 4. DÉFENSE MENACES DE 4 adversaire
        defense_moves = self._find_threat_moves(game_state, opponent, 4)
        if len(defense_moves) > 0:
            return defense_moves.tolist()
        
        # 5. MENACES DE 3 - créer des lignes de 3
        attack3_moves = self._find_threat_moves(game_state, board.turn, 3)
        if len(attack3_moves) > 0:
            return attack3_moves.tolist()[:5]  # Limite à 5 meilleurs
        
        # 6. Coups normaux si aucune tactique
        from .evaluation import GameEvaluator
        temp_evaluator = GameEvaluator()
        return self.get_candidate_moves(board, temp_evaluator)
    
    def _find_winning_moves(self, game_state: FastGameState, player: int) -> np.ndarray:
        """Trouve les coups gagnants avec NumPy"""
        winning_moves = []
        empty_positions = game_state.get_empty_positions()
        
        for x, y in empty_positions:
            # Simule le coup
            game_state.make_move(x, y, player)
            
            # Vérifie si c'est gagnant dans toutes les directions
            is_winning = False
            for dx, dy in DIRECTIONS:
                if game_state.count_consecutive(x, y, dx, dy, player) >= 5:
                    is_winning = True
                    break
            
            # Restaure
            game_state.undo_move(x, y, NOT_SELECTED)
            
            if is_winning:
                winning_moves.append((x, y))
        
        return np.array(winning_moves)
    
    def _find_threat_moves(self, game_state: FastGameState, player: int, target_length: int) -> np.ndarray:
        """Trouve les coups qui créent des menaces de longueur donnée"""
        threat_moves = []
        empty_positions = game_state.get_empty_positions()
        
        for x, y in empty_positions[:50]:  # Limite pour performance
            # Simule le coup
            game_state.make_move(x, y, player)
            
            # Vérifie si ça crée une menace de la longueur voulue
            creates_threat = False
            for dx, dy in DIRECTIONS:
                consecutive = game_state.count_consecutive(x, y, dx, dy, player)
                if consecutive >= target_length:
                    creates_threat = True
                    break
            
            # Restaure
            game_state.undo_move(x, y, NOT_SELECTED)
            
            if creates_threat:
                threat_moves.append((x, y))
        
        return np.array(threat_moves)