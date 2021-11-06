from kivymd.app import MDApp as App
from kivy.factory import Factory


Factory.register('PrepareGrid', module='widgets.grid')
Factory.register('PlayerGrid', module='widgets.grid')
Factory.register('EnemyGrid', module='widgets.grid')
Factory.register('MainMenu', module='screens.mainmenu')
Factory.register('Prepare', module='screens.prepare')
Factory.register('BattleField', module='screens.battlefield')


class BattleShip(App):
    def start_battle(self, ships, game_type):
        self.root.current = 'battlefield'
        self.root.battlefield.start_singleplayer(ships)


if __name__ == '__main__':
    app = BattleShip()
    app.run()
