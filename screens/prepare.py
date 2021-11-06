from kivy.lang.builder import Builder
from kivy.properties import ListProperty, OptionProperty
from kivymd.uix.screen import MDScreen

Builder.load_file('screens/prepare.kv')


class Prepare(MDScreen):
    game_type = OptionProperty('singleplayer', ['singleplayer', 'multiplayer'])
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])

    def on_kv_post(self, base_widget):
        self.grid.randomly_place_ships()

