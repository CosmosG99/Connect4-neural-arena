import math
import random
import time
import numpy as np
from config import ROWS, COLS, EMPTY, PLAYER, AI_AGENT
from board import Board

class AIStats:
    def __init__(self):
        self.nodes_explored = 0
        self.branches_pruned = 0
        self.start_time = 0
        self.end_time = 0
        self.best_move = None
        self.best_score = 0
        self.depth = 0
        self.algorithm = "None"
        self.thinking_move = None
        
    def reset(self, algorithm, depth):
        self.nodes_explored = 0
        self.branches_pruned = 0
        self.start_time = time.time()
        self.end_time = 0
        self.best_move = None
        self.best_score = 0
        self.algorithm = algorithm
        self.depth = depth
        self.thinking_move = None

class AI:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.stats = AIStats()
        self.is_thinking = False
        self.last_stats = None
        # Simple transposition table mapping board bytes to (depth, score)
        self.transposition_table = {}

    def get_best_move(self, board, piece):
        self.is_thinking = True
        self.transposition_table.clear()
        
        valid_locations = board.get_valid_locations()
        if not valid_locations:
            self.is_thinking = False
            return None

        opp_piece = PLAYER if piece == AI_AGENT else AI_AGENT

        # Variety Logic: Opening moves should be dynamic
        pieces_count = np.count_nonzero(board.state)
        if pieces_count < 2:
            # Pick from center columns with some randomness for variety
            openings = [c for c in [2, 3, 4] if c in valid_locations]
            if openings:
                col = random.choice(openings)
                self.stats.reset("Opening Library", 0)
                self.stats.best_move = col
                self.stats.end_time = time.time()
                self.last_stats = self.stats
                self.is_thinking = False
                return col

        if self.difficulty == 1: # Easy
            self.stats.reset("Random / Shallow", 1)
            time.sleep(0.3) # Artificial thinking delay
            col = random.choice(valid_locations)
            self.stats.best_move = col
            self.stats.end_time = time.time()
            self.last_stats = self.stats
            self.is_thinking = False
            return col
            
        elif self.difficulty == 2: # Medium
            self.stats.reset("Minimax", 3)
            col, score = self.minimax(board, 3, True, piece, opp_piece)
            self.stats.best_move = col
            self.stats.best_score = score
            self.stats.end_time = time.time()
            self.last_stats = self.stats
            self.is_thinking = False
            return col
            
        elif self.difficulty == 3: # Hard
            self.stats.reset("Alpha-Beta", 5)
            col, score = self.alphabeta(board, 5, -math.inf, math.inf, True, piece, opp_piece)
            self.stats.best_move = col
            self.stats.best_score = score
            self.stats.end_time = time.time()
            self.last_stats = self.stats
            self.is_thinking = False
            return col
            
        elif self.difficulty == 4: # Expert
            self.stats.reset("Alpha-Beta + Ordering", 6)
            col, score = self.alphabeta(board, 6, -math.inf, math.inf, True, piece, opp_piece)
            self.stats.best_move = col
            self.stats.best_score = score
            self.stats.end_time = time.time()
            self.last_stats = self.stats
            self.is_thinking = False
            return col
            
        elif self.difficulty == 5: # Impossible (Iterative Deepening + TT)
            self.stats.reset("Iterative Deepening", 7)
            # Iterative deepening up to depth 7
            best_col = valid_locations[COLS//2] if COLS//2 in valid_locations else valid_locations[0]
            best_score = 0
            
            # Use iterative deepening
            for depth in range(1, 8):
                # Update live depth for telemetry
                self.stats.depth = depth
                # We can reuse the transposition table across depths
                col, score = self.alphabeta(board, depth, -math.inf, math.inf, True, piece, opp_piece)
                if col is not None:
                    best_col = col
                    best_score = score
                # Early exit if we found a guaranteed win
                if score > 500000000:
                    break
                    
            self.stats.best_move = best_col
            self.stats.best_score = best_score
            self.stats.end_time = time.time()
            self.last_stats = self.stats
            self.is_thinking = False
            return best_col

    def minimax(self, board, depth, maximizingPlayer, piece, opp_piece):
        self.stats.nodes_explored += 1
        valid_locations = board.get_valid_locations()
        is_terminal = board.is_terminal_node()
        
        if depth == 0 or is_terminal:
            if is_terminal:
                if board.winning_move(piece):
                    return (None, 1000000000000)
                elif board.winning_move(opp_piece):
                    return (None, -100000000000)
                else: 
                    return (None, 0)
            else: 
                return (None, board.score_position(piece))

        if maximizingPlayer:
            value = -math.inf
            # Track all best moves for variety
            best_cols = []
            for col in valid_locations:
                row = board.get_next_open_row(col)
                b_copy = board.copy()
                b_copy.drop_piece(row, col, piece)
                new_score = self.minimax(b_copy, depth-1, False, piece, opp_piece)[1]
                if new_score > value:
                    value = new_score
                    best_cols = [col]
                    # Update live stats for telemetry
                    if depth == self.stats.depth:
                        self.stats.best_score = value
                        self.stats.thinking_move = col
                elif new_score == value:
                    best_cols.append(col)
            return random.choice(best_cols), value
        else: 
            value = math.inf
            best_cols = []
            for col in valid_locations:
                row = board.get_next_open_row(col)
                b_copy = board.copy()
                b_copy.drop_piece(row, col, opp_piece)
                new_score = self.minimax(b_copy, depth-1, True, piece, opp_piece)[1]
                if new_score < value:
                    value = new_score
                    best_cols = [col]
                    if depth == self.stats.depth:
                        self.stats.best_score = value
                        self.stats.thinking_move = col
                elif new_score == value:
                    best_cols.append(col)
            return random.choice(best_cols), value

    def alphabeta(self, board, depth, alpha, beta, maximizingPlayer, piece, opp_piece):
        board_hash = board.state.tobytes()
        if board_hash in self.transposition_table:
            stored_depth, stored_score = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return None, stored_score # We don't store the best move for simplicity here, just score

        self.stats.nodes_explored += 1
        valid_locations = board.get_valid_locations()
        
        # Move ordering: center first
        center = COLS // 2
        valid_locations.sort(key=lambda x: abs(center - x))
        
        is_terminal = board.is_terminal_node()
        
        if depth == 0 or is_terminal:
            if is_terminal:
                if board.winning_move(piece):
                    return (None, 1000000000000)
                elif board.winning_move(opp_piece):
                    return (None, -100000000000)
                else: 
                    return (None, 0)
            else: 
                score = board.score_position(piece)
                self.transposition_table[board_hash] = (depth, score)
                return (None, score)

        if maximizingPlayer:
            value = -math.inf
            best_cols = [valid_locations[0]]
            for col in valid_locations:
                row = board.get_next_open_row(col)
                b_copy = board.copy()
                b_copy.drop_piece(row, col, piece)
                new_score = self.alphabeta(b_copy, depth-1, alpha, beta, False, piece, opp_piece)[1]
                
                # Add tiny random jitter to equal scores to break ties and add variety
                if depth == self.stats.depth:
                    new_score += random.uniform(-0.1, 0.1)

                if new_score > value:
                    value = new_score
                    best_cols = [col]
                    # Update live stats for telemetry
                    if depth == self.stats.depth:
                        self.stats.best_score = value
                        self.stats.thinking_move = col
                elif new_score == value:
                    best_cols.append(col)
                alpha = max(alpha, value)
                if alpha >= beta:
                    self.stats.branches_pruned += 1
                    break
            self.transposition_table[board_hash] = (depth, value)
            return random.choice(best_cols), value
        else: 
            value = math.inf
            best_cols = [valid_locations[0]]
            for col in valid_locations:
                row = board.get_next_open_row(col)
                b_copy = board.copy()
                b_copy.drop_piece(row, col, opp_piece)
                new_score = self.alphabeta(b_copy, depth-1, alpha, beta, True, piece, opp_piece)[1]
                
                if depth == self.stats.depth:
                    new_score += random.uniform(-0.1, 0.1)

                if new_score < value:
                    value = new_score
                    best_cols = [col]
                    if depth == self.stats.depth:
                        self.stats.best_score = value
                        self.stats.thinking_move = col
                elif new_score == value:
                    best_cols.append(col)
                beta = min(beta, value)
                if alpha >= beta:
                    self.stats.branches_pruned += 1
                    break
            self.transposition_table[board_hash] = (depth, value)
            return random.choice(best_cols), value
