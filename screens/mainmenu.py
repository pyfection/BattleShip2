from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.graphics import RenderContext, Color, Rectangle
from kivymd.uix.screen import MDScreen
from kivy.uix.widget import Widget

Builder.load_file('screens/mainmenu.kv')


class MainMenu(MDScreen):
    pass
    # def on_kv_post(self, base_widget):
    #     self.background_.add_widget(Background())


class Background(Widget):
    def __init__(self, **kwargs):
        self.canvas = RenderContext(use_parent_projection=True, use_parent_modelview=True)
        self.canvas.shader.source = 'assets/wave.glsl'
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_shader, 0)

    def update_shader(self, *args):
        s = self.canvas
        s['projection_mat'] = Window.render_context['projection_mat']
        s['time'] = Clock.get_boottime()
        s['resolution'] = list(map(float, self.size))
        s.ask_update()
