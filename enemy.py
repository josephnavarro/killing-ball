import pygame, math, random
from constant import *

class Enemy(object):

    def __init__(self, hp, x, y):
        self.image = []
        self.hp = hp * HP_FACTOR
        self.display_hp = hp * HP_FACTOR
        self.max_hp = hp * HP_FACTOR
        self.index = 0
        self.hitstun = 0
        self.name = ''
        self.scale = 0.01
        self.movement = MOVEMENT_1
        self.speed = 5
        self.counter = 0
        self.threshold = THRESHOLD
        self.appear = True
        self.disappear = False
        self.has_set_target = False
        self.target_pos = (0, 0)
        self.fade = 0
        self.new_move = 0
        self.hurt_sound = pygame.mixer.Sound('res/snd/BOSS_HURT.ogg')

    def set_image(self, img):
        for x in xrange(2):
            im = img.subsurface(x * ENEMY_SIZE, 0, ENEMY_SIZE, ENEMY_SIZE)
            self.image.append(im)

        self.mask = pygame.mask.from_threshold(self.image[1], (0, 0, 0, 255), (1, 1, 1, 255))
        self.mask.invert()

    def set_rect(self, x, y):
        self.rect = pygame.Rect(0, 0, ENEMY_SIZE, ENEMY_SIZE)
        self.rect.center = (x, y)
        self.orig_pos = (x, y)

    def update(self, ball, player):
        self.hitstun = max(self.hitstun - 1, 0)
        overlap_ball = (ball.rect.x - self.rect.x, ball.rect.y - self.rect.y)
        overlap_player = (player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if self.appear:
            self.scale += 0.005
            if self.scale >= 1.0:
                self.scale = 1.0
                self.appear = False
        else:
            if self.mask.overlap(player.mask, overlap_player) and self.hp > 0 and self.scale == 1.0:
                if player.hitstun == 0:
                    player.hitstun = HITSTUN
                    player.get_hit = HIT
                    player.lives = max(0, player.lives - 1)
            if self.display_hp == 0:
                self.index = 1
                return True
            if self.mask.overlap(ball.mask, overlap_ball) and (abs(ball.velocity[0]) > 0 or abs(ball.velocity[1]) > 0):
                self.index += 0.25
                if self.hitstun == 0:
                    self.hurt_sound.play()
                    self.hitstun = HITSTUN
                    self.hp = max(0, self.hp - HP_FACTOR)
                self.rect.centerx = self.orig_pos[0] + random.randint(-1, 1)
                self.rect.centery = self.orig_pos[1] + random.randint(-1, 1)
            else:
                self.rect.center = self.orig_pos
                self.index = 0
            if self.movement == MOVEMENT_4 and self.counter == 0:
                self.new_move = random.randint(1, 3)
            if self.movement == MOVEMENT_1 or self.new_move == 1:
                self.counter += 1
                if self.counter >= self.threshold and not self.has_set_target:
                    self.target_pos = player.rect.midbottom
                    self.has_set_target = True
                if self.has_set_target:
                    dx = -self.rect.centerx + self.target_pos[0]
                    dy = -self.rect.centery + self.target_pos[1]
                    n = math.sqrt(dx * dx + dy * dy)
                    if n > 0:
                        dx = dx / n * self.speed
                        dy = dy / n * self.speed
                        self.orig_pos = (self.rect.centerx + dx, self.rect.centery + dy)
                        self.rect.center = self.orig_pos
                    if n <= 5:
                        self.target_pos = (WIDTH / 2, HEIGHT / 2)
                        if abs(self.rect.centerx - self.target_pos[0]) <= 5 and abs(self.rect.centery - self.target_pos[1]) <= 5:
                            self.has_set_target = False
                            self.counter = 0
                            self.new_move = 0
            elif self.movement == MOVEMENT_2 or self.new_move == 2:
                self.counter += 1
                if self.counter >= self.threshold and not self.has_set_target:
                    self.target_pos = player.rect.midbottom
                    self.has_set_target = True
                if self.has_set_target:
                    dx = -self.rect.centerx + self.target_pos[0]
                    dy = -self.rect.centery + self.target_pos[1]
                    n = math.sqrt(dx * dx + dy * dy)
                    if n > 0:
                        dx = dx / n * self.speed
                        dy = dy / n * self.speed
                        self.orig_pos = (self.rect.centerx + dx, self.rect.centery + dy)
                        self.rect.center = self.orig_pos
                    if n <= 5:
                        self.target_pos = (self.rect.centerx, HEIGHT / 2)
                        if abs(self.rect.centerx - self.target_pos[0]) <= 5 and abs(self.rect.centery - self.target_pos[1]) <= 5:
                            self.has_set_target = False
                            self.counter = 0
                            self.new_move = 0
            elif self.movement == MOVEMENT_3 or self.new_move == 3:
                self.counter += 1
                if self.counter >= self.threshold and not self.has_set_target:
                    a = random.randint(ENEMY_SIZE / 2, WIDTH - ENEMY_SIZE / 2)
                    b = random.randint(CEILING + ENEMY_SIZE / 2, FLOOR - ENEMY_SIZE / 2)
                    self.target_pos = (a, b)
                    self.has_set_target = True
                    self.disappear = True
                if self.has_set_target:
                    if self.disappear:
                        self.scale -= 0.05
                        if self.scale <= 0:
                            self.orig_pos = self.target_pos
                            self.rect.center = self.target_pos
                            self.disappear = False
                    else:
                        self.scale += 0.05
                        if self.scale >= 1.0:
                            self.scale = 1.0
                            self.has_set_target = False
                            self.counter = 0
                            self.new_move = 0
        return False
