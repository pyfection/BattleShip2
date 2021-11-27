from kivy.lang.builder import Builder
from kivy.factory import Factory
from kivy.properties import BooleanProperty, ListProperty, OptionProperty
from kivymd.uix.screen import MDScreen


class Prepare(MDScreen):
    _loaded = BooleanProperty(False)
    game_type = OptionProperty('singleplayer', options=['singleplayer', 'multiplayer'])
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])

    def on_pre_enter(self, *args):
        if not self._loaded:
            Factory.register('PrepareGrid', module='widgets.grid')
            Builder.load_file('screens/prepare.kv')
            Builder.apply(self, dispatch_kv_post=True)
            self._loaded = True
        self.grid.reset()
        self.grid.randomly_place_ships()
