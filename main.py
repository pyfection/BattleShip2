from kivymd.app import MDApp as App
from kivy.factory import Factory


Factory.register('BattleField', module='screens.battlefield')


class BattleShip(App):
    pass


if __name__ == '__main__':
    app = BattleShip()
    app.run()
