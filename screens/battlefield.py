from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock


Builder.load_file('screens/battlefield.kv')


class BattleField(MDScreen):
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'allowed_ships' not in kwargs:
            Clock.schedule_once(lambda dt: self._create(), 1)  # ToDo: to be removed

    def _create(self):
        self.player_grid.randomly_place_ships()
        self.enemy_grid.randomly_place_ships()
