from __future__ import absolute_import

from ast import literal_eval
from random import randint, choice

import pygame

from .events import (EVENT_GAME_OVER, EVENT_JUMP_TO_TITLE, EVENT_STOP_GAME,
    EVENT_STORY_SCRIPT_DELAY_BEFORE_SHIP, EVENT_STORY_SCRIPT_CAPTION,
    EVENT_STORY_SCRIPT_TYPE, EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH,
    EVENT_STORY_SCRIPT_POST_LAUGH_DELAY, EVENT_CHANGE_MODE)
from .literals import (COLOR_ALMOST_BLACK, COLOR_BLACK, COLOR_WHITE,
    DEFAULT_SCREENSIZE, GAME_OVER_TEXT, GAME_TITLE, PAUSE_TEXT, PAUSE_TEXT_VERTICAL_OFFSET,
    START_MESSAGE_TEXT, STORY_TEXT, GAME_MODE_STORY, GAME_MODE_ADDITION_LEVEL)
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

    def on_update(self):
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

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                post_event(event=EVENT_CHANGE_MODE, mode=GAME_MODE_STORY)

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

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            post_event(event=EVENT_CHANGE_MODE, mode=GAME_MODE_ADDITION_LEVEL)
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
            post_event(event=EVENT_CHANGE_MODE, mode=GAME_MODE_ADDITION_LEVEL)


class MathLevel(Level):
    def __init__(self, game):
        self.game = game
        self.is_game_over = False
        self.game_over_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 32)
        self.result = []
        self.stage_score_value = 0

    def on_start(self):
        pygame.mixer.music.load('assets/music/Zander Noriega - Darker Waves_0_looping.wav')
        pygame.mixer.music.play(-1)
        self.accept_input = True
        self.is_game_over = False

        self.enemies = []
        screen_size = self.game.screen.get_size()
        for i in range(self.enemy_count):
            origin_point = (randint(0, screen_size[0]), randint(0, screen_size[1]))
            self.enemies.append(EnemySprite(self.game, self.game.enemy_font, self.formula_function(), origin_point, self.enemy_speed, self.enemy_images, self.enemy_fps, self.enemy_score_value, self.enemy_attack_points))

    def on_event(self, event):
        if event.type == pygame.KEYDOWN and not self.game.paused and self.accept_input:
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
        if event.type == EVENT_STOP_GAME:
            self.stop_game()
        elif event.type == EVENT_GAME_OVER:
            self.game_over()

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
        pygame.time.set_timer(EVENT_JUMP_TO_TITLE, 3000)

    def on_update(self):
        # Redraw the background
        self.game.display_tile_map(self.map)

        # Draw player
        self.player_sprite.update(self.game.time_passed)
        self.player_sprite.blit()

        if self.is_game_over:
            text_size = self.game_over_font.size(GAME_OVER_TEXT)
            label = outlined_text(self.game_over_font, GAME_OVER_TEXT, COLOR_WHITE, COLOR_ALMOST_BLACK)
            self.game.screen.blit(label, (self.game.screen.get_size()[0] / 2 - text_size[0] / 2, self.game.screen.get_size()[1] / 2 - 90))

        # Update and redraw all creeps
        for enemy in self.enemies:
            if pygame.sprite.collide_mask(enemy, self.player_sprite) and enemy.alive:
                self.player_sprite.take_damage(enemy)
                enemy.defeat(self.enemies)
            enemy.update(self.game.time_passed)
            enemy.blitme()

        # Redraw the result box
        self.player_sprite.result(''.join(self.result))

        if EnemySprite.is_all_defeated(self.enemies):
            if self.player_sprite.alive:
                self.player_sprite.score += self.stage_score_value
                raise LevelComplete
            #self.player_sprite.win_scroll()


class AdditionLevel(MathLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.player_sprite = player
        self.enemy_images = EnemySprite.load_sliced_sprites(32, 32, 'enemies/eye_pod_strip.png')
        self.stage_score_value = 100
        self.formula_function = lambda :'%d + %d' % (randint(0, 9), randint(0, 9))
        self.enemy_count = 8
        self.enemy_speed = 0.05#025
        self.enemy_fps = 8
        self.enemy_score_value = 100
        self.enemy_attack_points = 50


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
