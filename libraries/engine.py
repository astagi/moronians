from __future__ import absolute_import

from ast import literal_eval
import logging
import os
from random import randint, choice
import sys

import pygame

from .events import (EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP, EVENT_STORY_SCRIPT_CAPTION,
    EVENT_STORY_SCRIPT_TYPE, EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH, EVENT_STORY_SCRIPT_POST_LAUGH_DELAY)
from .exceptions import LevelComplete
from .literals import (COLOR_ALMOST_BLACK, COLOR_BLACK, COLOR_WHITE,
    DEFAULT_SCREENSIZE, GAME_TITLE, PAUSE_TEXT, PAUSE_TEXT_VERTICAL_OFFSET,
    START_MESSAGE_TEXT, STORY_TEXT)
from .maps import Map1, Map2, Map3, Map4
from .sprites import EnemySprite, PlayerSprite, SpaceshipSprite
from .vec2d import vec2d

logger = logging.getLogger(__name__)


class Level(object):
    def __init__(self, game):
        self.game = game

    def setup(self):
        pass

    def start(self):
        pass

    def update(self):
        pass

    def process_event(self, event):
        pass


class TitleScreen(Level):
    def setup(self):
        image = pygame.image.load('assets/backgrounds/game_title.png').convert()
        self.title_image = background = pygame.transform.scale(image, (self.game.screen.get_size()[0], self.game.screen.get_size()[1]))
        #self.title_image = background = aspect_scale(image, (self.game.screen.get_size()[0], self.game.screen.get_size()[1]))
        self.show_start_message = True
        self.font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 24)

        self.title_delay = 1000 / 5
        self.title_last_update = 0

    def start(self):
        pygame.mixer.music.load('assets/music/OveMelaaTranceBitBit.ogg')
        pygame.mixer.music.play(-1)

    def update(self):
        # Redraw the background
        self.game.screen.blit(self.title_image, (0, 0))

        t = pygame.time.get_ticks()
        if t - self.title_last_update > self.title_delay:
            self.show_start_message = not self.show_start_message
            self.title_last_update = t

        if self.show_start_message:
            text_size = self.font.size(START_MESSAGE_TEXT)
            label = self.font.render(START_MESSAGE_TEXT, 1, COLOR_WHITE)
            self.game.screen.blit(label, (self.game.screen.get_size()[0] / 2 - text_size[0] / 2, self.game.screen.get_size()[1] - 60))

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                raise LevelComplete


class MathLevel(Level):
    def setup(self, player, enemies, speed, map, enemy_images, formula_function, enemy_fps=8, value=0):
        self.result = []
        self.map = map
        self.player_sprite = player

        #self.result_box_position = (self.game.screen.get_width() / 2 - RESULT_BOX_SIZE[0] / 2, self.game.screen.get_height() / 2 - RESULT_BOX_VERTICAL_OFFSET)
        enemy_images = EnemySprite.load_sliced_sprites(*enemy_images)

        self.enemies = []
        screen_size = self.game.screen.get_size()
        for i in range(enemies):
            origin_point = (randint(0, screen_size[0]), randint(0, screen_size[1]))
            self.enemies.append(EnemySprite(self.game, self.game.enemy_font, formula_function(), origin_point, speed, enemy_images, enemy_fps, value))

    def start(self):
        pygame.mixer.music.load('assets/music/Zander Noriega - Darker Waves_0_looping.wav')
        pygame.mixer.music.play(-1)

    def process_event(self, event):
        if event.type == pygame.KEYDOWN and not self.game.paused and not self.player_sprite.has_won:
            if event.key == pygame.K_RETURN:
                try:
                    EnemySprite.player_shot(self.player_sprite, literal_eval(''.join(self.result)), self.enemies)
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

        # Draw player
        self.player_sprite.update(self.game.time_passed)
        self.player_sprite.blit()

        # Update and redraw all creeps
        for enemy in self.enemies:
            #print pygame.sprite.collide_rect(enemy, self.player_sprite)
            enemy.update(self.game.time_passed)
            enemy.blitme()

        # Redraw the result box
        self.player_sprite.result(''.join(self.result))

        if EnemySprite.is_all_defeated(self.enemies):
            self.player_sprite.win()


class StoryLevel(Level):
    def setup(self):
        self.bio_ship_image = pygame.image.load('assets/enemies/bio_ship.png').convert()
        self.bio_ship = SpaceshipSprite(self.game, image=self.bio_ship_image, speed=0.04)
        screen_size = self.game.screen.get_size()
        image = pygame.image.load('assets/backgrounds/earth.png').convert()
        self.title_image = background = pygame.transform.scale(image, (self.game.screen.get_size()[0], self.game.screen.get_size()[1]))
        self.font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 15)
        self.caption_letter = 0
        self.laugh_sound = pygame.mixer.Sound('assets/sounds/evil-laughter-witch.ogg')

    def start(self):
        pygame.mixer.music.load('assets/music/LongDarkLoop.ogg')
        pygame.mixer.music.play(-1)
        pygame.time.set_timer(EVENT_STORY_SCRIPT_CAPTION, 2000)

    def update(self):
        self.game.screen.blit(self.title_image, (0, 0))

        text_size = self.font.size(STORY_TEXT[0: self.caption_letter])
        label = self.font.render(STORY_TEXT[0: self.caption_letter], 1, COLOR_WHITE)
        self.game.screen.blit(label, (self.game.screen.get_size()[0] / 2 - text_size[0] / 2, self.game.screen.get_size()[1] - 60))

        self.bio_ship.update(self.game.time_passed)
        self.bio_ship.blit()

    def type_caption_letter(self):
        self.caption_letter += 1
        if self.caption_letter > len(STORY_TEXT):
            pygame.time.set_timer(EVENT_STORY_SCRIPT_TYPE, 0)
            pygame.time.set_timer(EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP, 2000)


    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            raise LevelComplete
        elif event.type == EVENT_STORY_SCRIPT_CAPTION:
            pygame.time.set_timer(EVENT_STORY_SCRIPT_CAPTION, 0)
            pygame.time.set_timer(EVENT_STORY_SCRIPT_TYPE, 150)
        elif event.type == EVENT_STORY_SCRIPT_TYPE:
            self.type_caption_letter()
        elif event.type == EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP:
            pygame.time.set_timer(EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP, 0)
            self.bio_ship.activate()

        elif event.type == EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH:
            self.laugh_sound.play()
            pygame.time.set_timer(EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH, 0)
            pygame.time.set_timer(EVENT_STORY_SCRIPT_POST_LAUGH_DELAY, 4000)
        elif event.type == EVENT_STORY_SCRIPT_POST_LAUGH_DELAY:
            pygame.time.set_timer(EVENT_STORY_SCRIPT_POST_LAUGH_DELAY, 0)
            raise LevelComplete


class Game(object):
    def __init__(self):
        pygame.init()
        self.pause_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 15)
        self.enemy_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 12)

        self.screen = pygame.display.set_mode(DEFAULT_SCREENSIZE)#, 0, 32)
        self.clock = pygame.time.Clock()
        self.paused = False
        self.running = False
        self.pause_sound = pygame.mixer.Sound('assets/sounds/pause.wav')
        self.can_be_paused = False
        self.player_sprite = PlayerSprite(self)

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
                    elif (event.key == 112 or event.key == 80) and self.can_be_paused:  # lower & upper case p key
                        self.paused = not self.paused
                        if self.paused:
                            pygame.mixer.music.pause()
                            self.pause_sound.play()
                        else:
                            pygame.mixer.music.unpause()
                            self.pause_sound.play()
                    else:
                        self.current_mode.process_event(event)
                else:
                    self.current_mode.process_event(event)
            self.current_mode.update()

            if self.paused:
                self.display_pause_label(self.pause_font)

            pygame.display.flip()

    def run(self):
        pygame.display.set_caption(GAME_TITLE)

        title_screen = TitleScreen(self)
        title_screen.setup()

        story_level = StoryLevel(self)
        story_level.setup()

        math_level = MathLevel(self)
        math_level.setup(self.player_sprite, enemies=8, speed=0.0025, enemy_images=(32, 32, 'enemies/eye_pod_strip.png'), formula_function=lambda :'%d + %d' % (randint(0, 9), randint(0, 9)), map=Map1(), enemy_fps=8, value=100)

        substraction_level = MathLevel(self)
        substraction_level.setup(self.player_sprite, enemies=6, speed=0.005, enemy_images=(32, 32, 'enemies/redslime_strip.png'), formula_function=lambda :'%d - %d' % (randint(0, 9), randint(0, 9)), map=Map2(), enemy_fps=10, value=150)

        multiplication_level = MathLevel(self)
        multiplication_level.setup(self.player_sprite, enemies=4, speed=0.01, enemy_images=(32, 32, 'enemies/aracnid_strip.png'), formula_function=lambda :'%d * %d' % (randint(0, 9), randint(0, 9)), map=Map3(), enemy_fps=12, value=200)

        division_level = MathLevel(self)
        division_level.setup(self.player_sprite, enemies=2, speed=0.02, enemy_images=(32, 32, 'enemies/flying_bot_strip.png'), formula_function=lambda :'%d / %d' % (randint(0, 9), randint(1, 9)), map=Map4(), enemy_fps=14, value=300)

        self.current_mode = title_screen
        title_screen.start()

        self.running = True

        while self.running:
            try:
                self.main_loop()
            except LevelComplete:
                if self.current_mode == title_screen:
                    self.current_mode = story_level
                    story_level.start()

                elif self.current_mode == story_level:
                    self.can_be_paused = True

                    self.current_mode = math_level
                    math_level.start()
                elif self.current_mode == math_level:
                    self.current_mode = substraction_level
                    substraction_level.start()
                elif self.current_mode == substraction_level:
                    self.current_mode = multiplication_level
                    multiplication_level.start()
                elif self.current_mode == multiplication_level:
                    self.current_mode = division_level
                    division_level.start()
            else:
                self.running = False

    def exit_game(self):
        sys.exit()
