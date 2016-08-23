import pygame

class Text(object):

    def __init__(self, string, color = [255, 255, 255], size = 16):
        self.font = pygame.font.Font('res/fon/font.ttf', size)
        self.color = color
        self.text = string
        self.height = self.font.get_height()
        self.renderable = self.font.render(self.text, False, self.color)
        self.width = self.renderable.get_width()

    def draw(self, surface, pos = (0, 0)):
        surface.blit(self.renderable, pos)

    def update(self, string, color = [255, 255, 255]):
        if string != None and string != self.text:
            self.text = string
            self.renderable = self.font.render(self.text, False, color)
            self.width = self.renderable.get_width()
        return
