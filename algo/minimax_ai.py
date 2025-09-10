import time
from typing import Tuple
from const import *
from .evaluation import GameEvaluator
from .move_generator import MoveGenerator

class MinimaxAI:
    """IA Minimax refactorisée et lisible"""
    
    def __init__(self, max_depth: int = 4, time_limit: float = 3.0):
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.start_time = 0
        self.nodes_evaluated = 0
        self.transposition_table = {}
        self.evaluator = GameEvaluator()
        self.move_generator = MoveGenerator()
    
    def get_best_move(self, board) -> Tuple[int, int]:
        """Point d'entrée optimisé - retourne le meilleur coup"""
        self._reset_search()
        
        # Priorité 1: Coups gagnants ou de défense critique
        priority_moves = self.move_generator.get_priority_moves_numpy(board)
        if len(priority_moves) <= 3:  # Si peu de coups critiques, évalue-les tous
            moves = priority_moves
        else:
            moves = self.move_generator.get_candidate_moves(board, self.evaluator)
        
        return self._search_best_move(board, moves)
    
    def _reset_search(self):
        """Réinitialise les variables de recherche"""
        self.start_time = time.time()
        self.nodes_evaluated = 0
        self.transposition_table.clear()
    
    def _search_best_move(self, board, moves) -> Tuple[int, int]:
        """Recherche le meilleur coup parmi les candidats"""
        best_move = moves[0]
        best_value = float('-inf')
        
        for x, y in moves:
            if self._is_timeout():
                break
            
            value = self._evaluate_move(board, x, y)
            
            if value > best_value:
                best_value = value
                best_move = (x, y)
        
        return best_move
    
    def _evaluate_move(self, board, x: int, y: int) -> float:
        """Évalue un coup spécifique"""
        board.buttons[y][x].state = board.turn
        value = self._minimax(board, self.max_depth - 1, float('-inf'), float('inf'), False)
        board.buttons[y][x].state = NOT_SELECTED
        return value
    
    def _minimax(self, board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        """Algorithme minimax avec élagage alpha-beta"""
        self.nodes_evaluated += 1
        
        if self._should_stop(board, depth):
            return self._get_terminal_value(board, depth)
        
        # Table de transposition
        position_hash = self._hash_position(board)
        if self._use_cached_value(position_hash, depth):
            return self.transposition_table[position_hash][1]
        
        value = self._search_at_depth(board, depth, alpha, beta, is_maximizing)
        self.transposition_table[position_hash] = (depth, value)
        
        return value
    
    def _should_stop(self, board, depth: int) -> bool:
        """Vérifie les conditions d'arrêt"""
        return self._is_timeout() or depth == 0 or board.check_victory() != False
    
    def _get_terminal_value(self, board, depth: int) -> float:
        """Retourne la valeur pour un nœud terminal"""
        winner = board.check_victory()
        
        if winner == board.turn:
            return 10000 + depth
        elif winner != False:
            return -10000 - depth
        else:
            return self.evaluator.evaluate_position(board)
    
    def _use_cached_value(self, position_hash: int, depth: int) -> bool:
        """Vérifie si on peut utiliser une valeur en cache"""
        if position_hash in self.transposition_table:
            cached_depth, _ = self.transposition_table[position_hash]
            return cached_depth >= depth
        return False
    
    def _search_at_depth(self, board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        """Recherche à une profondeur donnée"""
        moves = self.move_generator.get_candidate_moves(board, self.evaluator)
        
        if is_maximizing:
            return self._maximize(board, moves, depth, alpha, beta)
        else:
            return self._minimize(board, moves, depth, alpha, beta)
    
    def _maximize(self, board, moves, depth: int, alpha: float, beta: float) -> float:
        """Phase de maximisation"""
        max_value = float('-inf')
        
        for x, y in moves:
            board.buttons[y][x].state = board.turn
            value = self._minimax(board, depth - 1, alpha, beta, False)
            board.buttons[y][x].state = NOT_SELECTED
            
            max_value = max(max_value, value)
            alpha = max(alpha, value)
            
            if beta <= alpha:  # Élagage
                break
        
        return max_value
    
    def _minimize(self, board, moves, depth: int, alpha: float, beta: float) -> float:
        """Phase de minimisation"""
        min_value = float('inf')
        opponent = WHITE if board.turn == BLACK else BLACK
        old_turn = board.turn
        board.turn = opponent
        
        for x, y in moves:
            board.buttons[y][x].state = opponent
            value = self._minimax(board, depth - 1, alpha, beta, True)
            board.buttons[y][x].state = NOT_SELECTED
            
            min_value = min(min_value, value)
            beta = min(beta, value)
            
            if beta <= alpha:  # Élagage
                break
        
        board.turn = old_turn
        return min_value
    
    def _hash_position(self, board) -> int:
        """Hash rapide de la position"""
        hash_value = 0
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                state = board.buttons[y][x].state
                if state != NOT_SELECTED:
                    hash_value = (hash_value * 3 + state) % (10**9 + 7)
        return hash_value
    
    def _is_timeout(self) -> bool:
        """Vérifie le timeout"""
        return time.time() - self.start_time > self.time_limit