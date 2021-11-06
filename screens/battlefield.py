from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivymd.uix.screen import MDScreen

from ai import AI


Builder.load_file('screens/battlefield.kv')


class BattleField(MDScreen):
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])
    dimensions = ListProperty((10, 10))

    def start_game(self, ships):
        self.player_grid.ships = ships

    def enemy_turn(self):
        pass


class SPBattleField(BattleField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai = AI(self.dimensions)

    def start_game(self, ships):
        super().start_game(ships)
        self.enemy_grid.randomly_place_ships()

    def enemy_turn(self):
        while True:
            if self.player_grid.hit_cell(self.ai.make_turn()) is False:  # Hit empty field
                break


class MPBattleField(BattleField):
    pass
