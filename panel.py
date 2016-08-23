import pygame
from constant import *

class Panel(object):

    def __init__(self, x, y, num, hitstun = 0, move_up = 0):
        self.rect = pygame.Rect(x + PANEL_SIZE / 2, y, PANEL_SIZE, PANEL_SIZE)
        self.disappear = False
        self.num = num
        self.x = x
        self.y = y
        self.rect.width = 0
        self.move_up = move_up
        self.hitstun = hitstun
        self.disappear_sound = pygame.mixer.Sound('res/snd/PANEL_SOUND.ogg')

    def update(self, ball, player):
        self.hitstun = max(self.hitstun - 1, 0)
        if self.hitstun > 0:
            self.move_up += 2
        else:
            self.move_up = 0
        if self.rect.colliderect(ball.rect) and self.hitstun == 0:
            self.disappear_sound.play()
            self.num -= 1
            if self.num <= 0:
                self.hitstun = HITSTUN
                self.disappear = True
            else:
                self.hitstun = HITSTUN
                self.__init__(self.x, self.y, self.num, self.hitstun, self.move_up)
            player.score += 100
        if not self.disappear:
            if self.rect.width < PANEL_SIZE:
                self.rect.width += 2
                self.rect.centerx -= 1
        else:
            self.rect.width -= 2
            self.rect.centerx += 1
            if self.rect.width <= 0:
                return True
        return False
