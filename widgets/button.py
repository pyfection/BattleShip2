from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivymd.uix.button import MDIconButton


Builder.load_string("""
<RoundButton>:
    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [self._radius]
""")


class RoundButton(ButtonBehavior, Label):
    _radius = NumericProperty(18)
    bg_color = ListProperty([.7, .7, .7, 1])


class AnimatedIconButton(MDIconButton):
    sources = ListProperty()
    iteration_speed = NumericProperty(0.2)
    _current_iteration = NumericProperty(0)
    _iteration_event = ObjectProperty()

    def on_kv_post(self, base_widget):
        self._iteration_event = Clock.schedule_interval(self.iterate, self.iteration_speed)

    def on_iteration_speed(self, _, iteration_speed):
        self._iteration_event.cancel()
        self._iteration_event = Clock.schedule_interval(self.iterate, self.iteration_speed)

    def iterate(self, *args):
        self._current_iteration = (self._current_iteration + 1) % len(self.sources)
        self.icon = self.sources[self._current_iteration]
