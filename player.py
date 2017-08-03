from collections import namedtuple
from enum import Enum
import math
import random
import pygame
import configparser
from pygame.rect import Rect

import client

class Movement(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
Position = namedtuple('Position', ['x', 'y'])

class Action(Enum):
    SPELL = 1
    SWIPE = 2

class Action_Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

class PlayerException(Exception):
    pass

class Player():
    def __init__(self, screen, map, position=(0, 0), size=(32, 32), colour=(255, 255, 255), name = "Name"):
        self.screen = screen
        self.map = map
        self.ready = False
        self.is_centre = False
        self.size = size
        self.step = self.size[0]
        self.colour = colour
        self.name = name
        self.cast_spell = None

        if len(position) > 0:
            self.initial_position = position
            self.set_position(position)

    def __raiseNoPosition(self):
        raise PlayerException({"message": "Player does not have a position set", "player": self})


    def save_to_config(self):
        config = configparser.ConfigParser()

        config['Player'] = {}
        config['Player']['name'] = self.name
        config['Player']['x'] = str(self.x)
        config['Player']['y'] = str(self.y)

        with open('player_save', 'w') as configfile:
            config.write(configfile)

        return

    def load_from_config(self):
        config = configparser.ConfigParser()
        config.read('player_save')

        if 'Player' in config:
            player_save_info = config['Player']

            self.set_name(player_save_info['name'])
            self.set_position(
                (
                    int(player_save_info['x']),
                    int(player_save_info['y'])
                )
            )

            return True

        return False

    def set_name(self, name, save = False):
        self.name = name
        if save: self.save_to_config()

    def set_position(self, position):
        self.x, self.y = position
        print('X: {0} Y: {1}'.format(self.x // self.size[0], self.y // self.size[1]))
        self.ready = True

    def render(self):
        centre = self.map.get_centre()

        font = pygame.font.Font(client.font, 30)

        name_tag = font.render(self.name, False, (255, 255, 255))

        if not self.is_centre:
            centre = (
                self.x - self.map.centre_player.x + centre[0],
                self.y - self.map.centre_player.y + centre[1]
            )

        name_tag_pos = (
                centre[0] + ((self.size[0] - name_tag.get_width()) // 2),
                centre[1] - ((self.size[1] + name_tag.get_height()) // 2)
        )

        # Check if the user has cast a spell.
        if self.cast_spell is not None:
            self.cast_spell.render()

        self.screen.blit(name_tag, name_tag_pos)
        pygame.draw.rect(self.screen, self.colour, Rect(centre, self.size))

    def move(self, direction):
        if not self.ready:
            self.__raiseNoPosition()

        collision = False

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

        if not self.map.can_move_to(tmp_x, tmp_y):
            return

        self.set_position(Position(tmp_x, tmp_y))

    def get_position(self):
        if not self.ready:
            self.__raiseNoPosition()

        return Position(self.x, self.y)

    def attack(self, action, direction):
        centre = self.map.get_centre()

        if action == Action.SPELL:
            if direction == Action_Direction.UP:
                self.cast_spell = Spell(self, 0, -10)
            elif direction == Action_Direction.RIGHT:
                self.cast_spell = Spell(self, 10, 0)
            elif direction == Action_Direction.DOWN:
                self.cast_spell = Spell(self, 0, 10)
            elif direction == Action_Direction.LEFT:
                self.cast_spell = Spell(self, -10, 0)
        elif action == Action.SWIPE:
            #TODO
            return

class Spell():
    def __init__(self, player, x_velocity, y_velocity, position=(0,0), size=(8,8), colour=(0,0,0)):
        self.player = player
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        self.size = size
        self.colour = colour
        self.x_distance = 0
        self.y_distance = 0

        self.set_position(position)

    def render(self):
        position = (
            self.player.map.get_centre()[0] + self.x_distance,
            self.player.map.get_centre()[1] + self.y_distance
        )

        if not self.player.is_centre:
            position = (
                self.x - self.player.map.centre_player.x + position[0] + self.x_distance,
                self.y - self.player.map.centre_player.y + position[1] + self.y_distance
            )

        pygame.draw.rect(self.player.screen, self.colour, Rect(position, self.size))
        self.x_distance += self.x_velocity
        self.y_distance += self.y_velocity

    def get_position(self):
        return Position(self.x, self.y)

    def set_position(self, position):
        self.x, self.y = position

    def hit_target(self,player): # Return if the spell has hit another player.
        return self.rect.colliderect(player.map.get_tile_attributes(player.x, player.y))

class PlayerManager():
    def __init__(self, me):
        self.me = me
        self.me.load_from_config()
        self.others = {}

    def set(self, players):
        newPlayers = {}
        for uuid in players:
            random.seed(uuid)
            colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            newPlayers[uuid] = self.others.get(uuid, Player(self.me.screen, self.me.map, colour=colour))
        self.others = newPlayers

    def all(self):
        return list(self.others.values()).push(self.me)

    def get(self, uuid):
        return self.others[uuid]
