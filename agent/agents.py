import random
from game.go import Board, opponent_color
import random

class Agent:
    def __init__(self, color):
        self.color = color

    @classmethod
    def terminal_test(cls, board):
        return board.winner is not None

    def get_action(self, board: Board):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__ + '; color: ' + self.color

