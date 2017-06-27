from collections import namedtuple
from enum import Enum

import pygame
from pygame.rect import Rect


class Movement(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
Position = namedtuple('Position', ['x', 'y'])

class PlayerException(Exception):
    pass

class Player():
    def __init__(self, screen, map, position=(), size=(16, 16)):
        self.screen = screen
        self.map = map
        self.ready = False
        self.size = size
        self.step = 16
        self.set_bound(Position(0,0))

        if len(position) > 0:
            self.set_position(position)

    def __raiseNoPosition(self):
        raise PlayerException({"message": "Player does not have a position set", "player": self})

    def set_bound(self, position):
        self.boundRect = Rect(position, self.size)

    def set_position(self, position):
        self.x, self.y = position
        self.set_bound(position)
        self.ready = True

    def render(self):
        pygame.draw.rect(self.screen, (255,255,255), self.boundRect)

    def move(self, direction):
        if not self.ready:
            self.__raiseNoPosition()

        tmp_x = self.x
        tmp_y = self.y

        if direction == Movement.UP:
            tmp_y -= self.step
        elif direction == Movement.RIGHT:
            tmp_x += self.step
        elif direction == Movement.DOWN:
            tmp_y += self.step
        elif direction == Movement.LEFT:
            tmp_x -= self.step

        collide = self.map.check_collision(tmp_x, tmp_y)

        # Only tiles of ID 6 are collidable right now.
        if(collide != 6):
            self.set_position(Position(tmp_x, tmp_y))

    def get_position(self):
        if not self.ready:
            self.__raiseNoPosition()

        return Position(self.x, self.y)

class PlayerManager():
    def __init__(self, me):
        self.me = me
        self.others = {}

    def set(self, players):
        newPlayers = {}
        for uuid in players:
            newPlayers[uuid] = self.others.get(uuid, Player(self.me.screen, self.me.map, (0,0)))
        self.others = newPlayers

    def all(self):
        return list(self.others.values()).push(self.me)

    def get(self, uuid):
        return self.others[uuid]
