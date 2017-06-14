import pygame
import pygame.locals
import socket
import select
import random
import time
import logging
import zmq
import pdb
from pyre import Pyre
from pyre import zhelper
from collections import namedtuple
from enum import Enum

class Movement(Enum):
    UP = 1;
    RIGHT = 2;
    DOWN = 3;
    LEFT = 4;
Position = namedtuple('Position', ['x', 'y']);

class Player():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.step = 10;

    def move(self, direction):
        if direction == Movement.UP:
            self.y -= self.step
        elif direction == Movement.RIGHT:
            self.x += self.step
        elif direction == Movement.DOWN:
            self.y += self.step
        elif direction == Movement.LEFT:
            self.x -= self.step

    def get_position(self):
        return Position(self.x, self.y);


class Network(): 
    def __init__(self):
        self.node = Pyre("GAME_NODE")
        self.node.set_header("HELLO", "ABC");
        self.node.start();
        self.node.join(GAME_GROUP);
        
        self.poller = zmq.Poller()
        self.poller.register(self.node.socket(), zmq.POLLIN)

    def poll(self):
        return dict(self.poller.poll(0))

    def peers():
        return self.node.peers()

    def stop(self):
        self.node.stop()

GAME_GROUP = "GAME"
class GameClient():
    def __init__(self):
        self.network = Network()
        self.player = Player();
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
                changes = self.network.poll()
                print("CHANGES", changes)
                print("NODE", self.network.node)
                print("PEERS", self.network.node.peers())

                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.locals.QUIT:
                        running = False
                        break
                    elif event.type == pygame.locals.KEYDOWN:
                        if event.key == pygame.locals.K_UP:
                            self.player.move(Movement.UP)
                        elif event.key == pygame.locals.K_DOWN:
                            self.player.move(Movement.DOWN)
                        elif event.key == pygame.locals.K_LEFT:
                            self.player.move(Movement.LEFT)
                        elif event.key == pygame.locals.K_RIGHT:
                            self.player.move(Movement.RIGHT)
                        pygame.event.clear(pygame.locals.KEYDOWN)

                self.screen.blit(
                       self.bg_surface, (0, 0))  # Draw the background
                self.screen.blit(self.image, self.player.get_position())

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
