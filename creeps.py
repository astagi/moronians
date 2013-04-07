#!/usr/bin/env python

import logging
import os
from random import randint, choice
import sys

import pygame

from vec2d import vec2d

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 640

SEX_MALE = 'm'
SEX_FEMALE = 'f'

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255,255,255)

RESULT_BOX_SIZE = (54, 24)
RESULT_BOX_VERTICAL_OFFSET = 60

logger = logging.getLogger(__name__)


class StageClear(Exception):
    pass


class Player(pygame.sprite.Sprite):
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
            SCREEN_WIDTH / 2 - self.size[0] / 2,
            SCREEN_HEIGHT / 2 - self.size[1] / 2
        )

    def blit(self):
        self.screen.blit(self.image, self.pos)


class CreepSprite(pygame.sprite.Sprite):
    _registry = {}

    @staticmethod
    def load_sliced_sprites(w, h, filename):
        images = []
        master_image = pygame.image.load(os.path.join('assets', filename)).convert_alpha()

        master_width, master_height = master_image.get_size()
        for i in xrange(int(master_width / w)):
            images.append(master_image.subsurface((i * w, 0 ,w ,h)))
        return images

    @classmethod
    def get_all(cls):
        return cls._registry.values()

    @classmethod
    def is_all_defeated(cls):
        return cls.get_all() == []

    @classmethod
    def player_shot(cls, value):
        for creep in cls.get_all():
            if creep.result == value:
                creep.defeat()
                if cls.is_all_defeated():
                    raise StageClear

    def __init__(self, game, font, text, screen, init_position, speed, images, fps = 10):
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

        self.pos = vec2d(init_position)

        # Calculate direction to the center of the screen
        self.direction = (vec2d(self.screen.get_size()[0] / 2,self.screen.get_size()[1] / 2) - vec2d(init_position)).normalized()

        self.__class__._registry[id(self)] = self

        # Call update to set our first image.
        self.update(pygame.time.get_ticks())

    def update(self, time_passed):
        if not self.game.paused:
            t = pygame.time.get_ticks()
            if t - self._last_update > self._delay:
                self._frame += 1
                if self._frame >= len(self._images):
                    self._frame = 0
                self.image = self._images[self._frame]
                self._last_update = t

            displacement = vec2d(
                self.direction.x * self.speed * time_passed,
                self.direction.y * self.speed * time_passed
            )

            self.pos += displacement

    def blitme(self):
        self.screen.blit(self.image, (self.pos.x, self.pos.y))
        text_size = self.font.size(self.text)
        label = self.font.render(self.text, 1, (255, 255, 0))
        self.screen.blit(label, (self.pos.x + self.size[0] / 2 - text_size[0] / 2, self.pos.y - 11))

    def defeat(self):
        self.__class__._registry.pop(id(self))


class Game(object):
    def __init__(self):
        pygame.init()
        self.result_font = pygame.font.Font(None, 18)
        self.pause_font = pygame.font.Font(None, 23)
        self.creep_font = pygame.font.SysFont('monospace', 15)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        self.clock = pygame.time.Clock()
        self.paused = False
        self.running = False

    def display_box(self, font, message, position, size):
        BORDER_SIZE = 2
        if len(message) != 0:
            pygame.draw.rect(self.screen, COLOR_BLACK, (position[0] + BORDER_SIZE, position[1] + BORDER_SIZE, size[0] - BORDER_SIZE, size[1] - BORDER_SIZE), 0)
            pygame.draw.rect(self.screen, COLOR_WHITE, (position[0], position[1], size[0], size[1]), 1)
            self.screen.blit(font.render(message, 1, COLOR_WHITE), (position[0] + BORDER_SIZE, position[1] + BORDER_SIZE))

    def display_pause_label(self, font):
        PAUSE_TEXT = 'PAUSE'
        PAUSE_TEXT_VERTICAL_OFFSET = 100

        text_size = font.size(PAUSE_TEXT)
        self.screen.blit(font.render(PAUSE_TEXT, 1, COLOR_WHITE), (self.screen.get_width() / 2 - text_size[0] / 2, self.screen.get_height() / 2 - text_size[1] / 2 - PAUSE_TEXT_VERTICAL_OFFSET))

    def math_level(self):
        CREEP_FILENAMES = [
            'assets/slimes/redslime.png',
            ]
        NUMBER_OF_CREEPS = 10
        CREEP_SPEED = 0.005
        background_img = pygame.image.load('assets/backgrounds/auto_fireball.jpg')
        background = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        background_rectangle = background.get_rect()
        self.screen.blit(background, background_rectangle)
        pygame.display.flip()
        red_slime_images = CreepSprite.load_sliced_sprites(32, 32, 'slimes/redslime_strip.png')
        player_sprite = Player(self.screen)

        result_box_position = (self.screen.get_width() / 2 - RESULT_BOX_SIZE[0] / 2, self.screen.get_height() / 2 - RESULT_BOX_VERTICAL_OFFSET)

        # Create NUMBER_OF_CREEPS random creeps.
        for i in range(NUMBER_OF_CREEPS):
            formula = '%d + %d' % (randint(0, 9), randint(0, 9))
            CreepSprite(self, self.creep_font, formula, self.screen, (randint(0, SCREEN_WIDTH), randint(0, SCREEN_HEIGHT)), CREEP_SPEED, red_slime_images)

        # The main game loop
        self.running = True
        result = []
        while self.running:
            # Limit frame speed to 60 FPS
            time_passed = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    # Check for control keys first
                    if event.key == pygame.K_ESCAPE:
                        self.exit_game()
                    elif event.key == 112 or event.key == 80:  # lower & upper case p key
                        self.paused = not self.paused
                    else:
                        # If not control key, try game mecanics keys
                        if not self.paused:
                            if event.key == pygame.K_RETURN:
                                try:
                                    CreepSprite.player_shot(eval(''.join(result)))
                                except StageClear:
                                    print 'WIN'
                                    self.exit_game()
                                except:
                                    pass
                                result = []
                            elif event.key == pygame.K_BACKSPACE:
                                result = result[0:-1]
                            elif event.key <= 127:
                                result.append(chr(event.key))

                if event.type == pygame.QUIT:
                    self.exit_game()

            # Redraw the background
            self.screen.blit(background, background_rectangle)

            self.display_box(self.result_font, ''.join(result), position=result_box_position, size=RESULT_BOX_SIZE)

            if self.paused:
                self.display_pause_label(self.pause_font)

            # Draw player
            player_sprite.blit()

            # Update and redraw all creeps
            for creep in CreepSprite.get_all():
                print pygame.sprite.collide_rect(creep, player_sprite)
                creep.update(time_passed)
                creep.blitme()

            pygame.display.flip()

    def run_game(self):
        self.math_level()

    def exit_game(self):
        sys.exit()


Game().run_game()
