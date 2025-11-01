import time
from typing import Tuple, List
from const import *
from .evaluation import GameEvaluator
from .move_generator import MoveGenerator
from .game_state import FastGameState

class MinimaxAI:
    """IA Minimax refactorisée et lisible avec gestion des captures"""

    def __init__(self, max_depth: int = 15, time_limit: float = 0.5):
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.start_time = 0
        self.nodes_evaluated = 0
        self.tt_hits = 0  # Compteur de hits dans la transposition table
        self.transposition_table = {}
        self.evaluator = GameEvaluator()
        self.move_generator = MoveGenerator()
        self.game_state = None  # Sera initialisé dans get_best_move
        self.reached_depth = 0  # Profondeur réellement atteinte
        self.best_moves_by_depth = {}  # Stocke les meilleurs coups par profondeur
    
    def get_best_move(self, board) -> Tuple[int, int]:
        """Point d'entrée avec iterative deepening - retourne le meilleur coup"""
        self._reset_search()

        # Initialise le FastGameState depuis le board
        self.game_state = FastGameState(board)

        # Priorité 1: Coups gagnants ou de défense critique
        priority_moves = self.move_generator.get_priority_moves_numpy(board)
        if len(priority_moves) <= 3:  # Si peu de coups critiques, évalue-les tous
            moves = priority_moves
        else:
            moves = self.move_generator.get_candidate_moves(board, self.evaluator)

        # Iterative deepening: augmente progressivement la profondeur
        return self._iterative_deepening_search(board, moves)
    
    def _reset_search(self):
        """Réinitialise les variables de recherche"""
        self.start_time = time.time()
        self.nodes_evaluated = 0
        self.tt_hits = 0
        self.transposition_table.clear()
        self.reached_depth = 0
        self.best_moves_by_depth.clear()

    def _iterative_deepening_search(self, board, moves) -> Tuple[int, int]:
        """Recherche avec iterative deepening pour maximiser la profondeur"""
        best_move = moves[0]
        safety_margin = 0.05  # Marge de sécurité pour éviter timeout

        # Itère sur les profondeurs croissantes
        for depth in range(1, self.max_depth + 1):
            # Vérifie qu'il reste assez de temps
            elapsed = time.time() - self.start_time
            if elapsed + safety_margin > self.time_limit:
                break

            # Recherche à cette profondeur
            try:
                current_best = self._search_at_depth(board, moves, depth)
                if not self._is_timeout():
                    best_move = current_best
                    self.reached_depth = depth
                    self.best_moves_by_depth[depth] = best_move
                else:
                    break  # Timeout pendant la recherche, garde le dernier résultat complet
            except Exception as e:
                print(f"  ⚠️  Exception à profondeur {depth}: {e}")
                break  # En cas d'erreur, retourne le dernier meilleur coup trouvé

        # Affiche les statistiques
        elapsed = time.time() - self.start_time
        tt_rate = (self.tt_hits / self.nodes_evaluated * 100) if self.nodes_evaluated > 0 else 0
        nodes_per_sec = int(self.nodes_evaluated / elapsed) if elapsed > 0 else 0

        print(f"  Profondeur: {self.reached_depth} | Temps: {elapsed:.3f}s | "
              f"Nœuds: {self.nodes_evaluated} ({nodes_per_sec}/s) | "
              f"TT hits: {self.tt_hits} ({tt_rate:.1f}%)")

        return best_move

    def _search_at_depth(self, board, moves, depth: int) -> Tuple[int, int]:
        """Recherche le meilleur coup à une profondeur donnée"""
        best_move = moves[0]
        best_value = float('-inf')

        for x, y in moves:
            if self._is_timeout():
                break

            value = self._evaluate_move_at_depth(board, x, y, depth)

            if value > best_value:
                best_value = value
                best_move = (x, y)

        return best_move

    def _evaluate_move_at_depth(self, board, x: int, y: int, depth: int) -> float:
        """Évalue un coup spécifique à une profondeur donnée"""
        move_data = self.game_state.make_move(x, y, board.turn)
        value = self._minimax(board, depth - 1, float('-inf'), float('inf'), False)
        self.game_state.undo_move(x, y, move_data)
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

        value = self._minimax_at_depth(board, depth, alpha, beta, is_maximizing)
        self.transposition_table[position_hash] = (depth, value)

        return value
    
    def _should_stop(self, board, depth: int) -> bool:
        """Vérifie les conditions d'arrêt"""
        return self._is_timeout() or depth == 0 or board.check_victory() != False
    
    def _get_terminal_value(self, board, depth: int) -> float:
        """Retourne la valeur pour un nœud terminal avec quiescence search"""
        winner = board.check_victory()

        if winner == board.turn:
            return 10000 + depth
        elif winner != False:
            return -10000 - depth
        else:
            # Si on atteint depth=0, utilise quiescence search pour les positions tactiques
            if depth == 0:
                return self._quiescence_search(board, float('-inf'), float('inf'), 3)
            return self.evaluator.evaluate_position(board)
    
    def _use_cached_value(self, position_hash: int, depth: int) -> bool:
        """Vérifie si on peut utiliser une valeur en cache"""
        if position_hash in self.transposition_table:
            cached_depth, _ = self.transposition_table[position_hash]
            if cached_depth >= depth:
                self.tt_hits += 1
                return True
        return False
    
    def _minimax_at_depth(self, board, depth: int, alpha: float, beta: float, is_maximizing: bool) -> float:
        """Recherche minimax à une profondeur donnée"""
        moves = self.move_generator.get_candidate_moves(board, self.evaluator)

        if is_maximizing:
            return self._maximize(board, moves, depth, alpha, beta)
        else:
            return self._minimize(board, moves, depth, alpha, beta)
    
    def _maximize(self, board, moves, depth: int, alpha: float, beta: float) -> float:
        """Phase de maximisation avec captures"""
        max_value = float('-inf')

        for x, y in moves:
            move_data = self.game_state.make_move(x, y, board.turn)
            value = self._minimax(board, depth - 1, alpha, beta, False)
            self.game_state.undo_move(x, y, move_data)

            max_value = max(max_value, value)
            alpha = max(alpha, value)

            if beta <= alpha:  # Élagage
                break

        return max_value
    
    def _minimize(self, board, moves, depth: int, alpha: float, beta: float) -> float:
        """Phase de minimisation avec captures"""
        min_value = float('inf')
        opponent = WHITE if board.turn == BLACK else BLACK
        old_turn = board.turn
        board.turn = opponent
        self.game_state.turn = opponent

        for x, y in moves:
            move_data = self.game_state.make_move(x, y, opponent)
            value = self._minimax(board, depth - 1, alpha, beta, True)
            self.game_state.undo_move(x, y, move_data)

            min_value = min(min_value, value)
            beta = min(beta, value)

            if beta <= alpha:  # Élagage
                break

        board.turn = old_turn
        self.game_state.turn = old_turn
        return min_value
    
    def _hash_position(self, board) -> int:
        """Hash rapide de la position avec Zobrist"""
        return int(self.game_state.zobrist_hash)
    
    def _is_timeout(self) -> bool:
        """Vérifie le timeout"""
        return time.time() - self.start_time > self.time_limit

    def _get_tactical_moves(self, board) -> List[Tuple[int, int]]:
        """Génère uniquement les coups tactiques (captures et menaces de 4)"""
        game_state = FastGameState(board)
        tactical_moves = []
        empty_positions = game_state.get_empty_positions()

        player = board.turn

        # Limite la recherche aux 30 premières positions vides pour performance
        for x, y in empty_positions[:30]:
            move_data = game_state.make_move(x, y, player)
            _, captured = move_data

            is_tactical = False

            # Capture
            if len(captured) > 0:
                is_tactical = True

            # Menace de 4+
            if not is_tactical:
                for dx, dy in DIRECTIONS:
                    if game_state.count_consecutive(x, y, dx, dy, player) >= 4:
                        is_tactical = True
                        break

            game_state.undo_move(x, y, move_data)

            if is_tactical:
                tactical_moves.append((x, y))

        return tactical_moves

    def _quiescence_search(self, board, alpha: float, beta: float, max_depth: int) -> float:
        """Recherche de quiescence pour éviter l'horizon effect"""
        self.nodes_evaluated += 1

        # Évaluation statique (stand pat)
        stand_pat = self.evaluator.evaluate_position(board)

        if stand_pat >= beta:
            return beta

        if alpha < stand_pat:
            alpha = stand_pat

        # Profondeur max atteinte ou timeout
        if max_depth <= 0 or self._is_timeout():
            return stand_pat

        # Génère uniquement les coups tactiques
        tactical_moves = self._get_tactical_moves(board)

        if len(tactical_moves) == 0:
            return stand_pat

        # Explore les coups tactiques
        for x, y in tactical_moves[:5]:  # Limite à 5 meilleurs coups tactiques
            move_data = self.game_state.make_move(x, y, board.turn)

            # Récursion avec alternance joueur
            old_turn = board.turn
            board.turn = WHITE if board.turn == BLACK else BLACK
            self.game_state.turn = board.turn

            score = -self._quiescence_search(board, -beta, -alpha, max_depth - 1)

            board.turn = old_turn
            self.game_state.turn = old_turn
            self.game_state.undo_move(x, y, move_data)

            if score >= beta:
                return beta

            if score > alpha:
                alpha = score

        return alpha