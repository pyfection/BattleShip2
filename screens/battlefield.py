import uuid
from time import sleep
import requests

from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.button import MDFillRoundFlatButton

from ai import MediumAI
from config import config


Builder.load_file('screens/battlefield.kv')


class BattleField(MDScreen):
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])
    dimensions = ListProperty((10, 10))
    has_won = BooleanProperty(None, allownone=True)

    def _check_player(self, grid, coords):
        # Check if player won
        cell = grid.cells[coords]
        if cell.is_hit:
            remaining_ships = len([c for c in grid.cells.values() if c.is_hit])
            allowed_ships = sum(self.allowed_ships)
            text = str(allowed_ships - remaining_ships)
            grid.info_cell.text = text
            if remaining_ships == allowed_ships:
                self.has_won = True
                self.playing_area.disabled = True

    def _check_enemy(self, grid, coords):
        cell = grid.cells[coords]
        if cell.is_hit:
            remaining_ships = len([c for c in grid.cells.values() if c.is_hit])
            allowed_ships = sum(self.allowed_ships)
            text = str(allowed_ships - remaining_ships)
            grid.info_cell.text = text
            if remaining_ships == allowed_ships:
                self.has_won = False
                self.playing_area.disabled = True

    def start_game(self, ships):
        self.enemy_grid.unbind(last_move=self._check_player)
        self.player_grid.unbind(last_move=self._check_enemy)
        self.enemy_grid.reset()
        self.player_grid.reset()
        self.playing_area.disabled = False
        self.has_won = None
        self.player_grid.ships = ships
        self.enemy_grid.bind(last_move=self._check_player)
        self.player_grid.bind(last_move=self._check_enemy)

    def enemy_turn(self):
        pass


class SPBattleField(BattleField):
    ai = ObjectProperty()

    def _enemy_turn(self, *args):
        successes = [c.coords for c in self.player_grid.cells.values() if c.is_hit]
        if self.player_grid.hit_cell(self.ai.make_turn(successes)) is True:  # Hit ship
            self.enemy_turn()
        self.enemy_grid.blocked = False

    def start_game(self, ships):
        super().start_game(ships)
        self.enemy_grid.randomly_place_ships()
        self.ai = MediumAI(self.dimensions)

    def enemy_turn(self):
        if self.has_won is None:
            Clock.schedule_once(self._enemy_turn, 1)


class MPBattleField(BattleField):
    enemy_decision = ObjectProperty()
    own_decision = ObjectProperty()
    player_id = StringProperty(str(uuid.uuid4()))
    player_name = config.get('PLAYER')['NAME']
    current_snackbar = ObjectProperty(allownone=True)

    def on_pre_enter(self, *args):
        self.enemy_grid.blocked = True
        self.disabled = True
        self.enemy_grid.bind(last_move=self._set_own_decision)
        Window.bind(on_request_close=self.disconnect)

    def on_leave(self, *args):
        self.disconnect()

    def _set_own_decision(self, player_grid, move):
        self.end_turn(move)

    def failure(self, req, result):
        def to_menu(*args):
            self.current_snackbar.dismiss()
            self.current_snackbar = None
            self.manager.current = 'main'

        btn = MDFillRoundFlatButton(text="Menu", on_press=to_menu)
        self.current_snackbar = Snackbar(
            text=f"An error has occured: {result['message']}",
            font_size='10sp',
            auto_dismiss=False,
            buttons=[btn],
        )
        self.current_snackbar.open()

    def disconnect(self, *args):
        print("Disconnecting")
        requests.get(
            url=f'{config["MULTIPLAYER_URL"]}/disconnect?userid={self.player_id}'
        )
        print('successful disconnected!')
        Window.unbind(on_request_close=self.disconnect)
        self.manager.current = 'main'

    def connect(self):
        ships = [s for sublist in self.player_grid.ships for s in sublist]
        ships = ''.join(
            [str(int((x, y) in ships)) for y in range(self.dimensions[1]) for x in range(self.dimensions[0])]
        )
        ships = int(ships, 2)
        UrlRequest(
            url=f'{config["MULTIPLAYER_URL"]}/connect?userid={self.player_id}&username={self.player_name}&ships={ships}',
            on_success=self._connect,
            on_failure=self.failure,
        )

    def _connect(self, req, result):
        if self.transition_state == 'out':
            return

        if req.resp_headers['status'] == 'waiting':
            sleep(1)
            print("Waiting for connection...")
            self.connect()
        elif req.resp_headers['status'] == 'connected':
            Snackbar(text=f"Player {result['username']} connected").open()
            w, h = self.dimensions
            bin_ships = list(map(int, bin(int(result['ships']))[2:].zfill(w*h)))
            self.enemy_grid.ships = [[(i % w, i // w)] for i, b in enumerate(bin_ships) if b]
            self.check_turn()
        else:
            raise ValueError(f"Status {req.resp_headers['status']} is not a valid status!")

    def check_turn(self):
        UrlRequest(
            url=f'{config["MULTIPLAYER_URL"]}/check-turn?userid={self.player_id}',
            on_success=self._check_turn,
            on_failure=self.failure,
        )

    def _check_turn(self, req, result):
        if self.transition_state == 'out':
            return

        w, h = self.dimensions
        bin_hits = list(map(int, bin(int(result['enemy_hits']))[2:].zfill(w * h)))
        for i, b in enumerate(bin_hits):
            if not b:
                continue
            x, y = (i % w, i // w)
            self.player_grid.hit_cell((x, y))

        if req.resp_headers['status'] == 'waiting':
            sleep(1)
            print("Waiting for turn...")
            self.check_turn()
        elif req.resp_headers['status'] == 'success' and result['has_turn']:
            Snackbar(text="Now is your turn!").open()
            self.enemy_grid.blocked = False
            self.disabled = False
        else:
            raise ValueError(f"Status {req.resp_headers['status']} is not a valid status!")

    def end_turn(self, move):
        self.enemy_grid.blocked = True
        self.disabled = True
        w, h = self.dimensions
        i = move[1]*w+move[0]
        hit = int('0'*i + '1' + '0'*(w*h-(i+1)), 2)
        UrlRequest(
            url=f'{config["MULTIPLAYER_URL"]}/end-turn?userid={self.player_id}&hit={hit}',
            on_success=self._end_turn,
            on_failure=self.failure,
        )

    def _end_turn(self, req, result):
        if self.transition_state == 'out':
            return

        if req.resp_headers['status'] == 'error':
            self.enemy_grid.blocked = False
            self.disabled = False
            print("Error:", result['error'])
        elif req.resp_headers['status'] == 'success':
            print("Sucessfully ended turn!")
            self.check_turn()
        else:
            raise ValueError(f"Status {req.resp_headers['status']} is not a valid status!")

    def start_game(self, ships):
        super().start_game(ships)
        print('establish connection')
        self.connect()

    def on_enemy_decision(self, _, enemy_decision):
        self.player_grid.hit_cell(enemy_decision)
        self.enemy_grid.blocked = False
        self.disabled = False
