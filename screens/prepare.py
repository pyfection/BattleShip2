from kivy.lang.builder import Builder
from kivy.properties import ListProperty, OptionProperty
from kivymd.uix.screen import MDScreen

Builder.load_file('screens/prepare.kv')


class Prepare(MDScreen):
    game_type = OptionProperty('singleplayer', options=['singleplayer', 'multiplayer'])
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])

    def on_pre_enter(self, *args):
        self.grid.reset()
        self.grid.randomly_place_ships()

