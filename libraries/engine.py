from __future__ import absolute_import

import logging
import os
from random import randint, choice
import sys

import pygame

from .exceptions import NotAMoronianEvent
from .events import (EVENT_GAME_OVER, EVENT_JUMP_TO_TITLE, EVENT_STOP_GAME,
    EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP, EVENT_STORY_SCRIPT_CAPTION,
    EVENT_STORY_SCRIPT_TYPE, EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH,
    EVENT_STORY_SCRIPT_POST_LAUGH_DELAY)
from .levels import TitleScreen, StoryLevel, AdditionLevel
from .literals import (COLOR_ALMOST_BLACK, COLOR_BLACK, COLOR_WHITE,
    DEFAULT_SCREENSIZE, GAME_OVER_TEXT, GAME_TITLE, PAUSE_TEXT, PAUSE_TEXT_VERTICAL_OFFSET,
    START_MESSAGE_TEXT, STORY_TEXT, GAME_MODE_TITLE, GAME_MODE_STORY, GAME_MODE_ADDITION_LEVEL,
    GAME_MODE_SUBSTRACT_LEVEL, GAME_MODE_MULTIPLICATION_LEVEL, GAME_MODE_DIVISION_LEVEL)
from .sprites import PlayerSprite
from .utils import hollow_text, outlined_text, post_event, check_event
from .vec2d import vec2d

logger = logging.getLogger(__name__)

from .events import EVENT_CHANGE_MODE


class Game(object):
    def __init__(self):
        self.paused = False
        self.running = False
        self.can_be_paused = False

    def on_init(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(DEFAULT_SCREENSIZE)#, 0, 32)
        self.running = True
        self.pause_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 15)
        self.enemy_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 12)
        self.pause_sound = pygame.mixer.Sound('assets/sounds/pause.wav')
        self.player_sprite = PlayerSprite(self)
        pygame.display.set_caption(GAME_TITLE)
        self.current_mode = None

        self.modes = {
            GAME_MODE_TITLE: TitleScreen(self),
            GAME_MODE_STORY: StoryLevel(self),
            GAME_MODE_ADDITION_LEVEL: AdditionLevel(game=self, player=self.player_sprite),
            #GAME_MODE_SUBSTRACT_LEVEL = 3
            #GAME_MODE_MULTIPLICATION_LEVEL = 4
            #GAME_MODE_DIVISION_LEVEL = 5
        }
        post_event(event=EVENT_CHANGE_MODE, mode=GAME_MODE_TITLE)
        #self.current_mode = GAME_MODE_TITLE

        #self.title_screen =
        #self.title_screen.setup()

        #story_level =
        #story_level.setup()

        #math_level =
        ##math_level.setup(self.player_sprite, enemies=8, speed=0.0025, enemy_images=(32, 32, 'enemies/eye_pod_strip.png'), formula_function=lambda :'%d + %d' % (randint(0, 9), randint(0, 9)), map=Map1(), enemy_fps=8, value=100, attack_points=1)
        #math_level.setup(self.player_sprite, enemies=8, speed=0.05, enemy_images=(32, 32, 'enemies/eye_pod_strip.png'), formula_function=lambda :'%d + %d' % (randint(0, 9), randint(0, 9)), map=Map1(), enemy_fps=8, value=100, attack_points=50)

        #substraction_level = MathLevel(self)
        #substraction_level.setup(self.player_sprite, enemies=6, speed=0.005, enemy_images=(32, 32, 'enemies/redslime_strip.png'), formula_function=lambda :'%d - %d' % (randint(0, 9), randint(0, 9)), map=Map2(), enemy_fps=10, value=150, attack_points=2)

        #multiplication_level = MathLevel(self)
        #multiplication_level.setup(self.player_sprite, enemies=4, speed=0.01, enemy_images=(32, 32, 'enemies/aracnid_strip.png'), formula_function=lambda :'%d * %d' % (randint(0, 9), randint(0, 9)), map=Map3(), enemy_fps=12, value=200, attack_points=4)

        #division_level = MathLevel(self)
        #division_level.setup(self.player_sprite, enemies=2, speed=0.02, enemy_images=(32, 32, 'enemies/flying_bot_strip.png'), formula_function=lambda :'%d / %d' % (randint(0, 9), randint(1, 9)), map=Map4(), enemy_fps=14, value=300, attack_points=8)

        #self.current_mode = self.title_screen
        #self.title_screen.start()

    def on_event(self, event):
        try:
            result = check_event(event)
        except NotAMoronianEvent:
            if event.type == pygame.QUIT:
                self.exit_game()
            #elif event.type == EVENT_JUMP_TO_TITLE:
            #    pygame.time.set_timer(EVENT_JUMP_TO_TITLE, 0)
            #    self.player_sprite.reset()
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
            #    else:
            #        self.current_mode.process_event(event)
            #else:
            #    self.current_mode.process_event(event)
        else:
            print 'MORONIAN EVENT', result
            if result['event'] == EVENT_CHANGE_MODE:
                self.current_mode = result['mode']
                self.modes[self.current_mode].on_start()

    def run(self):
        self.on_init()

        self.running = True
        while self.running:
            self.time_passed = self.clock.tick(60)

            for event in pygame.event.get():
                self.on_event(event)
                if not self.current_mode is None:
                    self.modes[self.current_mode].on_event(event)

            self.on_loop()
            self.on_render()

        self.on_cleanup()

    def on_loop(self):
        self.modes[self.current_mode].on_update()

        if self.paused:
            self.display_pause_label(self.pause_font)

    def on_render(self):
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

        '''
        try:
            self.main_loop()
        except LevelComplete:
            if self.current_mode == self.title_screen:
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
        '''

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

    def exit_game(self):
        self.running = False
