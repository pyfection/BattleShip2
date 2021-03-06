import random

from kivy.properties import BooleanProperty, DictProperty, ListProperty, ObjectProperty
from kivy.lang.builder import Builder
from kivy.graphics import Color, Line, Rectangle
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivymd.uix.floatlayout import MDFloatLayout
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


class Grid(MDFloatLayout):
    allowed_ships = ListProperty()
    dimensions = ListProperty((10, 10))
    ships = ListProperty()
    last_move = ObjectProperty(allownone=True)
    cross_sound = ObjectProperty()
    cells = DictProperty()
    info_cell = ObjectProperty()

    @property
    def cell_size(self):
        return self.width / (self.dimensions[0] + 1)

    def on_kv_post(self, base_widget):
        self.cross_sound = SoundLoader.load('assets/pen-cross.wav')
        self._create()

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        self.cell_click(self.pos_to_coord(*touch.pos))

    def in_dimensions(self, x, y):
        return 0 <= x < self.dimensions[0] and 0 <= y < self.dimensions[1]

    def on_dimensions(self, _, dimensions):
        self._create()
        self.draw_ships()

    def on_size(self, _, size):
        self._create()
        self.draw_ships()

    def on_pos(self, *args):
        self._create()
        self.draw_ships()

    def on_ships(self, _, ships):
        self.draw_ships()

    def _create(self):
        self.clear_widgets()
        self.canvas.before.clear()
        self.canvas.after.clear()
        w, h = self.dimensions
        self.cells = {(x, y): {'is_hit': None} for x in range(w) for y in range(h)}
        self.cols = w+1
        header_color = [20/255, 94/255, 138/255]
        cell_color = [0, 132/255, 210/255]
        cs = self.cell_size

        with self.canvas.before:  # Draw background
            Color(rgb=header_color)
            Rectangle(pos=self.pos, size=self.size)
            Color(rgb=cell_color)
            Rectangle(pos=(self.x+cs, self.y), size=(self.width-cs, self.height-cs))

        # with self.canvas.after:  # Draw lines
            Color(rgb=(0, 0, 0))
            for x in range(1, w+1):
                Rectangle(pos=(self.x+x*cs-1, self.y), size=(2, self.height))
            for y in range(1, h+1):
                Rectangle(pos=(self.x, self.y+y*cs-1), size=(self.width, 2))

        for x in range(1, w+1):
            label = MDLabel(
                pos=(self.x+x*cs, self.top-cs),
                text=chr(x+64),
                halign='center',
                size_hint=(None, None),
                size=(cs, cs)
            )
            self.add_widget(label)
        for y in range(1, h+1):
            label = MDLabel(
                pos=(self.x, self.top-(y+1)*cs),
                text=str(y),
                halign='center',
                size_hint=(None, None),
                size=(cs, cs)
            )
            self.add_widget(label)

        self.info_cell = MDLabel(
            pos=(self.x, self.top-cs),
            bold=True,
            halign='center',
            size_hint=(None, None),
            size=(cs, cs)
        )
        self.add_widget(self.info_cell)

    def reset(self):
        self.last_move = None
        self.info_cell.text = ""
        self.canvas.before.clear()
        self.canvas.clear()
        self.canvas.after.clear()
        for cell in self.cells.values():
            cell['is_hit'] = None
        self._create()
        self.draw_ships()

    def coords_to_pos(self, x, y, centered=True):
        cs = self.cell_size
        return (
            self.x + (x+1) * cs + cs * (.5 * int(centered)),
            self.y + (self.dimensions[1]-y-1) * cs + cs * (.5 * int(centered))
        )

    def pos_to_coord(self, x, y):
        cs = self.cell_size
        return (
            int((x - self.x) // cs) - 1,
            int(self.dimensions[1] - (y - self.y) // cs) - 1
        )

    def cell_click(self, cell):
        pass

    def hit_cell(self, cell_coords):
        def _draw_second_line_of_cross(color):
            cs = self.cell_size
            x, y = self.coords_to_pos(*cell_coords)
            x, y = x - cs * .5, y - cs * .5
            top, right = y + cs, x + cs
            with self.canvas.after:
                Color(rgb=color)
                l2 = Line(points=(right, top, right, top), width=2, group='crosses')
                anim2 = Animation(points=(right, top, x, y), d=.3)
                anim2.start(l2)
        cell = self.cells[cell_coords]
        if cell['is_hit'] is not None:
            print('Cell already tested')
            return None
        ships = [ship for sublist in self.ships for ship in sublist]
        if cell_coords in ships:
            cell['is_hit'] = hit = True
        else:
            cell['is_hit'] = hit = False
        self.cross_sound.play()
        self.cross_sound.seek(0)
        cs = self.cell_size

        with self.canvas.before:
            HIT_COLOR = [0.4, 0, 0]
            MISS_COLOR = [0, 0, 0.4]
            Color(rgb=HIT_COLOR if hit else MISS_COLOR)
            Rectangle(pos=self.coords_to_pos(*cell_coords, centered=False), size=(cs, cs))

        with self.canvas.after:
            if hit:
                color = (1, 0, 0)
            else:
                color = (0, 0, 1)
            Color(rgb=color)
            x, y = self.coords_to_pos(*cell_coords)
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
        w = 2
        s = cs - w
        with self.canvas:
            for ship in self.ships:
                for x, y in ship:
                    x, y = self.coords_to_pos(x, y, centered=False)
                    # x, y = x-s*.5, y-s*.5
                    Color(rgb=(.5, .5, .5))
                    Rectangle(pos=(x, y), size=(cs, cs), group='ships')
                    Color(rgb=(.7, .7, .7))
                    Rectangle(pos=(x+w*.5, y+w*.5), size=(s, s), group='ships')

                Color(rgb=(.5, .5, .5))
                x, y = ship[0]
                r, b = ship[-1]
                x, r = sorted([x, r])
                y, b = sorted([y, b])
                x, y = self.coords_to_pos(x, y-1, centered=False)
                r, b = self.coords_to_pos(r+1, b, centered=False)
                x, y, r, b = x+w, y-w, r-w, b+w
                Line(points=[x, y, r, y, r, b, x, b], width=w, close=True, group='ships')


class PrepareGrid(Grid):
    selected_ship = ObjectProperty(allownone=True)

    def reset(self):
        self.selected_ship = None
        super().reset()

    def cell_click(self, cell_coords):
        ships = [ship for sublist in self.ships for ship in sublist if sublist is not self.selected_ship]

        for ship in self.ships:
            if cell_coords in ship:
                if ship is self.selected_ship:  # Click on already selected ship
                    if cell_coords != self.selected_ship[0]:
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
                rx, ry = cell_coords[0]-self.selected_ship[0][0], cell_coords[1]-self.selected_ship[0][1]
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
    pass


class EnemyGrid(Grid):
    blocked = BooleanProperty(False)

    def cell_click(self, cell_coords):
        if not self.blocked:
            if self.hit_cell(cell_coords) is False:  # Hit empty cell
                self.blocked = True

    def draw_ships(self):
        pass  # Don't draw ships


# class CellHeader(MDLabel):
#     DEFAULT_COLOR = [20/255, 94/255, 138/255]
#     HIT_COLOR = [0.4, 0, 0]
#     MISS_COLOR = [0, 0, 0.4]
#     line_thickness = NumericProperty(2)
#     bg_color = ListProperty(DEFAULT_COLOR)
#
#
# class Cell(ButtonBehavior, CellHeader):
#     DEFAULT_COLOR = [0, 132/255, 210/255]
#     coords = ObjectProperty((0, 0))
#     is_hit = BooleanProperty(None, allownone=True)
#     bg_color = ListProperty(DEFAULT_COLOR)
#
#     def on_is_hit(self, *args):
#         if self.is_hit:
#             self.bg_color = self.HIT_COLOR
#         elif self.is_hit is False:
#             self.bg_color = self.MISS_COLOR
#         else:
#             self.bg_color = self.DEFAULT_COLOR
