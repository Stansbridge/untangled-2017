import pygame
import time

from enum import Enum

class Screen():
    def __init__(self, pygame_screen, font_path):
        self.pygame_screen = pygame_screen
        self.font_path = font_path
        self.fonts = {
            'small': pygame.font.Font(font_path, 35),
            'normal': pygame.font.Font(font_path, 55),
            'large': pygame.font.Font(font_path, 75),
            'heading': pygame.font.Font(font_path, 95),
        }


    def render(self):
        return

    def update(self, event):
        return

class MenuState(Enum):
    CHOICE = 0
    CHAR_SETUP = 1

class Menu(Screen):
    def __init__(self, pygame_screen, font_path):
        super().__init__(pygame_screen, font_path)

        self.selected = 0
        self.state = MenuState.CHOICE
        self.ticker = 0.0
        self.char_name = ''
        self.options = {
            'Play': {
                'pos': 0,
            },
            'Help': {
                'pos': 1,
            },
            'Quit': {
                'pos': 2,
            }
        }

    def render_text(self, font, text, pos = (0, 0), colour = (0, 0, 0)):
        rendered_text_surface = font.render(text, False, colour)
        self.pygame_screen.blit(rendered_text_surface, pos)

    def render(self, offset = (0, 0)):
        font = self.fonts['large']
        header_font = self.fonts['heading']

        self.ticker += 2
        self.ticker %= 100

        self.render_text(header_font, "Untangled 2017", (offset[0] - 125, 300), (100, 200,100))
        if(self.state == MenuState.CHOICE):
            for key, value in self.options.items():
                if(value['pos'] == self.selected):
                    key = ">{0}".format(key)

                self.render_text(font, key, (value['pos'] + offset[0], value['pos'] * 55 + offset[1]))
        elif(self.state == MenuState.CHAR_SETUP):
            self.render_text(font, 'Name: ', (offset[0] - 125, offset[1]))
            if(self.ticker > 50):
                self.render_text(font, self.char_name + '_', (offset[0], offset[1]))
            else:
                self.render_text(font, self.char_name, (offset[0], offset[1]))

    def update(self, event):
        # Update menu state based off of key press or joystick
        from client import GameState

        if event.type == pygame.locals.JOYAXISMOTION:
            # up/down
            if event.axis == 1:
                if int(event.value) < 0:
                    self.selected -= 1
                    self.selected %= 3  
                if int(event.value) > 0:
                    self.selected += 1
                    self.selected %= 3    
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_UP:
                self.selected -= 1
                self.selected %= 3
            elif event.key == pygame.locals.K_DOWN:
                self.selected += 1
                self.selected %= 3
            elif event.key == pygame.locals.K_SPACE or event.key == 54354:
                if(self.selected == 0):
                    # Leaving character name screen out for now
                    # self.state = MenuState.CHAR_SETUP
                    # return GameState.MENU
                    return GameState.PLAY
                elif(self.selected == 1):
                    return GameState.HELP
                elif(self.selected == 2):
                    return GameState.QUIT

        if(self.state == MenuState.CHAR_SETUP):
            if(event.type == pygame.locals.KEYDOWN):
                if(event.key == pygame.locals.K_BACKSPACE):
                    self.char_name = self.char_name[:-1]
                elif(event.key < 122 and event.key != 13):
                    self.char_name += chr(event.key)

        return


