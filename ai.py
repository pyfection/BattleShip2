import random


class AI:
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.possibilities = set((x, y) for x in range(self.dimensions[0]) for y in range(self.dimensions[1]))
        self.guesses = set()

    def make_turn(self):
        left = list(self.possibilities - self.guesses)
        coords = random.choice(left)
        self.guesses.add(coords)
        return coords
