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
import json
import uuid
from pyre import Pyre
from pyre import zhelper
from collections import namedtuple
from enum import Enum
from pprint import pprint

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
            self.setup(position)

    def __raiseNotSetup(self):
        raise PlayerException({"message": "Cannot move a player that has not been setup", "player": self})

    def setup(self, position):
        self.x, self.y = position
        self.ready = True

    def move(self, direction):
        if not self.ready:
            self.__raiseNotSetup()

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
            self.__raiseNotSetup()

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

class PlayerList():
    def __init__(self, me):
        self.me = me
        self.others = {}

    def add(self, uuid):
        if uuid not in self.others:
            self.others[uuid] = Player()

    def all(self):
        return list(self.others.values()).push(self.me)

class GameClient():
    def __init__(self):
        self.network = Network()
        self.players = PlayerList(Player(Position(0, 0)))
        self.setup_pygame()

    def setup_pygame(self, width=400, height=300):
        self.screen = pygame.display.set_mode((width, height))
        self.bg_surface = pygame.image.load("bg.png").convert()

        self.image = pygame.image.load("sprite.png").convert_alpha()

        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.locals.QUIT,
                                  pygame.locals.KEYDOWN])
        pygame.key.set_repeat(50, 50)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        tickspeed = 30

        try:
            while running:
                clock.tick(tickspeed)

                # handle inputs
                me = self.players.me
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.locals.QUIT:
                        running = False
                        break
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

                # draw me
                self.screen.blit(
                       self.bg_surface, (0, 0))  # Draw the background
                self.screen.blit(self.image, me.get_position())

                # check network
                print("NODE", self.network.node)
                print("PEERS", self.network.node.peers())
                changes = self.network.poll()
                if self.network.node.socket() in changes and changes[self.network.node.socket()] == zmq.POLLIN:
                    cmds = self.network.node.recv()
                    msg_type = cmds.pop(0)
                    print("NODE_MSG TYPE: %s" % msg_type)
                    print("NODE_MSG PEER: %s" % uuid.UUID(bytes=cmds.pop(0)))
                    print("NODE_MSG NAME: %s" % cmds.pop(0))
                    if msg_type.decode('utf-8') == "SHOUT":
                        print("NODE_MSG GROUP: %s" % cmds.pop(0))
                    elif msg_type.decode('utf-8') == "ENTER":
                        headers = json.loads(cmds.pop(0).decode('utf-8'))
                        print("NODE_MSG HEADERS: %s" % headers)
                        for key in headers:
                            print("key = {0}, value = {1}".format(key, headers[key]))
                    print("NODE_MSG PAYLOAD: %s" % cmds)
                
                otherPlayers = self.network.node.peers()
                for playerUUID in otherPlayers:
                    self.players.add(playerUUID)

                # if there are other peers we can start sending to groups
                if len(otherPlayers) > 0:
                    self.network.node.shout("world:position", bson.dumps(me.get_position()._asdict()))

                for playerUUID, player in self.players.others.items():
                    try:
                        self.screen.blit(self.image, player.get_position())
                    except PlayerException as e:
                        # PlayerException due to no initial position being set for that player
                        print(e)

                pygame.display.update()
                print("LOOP")
        finally:
            self.network.stop();


if __name__ == '__main__':
    logger = logging.getLogger("pyre")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.propagate = False

    g = GameClient()
    g.run()
