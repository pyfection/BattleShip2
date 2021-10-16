import random

from kivy.properties import BooleanProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.lang.builder import Builder
from kivy.metrics import dp
from kivy.graphics import Color, Line
from kivy.uix.behaviors.button import ButtonBehavior
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel


Builder.load_string("""
<CellHeader>:
    halign: "center"
    canvas.before:
        Color:
            rgb: 0, 0, 0
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgb: app.theme_cls.primary_color
        Rectangle:
            pos: self.x + self.line_thickness, self.y + self.line_thickness
            size: self.width - self.line_thickness*2, self.height - self.line_thickness*2
""")


class Grid(MDGridLayout):
    allowed_ships = ListProperty()
    is_enemy_grid = BooleanProperty(False)
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

    def on_pos(self, _, pos):
        if not self.is_enemy_grid:
            self.draw_ships()

    def on_ships(self, _, ships):
        if not self.is_enemy_grid:
            self.draw_ships()

    def coords_to_pos(self, x, y):
        return (
            self.x+(x+1)*self.cell_size+self.cell_size*.5,
            self.y+(self.dimensions[1]-y-1)*self.cell_size+self.cell_size*.5
        )

    def cell_click(self, cell):
        if self.is_enemy_grid:
            self.hit_cell(cell)

    def hit_cell(self, cell):
        if cell.tested:
            print('Cell already tested')
            return
        cell.tested = True
        ships = [ship for sublist in self.ships for ship in sublist]
        with self.canvas.after:
            if tuple(cell.coords) in ships:
                Color(rgb=(1, 0, 0))
            else:
                Color(rgb=(0, 0, 1))
            Line(points=(*cell.pos, cell.right, cell.top), width=2)
            Line(points=(cell.x, cell.top, cell.right, cell.y), width=2)

    def randomly_place_ships(self):
        ships = []
        for n in self.allowed_ships:
            size = [1, n]
            random.shuffle(size)
            w, h = size
            existing_ships = [s for sublist in ships for s in sublist]
            while True:
                x = random.randint(0, self.dimensions[0] - w)
                y = random.randint(0, self.dimensions[1] - h)
                points = [(cx+x, cy+y) for cx in range(w) for cy in range(h)]
                if any(p in existing_ships for p in points):
                    continue
                ships.append(points)
                break
        self.ships = ships

    def draw_ships(self):
        self.canvas.remove_group('ships')
        with self.canvas:
            for ship in self.ships:
                ship = [self.coords_to_pos(x, y) for x, y in ship]
                points = [i for sublist in ship for i in sublist]
                Color(rgb=(.7, .7, .7))
                Line(points=points, width=self.cell_size * .5 - 2, group='ships')


class PrepareGrid(Grid):
    selected_ship = ObjectProperty()

    def cell_click(self, cell):
        for ship in self.ships:
            if tuple(cell.coords) in ship:
                if ship is self.selected_ship:  # Click on already selected ship
                    ox, oy = ship[0]
                    ship = self.selected_ship.copy()
                    self.selected_ship.clear()
                    for x, y in ship:
                        self.selected_ship.append((ox+(y-oy), oy+(x-ox)))
                    break
                else:  # Clicked on another ship or no ship was selected
                    self.selected_ship = ship
                    break
        else:  # Clicked on free cell
            if self.selected_ship:
                rx, ry = cell.coords[0]-self.selected_ship[0][0], cell.coords[1]-self.selected_ship[0][1]
                ship = self.selected_ship.copy()
                self.selected_ship.clear()
                for x, y in ship:
                    self.selected_ship.append((x+rx, y+ry))
        self.draw_ships()


class CellHeader(MDLabel):
    line_thickness = NumericProperty(2)
    tested = BooleanProperty(False)


class Cell(ButtonBehavior, CellHeader):
    coords = ListProperty((0, 0))