from collections import namedtuple
from enum import Enum
import math
import random
import pygame
import configparser
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
    def __init__(self, screen, map, position=(0, 0), size=(32, 32), colour=(255, 255, 255), name = "Name"):
        self.screen = screen
        self.map = map
        self.ready = False
        self.is_centre = False
        self.size = size
        self.step = self.size[0]
        self.colour = colour
        self.name = name

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

        # get the font we want to use
        font = pygame.font.Font(None, 30)
        font.set_bold(True)

        # combine the text and font into an image
        name_tag = font.render(self.name, False, (255, 255, 255))

        # offset centre for the player's position on the screen if they are not
        # the centre player
        if not self.is_centre:
            centre = (
                self.x - self.map.centre_player.x + centre[0],
                self.x - self.map.centre_player.x + centre[1]
            )

        # position the name tag in a nice location, not directly over the player
        name_tag_pos = (
                centre[0] + ((self.size[0] - name_tag.get_width()) // 2), # shift text pos to be centre-aligned
                centre[1] - 20 # shift text pos to be above player
        )

        # put the text we've rendered onto the screen
        self.screen.blit(name_tag, name_tag_pos)

        # draw the player
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
