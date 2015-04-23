from __future__ import absolute_import

import logging
from random import randint

import pygame

from .actors import ActorPlayer
from .exceptions import SwallowEvent
from .events import EVENT_CHANGE_STAGE
from .literals import (
    COLOR_BLACK, COLOR_WHITE,
    DEFAULT_SCREENSIZE, GAME_FONT, GAME_TITLE, PAUSE_TEXT,
    PAUSE_TEXT_VERTICAL_OFFSET, TEXT_EXIT_CONFIRMATION,
    EXIT_TEXT_VERTICAL_OFFSET
)
from .utils import check_event, import_string, post_event

logger = logging.getLogger(__name__)


class Game(object):
    def __init__(self, module_name, fullscreen):
        pygame.init()
        self.fullscreen = fullscreen
        self.running = False
        self.paused = False
        self.finish = False

        try:
            self.module_class = import_string('modules.%s.module.Module' % module_name)
        except ImportError as exception:
            print 'Unable to import module %s; %s' % (module_name, exception)
            exit(1)

    def display_box(self, font, message, position, size):
        BORDER_SIZE = 2
        if len(message) != 0:
            pygame.draw.rect(self._screen, COLOR_BLACK, (position[0] + BORDER_SIZE, position[1] + BORDER_SIZE, size[0] - BORDER_SIZE, size[1] - BORDER_SIZE), 0)
            pygame.draw.rect(self._screen, COLOR_WHITE, (position[0], position[1], size[0], size[1]), 1)
            self.surface.blit(font.render(message, 1, COLOR_WHITE), (position[0] + BORDER_SIZE, position[1] + BORDER_SIZE))

    def display_pause_label(self, font):
        text_size = font.size(PAUSE_TEXT)
        self.surface.blit(font.render(PAUSE_TEXT, 1, COLOR_WHITE), (self._screen.get_width() / 2 - text_size[0] / 2, self._screen.get_height() / 2 - text_size[1] / 2 - PAUSE_TEXT_VERTICAL_OFFSET))

    def exit_confirmation(self, font):
        text_size = font.size(TEXT_EXIT_CONFIRMATION)
        self.surface.blit(font.render(TEXT_EXIT_CONFIRMATION, 1, COLOR_WHITE), (self._screen.get_width() / 2 - text_size[0] / 2, self._screen.get_height() / 2 - text_size[1] / 2 - EXIT_TEXT_VERTICAL_OFFSET))

    def exit_game(self):
        self.finish = True
        pygame.display.set_mode(DEFAULT_SCREENSIZE, pygame.HWSURFACE | pygame.DOUBLEBUF)

    def get_current_stage(self):
        return self.module.stages[self._current_stage]

    def on_blit(self):
        self.module.stages[self._current_stage].on_blit()

        if self._exit_prompt:
            self.exit_confirmation(self.font)

        if self.paused:
            self.display_pause_label(self.font)

        if self.shake_screen:
            self._screen.blit(self.surface, (randint(0, 10), randint(0, 10)))
        else:
            self._screen.blit(self.surface, (0, 0))

    def on_event(self, event):
        # Check pygame events

        if event.type == pygame.QUIT:
            self.exit_game()
        elif event.type == pygame.KEYDOWN:
            # Check for control keys first
            if self._exit_prompt:
                if event.key in [pygame.K_ESCAPE, ord('n'), ord('N')]:
                    self._exit_prompt = False
                    self.can_be_paused = self._can_be_paused
                    raise SwallowEvent
                elif event.key in [ord('y'), ord('Y')]:
                    self.exit_game()
            elif event.key == pygame.K_ESCAPE:
                if not self.ask_exit_confirm:
                    self.exit_game()
                else:
                    self._can_be_paused = self.can_be_paused
                    self._exit_prompt = True
                    raise SwallowEvent
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
        else:
            # Check game events
            result = check_event(event)
            if result:
                if result['event'] == EVENT_CHANGE_STAGE:
                    self.surface.fill(COLOR_BLACK)
                    if self._current_stage:
                        self.module.stages[self._current_stage].on_level_exit()

                    self._current_stage = result['stage']
                    try:
                        self.module.stages[self._current_stage].on_setup(game=self)
                        self.module.stages[self._current_stage].on_start()
                    except KeyError:
                        print 'Unknown stage: %d' % self._current_stage
                        exit(1)

    def on_events(self):
        for event in pygame.event.get():
            try:
                self.on_event(event)
            except SwallowEvent:
                pass
            else:
                if self._current_stage is not None:
                    self.module.stages[self._current_stage].on_event(event)

    def on_setup(self):
        self.clock = pygame.time.Clock()

        screen_mode = pygame.HWSURFACE | pygame.DOUBLEBUF

        if self.fullscreen:
            screen_mode |= pygame.FULLSCREEN

        self._screen = pygame.display.set_mode(DEFAULT_SCREENSIZE, screen_mode)
        self.surface = pygame.Surface(self._screen.get_size())
        self.running = True
        self.font = pygame.font.Font(GAME_FONT, 15)
        self.font_small = pygame.font.Font(GAME_FONT, 12)
        self.enemy_font = self.font_small
        self.pause_sound = pygame.mixer.Sound('assets/sounds/pause.wav')
        self.player = ActorPlayer(game=self)
        pygame.display.set_caption(GAME_TITLE)
        self._current_stage = None
        self.shake_screen = False
        self.can_be_paused = self._can_be_paused = False
        self._exit_prompt = False
        self.ask_exit_confirm = False
        self.module = self.module_class()
        self.initial_stage = self.module.initial_stage
        post_event(event=EVENT_CHANGE_STAGE, stage=self.initial_stage)

    def run(self):
        self.on_setup()

        while not self.finish:
            self.time_passed = self.clock.tick(60)

            self.on_events()
            self.module.stages[self._current_stage].on_update()
            self.on_blit()
            pygame.display.flip()
