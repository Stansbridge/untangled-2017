from collections import namedtuple
from enum import Enum
import math
import random
import pygame
import configparser
from pygame.rect import Rect

import client
import map as map_module

class Movement(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4
Position = namedtuple('Position', ['x', 'y'])
SpellProperties = namedtuple('SpellProperties', ['x', 'y', 'x_velocity', 'y_velocity',])

class Action(Enum):
    SPELL = 1
    SWIPE = 2

class PlayerException(Exception):
    pass

class Player():
    def __init__(self, screen, map, colour=(255, 255, 255)):
        self.screen = screen
        self.map = map
        self.ready = False
        self.is_centre = False
        self.size = (map_module.TILE_PIX_WIDTH, map_module.TILE_PIX_HEIGHT)
        self.step = 1
        self.colour = colour
        self.name = 'Name'
        self.cast_spell = None

        self.initial_position = (0, 0)
        self.set_position(self.initial_position)

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
        self.ready = True

    def render(self):
        font = pygame.font.Font(client.font, 30)
        name_tag = font.render(self.name, False, (255, 255, 255))

        centre = self.map.get_pixel_pos(self.x, self.y)

        name_tag_pos = (
            centre[0] + ((self.size[0] - name_tag.get_width()) // 2),
            centre[1] - ((self.size[1] + name_tag.get_height()) // 2)
        )

        self.screen.blit(name_tag, name_tag_pos)
        self.rect = pygame.draw.rect(self.screen, self.colour, Rect(centre, self.size))

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

        if not self.map.level.can_move_to(tmp_x, tmp_y):
            return

        self.set_position(Position(tmp_x, tmp_y))

    def get_position(self):
        if not self.ready:
            self.__raiseNoPosition()

        return Position(self.x, self.y)

    def attack(self, action, direction):
        if action == Action.SPELL:
            if direction == Movement.UP:
                self.cast_spell = Spell(self, (0, -0.25))
            elif direction == Movement.RIGHT:
                self.cast_spell = Spell(self, (0.25, 0))
            elif direction == Movement.DOWN:
                self.cast_spell = Spell(self, (0, 0.25))
            elif direction == Movement.LEFT:
                self.cast_spell = Spell(self, (-0.25, 0))
        elif action == Action.SWIPE:
            #TODO
            return

class Spell():
    def __init__(self, player, velocity, position=None, size=(0.25, 0.25), colour=(0,0,0)):
        self.player = player
        self.size = size
        self.colour = colour
        if position == None:
            # spawn at player - additional maths centres the spell
            self.x = self.player.x + 0.5 - (size[0] / 2)
            self.y = self.player.y + 0.5 - (size[1] / 2)
        else:
            self.set_position(position)

        self.set_velocity(velocity)

    def render(self):
        pixel_pos = self.player.map.get_pixel_pos(self.x, self.y);
        pixel_size = (
            self.size[0] * map_module.TILE_PIX_WIDTH,
            self.size[1] * map_module.TILE_PIX_HEIGHT
        )
        self.rect = pygame.draw.rect(self.player.screen, self.colour, Rect(pixel_pos, pixel_size))

        # move the projectile by its velocity
        self.x += self.velo_x
        self.y += self.velo_y

    def get_properties(self):
        return SpellProperties(self.x, self.y, self.velo_x, self.velo_y)

    def set_properties(self, properties):
        self.x, self.y, self.velo_x, self.velo_y = properties

    def set_position(self, position):
        self.x, self.y = position

    def set_velocity(self, velocity):
        self.velo_x, self.velo_y = velocity

    def hit_target(self, target):
        if self.rect.colliderect(target.rect):
            #TODO - decide on what to do with collision

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
