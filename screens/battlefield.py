import random

from kivy.lang.builder import Builder
from kivy.properties import BooleanProperty, NumericProperty, ListProperty
from kivy.metrics import dp
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.behaviors.button import ButtonBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel

from kivy.clock import Clock


Builder.load_file('screens/battlefield.kv')


class BattleField(MDScreen):
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'allowed_ships' not in kwargs:
            Clock.schedule_once(lambda dt: self._create(), 1)  # ToDo: to be removed

    def _create(self):
        ships = []
        for n in self.allowed_ships:
            size = [1, n]
            random.shuffle(size)
            w, h = size
            existing_ships = [s for sublist in ships for s in sublist]
            while True:
                x = random.randint(0, self.player_grid.dimensions[0] - w)
                y = random.randint(0, self.player_grid.dimensions[1] - h)
                points = [(cx+x, cy+y) for cx in range(w) for cy in range(h)]
                if any(p in existing_ships for p in points):
                    continue
                ships.append(points)
                break
        self.player_grid.ships = ships


class Grid(MDGridLayout):
    draw_ships = BooleanProperty(False)
    dimensions = ListProperty((10, 10))
    cell_size = NumericProperty(dp(30))
    ships = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_size = True
        self.col_force_default = True
        self.row_force_default = True
        self.col_default_width = self.cell_size
        self.row_default_height = self.cell_size
        if 'dimensions' not in kwargs:
            self._create()

    def on_dimensions(self, _, dimensions):
        self._create()

    def _create(self):
        self.clear_widgets()
        w, h = self.dimensions
        self.cols = w+1
        label = CellHeader()
        self.add_widget(label)

        for i in range(w):
            label = CellHeader(text=chr(i+65))
            self.add_widget(label)

        for y in range(h):
            label = CellHeader(text=str(y+1))
            self.add_widget(label)
            for x in range(w):
                cell = Cell(on_press=self.cell_click, coords=(x, y))
                self.add_widget(cell)

    def on_ships(self, _, ships):
        if self.draw_ships:
            with self.canvas:
                for ship in ships:
                    ship = [(x+1, self.dimensions[1]-y-1) for x, y in ship]
                    points = [i*self.cell_size+self.cell_size*.5 for sublist in ship for i in sublist]
                    Color(rgb=(.7, .7, .7))
                    Line(points=points, width=self.cell_size*.5-2)

    def cell_click(self, cell):
        pass


class CellHeader(MDLabel):
    line_thickness = NumericProperty(2)


class Cell(ButtonBehavior, CellHeader):
    coords = ListProperty((0, 0))
