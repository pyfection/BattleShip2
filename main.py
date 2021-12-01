from kivymd.app import MDApp as App
from kivy.logger import Logger
from kivy.base import EventLoop
from kivy.factory import Factory
from kivmob import KivMob, TestIds


Factory.register('ShadowLabel', module='widgets.shadowlabel')
Factory.register('RoundButton', module='widgets.button')

Factory.register('MainMenu', module='screens.mainmenu')
Factory.register('Prepare', module='screens.prepare')
Factory.register('SPBattleField', module='screens.battlefield')
Factory.register('MPBattleField', module='screens.battlefield')


class BattleShip(App):
    title = "BattleShip"
    icon = "icon.png"

    def build(self):
        self.ads = KivMob("ca-app-pub-4572994351915717~5230704479")
        self.ads.new_interstitial("ca-app-pub-4572994351915717/4247977059")
        self.ads.request_interstitial()

    def on_start(self):
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def on_resume(self):
        self.ads.request_interstitial()

    def hook_keyboard(self, window, key, *largs):
        if key == 27:  # Escape
            if self.root.current != 'main':
                if self.root.current in ('sp_battlefield', 'mp_battlefield'):
                    Logger.info("Show interstitial")
                    self.ads.show_interstitial()
                self.root.current = 'main'
            else:
                self.stop()
            return True

    def start_battle(self, ships, game_type):
        if game_type == 'singleplayer':
            self.root.current = 'sp_battlefield'
            self.root.sp_battlefield.start_game(ships)
        elif game_type == 'multiplayer':
            self.root.current = 'mp_battlefield'
            self.root.mp_battlefield.start_game(ships)


if __name__ == '__main__':
    app = BattleShip()
    app.run()
