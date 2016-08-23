import pygame, os, math, random
from text import Text
from enemy import Enemy
from panel import Panel
from player import Player
from ball import Ball
from bullet import Bullet, EnemyBullet
from constant import *
from pygame.locals import *
os.environ['SDL_VIDEO_CENTERED'] = '1'

class Main():

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()
        pygame.display.set_caption('Killing Ball')
        self.window = pygame.display.set_mode((WIDTH * 2, HEIGHT * 2), SWSURFACE)
        self.screen = pygame.Surface((WIDTH, HEIGHT)).convert()
        self.game_surf = pygame.Surface((WIDTH, HEIGHT)).convert()
        self.fade_mask = pygame.Surface((WIDTH, HEIGHT)).convert()
        self.fade_mask.fill((255, 255, 255))
        self.fade_mask.set_alpha(0)
        self.clock = pygame.time.Clock()
        self.title_im = pygame.image.load('res/img/title.png').convert()
        self.hiscore_im = pygame.image.load('res/img/hiscore.png').convert()
        self.background = pygame.image.load('res/img/background.png').convert()
        self.menu_sheet = pygame.image.load('res/img/menu.png').convert()
        self.menu = [self.menu_sheet.subsurface(0, 0, 160, 80), self.menu_sheet.subsurface(0, 80, 160, 120), self.menu_sheet.subsurface(0, 200, 160, 40)]
        self.sheet = pygame.image.load('res/img/sheet.png').convert()
        self.sheet.set_colorkey((0, 0, 0))
        im1 = self.sheet.subsurface((0, 0, 32, 32))
        im2 = self.sheet.subsurface((32, 0, 32, 32))
        self.player_im = [im1, im2]
        self.bullet_im = self.sheet.subsurface((64, 0, 8, 8))
        self.enemy_bullet_im = self.sheet.subsurface((64, 8, 8, 8))
        self.ball_im = self.sheet.subsurface((64, 16, 16, 16))
        self.ball_mask = pygame.mask.from_threshold(self.sheet.subsurface((80, 16, 16, 16)), (0, 0, 0, 255), (1, 1, 1, 255))
        self.ball_mask.invert()
        self.player_mask = pygame.mask.from_threshold(self.sheet.subsurface((96, 0, 32, 32)), (0, 0, 0, 255), (1, 1, 1, 255))
        self.player_mask.invert()
        self.bullet_mask = pygame.mask.from_threshold(self.sheet.subsurface((72, 8, 8, 8)), (0, 0, 0, 255), (1, 1, 1, 255))
        self.bullet_mask.invert()
        self.panel_im = []
        for x in xrange(4):
            im = self.sheet.subsurface((x * 32,
             32,
             32,
             32))
            self.panel_im.append(im)

        self.boss_dead = pygame.mixer.Sound('res/snd/BOSS_DEAD.ogg')
        self.player_dead = pygame.mixer.Sound('res/snd/PLAYER_DEAD.ogg')
        self.enemy_sound = pygame.mixer.Sound('res/snd/ENEMY_BULLET.ogg')
        self.player_sound = pygame.mixer.Sound('res/snd/PLAYER_BULLET.ogg')
        self.pause_text = [Text('Game is paused.'), Text('Continue'), Text('Quit')]
        self.menu_text = [Text('New Game'), Text('Hi-Score'), Text('Quit')]
        self.game_over_text = [Text("It's game over!"), Text('Retry'), Text('Quit')]
        self.win_text = Text('Congratulation!')
        self.get_text = Text('100')

    def load_level(self, num):
        self.mode = FSM_PLAY
        self.menu_choice = 1
        self.time = 120.0
        self.fade = 0
        self.bullets = []
        self.enemy_bullets = []
        self.loading_level = 1.0
        self.loading_wait = 1.0
        self.level += 1
        self.enemy = Enemy(0, 0, 0)
        self.load_text = Text('Level %02d' % (num + 1))
        if self.level % 5 == 0 and not self.is_boss_music:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('res/snd/BGM_01.ogg')
            pygame.mixer.music.play(-1)
            self.is_boss_music = True
        elif self.is_boss_music:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('res/snd/BGM_02.ogg')
            pygame.mixer.music.play(-1)
            self.is_boss_music = False
        f = open('res/lvl/%03d.lvl' % num).readlines()
        for y in xrange(len(f)):
            line = f[y].rstrip().lstrip()
            if line.startswith('#'):
                string = line.lstrip('#').lstrip().rstrip()
                if string == 'puzzle':
                    self.level_type = PUZZLE
                elif string == 'battle':
                    self.level_type = BATTLE
                else:
                    self.background = pygame.image.load('res/img/%s' % string).convert()
            elif self.level_type == PUZZLE:
                for x in xrange(len(line)):
                    if int(line[x]) > 0:
                        panel = Panel(x * 40 + 4, (y - 2) * 40 + 4 + CEILING, int(line[x]))
                        self.panels.append(panel)

            elif self.level_type == BATTLE:
                string = line.split('=')
                param = string[0].lstrip().rstrip()
                value = string[1].lstrip().rstrip()
                if param == 'hp':
                    self.enemy.hp = int(value) * HP_FACTOR
                    self.enemy.display_hp = int(value) * HP_FACTOR
                    self.enemy.max_hp = int(value) * HP_FACTOR
                elif param == 'img':
                    im = pygame.image.load('res/img/%s' % value).convert()
                    im.set_colorkey((0, 0, 0))
                    self.enemy.set_image(im)
                elif param == 'pos':
                    coord = value.split(',')
                    self.enemy.set_rect(int(coord[0]), int(coord[1]))
                elif param == 'name':
                    self.enemy.name = value
                elif param == 'move':
                    self.enemy.movement = int(value)

        self.enemy_text = Text('%s' % self.enemy.name)

    def title(self):
        self.menu_choice = 0
        timer = 0
        pygame.mixer.music.stop()
        pygame.mixer.music.load('res/snd/BGM_00.ogg')
        pygame.mixer.music.play(-1)
        while True:
            tick = self.clock.tick(FPS) / 1000.0
            self.screen.blit(self.title_im, (0, 0))
            timer = min(0.5, timer + tick)
            for x in xrange(MENU_LENGTH + 1):
                self.menu_text[x].update(self.menu_text[x].text.lstrip('>').lstrip())
                if x == self.menu_choice:
                    self.menu_text[x].update('>' + self.menu_text[x].text)
                else:
                    self.menu_text[x].update(' ' + self.menu_text[x].text)

            if timer == 0.5:
                menu_rect = self.menu[0].get_rect(center=(WIDTH / 2, 196))
                self.screen.blit(self.menu[0], menu_rect)
                for i in xrange(MENU_LENGTH + 1):
                    self.menu_text[i].draw(self.screen, (menu_rect.left + 12, menu_rect.top + 12 + i * 20))

            screen = pygame.transform.scale(self.screen, (WIDTH * 2, HEIGHT * 2))
            self.window.blit(screen, (0, 0))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit
                    elif e.key == pygame.K_UP:
                        self.menu_choice = max(0, self.menu_choice - 1)
                    elif e.key == pygame.K_DOWN:
                        self.menu_choice = min(MENU_LENGTH, self.menu_choice + 1)
                    elif e.key == pygame.K_z:
                        if self.menu_choice == 0:
                            self.new_game()
                        elif self.menu_choice == 1:
                            self.high_scores()
                        elif self.menu_choice == 2:
                            pygame.quit()
                            raise SystemExit

    def new_game(self):
        while True:
            pygame.mixer.music.load('res/snd/BGM_02.ogg')
            pygame.mixer.music.play(-1)
            self.init_objects()
            complete = self.main()
            self.high_scores(self.player.score)
            if complete:
                self.menu_choice = 0
                pygame.mixer.music.stop()
                pygame.mixer.music.load('res/snd/BGM_00.ogg')
                pygame.mixer.music.play(-1)
                return True

    def load_high_scores(self, new_score):
        scores = []
        hiscore_text = []
        if not os.path.exists('res/dat'):
            os.makedirs('res/dat')
        if new_score:
            try:
                f = open('res/dat/score.dat', 'r+')
                for line in f.readlines():
                    scores.append(int(line))

                scores.append(new_score)
                scores = sorted(scores)[::-1]
                f.seek(0)
                for x in xrange(SCORE_LENGTH):
                    f.write('%08d\n' % scores[x])

                f.truncate()
                f.close()
            except IOError:
                f = open('res/dat/score.dat', 'w')
                f.write('%08d\n' % new_score)
                scores.append(new_score)
                for x in xrange(1, SCORE_LENGTH):
                    f.write('00000000\n')
                    scores.append(0)

                f.close()

        else:
            try:
                f = open('res/dat/score.dat', 'r').readlines()
                for line in f:
                    scores.append(int(line))

            except IOError:
                f = open('res/dat/score.dat', 'w')
                for x in xrange(SCORE_LENGTH):
                    f.write('00000000\n')
                    scores.append(0)

                f.close()

            scores = sorted(scores)[::-1]
        for score in scores:
            string = '%08d' % score
            hiscore_text.append(Text(string.rstrip().lstrip()))

        return hiscore_text

    def high_scores(self, new_score = None):
        self.hiscore_text = self.load_high_scores(new_score)
        self.menu_choice = 0
        timer = 0
        while True:
            tick = self.clock.tick(FPS) / 1000.0
            self.screen.blit(self.hiscore_im, (0, 0))
            timer = min(0.5, timer + tick)
            has_highlighted = False
            for x in xrange(SCORE_LENGTH):
                if not self.hiscore_text[x].text.startswith('('):
                    color = [255, 255, 255]
                    if new_score == int(self.hiscore_text[x].text) and not has_highlighted:
                        color = [255, 255, 0]
                        has_highlighted = True
                    self.hiscore_text[x].update('(%02d)  ' % (x + 1) + self.hiscore_text[x].text, color)

            if timer == 0.5:
                menu_rect = self.menu[1].get_rect(center=(WIDTH / 2, HEIGHT / 2))
                self.screen.blit(self.menu[1], menu_rect)
                for i in xrange(SCORE_LENGTH):
                    self.hiscore_text[i].draw(self.screen, (menu_rect.left + 12, menu_rect.top + 12 + i * 20))

            screen = pygame.transform.scale(self.screen, (WIDTH * 2, HEIGHT * 2))
            self.window.blit(screen, (0, 0))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif e.type == pygame.KEYDOWN:
                    return

    def init_objects(self):
        self.player = Player(WIDTH / 2, self.player_mask)
        self.ball = Ball(WIDTH / 2, HEIGHT / 2, self.ball_mask)
        self.bullets = []
        self.enemy_bullets = []
        self.is_boss_music = False
        self.level_type = PUZZLE
        self.panels = []
        self.level = 0
        self.load_level(0)
        self.timer_text = Text('Time  : 00\'00"')
        self.score_text = Text('Score : 00000000')
        self.lives_text = Text('Lives : 000/050')
        self.screen_offset = (0, 0)
        self.cooldown = 0

    def render(self):
        self.fade_mask.set_alpha(self.fade)
        self.game_surf.blit(self.background, (0, 0))
        self.game_surf.blit(self.fade_mask, (0, 0))
        if self.level_type == PUZZLE:
            for panel in self.panels:
                index = max(0, panel.num - 1)
                panel_im = pygame.transform.scale(self.panel_im[index], (panel.rect.width, PANEL_SIZE))
                self.game_surf.blit(panel_im, panel.rect)
                if panel.hitstun > 0:
                    self.get_text.draw(self.game_surf, (panel.rect.centerx - self.get_text.width / 2, panel.rect.top - panel.move_up))

        elif self.level_type == BATTLE:
            if self.enemy:
                im = self.enemy.image[int(self.enemy.index) % 2]
                im = pygame.transform.scale(im, (int(ENEMY_SIZE * self.enemy.scale), int(ENEMY_SIZE * self.enemy.scale)))
                self.game_surf.blit(im, im.get_rect(center=self.enemy.rect.center))
                if self.enemy.fade > 0:
                    pygame.draw.rect(self.game_surf, (255, 255, 255), (0,
                     self.enemy.rect.centery - self.enemy.fade / 4,
                     WIDTH,
                     self.enemy.fade / 2))
        player_im = self.player_im[int(self.player.anim) % 2]
        if self.player.facing == -1:
            player_im = pygame.transform.flip(player_im, True, False)
        if self.player.scale > 0.05:
            width = int(PLAYER_SIZE * self.player.scale)
            height = int(PLAYER_SIZE / self.player.scale)
            player_im = pygame.transform.scale(player_im, (width, height))
            dw = (self.player.rect.width - width) / 2
            self.player.rect.width = width
            self.player.rect.height = height
            self.player.rect.midbottom = (self.player.rect.centerx + dw, FLOOR)
            self.game_surf.blit(player_im, self.player.rect)
        self.game_surf.blit(self.ball_im, self.ball.rect)
        for bullet in self.bullets:
            self.game_surf.blit(self.bullet_im, bullet.rect)

        for bullet in self.enemy_bullets:
            self.game_surf.blit(self.enemy_bullet_im, bullet.rect)

        self.screen.blit(self.game_surf, self.screen_offset)
        pygame.draw.rect(self.screen, (0, 0, 0), (0,
         FLOOR,
         WIDTH,
         HEIGHT - FLOOR))
        pygame.draw.rect(self.screen, (0, 0, 0), (0,
         0,
         WIDTH,
         CEILING))
        self.timer_text.draw(self.screen, (4, 4))
        self.score_text.draw(self.screen, (4, 20))
        self.lives_text.draw(self.screen, (160, 4))
        if self.level_type == BATTLE and self.enemy:
            if self.enemy.hp < self.enemy.display_hp:
                self.enemy.display_hp -= 5
            self.enemy_text.draw(self.screen, (160, 20))
            pygame.draw.rect(self.screen, (255, 255, 255), (228,
             24,
             int(self.enemy.display_hp / float(self.enemy.max_hp) * 88),
             8))
        if self.mode == FSM_PAUSE:
            menu_rect = self.menu[0].get_rect(center=(WIDTH / 2, HEIGHT / 2))
            self.screen.blit(self.menu[0], menu_rect)
            for i in xrange(MENU_LENGTH + 1):
                self.pause_text[i].draw(self.screen, (menu_rect.left + 12, menu_rect.top + 12 + i * 20))

        elif self.mode == FSM_GAMEOVER:
            menu_rect = self.menu[0].get_rect(center=(WIDTH / 2, HEIGHT / 2))
            self.screen.blit(self.menu[0], menu_rect)
            for i in xrange(MENU_LENGTH + 1):
                self.game_over_text[i].draw(self.screen, (menu_rect.left + 12, menu_rect.top + 12 + i * 20))

        elif self.mode == FSM_VICTORY:
            if self.loading_level > 0:
                width = WIDTH + self.menu[2].get_width()
                menu_rect = self.menu[2].get_rect(midleft=(WIDTH - int(self.loading_level * width) + width / self.menu[2].get_width(), HEIGHT / 2))
                self.screen.blit(self.menu[2], menu_rect)
                self.win_text.draw(self.screen, (menu_rect.left + 12, menu_rect.top + 12))
        elif self.mode == FSM_PLAY:
            if self.loading_level > 0:
                width = WIDTH + self.menu[2].get_width()
                menu_rect = self.menu[2].get_rect(midleft=(WIDTH - int(self.loading_level * width) + width / self.menu[2].get_width(), HEIGHT / 2))
                self.screen.blit(self.menu[2], menu_rect)
                self.load_text.draw(self.screen, (menu_rect.left + self.load_text.width / 2 + 12, menu_rect.top + 12))
        screen = pygame.transform.scale(self.screen, (WIDTH * 2, HEIGHT * 2))
        self.window.blit(screen, (0, 0))

    def main(self):
        while True:
            tick = self.clock.tick(FPS) / 1000.0
            if self.mode == FSM_PLAY:
                if self.loading_level > 0:
                    if abs(self.loading_level - 0.5) < 0.025 and self.loading_wait > 0:
                        self.loading_wait -= tick
                    else:
                        self.loading_level -= tick
                elif len(self.panels) > 0 or self.enemy and self.enemy.hp > 0:
                    self.time -= tick
                    if self.time <= 0:
                        self.mode = FSM_GAMEOVER
            elif self.mode == FSM_VICTORY:
                if self.loading_level > 0:
                    if abs(self.loading_level - 0.5) < 0.025 and self.loading_wait > 0:
                        self.loading_wait -= tick
                    else:
                        self.loading_level -= tick
                else:
                    return True
            self.timer_text.update('Time  : %02d\'%02d"' % (self.time / 60 % 60, self.time % 60))
            self.score_text.update('Score : %08d' % self.player.score)
            self.lives_text.update('Lives : %03d/050' % self.player.lives)
            self.render()
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE and self.loading_level <= 0:
                        if self.mode == FSM_PLAY:
                            self.mode = FSM_PAUSE
                        elif self.mode == FSM_PAUSE:
                            FSM_PLAY
                    elif e.key == pygame.K_UP and self.mode in [FSM_PAUSE, FSM_GAMEOVER]:
                        self.menu_choice = max(1, self.menu_choice - 1)
                    elif e.key == pygame.K_DOWN and self.mode in [FSM_PAUSE, FSM_GAMEOVER]:
                        self.menu_choice = min(MENU_LENGTH, self.menu_choice + 1)
                    elif e.key == pygame.K_z:
                        if self.mode == FSM_PLAY and self.loading_level <= 0:
                            if self.player.rect.colliderect(self.ball.rect):
                                if self.player.rect.centerx < self.ball.rect.centerx:
                                    self.ball.velocity[0] += 2
                                elif self.player.rect.centerx > self.ball.rect.centerx:
                                    self.ball.velocity[0] -= 2
                                self.ball.velocity[1] += 5
                        elif self.mode == FSM_PAUSE:
                            if self.menu_choice == MENU_LENGTH:
                                return True
                            if self.menu_choice == 1:
                                self.mode = FSM_PLAY
                        elif self.mode == FSM_GAMEOVER:
                            if self.menu_choice == MENU_LENGTH:
                                return True
                            if self.menu_choice == 1:
                                return False

            if self.mode == FSM_GAMEOVER:
                for x in xrange(1, MENU_LENGTH + 1):
                    self.game_over_text[x].update(self.game_over_text[x].text.lstrip('>').lstrip())
                    if x == self.menu_choice:
                        self.game_over_text[x].update('>' + self.game_over_text[x].text)
                    else:
                        self.game_over_text[x].update(' ' + self.game_over_text[x].text)

            elif self.mode == FSM_PAUSE:
                for x in xrange(1, MENU_LENGTH + 1):
                    self.pause_text[x].update(self.pause_text[x].text.lstrip('>').lstrip())
                    if x == self.menu_choice:
                        self.pause_text[x].update('>' + self.pause_text[x].text)
                    else:
                        self.pause_text[x].update(' ' + self.pause_text[x].text)

            elif self.mode == FSM_PLAY:
                if self.loading_level <= 0:
                    if not self.player.get_hit:
                        if self.player.lives == 0:
                            self.mode = FSM_GAMEOVER
                        else:
                            keys = pygame.key.get_pressed()
                            if keys[pygame.K_LEFT]:
                                dx = SPEED * -1
                            elif keys[pygame.K_RIGHT]:
                                dx = SPEED
                            else:
                                dx = 0
                            self.cooldown -= 1
                            if self.cooldown <= 0:
                                self.cooldown = 0
                            if keys[pygame.K_z] and (len(self.panels) != 0 or (self.enemy and self.enemy.hp != 0)):
                                if self.cooldown == 0:
                                    self.cooldown = COOLDOWN
                                    bullet = Bullet(self.player.rect.midtop)
                                    self.bullets.append(bullet)
                                    self.player_sound.play()
                            self.screen_offset = (0, 0)
                            if self.player.scale < 1.0:
                                self.player.scale += 0.05
                                if self.player.scale > 1.0:
                                    self.player.scale = 1.0
                            else:
                                self.player.update(dx)
                            for bullet in self.bullets:
                                if bullet.update():
                                    self.bullets.remove(bullet)

                            for bullet in self.enemy_bullets:
                                if bullet.update(self.player):
                                    self.enemy_bullets.remove(bullet)

                            self.ball.update(self.player, self.bullets)
                            if self.level_type == PUZZLE:
                                for panel in self.panels:
                                    if panel.update(self.ball, self.player):
                                        self.panels.remove(panel)
                                    if panel.rect.width < PANEL_SIZE and panel.rect.width % 5 == 0:
                                        enemy_bullet = EnemyBullet(panel.rect.center, self.player.rect.center, self.bullet_mask)
                                        self.enemy_bullets.append(enemy_bullet)
                                        self.enemy_sound.play()

                                if len(self.panels) == 0 and len(self.bullets) == 0 and len(self.enemy_bullets) == 0:
                                    if self.time > 0:
                                        self.time = max(0, int(self.time) - 1)
                                        self.player.score += 50
                                    elif self.level + 1 >= NUM_LEVELS:
                                        self.mode = FSM_VICTORY
                                        self.loading_level = 1.0
                                        self.loading_wait = 1.0
                                    else:
                                        self.load_level(min(NUM_LEVELS, self.level))
                            elif self.level_type == BATTLE:
                                if self.enemy:
                                    if self.enemy.update(self.ball, self.player):
                                        if self.enemy.fade == 0:
                                            self.boss_dead.play()
                                        self.enemy.fade += 1
                                        self.fade = self.enemy.fade
                                        if self.enemy.fade >= 250:
                                            self.enemy = None
                                    elif self.enemy.index > 0 and self.enemy.counter % 5 == 0:
                                        enemy_bullet = EnemyBullet(self.enemy.rect.center, self.player.rect.center, self.bullet_mask)
                                        self.enemy_bullets.append(enemy_bullet)
                                        self.enemy_sound.play()
                                else:
                                    self.fade = max(0, self.fade - 5)
                                    if self.fade == 0:
                                        if self.time > 0:
                                            self.time = max(0, int(self.time) - 1)
                                            self.player.score += 50
                                        elif self.level + 1 >= NUM_LEVELS:
                                            self.mode = FSM_VICTORY
                                            self.loading_level = 1.0
                                            self.loading_wait = 1.0
                                        else:
                                            self.load_level(min(NUM_LEVELS, self.level))
                    else:
                        if self.player.get_hit == HIT:
                            self.player_dead.play()
                        self.player.get_hit = max(1, self.player.get_hit - 1)
                        if self.player.get_hit == 1:
                            self.player.scale -= 0.05
                            if self.player.scale <= -1.0:
                                self.player.get_hit = 0
                                self.player.rect.centerx = WIDTH / 2
                                self.player.hitstun = HITSTUN * 4
                                self.player.anim = 1
                        self.screen_offset = (random.randint(-2, 2), random.randint(-2, 2))

        return


if __name__ == '__main__':
    main = Main()
    main.title()
