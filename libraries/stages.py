from __future__ import absolute_import

from random import randint

import pygame

from . import get_version
from .actions import ActorCommand, Background, DisplayText, End, PlaySound, PlayMusic
from .actors import (
    ActorSpaceship, ActorTracktorBeam, ActorBook01,
    ActorBook02, ActorBook03, ActorBook04, ActorBook05, ActorHumanShip,
)
from .effects import Blink, TypeWriter
from .events import EVENT_CHANGE_STAGE
from .literals import (
    COLOR_ALMOST_BLACK, COLOR_WHITE, CREDITS_TEXT, GAME_FONT,
    GAME_OVER_TEXT, HEALTH_BAR_TEXT, LEVEL_MODE_COMPLETE,
    LEVEL_MODE_GAME_OVER, LEVEL_MODE_PLAYER_DEATH, LEVEL_MODE_RUNNING,
    LEVEL_MODE_STOPPED, SCORE_TEXT, START_MESSAGE_TEXT, TEXT_BOSS_HIT_POINT,
    TEXT_FINAL_SCORE, TEXT_LEVEL_COMPLETE, TEXT_STEAL_BOOKS_1,
    TEXT_STEAL_BOOKS_2, TEXT_HERO, TEXT_STAGE_END, TEXT_YEAR
)
from .powerups import PowerUpApple, PowerUpShield
from .utils import BottomAlign, CenterAlign, LeftAlign, RightAlign, outlined_text, post_event


class Stage(object):
    def __init__(self, next_stage=None):
        if next_stage:
            self.next_stage = next_stage

    def add_actor(self, actor):
        if actor not in self.actors:
            actor.on_setup(stage=self)
            self.actors.append(actor)

    def on_blit(self):
        self.on_draw_background()

        for actor in self.actors:
            actor.on_blit()

    def on_draw_background(self):
        pass

    def on_event(self, event):
        pass

    def on_level_exit(self):
        self.actors = []
        self.script = {}
        self._runtime_script = {}
        pygame.mixer.music.stop()

    def on_setup(self, game):
        self.actors = []
        self.game = game
        self.script = {}
        self._runtime_script = {}

    def on_start(self):
        self._start_time = pygame.time.get_ticks()
        self._runtime_script = self.script.copy()

        for time, entry in self.script.items():
            entry.on_setup(stage=self)

    def on_update(self):
        if not self.game.paused:
            for actor in self.actors:
                actor.on_update(time_passed=self.game.time_passed)

            for time, entry in self._runtime_script.items():
                if pygame.time.get_ticks() > self._start_time + time:
                    entry = self._runtime_script.pop(time)
                    entry.on_execute()


class BasePlayLevel(Stage):
    level_song = 'assets/music/Zander Noriega - Darker Waves_0_looping.wav'
    enemy_count = 0
    miss_score_penalty = 50

    def __init__(self, *args, **kwargs):
        super(BasePlayLevel, self).__init__(*args, **kwargs)
        self.game_over_font = pygame.font.Font(GAME_FONT, 32)
        self.result = []
        self.stage_score_value = 0
        self.mode = LEVEL_MODE_STOPPED
        self.display_game_over = False
        self.display_level_complete = False

    def is_all_defeated(self):
        return self.enemies == []

    def on_draw_background(self):
        self.map.blit(self.game.surface)

    def on_blit(self):
        super(BasePlayLevel, self).on_blit()

        # TODO: merge these two
        for powerup in self.powerups:
            powerup.on_blit()

        if self.mode == LEVEL_MODE_GAME_OVER:
            text_size = self.game_over_font.size(GAME_OVER_TEXT)
            label = outlined_text(self.game_over_font, GAME_OVER_TEXT, COLOR_WHITE, COLOR_ALMOST_BLACK)
            self.game.surface.blit(label, (self.game.surface.get_size()[0] / 2 - text_size[0] / 2, self.game.surface.get_size()[1] / 2 - 90))

        if self.mode == LEVEL_MODE_COMPLETE:
            if self.display_level_complete:
                text_size = self.game_over_font.size(TEXT_LEVEL_COMPLETE)
                label = outlined_text(self.game_over_font, TEXT_LEVEL_COMPLETE, COLOR_WHITE, COLOR_ALMOST_BLACK)
                self.game.surface.blit(label, (self.game.surface.get_size()[0] / 2 - text_size[0] / 2, self.game.surface.get_size()[1] / 2 - 90))

        # Blit health bar
        text_size = self.font_health.size(HEALTH_BAR_TEXT)
        label = outlined_text(self.font_health, HEALTH_BAR_TEXT, COLOR_WHITE, COLOR_ALMOST_BLACK)
        self.game.surface.blit(label, (1, 1))
        self.game.surface.blit(self.health_bar_image, (text_size[0] + 10, 1), area=pygame.Rect(0, 0, self.health_bar_image.get_size()[0] * self.game.player.hit_points / float(self.game.player.total_hit_points), self.health_bar_image.get_size()[1]))

        # Blit score
        score_text = '%s %d' % (SCORE_TEXT, self.game.player.score)
        text_size = self.font_score.size(score_text)
        label = outlined_text(self.font_score, score_text, COLOR_WHITE, COLOR_ALMOST_BLACK)
        self.game.surface.blit(label, (self.game.surface.get_size()[0] - text_size[0] - 10, 1))

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.mode == LEVEL_MODE_GAME_OVER and pygame.time.get_ticks() > self._time_player_death + 2500:
                post_event(event=EVENT_CHANGE_STAGE, stage=self.next_stage)

        for actor in self.actors:
            actor.on_event(event)

    def on_game_over(self):
        self.next_stage = self.game.initial_stage
        self.game.can_be_paused = False
        self.mode = LEVEL_MODE_PLAYER_DEATH
        self.accept_input = False
        self.result = []
        pygame.mixer.music.stop()

        self._time_player_death = pygame.time.get_ticks()

    def on_level_complete(self):
        self.game.can_be_paused = False
        pygame.mixer.music.stop()
        self.accept_input = False
        self.result = []
        self.mode = LEVEL_MODE_COMPLETE
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.on_death()

        self._time_level_complete = pygame.time.get_ticks()

    def on_setup(self, game):
        super(BasePlayLevel, self).on_setup(game)

        self.font_health = pygame.font.Font(GAME_FONT, 12)
        self.font_score = pygame.font.Font(GAME_FONT, 12)
        self.health_bar_image = pygame.image.load('assets/players/healthBar_100x12px_green.png').convert_alpha()
        self.screen_size = self.game.surface.get_size()
        self.sound_misses = pygame.mixer.Sound('assets/players/05.ogg')
        self.game.player.on_setup(stage=self)
        self.game.player.show()
        self.enemies = []

    def on_start(self):
        self.powerups = [PowerUpApple(self.game), PowerUpShield(self.game)]

        pygame.mixer.music.load(self.level_song)
        pygame.mixer.music.play(-1)
        self.accept_input = True
        self.is_game_over = False

        self.game.can_be_paused = True
        self.mode = LEVEL_MODE_RUNNING

    def on_update(self):
        super(BasePlayLevel, self).on_update()
        if not self.game.paused:
            if self.mode == LEVEL_MODE_RUNNING:
                for powerup in self.powerups:
                    powerup.on_update(self.game.time_passed)

            if self.mode == LEVEL_MODE_PLAYER_DEATH:
                if pygame.time.get_ticks() > self._time_player_death + 2000:
                    pygame.mixer.music.load('assets/music/lose music 3 - 2.wav')
                    pygame.mixer.music.play()
                    self.mode = LEVEL_MODE_GAME_OVER

    def player_shot(self, player, answer):
        hit = False

        for enemy in self.enemies:
            if enemy.check_hit(answer):
                hit = True
                player.score += enemy.score_value
                enemy.on_death()
                break

        if hit is False:
            self.player_misses_shot()

    def player_misses_shot(self):
        self.game.player.score -= self.miss_score_penalty
        if self.game.player.score < 0:
            self.game.player.score = 0
        else:
            self.sound_misses.play()


class PlayLevel(BasePlayLevel):
    enemies = []

    def on_setup(self, *args, **kwargs):
        super(PlayLevel, self).on_setup(*args, **kwargs)

        for i in range(self.enemy_count):
            self.spawn_enemy(self.enemy_class)

    def on_update(self):
        super(PlayLevel, self).on_update()
        if self.is_all_defeated():
            if self.game.player.is_alive():
                self.game.player.score += self.stage_score_value
                post_event(event=EVENT_CHANGE_STAGE, stage=self.next_stage)

    def spawn_enemy(self, enemy_class, origin_point=None, speed=None):
        if not origin_point:
            screen_size = self.game.surface.get_size()
            origin_point = (randint(0, screen_size[0]), randint(0, screen_size[1]))
        question, answer = self.question_function()
        enemy_instance = enemy_class(game=self.game, font=self.game.enemy_font, question=question, answer=answer, init_position=origin_point, speed=speed)
        self.enemies.append(enemy_instance)
        self.add_actor(enemy_instance)
        enemy_instance.show()


class BossLevel(PlayLevel):
    level_song = 'assets/music/hold the line_1.ogg'

    def on_blit(self):
        super(BossLevel, self).on_blit()

        # Blit health bar
        if self.boss.is_alive():
            HP_BAR_HORIZONTAL_POSITION = 220
            HP_BAR_VERTICAL_POSITION = 0
            text_size = self.game.font.size(TEXT_BOSS_HIT_POINT)
            label = outlined_text(self.game.font, TEXT_BOSS_HIT_POINT, COLOR_WHITE, COLOR_ALMOST_BLACK)
            self.game.surface.blit(label, (HP_BAR_HORIZONTAL_POSITION, HP_BAR_VERTICAL_POSITION))
            self.game.surface.blit(self.hit_point_bar_image, (text_size[0] + HP_BAR_HORIZONTAL_POSITION + 5, HP_BAR_VERTICAL_POSITION), area=pygame.Rect(0, 0, self.hit_point_bar_image.get_size()[0] * self.boss.hit_points / float(self.boss.total_hit_points), self.hit_point_bar_image.get_size()[1]))

    def on_level_complete(self):
        super(BossLevel, self).on_level_complete()
        self.game.shake_screen = True

    def on_setup(self, game):
        super(BossLevel, self).on_setup(game)
        self.boss = self.boss_class(game=self.game)
        self.boss.on_setup(stage=self)
        self.boss.show()
        self.enemies.append(self.boss)
        self.hit_point_bar_image = pygame.image.load('assets/enemies/healthBar_100x12px_red.png').convert_alpha()

    def on_update(self):
        super(PlayLevel, self).on_update()
        if self.mode == LEVEL_MODE_COMPLETE:
            self.boss.set_rotation(randint(1, 360))

            if pygame.time.get_ticks() > self._time_level_complete + 2000:
                self.game.shake_screen = False
                self.boss.set_rotation(0)

            if pygame.time.get_ticks() > self._time_level_complete + 4000:
                self.game.player.on_win_scroll()
                self.display_level_complete = True

            if pygame.time.get_ticks() > self._time_level_complete + 8000:
                self.display_level_complete = True

            if pygame.time.get_ticks() > self._time_level_complete + 10000:
                self.game.player.reset_scroll()
                post_event(event=EVENT_CHANGE_STAGE, stage=self.next_stage)

    def player_shot(self, player, answer):
        super(BossLevel, self).player_shot(player, answer)
        self.boss.check_hit(answer)


class StageTitle(Stage):
    def on_setup(self, *args, **kwargs):
        super(StageTitle, self).on_setup(*args, **kwargs)
        text_press_enter = DisplayText(string=START_MESSAGE_TEXT, position=(0, 80), font_file=GAME_FONT, size=24, effect=Blink(200), horizontal_align=CenterAlign, vertical_align=BottomAlign)
        text_credit = DisplayText(string=CREDITS_TEXT, position=(0, 18), font_file=GAME_FONT, size=9, horizontal_align=CenterAlign, vertical_align=BottomAlign)
        text_version = DisplayText(string=get_version(), position=(100, 18), font_file=GAME_FONT, size=9, horizontal_align=RightAlign, vertical_align=BottomAlign)

        self.game.can_be_pause = False
        self.game.ask_exit_confirm = False

        self.script = {
            0000: Background(image_file='assets/backgrounds/game_title.png', fit=True),
            0001: PlayMusic('assets/music/OveMelaaTranceBitBit.ogg', loop=True),
            0002: ActorCommand(text_press_enter, lambda x: x.show()),
            0003: ActorCommand(text_credit, lambda x: x.show()),
            0004: ActorCommand(text_version, lambda x: x.show()),
        }

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            post_event(event=EVENT_CHANGE_STAGE, stage=self.next_stage)


class BaseStoryStage(Stage):
    def on_setup(self, *args, **kwargs):
        super(BaseStoryStage, self).on_setup(*args, **kwargs)
        self.game.can_be_pause = False
        self.game.ask_exit_confirm = True

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            post_event(event=EVENT_CHANGE_STAGE, stage=self.next_stage)


class StoryStage(BaseStoryStage):
    def on_setup(self, *args, **kwargs):
        super(StoryStage, self).on_setup(*args, **kwargs)
        evil_spaceship = ActorSpaceship(game=self.game)

        tractor_beam = ActorTracktorBeam(game=self.game)
        book_01 = ActorBook01(game=self.game)
        book_02 = ActorBook02(game=self.game)
        book_03 = ActorBook03(game=self.game)
        book_04 = ActorBook04(game=self.game)
        book_05 = ActorBook05(game=self.game)

        human_ship = ActorHumanShip(game=self.game)

        text_time = DisplayText(string=TEXT_YEAR, position=(0, 400), effect=TypeWriter(150, 'assets/sounds/08.ogg'), horizontal_align=CenterAlign)
        text_book_1 = DisplayText(string=TEXT_STEAL_BOOKS_1, position=(0, 350), effect=TypeWriter(50), horizontal_align=CenterAlign)
        text_book_2 = DisplayText(string=TEXT_STEAL_BOOKS_2, position=(0, 380), effect=TypeWriter(50), horizontal_align=CenterAlign)
        text_hero = DisplayText(string=TEXT_HERO, position=(0, 350), effect=TypeWriter(50), horizontal_align=CenterAlign)

        self.script = {
            0000: Background(image_file='assets/backgrounds/earth.png'),
            0001: PlayMusic('assets/music/LongDarkLoop.ogg'),

            1000: ActorCommand(text_time, lambda x: x.show()),
            6000: ActorCommand(text_time, lambda x: x.hide()),

            6500: ActorCommand(text_book_1, lambda x: x.show()),
            9000: ActorCommand(text_book_2, lambda x: x.show()),

            15000: ActorCommand(text_book_1, lambda x: x.hide()),
            15001: ActorCommand(text_book_2, lambda x: x.hide()),

            16500: ActorCommand(evil_spaceship, lambda x: x.set_position(220, -65)),
            16501: ActorCommand(evil_spaceship, lambda x: x.show()),
            16502: ActorCommand(evil_spaceship, lambda x: x.set_destination(235, 30, 0.04)),
            17500: ActorCommand(evil_spaceship, lambda x: x.set_destination(235, 30, 0.03)),
            19000: ActorCommand(evil_spaceship, lambda x: x.set_destination(235, 30, 0.01)),

            21000: ActorCommand(tractor_beam, lambda x: x.set_position(253, 70)),
            21001: ActorCommand(tractor_beam, lambda x: x.show()),
            21200: ActorCommand(tractor_beam, lambda x: x.strobe_start()),

            22100: ActorCommand(book_01, lambda x: x.set_destination(240, 40, 0.02)),
            22101: ActorCommand(book_01, lambda x: x.set_position(253, 170)),
            22102: ActorCommand(book_01, lambda x: x.show()),

            22300: ActorCommand(book_02, lambda x: x.set_destination(240, 40, 0.03)),
            22301: ActorCommand(book_02, lambda x: x.set_position(227, 190)),
            22302: ActorCommand(book_02, lambda x: x.show()),

            22500: ActorCommand(book_03, lambda x: x.set_destination(240, 40, 0.04)),
            22501: ActorCommand(book_03, lambda x: x.set_position(240, 185)),
            22502: ActorCommand(book_03, lambda x: x.show()),

            22700: ActorCommand(book_04, lambda x: x.set_destination(240, 40, 0.02)),
            22701: ActorCommand(book_04, lambda x: x.set_position(250, 200)),
            22702: ActorCommand(book_04, lambda x: x.show()),

            22900: ActorCommand(book_05, lambda x: x.set_destination(240, 40, 0.04)),
            22901: ActorCommand(book_05, lambda x: x.set_position(219, 210)),
            22902: ActorCommand(book_05, lambda x: x.show()),

            31000: ActorCommand(tractor_beam, lambda x: x.hide()),
            31001: ActorCommand(book_01, lambda x: x.hide()),
            31002: ActorCommand(book_02, lambda x: x.hide()),
            31003: ActorCommand(book_03, lambda x: x.hide()),
            31004: ActorCommand(book_04, lambda x: x.hide()),
            31005: ActorCommand(book_05, lambda x: x.hide()),

            32500: ActorCommand(evil_spaceship, lambda x: x.set_destination(300, -65, 0.03)),
            32500: ActorCommand(evil_spaceship, lambda x: x.set_destination(300, -65, 0.07)),

            34500: PlaySound('assets/sounds/evil-laughter-witch.ogg'),

            39000: ActorCommand(text_hero, lambda x: x.show()),
            42000: ActorCommand(human_ship, lambda x: x.set_position(220, 200)),
            42001: ActorCommand(human_ship, lambda x: x.set_destination(300, -65, 0.07)),
            42002: ActorCommand(human_ship, lambda x: x.show()),
            46999: ActorCommand(text_hero, lambda x: x.hide()),
            47000: End(),
        }


class StagePlanetTravel(BaseStoryStage):
    def on_setup(self, *args, **kwargs):
        super(StagePlanetTravel, self).on_setup(*args, **kwargs)

        human_ship = ActorHumanShip(game=self.game)
        planet_name = DisplayText(string=self.planet_name, position=(0, 400), effect=TypeWriter(150, 'assets/sounds/19.ogg'), horizontal_align=CenterAlign)

        self.script = {
            0000: Background(image_file=self.background_file),

            2000: ActorCommand(planet_name, lambda x: x.show()),
            6000: ActorCommand(planet_name, lambda x: x.hide()),

            6002: PlaySound('assets/players/ship_engine.wav'),

            8000: ActorCommand(human_ship, lambda x: x.set_destination(300, 200, 0.08)),
            8001: ActorCommand(human_ship, lambda x: x.set_position(150, 448)),
            8002: ActorCommand(human_ship, lambda x: x.show()),

            8500: ActorCommand(human_ship, lambda x: x.set_scale(0.9)),
            8501: ActorCommand(human_ship, lambda x: x.set_destination(300, 200, 0.07)),

            9500: ActorCommand(human_ship, lambda x: x.set_scale(0.8)),
            9501: ActorCommand(human_ship, lambda x: x.set_destination(300, 200, 0.06)),

            10100: ActorCommand(human_ship, lambda x: x.set_scale(0.7)),
            10101: ActorCommand(human_ship, lambda x: x.set_destination(300, 200, 0.05)),

            10800: ActorCommand(human_ship, lambda x: x.set_scale(0.6)),
            10801: ActorCommand(human_ship, lambda x: x.set_destination(300, 200, 0.04)),

            11600: ActorCommand(human_ship, lambda x: x.set_scale(0.5)),
            11601: ActorCommand(human_ship, lambda x: x.set_destination(300, 200, 0.03)),

            12300: ActorCommand(human_ship, lambda x: x.set_scale(0.4)),
            12301: ActorCommand(human_ship, lambda x: x.set_destination(300, 200, 0.02)),

            13100: ActorCommand(human_ship, lambda x: x.set_scale(0.3)),
            13101: ActorCommand(human_ship, lambda x: x.set_destination(300, 200, 0.01)),

            14500: ActorCommand(human_ship, lambda x: x.hide()),

            15500: End(),
        }



class StageEnd(Stage):
    def on_setup(self, *args, **kwargs):
        super(StageEnd, self).on_setup(*args, **kwargs)

        human_ship = ActorHumanShip(game=self.game)
        text_score = DisplayText(string='%s: %d' % (TEXT_FINAL_SCORE, self.game.player.score), position=(0, 100), effect=TypeWriter(110), horizontal_align=CenterAlign)

        text_hero_1 = DisplayText(string=TEXT_STAGE_END[0], position=(0, 350), effect=TypeWriter(110), horizontal_align=CenterAlign)
        text_hero_2 = DisplayText(string=TEXT_STAGE_END[1], position=(0, 380), effect=TypeWriter(110), horizontal_align=CenterAlign)
        text_hero_3 = DisplayText(string=TEXT_STAGE_END[2], position=(0, 410), effect=TypeWriter(110), horizontal_align=CenterAlign)
        text_hero_4 = DisplayText(string=TEXT_STAGE_END[3], position=(0, 350), effect=TypeWriter(110), horizontal_align=CenterAlign)
        text_hero_5 = DisplayText(string=TEXT_STAGE_END[4], position=(0, 380), effect=TypeWriter(110), horizontal_align=CenterAlign)
        text_hero_6 = DisplayText(string=TEXT_STAGE_END[5], position=(0, 410), effect=TypeWriter(110), horizontal_align=CenterAlign)
        text_hero_7 = DisplayText(string=TEXT_STAGE_END[6], position=(0, 350), effect=TypeWriter(110), horizontal_align=CenterAlign)
        text_hero_8 = DisplayText(string=TEXT_STAGE_END[7], position=(0, 380), effect=TypeWriter(110), horizontal_align=CenterAlign)
        text_hero_9 = DisplayText(string=TEXT_STAGE_END[8], position=(0, 350), effect=TypeWriter(110), horizontal_align=CenterAlign)
        text_hero_10 = DisplayText(string=TEXT_STAGE_END[9], position=(0, 380), effect=TypeWriter(120, 'assets/sounds/08.ogg'), horizontal_align=CenterAlign)
        text_hero_11 = DisplayText(string=TEXT_STAGE_END[10], position=(0, 220), effect=TypeWriter(110), horizontal_align=CenterAlign)

        self.script = {
            0000: Background(image_file='assets/backgrounds/earth.png'),
            0001: PlayMusic('assets/music/Grassy World (8-Bit_Orchestral Overture) - Main Title Theme.mp3'),

            1000: ActorCommand(text_hero_1, lambda x: x.show()),
            5000: ActorCommand(text_hero_2, lambda x: x.show()),
            10000: ActorCommand(text_hero_3, lambda x: x.show()),

            2000: ActorCommand(human_ship, lambda x: x.set_rotation(160)),
            2001: ActorCommand(human_ship, lambda x: x.set_destination(220, 200, 0.03)),
            2002: ActorCommand(human_ship, lambda x: x.set_position(300, -65)),
            2003: ActorCommand(human_ship, lambda x: x.show()),

            2010: ActorCommand(text_score, lambda x: x.show()),

            6000: ActorCommand(human_ship, lambda x: x.set_destination(220, 200, 0.02)),
            6001: ActorCommand(human_ship, lambda x: x.set_scale(0.8)),
            6002: ActorCommand(human_ship, lambda x: x.set_rotation(170)),

            9000: ActorCommand(human_ship, lambda x: x.set_destination(220, 200, 0.01)),
            9001: ActorCommand(human_ship, lambda x: x.set_scale(0.6)),
            9002: ActorCommand(human_ship, lambda x: x.set_rotation(180)),

            15000: ActorCommand(human_ship, lambda x: x.set_destination(220, 200, 0.007)),
            15001: ActorCommand(human_ship, lambda x: x.set_scale(0.4)),
            15002: ActorCommand(human_ship, lambda x: x.set_rotation(190)),

            15004: ActorCommand(text_hero_1, lambda x: x.hide()),
            16000: ActorCommand(text_hero_2, lambda x: x.hide()),
            17000: ActorCommand(text_hero_3, lambda x: x.hide()),

            18000: ActorCommand(human_ship, lambda x: x.hide()),

            19000: ActorCommand(text_hero_4, lambda x: x.show()),
            24000: ActorCommand(text_hero_5, lambda x: x.show()),
            29000: ActorCommand(text_hero_6, lambda x: x.show()),

            34002: ActorCommand(text_hero_4, lambda x: x.hide()),
            35000: ActorCommand(text_hero_5, lambda x: x.hide()),
            36000: ActorCommand(text_hero_6, lambda x: x.hide()),

            37000: ActorCommand(text_hero_7, lambda x: x.show()),
            42000: ActorCommand(text_hero_8, lambda x: x.show()),

            47002: ActorCommand(text_hero_7, lambda x: x.hide()),
            48000: ActorCommand(text_hero_8, lambda x: x.hide()),

            50000: ActorCommand(text_hero_9, lambda x: x.show()),
            55000: ActorCommand(text_hero_10, lambda x: x.show()),

            60000: ActorCommand(text_hero_9, lambda x: x.hide()),
            61000: ActorCommand(text_hero_10, lambda x: x.hide()),

            62000: ActorCommand(text_hero_11, lambda x: x.show()),

            72000: End(),
        }
