import pygame
from constant import *

class Ball():

    def __init__(self, x, y, mask):
        self.rect = pygame.Rect(0, 0, 16, 16)
        self.rect.center = (x, y)
        self.velocity = [2, 2]
        self.mask = mask
        self.collide_sound = pygame.mixer.Sound('res/snd/COLLIDE_SOUND.ogg')

    def update(self, player, bullets):
        if self.rect.bottom >= FLOOR and abs(self.velocity[1]) <= 3:
            self.velocity = [0, 0]
            return True
        self.velocity[1] += GRAVITY
        self.rect.centerx += self.velocity[0]
        self.rect.bottom += self.velocity[1]
        for bullet in bullets:
            if self.rect.colliderect(bullet.rect):
                if self.rect.bottom >= bullet.rect.top:
                    self.rect.bottom = bullet.rect.top
                    self.velocity[1] = self.velocity[1] * -1 * REDUCTION + bullet.velocity * 2
                if self.rect.centerx < bullet.rect.centerx:
                    self.velocity[0] = abs(self.velocity[0]) + bullet.velocity * REDUCTION
                elif self.rect.centerx > bullet.rect.centerx:
                    self.velocity[0] = abs(self.velocity[0]) * -1 - bullet.velocity * REDUCTION

        if player.scale >= 1.0 and self.rect.colliderect(player.rect):
            if self.rect.bottom >= player.rect.top:
                self.rect.bottom = player.rect.top
                self.velocity[1] *= -1 * REDUCTION
            if self.rect.left <= player.rect.right or self.rect.right <= player.rect.left:
                self.velocity[0] = self.velocity[0] * -1 * REDUCTION
        elif self.rect.bottom >= FLOOR:
            self.collide_sound.play()
            self.rect.bottom = FLOOR
            self.velocity[1] *= -1 * REDUCTION
        elif self.rect.top < CEILING:
            self.collide_sound.play()
            self.rect.top = CEILING
            self.velocity[1] *= -1 * REDUCTION
        if self.rect.left <= 0:
            self.collide_sound.play()
            self.rect.left = 0
            self.velocity[0] *= -1 * REDUCTION
        elif self.rect.right >= WIDTH:
            self.collide_sound.play()
            self.rect.right = WIDTH
            self.velocity[0] *= -1 * REDUCTION
        return False
