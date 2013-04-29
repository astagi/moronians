from __future__ import absolute_import

from ast import literal_eval
from random import randint, choice

import pygame

from . import get_version
from .actors import (ActorSpaceship, ActorTracktorBeam, ActorBook01,
    ActorBook02, ActorBook03, ActorBook04, ActorBook05, ActorHumanShip)
from .events import (EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP,
    EVENT_STORY_SCRIPT_CAPTION, EVENT_STORY_SCRIPT_TYPE, EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH,
    EVENT_STORY_SCRIPT_POST_LAUGH_DELAY, EVENT_CHANGE_LEVEL)
from .literals import (COLOR_ALMOST_BLACK, COLOR_BLACK, COLOR_WHITE,
    DEFAULT_SCREENSIZE, GAME_OVER_TEXT, GAME_TITLE, PAUSE_TEXT,
    PAUSE_TEXT_VERTICAL_OFFSET,
    START_MESSAGE_TEXT, TEXT_YEAR, GAME_LEVEL_STORY,
    GAME_LEVEL_TITLE, GAME_LEVEL_FIRST, VERSION_TEXT, CREDITS_TEXT, TEXT_LEVEL_COMPLETE,
    LEVEL_MODE_STOPPED, LEVEL_MODE_RUNNING, LEVEL_MODE_COMPLETE,
    LEVEL_MODE_PLAYER_DEATH, LEVEL_MODE_GAME_OVER, GAME_LEVEL_FIRST,
    TEXT_STEAL_BOOKS_1, TEXT_STEAL_BOOKS_2, TEXT_HERO)
from .utils import check_event, hollow_text, outlined_text, post_event


class Stage(object):
    def __init__(self, game, next_stage=None):
        self.game = game
        self.canvas = pygame.Surface(self.game.surface.get_size())
        if next_stage:
            self.next_stage = next_stage

        self.actors = []
        self.script = {}

    def setup(self):
        pass

    def on_play(self, script):
        self.script = script
        self.on_start()

    def on_start(self):
        self._start_time = pygame.time.get_ticks()
        for time, entry in self.script.items():
            entry.on_setup(self)

    def on_update(self):
        for actor in self.actors:
            actor.on_update(self.game.time_passed)

        for time, entry in self.script.items():
            entry.on_update(self.game.time_passed)
            if pygame.time.get_ticks() > self._start_time + time:
                entry.on_execute()

    def process_event(self, event):
        pass

    def on_event(self, event):
        pass

    def on_blit(self):
        for time, entry in self.script.items():
            try:
                entry.on_blit()
            except AttributeError:
                pass

        for actor in self.actors:
            actor.on_blit()

        self.game.surface.blit(self.canvas, (0, 0))


class Action(object):
    def __init__(self):
        self._active = False
        self._executed = False
        self._complete = False

    def on_setup(self, stage):
        self.stage = stage

    def on_execute(self):
        if not self._active and not self._complete:
            self._start_time = pygame.time.get_ticks()
            self._active = True

    def on_update(self, time_passed):
        pass

    def on_blit(self):
        pass


class TextEffect(object):
    def on_setup(self, action):
        self.action = action


class TypeWriter(TextEffect):
    def __init__(self, delay, sound_file=None):
        self.delay = delay
        if sound_file:
            self.sound = pygame.mixer.Sound(sound_file)
        else:
            self.sound = None
        self._letter_index = 0
        self._last_letter_time = 0

    def on_setup(self, action):
        TextEffect.on_setup(self, action)
        self.original_string = action.string
        action.string = ''

    def on_update(self, time_passed):
        if self.action._active:
            if not self._last_letter_time:
                self._last_letter_time = self.action._start_time

            if pygame.time.get_ticks() > self._last_letter_time + self.delay:
                self._last_letter_time = pygame.time.get_ticks()
                self._letter_index += 1
                if self._letter_index > len(self.original_string):
                    self._letter_index = len(self.original_string)
                else:
                    if self.sound:
                        self.sound.play()
                self.action.string = self.original_string[0:self._letter_index]


class Blink(TextEffect):
    def __init__(self, delay=1000, sound_file=None):
        self.delay = delay
        if sound_file:
            self.sound = pygame.mixer.Sound(sound_file)
        else:
            self.sound = None
        self._last_time = 0

    def on_update(self, time_passed):
        if self.action._active:
            if pygame.time.get_ticks() > self._last_time + self.delay:
                self._last_time = pygame.time.get_ticks()
                self.action._visible = not self.action._visible
                if self.action._visible and self.sound:
                    self.sound.play()


class TextAlignment(object):
    def get_result(self):
        return self.position

# Horizontal
class LeftAlign(TextAlignment):
    def __init__(self, action, position):
        self.position = position


class CenterAlign(TextAlignment):
    def __init__(self, action, position):
        text_size = action.font.size(action.string)
        self.position = action.stage.canvas.get_size()[0] / 2 - text_size[0] / 2 + position


class RightAlign(TextAlignment):
    def __init__(self, action, position):
        text_size = action.font.size(action.string)
        self.position = action.stage.canvas.get_size()[0] - position


# Vertical
class TopAlign(TextAlignment):
    def __init__(self, action, position):
        self.position = position


class MiddleAlign(TextAlignment):
    def __init__(self, action, position):
        text_size = action.font.size(action.string)
        self.position = action.stage.canvas.get_size()[1] / 2 - text_size[1] / 2 + position


class BottomtAlign(TextAlignment):
    def __init__(self, action, position):
        text_size = action.font.size(action.string)
        self.position = action.stage.canvas.get_size()[1] - position


class DisplayText(Action):
    def __init__(self, stage, string, position, font_file, size, color, antialiasing=True, effect=None, horizontal_align=LeftAlign, vertical_align=TopAlign):
        Action.__init__(self)
        self.stage = stage
        self.string = string

        self.font = pygame.font.Font(font_file, size)
        self.size = size
        self.color = color
        self.antialiasing = antialiasing
        self.effect = effect
        self._visible = False

        self.position = (
            horizontal_align(self, position[0]).get_result(),
            vertical_align(self, position[1]).get_result()
        )
        self.on_setup(stage)

    def on_setup(self, *args, **kwargs):
        Action.on_setup(self, *args, **kwargs)
        if self.effect:
            self.effect.on_setup(self)

    def show(self):
        self._visible = True
        self.on_execute()

    def hide(self):
        self._visible = False
        self._active = False

    def on_update(self, time_passed):
        if self.effect:
            self.effect.on_update(time_passed)

    def on_blit(self):
        if self._active and self._visible:
            self.stage.canvas.blit(self.font.render(self.string, self.antialiasing, self.color), self.position)


class Background(Action):
    def __init__(self, image_file, fit=False):
        Action.__init__(self)
        self.image = pygame.image.load(image_file).convert()
        self.fit = fit

    def on_setup(self, stage):
        Action.on_setup(self, stage)
        if self.fit:
            self.image = pygame.transform.scale(self.image, (self.stage.game.surface.get_size()[0], self.stage.game.surface.get_size()[1]))

    def on_blit(self):
        if self._active:
            self.stage.canvas.blit(self.image, (0, 0))

    def on_execute(self):
        Action.on_execute(self)
        if self._active:
            self._complete = True


class PlaySound(Action):
    def __init__(self, sound_file):
        Action.__init__(self)
        self.sound = pygame.mixer.Sound(sound_file)

    def on_execute(self):
        Action.on_execute(self)
        if self._active:
            self.sound.play()
            self._active = False
            self._complete = True


class PlayMusic(Action):
    def __init__(self, music_file, loop=False):
        Action.__init__(self)
        self.loop = loop
        self.music_file = music_file

    def on_execute(self):
        Action.on_execute(self)
        if self._active:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(-1 if self.loop else 0)
            self._active = False
            self._complete = True


class End(Action):
    def __init__(self, stop_music=True):
        Action.__init__(self)
        self.stop_music = stop_music

    def on_execute(self):
        Action.on_execute(self)
        if self._active:
            post_event(event=EVENT_CHANGE_LEVEL, mode=self.stage.next_stage)
            self._active = False
            self._complete = True
            if self.stop_music:
                pygame.mixer.music.stop()


class ActorCommand(Action):
    def __init__(self, actor, command):
        Action.__init__(self)
        self.actor = actor
        self.command = command

    def on_execute(self):
        Action.on_execute(self)
        if self._active:
            self.command(self.actor)
            self._active = False
            self._complete = True


class StoryStage(Stage):
    def __init__(self, *args, **kwargs):
        Stage.__init__(self, *args, **kwargs)

        evil_spaceship = ActorSpaceship(self)
        evil_spaceship.set_position(220, -65)
        evil_spaceship.show()

        tractor_beam = ActorTracktorBeam(self)
        tractor_beam.set_position(253, 70)

        book_01 = ActorBook01(self)
        book_01.set_position(253, 170)

        book_02 = ActorBook02(self)
        book_02.set_position(227, 190)

        book_03 = ActorBook03(self)
        book_03.set_position(240, 185)

        book_04 = ActorBook04(self)
        book_04.set_position(250, 200)

        book_05 = ActorBook05(self)
        book_05.set_position(219, 210)

        human_ship = ActorHumanShip(self)
        human_ship.set_position(220, 200)

        text_time = DisplayText(self, TEXT_YEAR, (0, 400), 'assets/fonts/PressStart2P-Regular.ttf', 15, COLOR_WHITE, False, TypeWriter(150, 'assets/sounds/08.ogg'), horizontal_align=CenterAlign)
        text_book_1 = DisplayText(self, TEXT_STEAL_BOOKS_1, (0, 350), 'assets/fonts/PressStart2P-Regular.ttf', 15, COLOR_WHITE, False, TypeWriter(50), horizontal_align=CenterAlign)
        text_book_2 = DisplayText(self, TEXT_STEAL_BOOKS_2, (0, 380), 'assets/fonts/PressStart2P-Regular.ttf', 15, COLOR_WHITE, False, TypeWriter(50), horizontal_align=CenterAlign)
        text_hero = DisplayText(self, TEXT_HERO, (0, 350), 'assets/fonts/PressStart2P-Regular.ttf', 15, COLOR_WHITE, False, TypeWriter(50), horizontal_align=CenterAlign)

        self.actors = [book_01, book_02, book_03, book_04, book_05, evil_spaceship,
            tractor_beam, human_ship, text_time, text_book_1, text_book_2, text_hero]

        self.script = {
            0000: Background('assets/backgrounds/earth.png'),
            0001: PlayMusic('assets/music/LongDarkLoop.ogg'),

            1000: ActorCommand(text_time, lambda x: x.show()),
            6000: ActorCommand(text_time, lambda x: x.hide()),

            6500: ActorCommand(text_book_1, lambda x: x.show()),
            9000: ActorCommand(text_book_2, lambda x: x.show()),

            15000: ActorCommand(text_book_1, lambda x: x.hide()),
            15001: ActorCommand(text_book_2, lambda x: x.hide()),

            16501: ActorCommand(evil_spaceship, lambda x: x.set_destination(235, 30, 0.04)),
            17500: ActorCommand(evil_spaceship, lambda x: x.set_destination(235, 30, 0.03)),
            19000: ActorCommand(evil_spaceship, lambda x: x.set_destination(235, 30, 0.01)),

            21000: ActorCommand(tractor_beam, lambda x: x.show()),
            21200: ActorCommand(tractor_beam, lambda x: x.strobe_start()),

            22100: ActorCommand(book_01, lambda x: x.set_destination(240, 40, 0.02)),
            22101: ActorCommand(book_01, lambda x: x.show()),

            22300: ActorCommand(book_02, lambda x: x.set_destination(240, 40, 0.03)),
            22301: ActorCommand(book_02, lambda x: x.show()),

            22500: ActorCommand(book_03, lambda x: x.set_destination(240, 40, 0.04)),
            22501: ActorCommand(book_03, lambda x: x.show()),

            22700: ActorCommand(book_04, lambda x: x.set_destination(240, 40, 0.02)),
            22701: ActorCommand(book_04, lambda x: x.show()),

            22900: ActorCommand(book_05, lambda x: x.set_destination(240, 40, 0.04)),
            22901: ActorCommand(book_05, lambda x: x.show()),

            31000: ActorCommand(tractor_beam, lambda x: x.hide()),
            31001: ActorCommand(book_01, lambda x: x.hide()),
            31002: ActorCommand(book_02, lambda x: x.hide()),
            31003: ActorCommand(book_03, lambda x: x.hide()),
            31004: ActorCommand(book_04, lambda x: x.hide()),
            31005: ActorCommand(book_05, lambda x: x.hide()),

            32500: ActorCommand(evil_spaceship, lambda x: x.set_destination(300, -65, 0.04)),
            32500: ActorCommand(evil_spaceship, lambda x: x.set_destination(300, -65, 0.08)),

            34500: PlaySound('assets/sounds/evil-laughter-witch.ogg'),

            39000: ActorCommand(text_hero, lambda x: x.show()),
            42000: ActorCommand(human_ship, lambda x: x.set_destination(300, -65, 0.08)),
            42001: ActorCommand(human_ship, lambda x: x.show()),
            46999: ActorCommand(text_hero, lambda x: x.hide()),
            47000: End(),
        }

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            pygame.mixer.music.stop()
            post_event(event=EVENT_CHANGE_LEVEL, mode=self.next_stage)


class StagePlanetTravel(Stage):
    def __init__(self, *args, **kwargs):
        Stage.__init__(self, *args, **kwargs)

        human_ship = ActorHumanShip(self)
        human_ship.set_position(150, 448)

        planet_name = DisplayText(self, self.planet_name, (0, 400), 'assets/fonts/PressStart2P-Regular.ttf', 15, COLOR_WHITE, False, TypeWriter(150, 'assets/sounds/19.ogg'), horizontal_align=CenterAlign)

        self.actors = [human_ship, planet_name]

        self.script = {
            0000: Background(self.background_file),

            2000: ActorCommand(planet_name, lambda x: x.show()),
            6000: ActorCommand(planet_name, lambda x: x.hide()),

            6002: PlaySound('assets/players/ship_engine.wav'),

            8000: ActorCommand(human_ship, lambda x: x.set_destination(300, 200, 0.08)),
            8001: ActorCommand(human_ship, lambda x: x.show()),

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

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            post_event(event=EVENT_CHANGE_LEVEL, mode=self.next_stage)


class StageTitle(Stage):
    def __init__(self, *args, **kwargs):
        Stage.__init__(self, *args, **kwargs)

        text_press_enter = DisplayText(self, START_MESSAGE_TEXT, (0, 80), 'assets/fonts/PressStart2P-Regular.ttf', 24, COLOR_WHITE, False, Blink(200), horizontal_align=CenterAlign, vertical_align=BottomtAlign)
        text_credit = DisplayText(self, CREDITS_TEXT, (0, 18), 'assets/fonts/PressStart2P-Regular.ttf', 9, COLOR_WHITE, False, horizontal_align=CenterAlign, vertical_align=BottomtAlign)
        text_version = DisplayText(self, get_version(), (100, 18), 'assets/fonts/PressStart2P-Regular.ttf', 9, COLOR_WHITE, False, horizontal_align=RightAlign, vertical_align=BottomtAlign)

        self.actors = [text_press_enter, text_credit, text_version]

        self.script = {
            0000: Background('assets/backgrounds/game_title.png', fit=True),
            0001: PlayMusic('assets/music/OveMelaaTranceBitBit.ogg', loop=True),
            0002: ActorCommand(text_press_enter, lambda x: x.show()),
            0003: ActorCommand(text_credit, lambda x: x.show()),
            0004: ActorCommand(text_version, lambda x: x.show()),
        }

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            post_event(event=EVENT_CHANGE_LEVEL, mode=self.next_stage)
