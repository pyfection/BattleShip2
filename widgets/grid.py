import random

from kivy.properties import BooleanProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.lang.builder import Builder
from kivy.graphics import Color, Line, Rectangle
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.uix.behaviors.button import ButtonBehavior
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel


Builder.load_string("""
<Grid>:
    size_hint: None, None

<CellHeader>:
    halign: "center"
    canvas.before:
        Color:
            rgb: 0, 0, 0
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgb: self.bg_color
        Rectangle:
            pos: self.x + self.line_thickness, self.y + self.line_thickness
            size: self.width - self.line_thickness*2, self.height - self.line_thickness*2
""")


class Grid(MDGridLayout):
    allowed_ships = ListProperty()
    dimensions = ListProperty((10, 10))
    ships = ListProperty()
    last_move = ObjectProperty(allownone=True)
    cross_sound = ObjectProperty()
    cells = ObjectProperty()
    info_cell = ObjectProperty()

    @property
    def cell_size(self):
        return self.width / (self.dimensions[0] + 1)

    def on_kv_post(self, base_widget):
        self.cross_sound = SoundLoader.load('assets/pen-cross.wav')
        self._create()

    def in_dimensions(self, x, y):
        return 0 <= x < self.dimensions[0] and 0 <= y < self.dimensions[1]

    def on_dimensions(self, _, dimensions):
        self._create()

    def _create(self):
        self.cells = {}
        self.clear_widgets()
        w, h = self.dimensions
        self.cols = w+1
        self.info_cell = CellHeader(bold=True)
        self.add_widget(self.info_cell)

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
        self.info_cell.text = ""
        self.canvas.remove_group('ships')
        self.canvas.after.remove_group('crosses')
        for cell in self.cells.values():
            cell.is_hit = None

    def coords_to_pos(self, x, y):
        cs = self.cell_size
        return (
            self.x + (x+1) * cs + cs * .5,
            self.y + (self.dimensions[1]-y-1) * cs + cs * .5
        )

    def cell_click(self, cell):
        pass

    def hit_cell(self, cell_coords):
        def _draw_second_line_of_cross(color):
            cs = self.cell_size
            x, y = self.coords_to_pos(*cell.coords)
            x, y = x - cs * .5, y - cs * .5
            top, right = y + cs, x + cs
            with self.canvas.after:
                Color(rgb=color)
                l2 = Line(points=(right, top, right, top), width=2, group='crosses')
                anim2 = Animation(points=(right, top, x, y), d=.3)
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
            cs = self.cell_size
            x, y = self.coords_to_pos(*cell.coords)
            x, y = x - cs * .5, y - cs * .5
            top, right = y + cs, x + cs
            l1 = Line(points=(x, top, x, top), width=2, group='crosses')
            anim1 = Animation(points=(x, top, right, y), d=.3)
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
        cs = self.cell_size
        s = cs - 2
        with self.canvas:
            Color(rgb=(.7, .7, .7))
            for ship in self.ships:
                for x, y in ship:
                    x, y = self.coords_to_pos(x, y)
                    x, y = x-s*.5, y-s*.5
                    Rectangle(pos=(x, y), size=(s, s), group='ships')


class PrepareGrid(Grid):
    selected_ship = ObjectProperty(allownone=True)

    def on_pos(self, *args):
        self.draw_ships()

    def on_ships(self, _, ships):
        self.draw_ships()

    def reset(self):
        self.selected_ship = None
        super().reset()

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
            s = self.cell_size - 2
            with self.canvas:
                for x, y in self.selected_ship:
                    x, y = self.coords_to_pos(x, y)
                    x, y = x-s*.5, y-s*.5
                    Color(rgb=(.1, .7, .1))
                    Line(points=[x, y, x+s, y, x+s, y+s, x, y+s], width=3, close=True, group='ships')


class PlayerGrid(Grid):
    def on_size(self, _, size):
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
    DEFAULT_COLOR = [0, 132/255, 210/255]
    HIT_COLOR = [0.4, 0, 0]
    MISS_COLOR = [0, 0, 0.4]
    line_thickness = NumericProperty(2)
    bg_color = ListProperty(DEFAULT_COLOR)


class Cell(ButtonBehavior, CellHeader):
    coords = ObjectProperty((0, 0))
    is_hit = BooleanProperty(None, allownone=True)

    def on_is_hit(self, *args):
        if self.is_hit:
            self.bg_color = self.HIT_COLOR
        elif self.is_hit is False:
            self.bg_color = self.MISS_COLOR
        else:
            self.bg_color = self.DEFAULT_COLOR
