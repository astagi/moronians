#!/usr/bin/env python

from ast import literal_eval
import logging
import os
from random import randint, choice
import sys

import pygame

from vec2d import vec2d

from maps import Map1, Map2

#SCREEN_WIDTH, SCREEN_HEIGHT = 640, 640
DEFAULT_SCREENSIZE = [512, 448] #16 X 14 grid with 32px X 32px cell

SEX_MALE = 'm'
SEX_FEMALE = 'f'

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255,255,255)

RESULT_BOX_SIZE = (54, 24)
RESULT_BOX_VERTICAL_OFFSET = 60

# Game strings
GAME_TITLE = 'Attack of the Moronians'
PAUSE_TEXT = 'PAUSE'

PAUSE_TEXT_VERTICAL_OFFSET = 100  # Vertical offset of the 'PAUSE' message


logger = logging.getLogger(__name__)


class LevelComplete(Exception):
    pass


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, screen, sex=SEX_MALE):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        if sex == SEX_MALE:
            self.image = pygame.image.load('assets/players/boy.png').convert_alpha()
        else:
            self.image = pygame.image.load('assets/players/girl.png').convert_alpha()

        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.pos = (
            self.screen.get_size()[0] / 2 - self.size[0] / 2,
            self.screen.get_size()[1] / 2 - self.size[1] / 2
        )

    def blit(self):
        self.screen.blit(self.image, self.pos)


class EnemySprite(pygame.sprite.Sprite):
    @staticmethod
    def load_sliced_sprites(w, h, filename):
        images = []
        master_image = pygame.image.load(os.path.join('assets', filename)).convert_alpha()

        master_width, master_height = master_image.get_size()
        for i in xrange(int(master_width / w)):
            images.append(master_image.subsurface((i * w, 0, w , h)))
        return images

    @staticmethod
    def is_all_defeated(enemies):
        return enemies == []

    @staticmethod
    def player_shot(value, enemies):
        for enemy in enemies:
            if enemy.result == value:
                enemy.defeat(enemies)

    def __init__(self, game, font, text, screen, init_position, speed, images, fps):
        pygame.sprite.Sprite.__init__(self)
        self._images = images
        self.screen = screen
        self.speed = speed
        self._start = pygame.time.get_ticks()
        self._delay = 1000 / fps
        self._last_update = 0
        self._frame = 0
        self.font = font
        self.text = text
        self.result = eval(text)
        self.rect = self._images[0].get_rect()
        self.size = self._images[0].get_size()
        self.game = game
        self.alive = True
        self.loop = True

        self.pos = vec2d(init_position)
        self.smoke_images = [
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0001.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0002.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0003.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0004.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0005.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0006.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0007.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0008.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0009.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0010.32x32.png')
        ]

        self.death_sound = pygame.mixer.Sound('assets/sounds/8bit_bomb_explosion.wav')

        # Calculate direction to the center of the screen
        self.direction = (vec2d(self.screen.get_size()[0] / 2,self.screen.get_size()[1] / 2) - vec2d(init_position)).normalized()

        # Call update to set our first image.
        self.update(pygame.time.get_ticks(), force=True)

    def update(self, time_passed, force=False):
        if not self.game.paused:
            t = pygame.time.get_ticks()
            if t - self._last_update > self._delay or force:
                self._frame += 1
                if self._frame >= len(self._images):
                    if self.loop:
                        self._frame = 0
                    else:
                        self._frame -= 1
                        self.enemies.remove(self)

                self.image = self._images[self._frame]
                self._last_update = t

            if self.alive:
                displacement = vec2d(
                    self.direction.x * self.speed * time_passed,
                    self.direction.y * self.speed * time_passed
                )

                self.pos += displacement

    def blitme(self):
        self.screen.blit(self.image, (self.pos.x, self.pos.y))
        if self.alive:
            # If enemy is alive show it's formula
            text_size = self.font.size(self.text)
            label = self.font.render(self.text, 1, (255, 255, 0))
            self.screen.blit(label, (self.pos.x + self.size[0] / 2 - text_size[0] / 2, self.pos.y - 11))

    def defeat(self, enemies):
        self.alive = False
        self.loop = False
        self.enemies = enemies
        self._images = self.smoke_images
        self.death_sound.play()


class Level(object):
    def __init__(self, game):
        self.game = game

    def setup(self):
        pass

    def update(self):
        pass

    def process_event(self, event):
        pass


class MathLevel(Level):
    def setup(self, enemies, speed, map, enemy_images, formula_function):
        self.result = []
        self.map = map
        self.player_sprite = PlayerSprite(self.game.screen)

        self.result_box_position = (self.game.screen.get_width() / 2 - RESULT_BOX_SIZE[0] / 2, self.game.screen.get_height() / 2 - RESULT_BOX_VERTICAL_OFFSET)
        enemy_images = EnemySprite.load_sliced_sprites(*enemy_images)

        self.enemies = []
        screen_size = self.game.screen.get_size()
        for i in range(enemies):
            origin_point = (randint(0, screen_size[0]), randint(0, screen_size[1]))
            self.enemies.append(EnemySprite(self.game, self.game.creep_font, formula_function(), self.game.screen, origin_point, speed, enemy_images, 8))

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and not self.game.paused:
            if event.key == pygame.K_RETURN:
                try:
                    EnemySprite.player_shot(literal_eval(''.join(self.result)), self.enemies)
                except (SyntaxError, ValueError):
                    pass
                self.result = []
            elif event.key == pygame.K_BACKSPACE:
                self.result = self.result[0:-1]
            elif event.key <= 127 and event.key >= 32:
                self.result.append(chr(event.key))

    def update(self):
        # Redraw the background
        self.game.display_tile_map(self.map)

        # Redraw the result box
        self.game.display_box(self.game.result_font, ''.join(self.result), position=self.result_box_position, size=RESULT_BOX_SIZE)

        # Draw player
        self.player_sprite.blit()

        # Update and redraw all creeps
        for enemy in self.enemies:
            #print pygame.sprite.collide_rect(creep, self.player_sprite)
            enemy.update(self.game.time_passed)
            enemy.blitme()

        if EnemySprite.is_all_defeated(self.enemies):
            raise LevelComplete


class Game(object):
    def __init__(self):
        pygame.init()
        self.result_font = pygame.font.Font(None, 18)
        self.pause_font = pygame.font.Font(None, 23)
        self.creep_font = pygame.font.SysFont('monospace', 15)
        self.screen = pygame.display.set_mode(DEFAULT_SCREENSIZE)#, 0, 32)
        self.clock = pygame.time.Clock()
        self.paused = False
        self.running = False
        self.game_music = pygame.mixer.music.load('assets/music/Zander Noriega - Darker Waves_0_looping.wav')
        self.pause_sound = pygame.mixer.Sound('assets/sounds/pause.wav')

    def display_box(self, font, message, position, size):
        BORDER_SIZE = 2
        if len(message) != 0:
            pygame.draw.rect(self.screen, COLOR_BLACK, (position[0] + BORDER_SIZE, position[1] + BORDER_SIZE, size[0] - BORDER_SIZE, size[1] - BORDER_SIZE), 0)
            pygame.draw.rect(self.screen, COLOR_WHITE, (position[0], position[1], size[0], size[1]), 1)
            self.screen.blit(font.render(message, 1, COLOR_WHITE), (position[0] + BORDER_SIZE, position[1] + BORDER_SIZE))

    def display_pause_label(self, font):
        text_size = font.size(PAUSE_TEXT)
        self.screen.blit(font.render(PAUSE_TEXT, 1, COLOR_WHITE), (self.screen.get_width() / 2 - text_size[0] / 2, self.screen.get_height() / 2 - text_size[1] / 2 - PAUSE_TEXT_VERTICAL_OFFSET))

    def display_tile_map(self, map):
        #loops through map to set background
        for y in range(len(map.grid)):
            for x in range(len(map.grid[y])):
                location = (x * 32, y * 32)
                self.screen.blit(map.tileset, location, map.grid[y][x])

    def main_loop(self):
        while self.running:
            self.time_passed = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    # Check for control keys first
                    if event.key == 113 or event.key == 81:  # lower & upper case q key
                        self.exit_game()
                    elif event.key == 112 or event.key == 80:  # lower & upper case p key
                        self.paused = not self.paused
                        if self.paused:
                            pygame.mixer.music.pause()
                            self.pause_sound.play()
                        else:
                            pygame.mixer.music.unpause()
                    else:
                        self.current_mode.process_event(event)

            self.current_mode.update()

            if self.paused:
                self.display_pause_label(self.pause_font)

            pygame.display.flip()

    def run(self):
        pygame.display.set_caption(GAME_TITLE)

        math_level = MathLevel(self)
        math_level.setup(enemies=2, speed=0.005, enemy_images=(32, 32, 'enemies/aracnid_strip.png'), formula_function=lambda :'%d + %d' % (randint(0, 9), randint(0, 9)), map=Map1())

        substraction_level = MathLevel(self)
        substraction_level.setup(enemies=2, speed=0.005, enemy_images=(32, 32, 'slimes/redslime_strip.png'), formula_function=lambda :'%d + %d' % (randint(0, 9), randint(0, 9)), map=Map2())

        self.current_mode = math_level

        self.running = True

        pygame.mixer.music.play(-1)

        while self.running:
            try:
                self.main_loop()
            except LevelComplete:
                if self.current_mode == math_level:
                    self.current_mode = substraction_level
            else:
                self.running = False

    def exit_game(self):
        sys.exit()


Game().run()
