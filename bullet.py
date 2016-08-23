import pygame, math
from constant import *

class Bullet(object):

    def __init__(self, pos):
        self.rect = pygame.Rect(0, 0, BULLET_SIZE, BULLET_SIZE)
        self.rect.midbottom = (pos[0], pos[1])
        self.velocity = -1 * BULLET_SPEED

    def update(self):
        if self.rect.bottom <= CEILING:
            return True
        self.rect.bottom += self.velocity
        return False

class EnemyBullet(object):

    def __init__(self, pos, target_pos, mask):
        self.rect = pygame.Rect(0, 0, BULLET_SIZE, BULLET_SIZE)
        self.rect.center = (pos[0], pos[1])
        self.target_pos = target_pos
        self.mask = mask
        self.dx = 0
        self.dy = 0
        dx = -self.rect.centerx + self.target_pos[0]
        dy = -self.rect.centery + self.target_pos[1]
        n = math.sqrt(dx * dx + dy * dy)
        if n > 0:
            self.dx = dx / n * BULLET_SPEED / 2
            self.dy = dy / n * BULLET_SPEED / 2

    def update(self, player):
        overlap_player = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if player.hitstun == 0 and player.scale >= 1.0 and self.mask.overlap(player.mask, overlap_player):
            player.get_hit = HIT
            player.lives = max(0, player.lives - 1)
        if self.rect.bottom <= CEILING:
            return True
        if self.rect.top >= FLOOR:
            return True
        if self.rect.left >= WIDTH:
            return True
        if self.rect.right <= 0:
            return True
        self.rect.center = (self.rect.centerx + self.dx, self.rect.centery + self.dy)
        return False
