import random


POSITIONS = ("A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4")
PET_NAMES = ("Cordelia", "Yam", "Burger", "ChaCha")


class PetMemoryGame:
    def __init__(self):
        self.board = {}
        self.matched = set()
        self.scores = {}
        self.active_player = None
        self.players = []

    def start(self, player_one, player_two):
        cards = list(PET_NAMES) * 2
        random.shuffle(cards)

        self.board = dict(zip(POSITIONS, cards))
        self.matched = set()
        self.scores = {
            player_one: 0,
            player_two: 0,
        }
        self.players = [player_one, player_two]
        self.active_player = player_one

    def other_player(self, player_id):
        for player in self.players:
            if player != player_id:
                return player

        return None

    def board_view(self, revealed=()):
        view = {}

        for position in POSITIONS:
            if position in self.matched or position in revealed:
                view[position] = self.board[position]
            else:
                view[position] = "HIDDEN"

        return view

    def validate_move(self, player_id, positions):
        if player_id != self.active_player:
            return "NOT_YOUR_TURN"

        if not isinstance(positions, list) or len(positions) != 2:
            return "MALFORMED_MESSAGE"

        first, second = positions

        if first == second:
            return "DUPLICATE_POSITION"

        if first not in POSITIONS or second not in POSITIONS:
            return "INVALID_POSITION"

        if first in self.matched or second in self.matched:
            return "CARD_ALREADY_MATCHED"

        return None

    def evaluate_move(self, player_id, positions):
        first, second = positions
        is_match = self.board[first] == self.board[second]

        if is_match:
            self.matched.update(positions)
            self.scores[player_id] += 1
        else:
            self.active_player = self.other_player(player_id)

        game_over = len(self.matched) == len(POSITIONS)

        return {
            "is_match": is_match,
            "game_over": game_over,
            "revealed": positions,
        }