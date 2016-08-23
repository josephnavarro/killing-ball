import pygame
from constant import *

class Player():

    def __init__(self, x, mask):
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.midbottom = (x, FLOOR)
        self.mask = mask
        self.velocity = 0
        self.bullet_cooldown = 0
        self.anim = 1
        self.facing = 1
        self.index = 0
        self.hitstun = 0
        self.score = 0
        self.scale = 1.0
        self.get_hit = 0
        self.lives = 50

    def update(self, dx):
        self.hitstun = max(0, self.hitstun - 1)
        if dx > 0:
            self.facing = 1
        elif dx < 0:
            self.facing = -1
        if abs(dx) > 0:
            self.anim += 0.25
        else:
            self.anim = 1
        self.rect.centerx += dx
        if self.rect.left <= 0:
            self.rect.left = 0
        elif self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        self.velocity = dx
