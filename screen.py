import pygame


class Screen():
    def __init__(self, pygame_screen, font_path):
        self.pygame_screen = pygame_screen
        self.font_path = font_path
        self.fonts = {
            'small': pygame.font.Font(font_path, 35),
            'normal': pygame.font.Font(font_path, 55),
            'large': pygame.font.Font(font_path, 75),
        }


    def render(self):
        return

    def update(self, event):
        return

class Menu(Screen):
    def __init__(self, pygame_screen, font_path):
        super().__init__(pygame_screen, font_path)

        self.selected = 0

        self.options = {
            'Play': {
                'action': '',
                'selected': True,
                'pos': 0,
            },
            'Help': {
                'action': '',
                'selected': False,
                'pos': 1,
            },
            'Quit': {
                'action': '',
                'selected': False,
                'pos': 2,
            }
        }

    def render_text(self, font, text, pos = (0, 0), colour = (0, 0, 0)):
        rendered_text_surface = font.render(text, False, colour)
        self.pygame_screen.blit(rendered_text_surface, pos)

    def render(self):
        font = self.fonts['large']

        for key, value in self.options.items():
            if(value['pos'] == self.selected):
                key = ">{0}".format(key)

            self.render_text(font, key, (value['pos'], value['pos'] * 55))


    def update(self, event):
        # Update menu state based off of key press
        # if event.type == pygame.locals.JOYAXISMOTION:
        #     # up/down
        #     if event.axis == 1:
        #         if int(event.value) < 0:
        #
        #         if int(event.value) > 0:
        #

        if event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_UP:
                self.selected -= 1
                self.selected %= 3
            elif event.key == pygame.locals.K_DOWN:
                self.selected += 1
                self.selected %= 3

            # pygame.event.clear(pygame.locals.KEYDOWN)



        return


