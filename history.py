import json
import os
import time

class HistoryManager:
    def __init__(self, filename="match_history.json"):
        self.filename = filename
        self.history = self.load_history()

    def load_history(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_match(self, match_data):
        """
        match_data should include:
        - mode
        - winner (0: Draw, 1: P1, 2: P2)
        - duration (seconds)
        - total_moves
        - timestamp (epoch)
        - p1_diff, p2_diff
        - board_state (list of lists)
        """
        match_data['date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.history.insert(0, match_data) # Newest first
        # Keep only last 50 matches
        if len(self.history) > 50:
            self.history = self.history[:50]
        
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def get_history(self):
        return self.history

# Global instance
history_manager = HistoryManager()
