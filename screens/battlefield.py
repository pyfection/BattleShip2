from kivy.properties import BooleanProperty, NumericProperty, ListProperty
from kivy.metrics import dp
from kivy.graphics import Color, Line
from kivy.uix.behaviors.button import ButtonBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel


class BattleField(MDScreen):
    pass


class Grid(MDGridLayout):
    draw_ships = BooleanProperty(False)
    dimensions = ListProperty((10, 10))
    cell_size = NumericProperty(dp(30))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_size = True
        self.col_force_default = True
        self.row_force_default = True
        self.col_default_width = self.cell_size
        self.row_default_height = self.cell_size

    def on_pos(self, _, pos):
        self.on_dimensions(_, self.dimensions)

    def on_dimensions(self, _, dimensions):
        w, h = dimensions
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
                cell = Cell(on_press=lambda _, x=x, y=y: self.cell_click(x, y))
                self.add_widget(cell)

    def cell_click(self, x, y):
        print(x, y)


class CellHeader(MDLabel):
    line_thickness = NumericProperty(2)


class Cell(ButtonBehavior, CellHeader):
    pass
