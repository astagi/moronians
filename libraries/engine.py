from __future__ import absolute_import

import logging
import os
from random import randint, choice
import sys

import pygame

from .exceptions import SwallowEvent
from .events import (EVENT_GAME_OVER, EVENT_JUMP_TO_TITLE,
    EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP, EVENT_STORY_SCRIPT_CAPTION,
    EVENT_STORY_SCRIPT_TYPE, EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH,
    EVENT_STORY_SCRIPT_POST_LAUGH_DELAY, EVENT_CHANGE_LEVEL)
from .levels import (TitleScreen, StoryLevel, AdditionLevel, SubstractionLevel,
    MultiplicationLevel, DivisionLevel)
from .literals import (COLOR_ALMOST_BLACK, COLOR_BLACK, COLOR_WHITE,
    DEFAULT_SCREENSIZE, GAME_OVER_TEXT, GAME_TITLE, PAUSE_TEXT, PAUSE_TEXT_VERTICAL_OFFSET,
    START_MESSAGE_TEXT, STORY_TEXT, GAME_LEVEL_TITLE, GAME_LEVEL_STORY, GAME_LEVEL_ADDITION_LEVEL,
    GAME_LEVEL_SUBSTRACT_LEVEL, GAME_LEVEL_MULTIPLICATION_LEVEL, GAME_LEVEL_DIVISION_LEVEL)
from .sprites import PlayerSprite
from .utils import hollow_text, outlined_text, post_event, check_event
from .vec2d import vec2d

logger = logging.getLogger(__name__)



class Game(object):
    def __init__(self):
        self.paused = False
        self.running = False
        self.can_be_paused = False

    def on_init(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        #self.screen = pygame.display.set_mode(DEFAULT_SCREENSIZE)#, 0, 32)
        self.screen = pygame.display.set_mode(DEFAULT_SCREENSIZE, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.running = True
        self.pause_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 15)
        self.enemy_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 12)
        self.pause_sound = pygame.mixer.Sound('assets/sounds/pause.wav')
        self.player_sprite = PlayerSprite(self)
        pygame.display.set_caption(GAME_TITLE)
        self._current_level = None

        self.modes = {
            GAME_LEVEL_TITLE: TitleScreen(self),
            GAME_LEVEL_STORY: StoryLevel(self),
            GAME_LEVEL_ADDITION_LEVEL: AdditionLevel(game=self, player=self.player_sprite),
            GAME_LEVEL_SUBSTRACT_LEVEL: SubstractionLevel(game=self, player=self.player_sprite),
            GAME_LEVEL_MULTIPLICATION_LEVEL: MultiplicationLevel(game=self, player=self.player_sprite),
            GAME_LEVEL_DIVISION_LEVEL: DivisionLevel(game=self, player=self.player_sprite),
        }
        post_event(event=EVENT_CHANGE_LEVEL, mode=GAME_LEVEL_TITLE)

    def get_current_level(self):
        return self.modes[self._current_level]

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.exit_game()
        elif event.type == pygame.KEYDOWN:
            # Check for control keys first
            if event.key == 113 or event.key == 81:  # lower & upper case q key
                self.exit_game()
            elif (event.key == 112 or event.key == 80) and self.can_be_paused:  # lower & upper case p key
                # Get next event, thus emulate swallowing this one
                self.paused = not self.paused
                if self.paused:
                    pygame.mixer.music.pause()
                    self.pause_sound.play()
                else:
                    pygame.mixer.music.unpause()
                    self.pause_sound.play()
                raise SwallowEvent

        result = check_event(event)
        if result:
            #print 'MORONIAN EVENT', result
            if result['event'] == EVENT_CHANGE_LEVEL:
                self._current_level = result['mode']
                self.modes[self._current_level].on_start()

    def run(self):
        self.on_init()

        self.running = True
        while self.running:
            self.time_passed = self.clock.tick(60)

            for event in pygame.event.get():
                try:
                    self.on_event(event)
                except SwallowEvent:
                    pass
                else:
                    if not self._current_level is None:
                        self.modes[self._current_level].on_event(event)

            self.on_loop()
            self.on_blit()
            self.on_render()

        self.on_cleanup()

    def on_loop(self):
        self.modes[self._current_level].on_update()

    def on_blit(self):
        self.modes[self._current_level].blit()

        if self.paused:
            self.display_pause_label(self.pause_font)

    def on_render(self):
        pygame.display.flip()

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
        pygame.quit()
