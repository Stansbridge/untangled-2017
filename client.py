import pygame
import pygame.locals
import socket
import select
import random
import time
import logging
import zmq
import pdb
import bson
import uuid
from pyre import Pyre
from pyre import zhelper
from collections import namedtuple
from enum import Enum

from map import Map
from network import Network
from player import *
from screen import Menu

white = (255,255,255)
black = (0,0,0)
red = (255, 0, 0)


class GameState(Enum):
    MENU = 0
    PLAY = 1
    HELP = 2
    CHARACTER = 3
    QUIT = 4

class GameClient():
    game_state = GameState.MENU

    def __init__(self):
        self.network = Network()
        self.setup_pygame()
        self.players = PlayerManager(Player(self.screen, self.map, (0, 0), (32, 32)))
        self.map.set_centre_player(self.players.me) 

        self.menu = Menu(self.screen, 'alterebro-pixel-font.ttf')

    def setup_pygame(self, width=1024, height=1024):
        self.screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)
        self.player_image = pygame.image.load("sprite.png").convert_alpha()

        # Initialise fonts.
        pygame.font.init()

        # Initialise the joystick.
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in joysticks:
            joystick.init()

        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.locals.QUIT,
            pygame.locals.JOYAXISMOTION,
            pygame.locals.KEYDOWN])
        pygame.key.set_repeat(50, 50)

        # @TODO: Move tileset functionality from the Map into its own class.
        tileset = pygame.image.load("tileset.png").convert()
        self.map = Map(self.screen, tileset, (32, 32), (64, 64))
        self.map.init_grid()

    def set_state(self, new_state):
        if(new_state and new_state != self.game_state):
            self.game_state = new_state

    def run(self):
        running = True
        clock = pygame.time.Clock()
        tickspeed = 60

        try:
            while running:
                self.screen.fill((white))
                clock.tick(tickspeed)
                if(self.game_state.value == GameState.MENU.value):
                    self.menu.render((self.map.screen_size[0] * 0.45, self.map.screen_size[1]*0.4))
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or event.type == pygame.locals.QUIT or event.key == pygame.locals.K_ESCAPE:
                            running = False
                            break

                        self.set_state(self.menu.update(event))
                elif(self.game_state.value == GameState.QUIT.value):
                    running = False
                    break
                else:
                    # handle inputs
                    me = self.players.me
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or event.type == pygame.locals.QUIT:
                            running = False
                            break
                        elif event.key == pygame.locals.K_ESCAPE:
                            self.set_state(GameState.MENU)
                        # JOYAXISMOTION triggers when the value changes
                        # We need to retain the direction value each tick
                        # To emulate 'keydown' functionality
                        elif event.type == pygame.locals.JOYAXISMOTION:
                            # up/down
                            if event.axis == 1:
                                if int(event.value) < 0:
                                    me.move(Movement.UP)
                                if int(event.value) > 0:
                                    me.move(Movement.DOWN)
                            # left/right
                            elif event.axis == 0:
                                if int(event.value) < 0:
                                    me.move(Movement.LEFT)
                                if int(event.value) > 0:
                                    me.move(Movement.RIGHT)
                        elif event.type == pygame.locals.KEYDOWN:
                            if event.key == pygame.locals.K_UP:
                                me.move(Movement.UP)
                            elif event.key == pygame.locals.K_DOWN:
                                me.move(Movement.DOWN)
                            elif event.key == pygame.locals.K_LEFT:
                                me.move(Movement.LEFT)
                            elif event.key == pygame.locals.K_RIGHT:
                                me.move(Movement.RIGHT)
                            pygame.event.clear(pygame.locals.KEYDOWN)

                    self.map.render()
                    me.render()

                    self.players.set(self.network.node.peers())
                    # check network
                    events = self.network.get_events()
                    if events:
                        try:
                            for event in self.network.get_events():
                                print(event.peer_uuid, event.type, event.group, event.msg)

                                if event.group == "world:position":
                                    new_position = bson.loads(event.msg[0])
                                    network_player = self.players.get(event.peer_uuid)

                                    if network_player:
                                        network_player.set_position(Position(**new_position))
                        except Exception as e:
                            print(e)
                            pass

                    # if there are other peers we can start sending to groups
                    if self.players.others:
                        self.network.node.shout("world:position", bson.dumps(me.get_position()._asdict()))

                    for playerUUID, player in self.players.others.items():
                        try:
                            # self.screen.blit(self.player_image, player.get_position())
                            player.render()
                        except PlayerException as e:
                            # PlayerException due to no initial position being set for that player
                            print(e)
                            pass

                pygame.display.update()
        finally:
            self.network.stop()

if __name__ == '__main__':
    logger = logging.getLogger("pyre")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.propagate = False

    g = GameClient()
    g.run()
