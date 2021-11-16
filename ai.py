import random


class AI:
    def __init__(self, dimensions):
        self.dimensions = dimensions
        self.possibilities = set((x, y) for x in range(self.dimensions[0]) for y in range(self.dimensions[1]))
        self.guesses = set()

    def make_turn(self, successes):
        left = list(self.possibilities - self.guesses)
        coords = random.choice(left)
        self.guesses.add(coords)
        return coords


class MediumAI(AI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        w, h = self.dimensions
        self._grid = ((x, y) for x in range(w) for y in range(h) if x % 2 == y % 2)

    def make_turn(self, successes):
        try:
            coords = next(self._grid)
        except StopIteration:
            for success in successes:
                coords = self.get_free_neighbor(*success)
                if coords:
                    break
            else:
                raise StopIteration("No more available fields!")
        self.guesses.add(coords)
        return coords

    def get_free_neighbor(self, x, y):
        for coords in self.get_neighbors(x, y):
            if not (0 <= coords[0] < self.dimensions[0] and 0 <= coords[1] < self.dimensions[1]):
                continue
            if coords not in self.guesses:
                return coords

    def get_neighbors(self, x, y):
        return ((rx+x, ry+y) for rx, ry in ((-1, 0), (0, 1), (1, 0), (0, -1)))
