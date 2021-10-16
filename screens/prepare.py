from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen


Builder.load_file('screens/prepare.kv')


class Prepare(MDScreen):
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'allowed_ships' not in kwargs:
            Clock.schedule_once(lambda dt: self._create(), 1)  # ToDo: to be removed

    def _create(self):
        self.grid.randomly_place_ships()

