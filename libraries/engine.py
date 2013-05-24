from __future__ import absolute_import

import logging
import os
from random import randint, choice
import sys

import pygame

from .exceptions import SwallowEvent
from .events import (EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP, EVENT_STORY_SCRIPT_CAPTION,
    EVENT_STORY_SCRIPT_TYPE, EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH,
    EVENT_STORY_SCRIPT_POST_LAUGH_DELAY, EVENT_CHANGE_LEVEL)
from .literals import (COLOR_ALMOST_BLACK, COLOR_BLACK, COLOR_WHITE,
    DEFAULT_SCREENSIZE, GAME_OVER_TEXT, GAME_TITLE, PAUSE_TEXT,
    PAUSE_TEXT_VERTICAL_OFFSET, START_MESSAGE_TEXT, GAME_LEVEL_TITLE,
    GAME_LEVEL_STORY, TEXT_EXIT_CONFIRMATION,
    EXIT_TEXT_VERTICAL_OFFSET)
from .sprites import SpritePlayer
from .stages import StoryStage
from .utils import hollow_text, outlined_text, post_event, check_event
from .vec2d import vec2d
from utils.importlib import import_module

logger = logging.getLogger(__name__)


class Game(object):
    def __init__(self, module_name, debug=False):
        self.running = False
        self.paused = False
        self.finish = False
        self.debug = debug
        #try:
        self.module_class = import_module('modules.%s.module' % module_name).Module
        #except ImportError:
        #    print 'Unable to import module %s' % module_name
        #    exit(1)

    def on_init(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(DEFAULT_SCREENSIZE, pygame.HWSURFACE | pygame.DOUBLEBUF)# | pygame.FULLSCREEN)
        self.surface = pygame.Surface(self._screen.get_size())
        self.running = True
        self.font_debug = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 12)
        self.pause_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 15)
        self.enemy_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 12)
        self.font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 12)
        self.pause_sound = pygame.mixer.Sound('assets/sounds/pause.wav')
        self.player = SpritePlayer(self)
        pygame.display.set_caption(GAME_TITLE)
        self._current_level = None
        self.shake_screen = False
        self.can_be_paused = False
        self.exit_confirm = False
        self.module = self.module_class(self)
        self.module.on_start()

    def get_current_level(self):
        return self.module.modes[self._current_level]

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.exit_game()
        elif event.type == pygame.KEYDOWN:
            # Check for control keys first
            if self.exit_confirm:
                if event.key in [pygame.K_ESCAPE, ord('n'), ord('N')]:
                    self.exit_confirm = False
                    self.can_be_pause = True
                    raise SwallowEvent
                elif event.key in [ord('y'), ord('Y')]:
                    self.exit_game()
            elif event.key == pygame.K_ESCAPE:
                if self._current_level == GAME_LEVEL_TITLE:
                    self.exit_game()
                elif self._current_level != GAME_LEVEL_STORY:
                    self.can_be_pause = False
                    self.exit_confirm = True
            elif event.key == pygame.K_PAUSE and self.can_be_paused:
                # Get next event, thus emulate swallowing this one
                self.paused = not self.paused
                self.running = not self.running
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
                self.module.modes[self._current_level].on_start()

    def run(self):
        self.on_init()

        while not self.finish:
            self.time_passed = self.clock.tick(60)

            for event in pygame.event.get():
                try:
                    self.on_event(event)
                except SwallowEvent:
                    pass
                else:
                    if not self._current_level is None:
                        self.module.modes[self._current_level].on_event(event)

            self.on_loop()
            self.on_blit()
            self.on_render()

    def on_loop(self):
        self.module.modes[self._current_level].on_update()

    def on_blit(self):
        self.module.modes[self._current_level].on_blit()

        if self.exit_confirm:
            self.exit_confirmation(self.pause_font)

        if self.paused:
            self.display_pause_label(self.pause_font)

        if self.debug:
            self.display_debug_info(self.font_debug)

        if self.shake_screen:
            self._screen.blit(self.surface, (randint(0, 10), randint(0, 10)))
        else:
            self._screen.blit(self.surface, (0, 0))

    def on_render(self):
        pygame.display.flip()

    def display_box(self, font, message, position, size):
        BORDER_SIZE = 2
        if len(message) != 0:
            pygame.draw.rect(self._screen, COLOR_BLACK, (position[0] + BORDER_SIZE, position[1] + BORDER_SIZE, size[0] - BORDER_SIZE, size[1] - BORDER_SIZE), 0)
            pygame.draw.rect(self._screen, COLOR_WHITE, (position[0], position[1], size[0], size[1]), 1)
            self.surface.blit(font.render(message, 1, COLOR_WHITE), (position[0] + BORDER_SIZE, position[1] + BORDER_SIZE))

    def display_pause_label(self, font):
        text_size = font.size(PAUSE_TEXT)
        self.surface.blit(font.render(PAUSE_TEXT, 1, COLOR_WHITE), (self._screen.get_width() / 2 - text_size[0] / 2, self._screen.get_height() / 2 - text_size[1] / 2 - PAUSE_TEXT_VERTICAL_OFFSET))

    def display_debug_info(self, font):
        debug_text = 'tick: %d' % pygame.time.get_ticks()
        #text_size = font.size(debug_text)
        self.surface.blit(font.render(debug_text, False, COLOR_WHITE), (0, 0))

    def exit_confirmation(self, font):
        text_size = font.size(TEXT_EXIT_CONFIRMATION)
        self.surface.blit(font.render(TEXT_EXIT_CONFIRMATION, 1, COLOR_WHITE), (self._screen.get_width() / 2 - text_size[0] / 2, self._screen.get_height() / 2 - text_size[1] / 2 - EXIT_TEXT_VERTICAL_OFFSET))

    def display_tile_map(self, map):
        #loops through map to set background
        for y in range(len(map.grid)):
            for x in range(len(map.grid[y])):
                location = (x * 32, y * 32)
                self.surface.blit(map.tileset, location, map.grid[y][x])

    def exit_game(self):
        self.finish = True
        pygame.display.set_mode(DEFAULT_SCREENSIZE, pygame.HWSURFACE | pygame.DOUBLEBUF)
