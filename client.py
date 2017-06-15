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


white = (255,255,255)
black = (0,0,0)
red = (255, 0, 0)

class Movement(Enum):
    UP = 1;
    RIGHT = 2;
    DOWN = 3;
    LEFT = 4;
Position = namedtuple('Position', ['x', 'y']);

class PlayerException(Exception):
    pass

class Player():
    def __init__(self, position=()):
        self.ready = False
        self.step = 10;
        if len(position) > 0:
            self.set_position(position)

    def __raiseNoPosition(self):
        raise PlayerException({"message": "Player does not have a position set", "player": self})

    def set_position(self, position):
        self.x, self.y = position
        self.ready = True

    def move(self, direction):
        if not self.ready:
            self.__raiseNoPosition()

        if direction == Movement.UP:
            self.y -= self.step
        elif direction == Movement.RIGHT:
            self.x += self.step
        elif direction == Movement.DOWN:
            self.y += self.step
        elif direction == Movement.LEFT:
            self.x -= self.step

    def get_position(self):
        if not self.ready:
            self.__raiseNoPosition()

        return Position(self.x, self.y);

class Network(): 
    def __init__(self):
        self.node = Pyre("GAME_NODE")
        self.node.set_header("HELLO", "ABC");
        self.node.start();
        self.node.join("world:position");
        
        self.poller = zmq.Poller()
        self.poller.register(self.node.socket(), zmq.POLLIN)

    def poll(self):
        return dict(self.poller.poll(0))

    def peers():
        return self.node.peers()

    def stop(self):
        self.node.stop()

    def get_events(self):
        changes = self.poll()
        if self.node.socket() in changes and changes[self.node.socket()] == zmq.POLLIN:
            events = self.node.recent_events()
            return events

class PlayerList():
    def __init__(self, me):
        self.me = me
        self.others = {}

    def add(self, uuid):
        if uuid not in self.others:
            self.others[uuid] = Player()

    def all(self):
        return list(self.others.values()).push(self.me)

    def get(self, uuid):
        return self.others[uuid]

class GameClient():
    def __init__(self):
        self.network = Network()
        self.players = PlayerList(Player(Position(0, 0)))
        self.setup_pygame()

    def setup_pygame(self, width=400, height=300):
        self.screen = pygame.display.set_mode((width, height))
        self.player_image = pygame.image.load("sprite.png").convert_alpha()

        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in joysticks:
            joystick.init()

        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.locals.QUIT,
            pygame.locals.JOYAXISMOTION,
            pygame.locals.KEYDOWN])
        pygame.key.set_repeat(50, 50)

        tileset = pygame.image.load("tileset.png").convert()
        self.map = Map(self.screen, tileset);
        self.map.init_grid();

    def run(self):
        running = True
        clock = pygame.time.Clock()
        tickspeed = 30

        try:
            while running:
                self.screen.fill((white))
                clock.tick(tickspeed)

                # handle inputs
                me = self.players.me
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.locals.QUIT:
                        running = False
                        break
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
                self.screen.blit(self.player_image, me.get_position())
                
                otherPlayers = self.network.node.peers()
                for playerUUID in otherPlayers:
                    self.players.add(playerUUID)

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
                if len(otherPlayers) > 0:
                    self.network.node.shout("world:position", bson.dumps(me.get_position()._asdict()))

                for playerUUID, player in self.players.others.items():
                    try:
                        self.screen.blit(self.player_image, player.get_position())
                    except PlayerException as e:
                        # PlayerException due to no initial position being set for that player
                        print(e)
                        pass

                pygame.display.update()
        finally:
            self.network.stop();

if __name__ == '__main__':
    logger = logging.getLogger("pyre")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.propagate = False

    g = GameClient()
    g.run()
