from __future__ import absolute_import

from ast import literal_eval
from random import randint, choice

import pygame

from . import get_version
from .events import (EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP,
    EVENT_STORY_SCRIPT_CAPTION, EVENT_STORY_SCRIPT_TYPE, EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH,
    EVENT_STORY_SCRIPT_POST_LAUGH_DELAY, EVENT_CHANGE_LEVEL)
from .literals import (COLOR_ALMOST_BLACK, COLOR_BLACK, COLOR_WHITE,
    DEFAULT_SCREENSIZE, GAME_OVER_TEXT, GAME_TITLE, PAUSE_TEXT,
    PAUSE_TEXT_VERTICAL_OFFSET,
    START_MESSAGE_TEXT, TEXT_YEAR, GAME_FONT, GAME_LEVEL_STORY,
    GAME_LEVEL_TITLE, GAME_LEVEL_FIRST, VERSION_TEXT, CREDITS_TEXT, TEXT_LEVEL_COMPLETE,
    LEVEL_MODE_STOPPED, LEVEL_MODE_RUNNING, LEVEL_MODE_COMPLETE,
    LEVEL_MODE_PLAYER_DEATH, LEVEL_MODE_GAME_OVER, GAME_LEVEL_FIRST,
    TEXT_STEAL_BOOKS_1, TEXT_STEAL_BOOKS_2, TEXT_HERO)
from .powerups import PowerUpApple, PowerUpShield
from .settings import SOUND_SUPPORT
from .utils import check_event, hollow_text, outlined_text, post_event


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


class PlayLevel(Level):
    boss_song = 'assets/music/hold the line_1.ogg'
    normal_song = 'assets/music/Zander Noriega - Darker Waves_0_looping.wav'

    def __init__(self, game, next_level=None):
        self.game = game
        self.game_over_font = pygame.font.Font(GAME_FONT, 32)
        self.result = []
        self.stage_score_value = 0
        self.mode = LEVEL_MODE_STOPPED
        self.boss_level = False
        self.display_game_over = False
        self.display_level_complete = False
        self.powerups = [PowerUpApple(self.game), PowerUpShield(self.game)]
        if next_level:
            self.next_level = next_level

    def on_start(self):
        if SOUND_SUPPORT:
            if self.boss_level:
                pygame.mixer.music.load(self.boss_song)
            else:
                pygame.mixer.music.load(self.normal_song)
            pygame.mixer.music.play(-1)
        self.accept_input = True
        self.is_game_over = False

        self.enemies = []
        screen_size = self.game.surface.get_size()
        self.game.can_be_paused = True
        self.mode = LEVEL_MODE_RUNNING
        self.game.player.reset_position()

        if self.boss_level:
            origin_point = (randint(0, screen_size[0]), 0)
            self.boss = self.boss_class(game=self.game, font=self.game.enemy_font, init_position=origin_point)
        else:
            #if self.enemy_images:
            for i in range(self.enemy_count):
                #origin_point = (randint(0, screen_size[0]), randint(0, screen_size[1]))
                #question, answer = self.question_function()
                #self.enemies.append(self.sprite_class(self.game, self.game.enemy_font, question, answer, origin_point, self.enemy_speed, self.enemy_images, self.enemy_fps, self.enemy_score_value, self.enemy_attack_points))
                self.spawn_enemy(self.enemy_class)

    def spawn_enemy(self, enemy_class, origin_point=None, speed=None):
        if not origin_point:
            screen_size = self.game.surface.get_size()
            origin_point = (randint(0, screen_size[0]), randint(0, screen_size[1]))
        question, answer = self.question_function()
        self.enemies.append(enemy_class(self.game, self.game.enemy_font, question, answer, origin_point, speed=speed))

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.mode == LEVEL_MODE_GAME_OVER and pygame.time.get_ticks() > self._time_player_death + 2500:
                post_event(event=EVENT_CHANGE_LEVEL, mode=GAME_LEVEL_TITLE)
        else:
            result = check_event(event)
            #if result:
                #print 'MORONIAN EVENT', result
                #if result['event'] == EVENT_CHANGE_LEVEL:
                    #self._current_level = result['mode']
                    #self.modes[self._current_level].on_start()

        if self.player.is_alive():
            self.player.on_event(event)

    def on_update(self):
        # Draw player
        self.player.update(self.game.time_passed)

        if self.mode == LEVEL_MODE_RUNNING:
            for powerup in self.powerups:
                powerup.on_update(self.game.time_passed)

        # Update and redraw all enemies
        for enemy in self.enemies:
            enemy.update(self.game.time_passed)

        if self.boss_level:
            self.boss.update(self.game.time_passed)
        else:
            if self.is_all_defeated():
                if self.player.is_alive():
                    self.player.score += self.stage_score_value
                    post_event(event=EVENT_CHANGE_LEVEL, mode=self.next_level)
                #self.player.win_scroll()

        if self.mode == LEVEL_MODE_PLAYER_DEATH:
            if pygame.time.get_ticks() > self._time_player_death + 2000:
                if SOUND_SUPPORT:
                    pygame.mixer.music.load('assets/music/lose music 3 - 2.wav')
                    pygame.mixer.music.play()
                self.mode = LEVEL_MODE_GAME_OVER

        if self.mode == LEVEL_MODE_COMPLETE:
            if pygame.time.get_ticks() > self._time_level_complete + 2000:
                self.game.shake_screen = False
            else:
                self.boss.on_explode()

            if pygame.time.get_ticks() > self._time_level_complete + 4000:
                self.game.get_current_level().player.on_win_scroll()
                self.display_level_complete = True

            if pygame.time.get_ticks() > self._time_level_complete + 8000:
                self.display_level_complete = True

            if pygame.time.get_ticks() > self._time_level_complete + 10000:
                self.game.get_current_level().player.reset_scroll()
                post_event(event=EVENT_CHANGE_LEVEL, mode=self.next_level)

    def on_blit(self):
        # Redraw the background
        self.game.display_tile_map(self.map)

        for powerup in self.powerups:
            powerup.blit()

        self.player.blit()
        if self.boss_level:
            self.boss.blit()

        # Update and redraw all creeps
        for enemy in self.enemies:
            enemy.blit()

        if self.mode == LEVEL_MODE_GAME_OVER:
            text_size = self.game_over_font.size(GAME_OVER_TEXT)
            label = outlined_text(self.game_over_font, GAME_OVER_TEXT, COLOR_WHITE, COLOR_ALMOST_BLACK)
            self.game.surface.blit(label, (self.game.surface.get_size()[0] / 2 - text_size[0] / 2, self.game.surface.get_size()[1] / 2 - 90))

        if self.mode == LEVEL_MODE_COMPLETE:
            if self.display_level_complete:
                text_size = self.game_over_font.size(TEXT_LEVEL_COMPLETE)
                label = outlined_text(self.game_over_font, TEXT_LEVEL_COMPLETE, COLOR_WHITE, COLOR_ALMOST_BLACK)
                self.game.surface.blit(label, (self.game.surface.get_size()[0] / 2 - text_size[0] / 2, self.game.surface.get_size()[1] / 2 - 90))

    def on_game_over(self):
        self.game.can_be_paused = False
        self.mode = LEVEL_MODE_PLAYER_DEATH
        self.accept_input = False
        self.result = []
        if SOUND_SUPPORT:
            pygame.mixer.music.stop()

        if not self.boss_level:
            for enemy in self.enemies:
                if enemy.alive:
                    enemy.defeat(self.enemies)

        self._time_player_death = pygame.time.get_ticks()

    def is_all_defeated(self):
        return self.enemies == []

    def player_shot(self, player, answer):
        hit = False
        if self.boss_level:
            self.boss.check_hit(answer)
        for enemy in self.enemies:
            if enemy.check_hit(answer):
                hit = True
                player.score += enemy.score_value
                enemy.defeat(self.enemies)
                break

        if hit is False:
            player.player_misses_shot()

    def on_level_complete(self):
        self.game.can_be_paused = False
        if SOUND_SUPPORT:
            pygame.mixer.music.stop()
        self.accept_input = False
        self.result = []
        self.mode = LEVEL_MODE_COMPLETE
        for enemy in self.enemies:
            if enemy.alive:
                enemy.defeat(self.enemies)

        if self.boss_level:
            self._time_level_complete = pygame.time.get_ticks()
            self.game.shake_screen = True
