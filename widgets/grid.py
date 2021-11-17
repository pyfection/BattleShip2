import random

from kivy.properties import BooleanProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.lang.builder import Builder
from kivy.metrics import dp
from kivy.graphics import Color, Line
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
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
    dimensions = ListProperty((10, 10))
    cell_size = NumericProperty(dp(30))
    ships = ListProperty()
    last_move = ObjectProperty(allownone=True)
    cross_sound = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_size = True
        self.col_force_default = True
        self.row_force_default = True
        self.col_default_width = self.cell_size
        self.row_default_height = self.cell_size
        self.cells = {}
        if 'dimensions' not in kwargs:
            self._create()

    def on_kv_post(self, base_widget):
        self.cross_sound = SoundLoader.load('assets/pen-cross.wav')

    def in_dimensions(self, x, y):
        return 0 <= x < self.dimensions[0] and 0 <= y < self.dimensions[1]

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
                self.cells[(x, y)] = cell
                self.add_widget(cell)

    def reset(self):
        self.last_move = None
        self.canvas.remove_group('ships')
        self.canvas.after.remove_group('crosses')
        for cell in self.cells.values():
            cell.is_hit = None

    def coords_to_pos(self, x, y):
        return (
            self.x+(x+1)*self.cell_size+self.cell_size*.5,
            self.y+(self.dimensions[1]-y-1)*self.cell_size+self.cell_size*.5
        )

    def cell_click(self, cell):
        pass

    def hit_cell(self, cell_coords):
        def _draw_second_line_of_cross(color):
            with self.canvas.after:
                Color(rgb=color)
                l2 = Line(points=(cell.right, cell.top, cell.right, cell.top), width=2, group='crosses')
                anim2 = Animation(points=(cell.right, cell.top, *cell.pos), d=.3)
                anim2.start(l2)
        cell = self.cells[cell_coords]
        if cell.is_hit is not None:
            print('Cell already tested')
            return None
        ships = [ship for sublist in self.ships for ship in sublist]
        self.cross_sound.play()
        self.cross_sound.seek(0)
        with self.canvas.after:
            if cell.coords in ships:
                cell.is_hit = hit = True
                color = (1, 0, 0)
            else:
                cell.is_hit = hit = False
                color = (0, 0, 1)
            Color(rgb=color)
            l1 = Line(points=(cell.x, cell.top, cell.x, cell.top), width=2, group='crosses')
            anim1 = Animation(points=(cell.x, cell.top, cell.right, cell.y), d=.3)
            anim1.bind(on_complete=lambda anim, widget, color=color: _draw_second_line_of_cross(color))
            anim1.start(l1)
        self.last_move = cell_coords
        return hit

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

    def on_pos(self, *args):
        self.draw_ships()

    def on_ships(self, _, ships):
        self.draw_ships()

    def cell_click(self, cell):
        ships = [ship for sublist in self.ships for ship in sublist if sublist is not self.selected_ship]

        for ship in self.ships:
            if cell.coords in ship:
                if ship is self.selected_ship:  # Click on already selected ship
                    if cell.coords != self.selected_ship[0]:
                        continue  # Only clicking on left upper part of ship should rotate it
                    # Rotate it
                    ox, oy = ship[0]
                    new_ship = [(ox+(y-oy), oy+(x-ox)) for x, y in self.selected_ship]
                    if all(self.in_dimensions(tx, ty) and not (tx, ty) in ships for tx, ty in new_ship[1:]):
                        ship.clear()
                        ship.extend(new_ship)
                        self.selected_ship = ship
                    break
                else:  # Clicked on another ship
                    # Select ship
                    self.selected_ship = ship
                    break

        else:  # Clicked on free cell
            if self.selected_ship:
                # Move selected ship to new location
                rx, ry = cell.coords[0]-self.selected_ship[0][0], cell.coords[1]-self.selected_ship[0][1]
                new_ship = [(x+rx, y+ry) for x, y in self.selected_ship]
                if all(self.in_dimensions(tx, ty) and not (tx, ty) in ships for tx, ty in new_ship[1:]):
                    self.selected_ship.clear()
                    self.selected_ship.extend(new_ship)
        self.draw_ships()

    def draw_ships(self):
        super().draw_ships()
        if self.selected_ship:
            with self.canvas:
                ship = [self.coords_to_pos(x, y) for x, y in self.selected_ship]
                points = [i for sublist in ship for i in sublist]
                Color(rgb=(.1, .7, .1))
                Line(points=points, width=self.cell_size * .5 - 2, group='ships')


class PlayerGrid(Grid):
    def on_pos(self, _, pos):
        self.draw_ships()

    def on_ships(self, _, ships):
        self.draw_ships()


class EnemyGrid(Grid):
    blocked = BooleanProperty(False)

    def cell_click(self, cell):
        if not self.blocked:
            if self.hit_cell(cell.coords) is False:  # Hit empty cell
                self.blocked = True


class CellHeader(MDLabel):
    line_thickness = NumericProperty(2)


class Cell(ButtonBehavior, CellHeader):
    coords = ObjectProperty((0, 0))
    is_hit = BooleanProperty(None, allownone=True)
