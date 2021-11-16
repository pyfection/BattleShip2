import os
import uuid
from time import sleep
import json
import requests

from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.screen import MDScreen

from ai import MediumAI
from config import config


Builder.load_file('screens/battlefield.kv')


class BattleField(MDScreen):
    allowed_ships = ListProperty([5, 4, 4, 3, 3, 3, 2, 2, 2, 2])
    dimensions = ListProperty((10, 10))
    has_won = BooleanProperty(None, allownone=True)

    def _check_player(self, *args):
        # Check if player won
        if len([c for c in self.enemy_grid.cells.values() if c.is_hit]) == sum(self.allowed_ships):
            self.has_won = True
            self.playing_area.disabled = True

    def _check_enemy(self, *args):
        if len([c for c in self.player_grid.cells.values() if c.is_hit]) == sum(self.allowed_ships):
            self.has_won = False
            self.playing_area.disabled = True

    def start_game(self, ships):
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

    def start_game(self, ships):
        super().start_game(ships)
        self.enemy_grid.randomly_place_ships()
        self.ai = MediumAI(self.dimensions)

    def enemy_turn(self):
        while self.has_won is None:
            successes = [c.coords for c in self.player_grid.cells.values() if c.is_hit]
            if self.player_grid.hit_cell(self.ai.make_turn(successes)) is False:  # Hit empty field
                break
        self.enemy_grid.blocked = False


class MPBattleField(BattleField):
    enemy_decision = ObjectProperty()
    own_decision = ObjectProperty()
    player_id = StringProperty(str(uuid.uuid4()))
    player_name = config['PLAYERNAME']

    def on_pre_enter(self, *args):
        self.enemy_grid.blocked = True
        self.disabled = True
        self.enemy_grid.bind(last_move=self._set_own_decision)
        Window.bind(on_request_close=lambda *args: self.disconnect())

    def on_leave(self, *args):
        self.disconnect()

    def _set_own_decision(self, player_grid, move):
        self.end_turn(move)

    def disconnect(self):
        print("Disconnecting")
        requests.get(
            url=f'{config["MULTIPLAYER_URL"]}/disconnect?userid={self.player_id}'
        )
        print('successful disconnected!')

    def connect(self):
        ships = [s for sublist in self.player_grid.ships for s in sublist]
        ships = ''.join(
            [str(int((x, y) in ships)) for y in range(self.dimensions[1]) for x in range(self.dimensions[0])]
        )
        ships = int(ships, 2)
        UrlRequest(
            url=f'{config["MULTIPLAYER_URL"]}/connect?userid={self.player_id}&username={self.player_name}&ships={ships}',
            on_success=self._connect,
        )

    def _connect(self, req, result):
        if self.transition_state == 'out':
            return

        if req.resp_headers['status'] == 'waiting':
            sleep(1)
            print("Waiting for connection...")
            self.connect()
        elif req.resp_headers['status'] == 'connected':
            # ToDo: set enemy username  # result['username']
            print("Player", result['username'], "successfully connected!")
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
        )

    def _check_turn(self, req, result):
        if self.transition_state == 'out':
            return

        if req.resp_headers['status'] == 'waiting':
            sleep(1)
            print("Waiting for turn...")
            self.check_turn()
        elif req.resp_headers['status'] == 'success' and result['has_turn']:
            print("Now is your turn!", result['has_turn'])
            w, h = self.dimensions
            bin_hits = list(map(int, bin(int(result['enemy_hits']))[2:].zfill(w * h)))
            for i, b in enumerate(bin_hits):
                if not b:
                    continue
                x, y = (i % w, i // w)
                self.player_grid.hit_cell((x, y))
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
