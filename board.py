import numpy as np
from config import ROWS, COLS, EMPTY, PLAYER, AI_AGENT

class Board:
    def __init__(self):
        self.state = np.zeros((ROWS, COLS), dtype=int)

    def drop_piece(self, row, col, piece):
        self.state[row][col] = piece

    def is_valid_location(self, col):
        return self.state[0][col] == 0

    def get_valid_locations(self):
        valid_locations = []
        for col in range(COLS):
            if self.is_valid_location(col):
                valid_locations.append(col)
        return valid_locations

    def get_next_open_row(self, col):
        for r in range(ROWS-1, -1, -1):
            if self.state[r][col] == 0:
                return r
        return None

    def winning_move(self, piece):
        # Check horizontal locations
        for c in range(COLS-3):
            for r in range(ROWS):
                if self.state[r][c] == piece and self.state[r][c+1] == piece and self.state[r][c+2] == piece and self.state[r][c+3] == piece:
                    return True

        # Check vertical locations
        for c in range(COLS):
            for r in range(ROWS-3):
                if self.state[r][c] == piece and self.state[r+1][c] == piece and self.state[r+2][c] == piece and self.state[r+3][c] == piece:
                    return True

        # Check positively sloped diagonals
        for c in range(COLS-3):
            for r in range(ROWS-3):
                if self.state[r][c] == piece and self.state[r+1][c+1] == piece and self.state[r+2][c+2] == piece and self.state[r+3][c+3] == piece:
                    return True

        # Check negatively sloped diagonals
        for c in range(COLS-3):
            for r in range(3, ROWS):
                if self.state[r][c] == piece and self.state[r-1][c+1] == piece and self.state[r-2][c+2] == piece and self.state[r-3][c+3] == piece:
                    return True
                    
        return False

    def is_terminal_node(self):
        return self.winning_move(PLAYER) or self.winning_move(AI_AGENT) or len(self.get_valid_locations()) == 0

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = PLAYER
        if piece == PLAYER:
            opp_piece = AI_AGENT

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 4

        return score

    def score_position(self, piece):
        score = 0
        
        # Score center column
        center_array = [int(i) for i in list(self.state[:, COLS//2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Score Horizontal
        for r in range(ROWS):
            row_array = [int(i) for i in list(self.state[r,:])]
            for c in range(COLS-3):
                window = row_array[c:c+4]
                score += self.evaluate_window(window, piece)

        # Score Vertical
        for c in range(COLS):
            col_array = [int(i) for i in list(self.state[:,c])]
            for r in range(ROWS-3):
                window = col_array[r:r+4]
                score += self.evaluate_window(window, piece)

        # Score positive diagonal
        for r in range(ROWS-3):
            for c in range(COLS-3):
                window = [self.state[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        # Score negative diagonal
        for r in range(ROWS-3):
            for c in range(COLS-3):
                window = [self.state[r+3-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def get_winning_line(self, piece):
        # Returns the coordinates of the winning line for animation
        for c in range(COLS-3):
            for r in range(ROWS):
                if self.state[r][c] == piece and self.state[r][c+1] == piece and self.state[r][c+2] == piece and self.state[r][c+3] == piece:
                    return [(r, c+i) for i in range(4)]
        for c in range(COLS):
            for r in range(ROWS-3):
                if self.state[r][c] == piece and self.state[r+1][c] == piece and self.state[r+2][c] == piece and self.state[r+3][c] == piece:
                    return [(r+i, c) for i in range(4)]
        for c in range(COLS-3):
            for r in range(ROWS-3):
                if self.state[r][c] == piece and self.state[r+1][c+1] == piece and self.state[r+2][c+2] == piece and self.state[r+3][c+3] == piece:
                    return [(r+i, c+i) for i in range(4)]
        for c in range(COLS-3):
            for r in range(3, ROWS):
                if self.state[r][c] == piece and self.state[r-1][c+1] == piece and self.state[r-2][c+2] == piece and self.state[r-3][c+3] == piece:
                    return [(r-i, c+i) for i in range(4)]
        return None

    def copy(self):
        new_board = Board()
        new_board.state = np.copy(self.state)
        return new_board
