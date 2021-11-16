from kivy.lang.builder import Builder
from kivy.properties import ListProperty
from kivymd.uix.label import MDLabel


Builder.load_string("""
<ShadowLabel>:
    canvas.before:
        Color:
            rgba: root.tint

        Rectangle:
            pos:
                int(self.center_x - self.texture_size[0] / 2.) + root.decal[0],\
                int(self.center_y - self.texture_size[1] / 2.) + root.decal[1]

            size: root.texture_size
            texture: root.texture

        Color:
            rgba: 1, 1, 1, 1
""")


class ShadowLabel(MDLabel):
    decal = ListProperty([0, 0])
    tint = ListProperty([1, 1, 1, 1])
