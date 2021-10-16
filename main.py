from kivymd.app import MDApp as App
from kivy.factory import Factory


Factory.register('Grid', module='widgets.grid')
Factory.register('PrepareGrid', module='widgets.grid')
Factory.register('Prepare', module='screens.prepare')
Factory.register('BattleField', module='screens.battlefield')


class BattleShip(App):
    def start_battle(self, ships):
        self.root.current = 'battlefield'
        self.root.battlefield.start_singleplayer(ships)


if __name__ == '__main__':
    app = BattleShip()
    app.run()
