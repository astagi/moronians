from __future__ import absolute_import

from ast import literal_eval
from random import randint, choice

import pygame

from .events import (EVENT_GAME_OVER, EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP,
    EVENT_STORY_SCRIPT_CAPTION, EVENT_STORY_SCRIPT_TYPE, EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH,
    EVENT_STORY_SCRIPT_POST_LAUGH_DELAY, EVENT_CHANGE_LEVEL)
from .literals import (COLOR_ALMOST_BLACK, COLOR_BLACK, COLOR_WHITE,
    DEFAULT_SCREENSIZE, GAME_OVER_TEXT, GAME_TITLE, PAUSE_TEXT, PAUSE_TEXT_VERTICAL_OFFSET,
    START_MESSAGE_TEXT, STORY_TEXT, GAME_LEVEL_STORY, GAME_LEVEL_ADDITION_LEVEL,
    GAME_LEVEL_SUBSTRACT_LEVEL, GAME_LEVEL_MULTIPLICATION_LEVEL, GAME_LEVEL_DIVISION_LEVEL,
    GAME_LEVEL_TITLE)
from .maps import Map1, Map2, Map3, Map4
from .sprites import EnemySprite, PlayerSprite, SpaceshipSprite
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


class TitleScreen(Level):
    def __init__(self, game):
        self.game = game
        image = pygame.image.load('assets/backgrounds/game_title.png').convert()
        self.title_image = background = pygame.transform.scale(image, (self.game.screen.get_size()[0], self.game.screen.get_size()[1]))
        #self.title_image = background = aspect_scale(image, (self.game.screen.get_size()[0], self.game.screen.get_size()[1]))
        self.show_start_message = True
        self.font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 24)
        self.title_delay = 1000 / 5  # 5 FPS
        self.title_last_update = 0

    def on_start(self):
        pygame.mixer.music.load('assets/music/OveMelaaTranceBitBit.ogg')
        pygame.mixer.music.play(-1)
        self.game.player_sprite.reset()

    def on_update(self):
        t = pygame.time.get_ticks()
        if t - self.title_last_update > self.title_delay:
            self.show_start_message = not self.show_start_message
            self.title_last_update = t

    def blit(self):
        # Redraw the background
        self.game.screen.blit(self.title_image, (0, 0))

        if self.show_start_message:
            text_size = self.font.size(START_MESSAGE_TEXT)
            label = self.font.render(START_MESSAGE_TEXT, 1, COLOR_WHITE)
            self.game.screen.blit(label, (self.game.screen.get_size()[0] / 2 - text_size[0] / 2, self.game.screen.get_size()[1] - 60))

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                post_event(event=EVENT_CHANGE_LEVEL, mode=GAME_LEVEL_STORY)

    def on_exit(self):
        pygame.mixer.music.stop()


class StoryLevel(Level):
    def __init__(self, game):
        self.game = game
        self.caption_letter = 0

        self.bio_ship_image = pygame.image.load('assets/enemies/bio_ship.png').convert()
        self.bio_ship = SpaceshipSprite(self.game, image=self.bio_ship_image, speed=0.04)
        screen_size = self.game.screen.get_size()
        image = pygame.image.load('assets/backgrounds/earth.png').convert()
        self.title_image = background = pygame.transform.scale(image, (self.game.screen.get_size()[0], self.game.screen.get_size()[1]))

        self.font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 15)
        self.laugh_sound = pygame.mixer.Sound('assets/sounds/evil-laughter-witch.ogg')

    def on_start(self):
        pygame.mixer.music.load('assets/music/LongDarkLoop.ogg')
        pygame.mixer.music.play(-1)
        pygame.time.set_timer(EVENT_STORY_SCRIPT_CAPTION, 2000)

    def on_update(self):
        self.bio_ship.update(self.game.time_passed)

    def blit(self):
        self.game.screen.blit(self.title_image, (0, 0))

        text_size = self.font.size(STORY_TEXT[0: self.caption_letter])
        label = self.font.render(STORY_TEXT[0: self.caption_letter], 1, COLOR_WHITE)
        self.game.screen.blit(label, (self.game.screen.get_size()[0] / 2 - text_size[0] / 2, self.game.screen.get_size()[1] - 60))

        self.bio_ship.blit()

    def type_caption_letter(self):
        self.caption_letter += 1
        if self.caption_letter > len(STORY_TEXT):
            pygame.time.set_timer(EVENT_STORY_SCRIPT_TYPE, 0)
            pygame.time.set_timer(EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP, 2000)

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            pygame.time.set_timer(EVENT_STORY_SCRIPT_TYPE, 0)
            post_event(event=EVENT_CHANGE_LEVEL, mode=GAME_LEVEL_ADDITION_LEVEL)
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
            post_event(event=EVENT_CHANGE_LEVEL, mode=GAME_LEVEL_ADDITION_LEVEL)


class PlayLevel(Level):
    MODE_STOPPED = 0
    MODE_RUNNING = 1
    MODE_CLEAR = 2
    MODE_GAME_OVER = 3

    def __init__(self, game):
        self.game = game
        self.is_game_over = False
        self.game_over_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 32)
        self.result = []
        self.stage_score_value = 0
        self.mode = self.MODE_STOPPED

    def on_start(self):
        pygame.mixer.music.load('assets/music/Zander Noriega - Darker Waves_0_looping.wav')
        pygame.mixer.music.play(-1)
        self.accept_input = True
        self.is_game_over = False

        self.enemies = []
        screen_size = self.game.screen.get_size()
        for i in range(self.enemy_count):
            origin_point = (randint(0, screen_size[0]), randint(0, screen_size[1]))
            question, answer = self.question_function()
            self.enemies.append(EnemySprite(self.game, self.game.enemy_font, question, answer, origin_point, self.enemy_speed, self.enemy_images, self.enemy_fps, self.enemy_score_value, self.enemy_attack_points))

        self.game.can_be_paused = True
        self.mode = self.MODE_RUNNING

    def on_event(self, event):
        if event.type == pygame.KEYDOWN and self.is_game_over:
            post_event(event=EVENT_CHANGE_LEVEL, mode=GAME_LEVEL_TITLE)
        elif event.type == EVENT_GAME_OVER:
            self.game_over()
        else:
            result = check_event(event)
            #if result:
                #print 'MORONIAN EVENT', result
                #if result['event'] == EVENT_CHANGE_LEVEL:
                    #self._current_level = result['mode']
                    #self.modes[self._current_level].on_start()

        if self.accept_input:
            self.player_sprite.on_event(event)

    def on_update(self):
        # Draw player
        self.player_sprite.update(self.game.time_passed)

        # Update and redraw all creeps
        for enemy in self.enemies:
            enemy.update(self.game.time_passed)
            if pygame.sprite.collide_mask(enemy, self.player_sprite) and enemy.alive:
                self.player_sprite.take_damage(enemy)
                enemy.defeat(self.enemies)

        if EnemySprite.is_all_defeated(self.enemies):
            if self.player_sprite.alive:
                self.player_sprite.score += self.stage_score_value
                post_event(event=EVENT_CHANGE_LEVEL, mode=self.next_level)
            #self.player_sprite.win_scroll()

        if self.player_sprite.death:
            self.stop_game()

    def blit(self):
        # Redraw the background
        self.game.display_tile_map(self.map)

        self.player_sprite.blit()

        # Update and redraw all creeps
        for enemy in self.enemies:
            enemy.blit()

        if self.is_game_over:
            text_size = self.game_over_font.size(GAME_OVER_TEXT)
            label = outlined_text(self.game_over_font, GAME_OVER_TEXT, COLOR_WHITE, COLOR_ALMOST_BLACK)
            self.game.screen.blit(label, (self.game.screen.get_size()[0] / 2 - text_size[0] / 2, self.game.screen.get_size()[1] / 2 - 90))

    def stop_game(self):
        self.accept_input = False
        self.result = []
        pygame.mixer.music.stop()
        for enemy in self.enemies:
            if enemy.alive:
                enemy.defeat(self.enemies)

        pygame.time.set_timer(EVENT_GAME_OVER, 3000)

    def game_over(self):
        self.is_game_over = True
        pygame.time.set_timer(EVENT_GAME_OVER, 0)
        pygame.mixer.music.load('assets/music/lose music 3 - 2.wav')
        pygame.mixer.music.play()


OPERATOR_ADD = 1
OPERATOR_SUB = 2
OPERATOR_MUL = 3
OPERATOR_DIV = 4

def formula_generator(operation, digits_1=1, digits_2=1, range_1=None, range_2=None, even_1=False, even_2=False, big_endian=False):
    if range_1:
        low_limit_1, high_limit_1 = range_1
    else:
        low_limit_1 = 10 ** (digits_1 - 1)
        high_limit_1 = 10 ** digits_1 - 1

    if range_2:
        low_limit_2, high_limit_2 = range_2
    else:
        low_limit_2 = 10 ** (digits_2 - 1)
        high_limit_2 = 10 ** digits_2 - 1

    if operation == OPERATOR_DIV and low_limit_2 == 0:
        # Avoid generating a div by zero
        low_limit_2 = 1

    first_number = randint(low_limit_1, high_limit_1)
    second_number = randint(low_limit_2, high_limit_2)

    if even_1 and first_number % 2 != 0:
        first_number += 1

    if even_2 and second_number % 2 != 0:
        second_number += 1

    if big_endian and second_number > first_number:
        return formula_generator(operation, digits_1, digits_2, range_1, range_2, even_1, even_2, big_endian)

    if operation == OPERATOR_ADD:
        return '%d + %d' % (first_number, second_number), first_number + second_number
    elif operation == OPERATOR_SUB:
        return '%d - %d' % (first_number, second_number), first_number - second_number
    elif operation == OPERATOR_MUL:
        return '%d * %d' % (first_number, second_number), first_number * second_number
    elif operation == OPERATOR_DIV:
        return '%d / %d' % (first_number, second_number), first_number / second_number


class AdditionLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.player_sprite = player
        self.enemy_images = EnemySprite.load_sliced_sprites(32, 32, 'enemies/eye_pod_strip.png')
        self.stage_score_value = 100
        self.question_function = lambda: formula_generator(OPERATOR_ADD, digits_1=1, digits_2=1)
        self.enemy_count = 8
        self.enemy_speed = 0.005
        self.enemy_fps = 8
        self.enemy_score_value = 100
        self.enemy_attack_points = 5
        self.next_level = GAME_LEVEL_SUBSTRACT_LEVEL


class SubstractionLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.player_sprite = player
        self.enemy_images = EnemySprite.load_sliced_sprites(32, 32, 'enemies/redslime_strip.png')
        self.stage_score_value = 150
        self.question_function = lambda: formula_generator(OPERATOR_SUB, digits_1=1, digits_2=1, big_endian=True)
        self.enemy_count = 6
        self.enemy_speed = 0.01
        self.enemy_fps = 10
        self.enemy_score_value = 150
        self.enemy_attack_points = 10
        self.next_level = GAME_LEVEL_MULTIPLICATION_LEVEL


class MultiplicationLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.player_sprite = player
        self.enemy_images = EnemySprite.load_sliced_sprites(32, 32, 'enemies/aracnid_strip.png')
        self.stage_score_value = 200
        self.question_function = lambda: formula_generator(OPERATOR_MUL, digits_1=1, digits_2=1, even_1=True, even_2=True)
        self.enemy_count = 4
        self.enemy_speed = 0.025
        self.enemy_fps = 12
        self.enemy_score_value = 200
        self.enemy_attack_points = 15
        self.next_level = GAME_LEVEL_DIVISION_LEVEL


class DivisionLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map4()
        self.player_sprite = player
        self.enemy_images = EnemySprite.load_sliced_sprites(32, 32, 'enemies/flying_bot_strip.png')
        self.stage_score_value = 200
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(0,2), even_1=True, even_2=True, big_endian=True)
        self.enemy_count = 2
        self.enemy_speed = 0.05
        self.enemy_fps = 14
        self.enemy_score_value = 300
        self.enemy_attack_points = 20
        self.next_level = GAME_LEVEL_TITLE


class IntermissionLevel(Level):
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
