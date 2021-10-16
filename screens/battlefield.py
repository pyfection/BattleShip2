from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock


Builder.load_file('screens/battlefield.kv')


class BattleField(MDScreen):
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])

    def start_singleplayer(self, ships):
        self.enemy_grid.randomly_place_ships()
        self.player_grid.ships = ships
