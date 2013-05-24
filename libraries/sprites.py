from __future__ import absolute_import

from ast import literal_eval
import os
from random import randint, choice

import pygame

from .events import EVENT_STORY_SCRIPT_DELAY_FOR_LAUGH
from .literals import (COLOR_ALMOST_BLACK, COLOR_BLACK, COLOR_WHITE,
    HEALTH_BAR_TEXT, SCORE_TEXT, SEX_MALE, ENEMY_STATE_ALIVE, ENEMY_STATE_FIRING,
    ENEMY_STATE_HIT, ENEMY_STATE_DEFEATED, PLAYER_STATE_ALIVE, PLAYER_STATE_FIRING,
    PLAYER_STATE_HIT, PLAYER_STATE_INVINCIBLE, PLAYER_STATE_DEFEATED, PLAYER_STATE_DEAD,
    TEXT_BOSS_HIT_POINT)
from .utils import outlined_text
from .vec2d import vec2d

INTERVAL_INVINCIBLE = 1000


class SpriteCustom(pygame.sprite.Sprite):
    @staticmethod
    def load_sliced_sprites(width, height, filename, origin_y=0):
        images = []
        master_image = pygame.image.load(os.path.join('assets', filename))#.convert_alpha()

        master_width, master_height = master_image.get_size()
        for i in xrange(int(master_width / width)):
            images.append(master_image.subsurface((i * width, origin_y, width , height)))
        return images


class SpritePlayer(SpriteCustom):
    def __init__(self, game, sex=SEX_MALE):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.result_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 12)
        self.thought_image = pygame.image.load('assets/players/thought.png').convert_alpha()
        self.scroll = pygame.image.load('assets/players/I_Scroll02.png').convert_alpha()
        self.music_win = 'assets/players/141695__copyc4t__levelup.wav'
        self.scroll_speed = 0.008
        self.total_health = 100
        self.hit_score_penalty = 100
        self.miss_score_penalty = 50
        self.health_bar_image = pygame.image.load('assets/players/healthBar_100x12px_green.png').convert_alpha()
        self.score = 0
        self.die_sound = pygame.mixer.Sound('assets/players/falldown.wav')
        self.sound_hit = pygame.mixer.Sound('assets/players/04.ogg')
        self.sound_misses = pygame.mixer.Sound('assets/players/05.ogg')
        self.sex = sex
        self.speed = 0.08
        self.fps = 8
        self.walk_down_images = SpritePlayer.load_sliced_sprites(34, 34, 'players/boy_walk_down_stripe.png')
        self.walk_up_images = SpritePlayer.load_sliced_sprites(34, 34, 'players/boy_walk_up_stripe.png')
        self.walk_left_images = SpritePlayer.load_sliced_sprites(34, 34, 'players/boy_walk_left_stripe.png')
        self.walk_right_images = SpritePlayer.load_sliced_sprites(34, 34, 'players/boy_walk_right_stripe.png')
        self.visible = True
        self._invincible_initial_time = 0

        self.reset()

        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.pos = (
            self.game.surface.get_size()[0] / 2 - self.size[0] / 2,
            self.game.surface.get_size()[1] / 2 - self.size[1] / 2
        )
        self.rect.topleft = [self.pos[0], self.pos[1]]
        self._images = []

        self._start = pygame.time.get_ticks()
        self._delay = 1000 / self.fps
        self._last_update = 0
        self._frame = 0
        self._state = PLAYER_STATE_ALIVE

        # Call update to set our first image.
        self.update(pygame.time.get_ticks(), force=True)

    def set_image(self):
        self.image = self.walk_down_images[0]
        #if self.sex == SEX_MALE:
        #    self.image = pygame.image.load('assets/players/boy.png').convert_alpha()
        #else:
        #    self.image = pygame.image.load('assets/players/girl.png').convert_alpha()

    def reset(self):
        self._state = PLAYER_STATE_ALIVE
        self.health = self.total_health
        self.score = 0
        self.set_image()
        self.answer = []
        #self.accept_input = True
        self.has_scroll = False

    def reset_position(self):
        self.pos = (
            self.game.surface.get_size()[0] / 2 - self.size[0] / 2,
            self.game.surface.get_size()[1] / 2 - self.size[1] / 2
        )
        self.rect.topleft = [self.pos[0], self.pos[1]]

    def set_direction(self, vector):
        self.direction = vector

    def on_event(self, event):
        if event.type == pygame.KEYDOWN and not self.game.paused:
            if event.key == pygame.K_RETURN and self.answer:
                self.game.get_current_level().player_shot(self, ''.join(self.answer))
                self.answer = []
            elif event.key == pygame.K_BACKSPACE:
                self.answer = self.answer[0: -1]
            elif event.key <= 127 and event.key >= 32:
                self.answer.append(chr(event.key))

            if event.key == pygame.K_DOWN:
                self._images = self.walk_down_images
            elif event.key == pygame.K_UP:
                self._images = self.walk_up_images
            elif event.key == pygame.K_RIGHT:
                self._images = self.walk_right_images
            elif event.key == pygame.K_LEFT:
                self._images = self.walk_left_images

    def update(self, time_passed, force=False):
        if not self.game.running:
            self._invincible_initial_time += time_passed

        if self.game.running and self.is_alive():
            keys_pressed = pygame.key.get_pressed()

            direction_y = 0
            direction_x = 0

            if keys_pressed[pygame.K_LEFT]:
                direction_x = -1

            if keys_pressed[pygame.K_RIGHT]:
                direction_x = 1

            if keys_pressed[pygame.K_UP]:
                direction_y = -1

            if keys_pressed[pygame.K_DOWN]:
                direction_y = 1

            #if not wait(2000).next():
            #    print 'asd'
            #    #self.die_sound.play()

            self.set_direction(vec2d(direction_x, direction_y).normalized())

            if direction_x != 0 or direction_y != 0:
                t = pygame.time.get_ticks()
                if t - self._last_update > self._delay or force:
                    self._frame += 1
                    if self._frame >= len(self._images):
                        self._frame = 0
                    self.image = self._images[self._frame]
                    self._last_update = t
            else:
                self._frame = 0

            displacement = vec2d(
                self.direction.x * self.speed * time_passed,
                self.direction.y * self.speed * time_passed
            )

            self.pos += displacement
            bounds_rect = self.game.surface.get_rect()

            if self.pos.x < bounds_rect.left:
                self.pos.x = bounds_rect.left
            elif self.pos.x + self.size[0] > bounds_rect.right:
                self.pos.x = bounds_rect.right - self.size[0]
            elif self.pos.y < bounds_rect.top:
                self.pos.y = bounds_rect.top
            elif self.pos.y + self.size[1] > bounds_rect.bottom:
                self.pos.y = bounds_rect.bottom - self.size[1]
            self.rect.topleft = [self.pos.x, self.pos.y]

        if self.has_scroll:
            if not self.scroll_position[1] < self.scroll_original_position[1] - 40:
                displacement = vec2d(
                    self.scroll_direction.x * self.scroll_speed * time_passed,
                    self.scroll_direction.y * self.scroll_speed * time_passed
                )
                self.scroll_position += displacement
            #else:
            #    if self.win_time + 8000 < pygame.time.get_ticks():
            #        self.game.can_be_paused = True
            #        self.has_scroll = False
            #        raise LevelComplete

        if self._state == PLAYER_STATE_DEFEATED:
            if pygame.time.get_ticks() > self._time_death + 1000:
                self.accept_input = False
                self.die_sound.play()
                self._state = PLAYER_STATE_DEAD
                self.image = pygame.transform.rotozoom(self.walk_left_images[0], 90, 1)

        if self._state == PLAYER_STATE_INVINCIBLE:
            if pygame.time.get_ticks() > self._invincible_initial_time + INTERVAL_INVINCIBLE:
                self._state = PLAYER_STATE_ALIVE
            else:
                self.visible = not self.visible

        if self._state == PLAYER_STATE_ALIVE:
            self.visible = True

    def blit(self):
        if self.visible:
            self.game.surface.blit(self.image, self.pos)

        # Blit health bar
        text_size = self.result_font.size(HEALTH_BAR_TEXT)
        label = outlined_text(self.result_font, HEALTH_BAR_TEXT, COLOR_WHITE, COLOR_ALMOST_BLACK)
        self.game.surface.blit(label, (1, 1))
        self.game.surface.blit(self.health_bar_image, (text_size[0] + 10, 1), area=pygame.Rect(0, 0, self.health_bar_image.get_size()[0] * self.health / float(self.total_health), self.health_bar_image.get_size()[1]))

        # Blit score
        score_text = '%s %d' % (SCORE_TEXT, self.score)
        text_size = self.result_font.size(score_text)
        label = outlined_text(self.result_font, score_text, COLOR_WHITE, COLOR_ALMOST_BLACK)
        self.game.surface.blit(label, (self.game.surface.get_size()[0] - text_size[0] - 10, 1))

        if self.has_scroll:
            self.game.surface.blit(self.scroll, self.scroll_position)

        # Redraw the result box
        if len(self.answer) != 0:
            answer_string = ''.join(self.answer)
            thought_size = self.thought_image.get_size()
            self.game.surface.blit(self.thought_image, (self.pos[0] + thought_size[1] / 2, self.pos[1] - 20))

            text_size = self.result_font.size(answer_string)
            label = outlined_text(self.result_font, answer_string, COLOR_WHITE, COLOR_ALMOST_BLACK)
            self.game.surface.blit(label, (self.pos[0] + self.size[0] / 2 - text_size[0] / 2, self.pos[1] - 30))

    def on_win_scroll(self):
        if not self.has_scroll:
            self.has_scroll = True
            pygame.mixer.music.load(self.music_win)
            pygame.mixer.music.play()
            self.scroll_direction = (vec2d(self.pos[0], 0) - vec2d(self.pos)).normalized()
            self.scroll_position = ((self.pos[0] + self.size[0] / 2) - self.scroll.get_size()[0] / 2, self.pos[1] - 80)
            self.scroll_original_position = self.scroll_position
            self._time_win_time = pygame.time.get_ticks()

    def take_damage(self, enemy):
        if self._state == PLAYER_STATE_ALIVE:
            displacement = vec2d(
                enemy.direction.x * 50,
                enemy.direction.y * 50
            )

            self.pos += displacement
            self.rect.topleft = [self.pos.x, self.pos.y]

            self.sound_hit.play()
            self._invincible_initial_time = pygame.time.get_ticks()
            self._state = PLAYER_STATE_INVINCIBLE
            self.score -= self.hit_score_penalty
            if self.score < 0:
                self.score = 0
            self.health -= enemy.attack_points
            if self.health <= 0:
                self.health = 0
                self.player_dies()

    def player_dies(self):
        self.alive = False
        self.answer = []
        self.game.get_current_level().on_game_over()
        self._state = PLAYER_STATE_DEFEATED
        self._time_death = pygame.time.get_ticks()

    def player_misses_shot(self):
        self.score -= self.miss_score_penalty
        if self.score < 0:
            self.score = 0
        else:
            self.sound_misses.play()

    def is_alive(self):
        if self._state != PLAYER_STATE_DEAD and self._state != PLAYER_STATE_DEFEATED:
            return True
        else:
            return False


class SpriteEnemy(SpriteCustom):
    def __init__(self, game, font, question, answer, init_position, speed=None):
        pygame.sprite.Sprite.__init__(self)
        self._start = pygame.time.get_ticks()
        self._delay = 1000 / self.fps
        self._last_update = 0
        self._frame = 0
        self.font = font
        self.question = question
        self.answer = answer
        self.rect = self.images[0].get_rect()
        self.size = self.images[0].get_size()
        self.game = game
        self.alive = True
        self.loop = True
        self.state = ENEMY_STATE_ALIVE
        self.pos = vec2d(init_position)
        if speed:
            self.speed = speed
        self.smoke_images = [
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0001.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0002.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0003.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0004.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0005.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0006.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0007.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0008.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0009.32x32.png'),
            pygame.image.load('assets/explosions/smoke_puff/smoke_puff_0010.32x32.png')
        ]

        self.death_sound = pygame.mixer.Sound('assets/sounds/8bit_bomb_explosion.wav')

        # Calculate initial direction
        self.direction = (vec2d(self.game.surface.get_size()[0] / 2,self.game.surface.get_size()[1] / 2) - vec2d(init_position)).normalized()

        # Call update to set our first image.
        self.update(0, force=True)

    def set_direction(self, vector):
        self.direction = vector

    def update(self, time_passed, force=False):
        if not self.game.paused:
            self.set_direction((self.game.player.pos - self.pos).normalized())

            t = pygame.time.get_ticks()
            if t - self._last_update > self._delay or force:
                self._frame += 1
                if self._frame >= len(self.images):
                    if self.loop:
                        self._frame = 0
                    else:
                        self._frame -= 1
                        self.enemies.remove(self)

                self.image = self.images[self._frame]
                self._last_update = t

            if self.alive:
                displacement = vec2d(
                    self.direction.x * self.speed * time_passed,
                    self.direction.y * self.speed * time_passed
                )

                self.pos += displacement
                self.rect.topleft = [self.pos.x, self.pos.y]

            player = self.game.get_current_level().player

            if pygame.sprite.collide_mask(self, player) and self.alive and player.is_alive():
                player.take_damage(self)
                self.defeat(self.game.get_current_level().enemies)

    def blit(self):
        self.game.surface.blit(self.image, (self.pos.x, self.pos.y))
        if self.alive:
            # If enemy is alive show it's question
            text_size = self.font.size(self.question)
            label = outlined_text(self.font, self.question, COLOR_WHITE, COLOR_ALMOST_BLACK)

            self.game.surface.blit(label, (self.pos.x + self.size[0] / 2 - text_size[0] / 2, self.pos.y - 11))

    def defeat(self, enemies):
        if self.alive:
            self.alive = False
            self.loop = False
            self.images = self.smoke_images
            self.death_sound.play()
            self.enemies = enemies

    def check_hit(self, answer):
        if answer == self.answer:
            return True
        else:
            return False

    def is_alive(self):
        if self._state != ENEMY_STATE_DEFEATED:
            return True
        else:
            return False


class EnemyEyePod(SpriteEnemy):
    images = SpriteEnemy.load_sliced_sprites(32, 32, 'enemies/eye_pod_strip.png')
    speed = 0.005
    fps = 8
    score_value = 100
    attack_points = 5


class EnemyRedSlime(SpriteEnemy):
    images = SpriteEnemy.load_sliced_sprites(32, 32, 'enemies/redslime_strip.png')
    speed = 0.01
    fps = 10
    score_value = 150
    attack_points = 10


class EnemyArachnid(SpriteEnemy):
    images = SpriteEnemy.load_sliced_sprites(32, 32, 'enemies/aracnid_strip.png')
    speed = 0.025
    fps = 12
    score_value = 200
    attack_points = 15


class EnemyFlyingBot(SpriteEnemy):
    images = SpriteEnemy.load_sliced_sprites(32, 32, 'enemies/flying_bot_strip.png')
    speed = 0.05
    fps = 14
    score_value = 300
    attack_points = 20


class SpriteBoss(SpriteEnemy):
    def __init__(self, game, font, init_position):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.images[0]
        self.rect = self.images[0].get_rect()
        self.size = self.images[0].get_size()
        self.game = game
        self.alive = True
        self._state = ENEMY_STATE_ALIVE
        self._move_time = 0
        self.hit_point_bar_image = pygame.image.load('assets/enemies/healthBar_100x12px_red.png').convert_alpha()

        self.pos = vec2d(init_position)
        self.sound_death = pygame.mixer.Sound('assets/enemies/zombie-17.wav')
        self.sound_hit = pygame.mixer.Sound('assets/enemies/zombie-5.wav')
        self.death_scream_done = False

        # Calculate initial direction
        self.direction = vec2d(1, 0)  # To the right

        # Call update to set our first image.
        #self.update(pygame.time.get_ticks(), force=True)


    def update(self, time_passed, force=False):
        # Re calculate direction to follow player
        #self.direction = (self.game.player.pos - self.pos).normalized()

        if self._state == ENEMY_STATE_ALIVE:
            if pygame.time.get_ticks() > self._move_time + 1000:
                self._state = ENEMY_STATE_FIRING
                self._time_fire = pygame.time.get_ticks()

        if self._state == ENEMY_STATE_FIRING:
            if pygame.time.get_ticks() > self._time_fire + 200:
                self.image = self.images[0]
                self._state = ENEMY_STATE_ALIVE
                self._move_time = pygame.time.get_ticks()
                self.game.get_current_level().spawn_enemy(EnemyEyePod, origin_point=(self.pos[0] + self.image.get_size()[0] / 2, self.pos[1] + self.image.get_size()[1]), speed=EnemyEyePod.speed * 8)
            else:
                self.image = self.images[1]

        if self._state == ENEMY_STATE_HIT:
            if pygame.time.get_ticks() > self._time_hit + 500:
                self._state = ENEMY_STATE_ALIVE
                self.direction = self.old_direction
                self._move_time = pygame.time.get_ticks()

        if self.alive:
            displacement = vec2d(
                self.direction.x * self.speed * time_passed,
                self.direction.y * self.speed * time_passed
            )

            self.pos += displacement
            self.rect.topleft = [self.pos.x, self.pos.y]
            self.image_w, self.image_h = self.image.get_size()
            bounds_rect = self.game.surface.get_rect().inflate(-self.image_w, -self.image_h)

            if self.pos.x < bounds_rect.left:
                self.pos.x = bounds_rect.left
                self.direction.x *= -1
            elif self.pos.x > bounds_rect.right:
                self.pos.x = bounds_rect.right
                self.direction.x *= -1
            elif self.pos.y < bounds_rect.top:
                self.pos.y = bounds_rect.top
                self.direction.y *= -1
            elif self.pos.y > bounds_rect.bottom:
                self.pos.y = bounds_rect.bottom
                self.direction.y *= -1

            if pygame.sprite.collide_mask(self, self.game.get_current_level().player) and self.alive:
                self.game.get_current_level().player.take_damage(self)

    def blit(self):
        self.game.surface.blit(self.image, (self.pos.x, self.pos.y))
        #if self.alive:
        #    # If enemy is alive show it's question
        #    text_size = self.font.size(self.question)
        #    label = outlined_text(self.font, self.question, COLOR_WHITE, COLOR_ALMOST_BLACK)

        #    self.game.surface.blit(label, (self.pos.x + self.size[0] / 2 - text_size[0] / 2, self.pos.y - 11))

        # Blit health bar
        if self.is_alive():
            HP_BAR_HORIZONTAL_POSITION = 170
            HP_BAR_VERTICAL_POSITION = 40
            text_size = self.game.font.size(TEXT_BOSS_HIT_POINT)
            label = outlined_text(self.game.font, TEXT_BOSS_HIT_POINT, COLOR_WHITE, COLOR_ALMOST_BLACK)
            self.game.surface.blit(label, (HP_BAR_HORIZONTAL_POSITION, HP_BAR_VERTICAL_POSITION))
            self.game.surface.blit(self.hit_point_bar_image, (text_size[0] + HP_BAR_HORIZONTAL_POSITION + 5, HP_BAR_VERTICAL_POSITION), area=pygame.Rect(0, 0, self.hit_point_bar_image.get_size()[0] * self.hit_points / float(self.total_hit_points), self.hit_point_bar_image.get_size()[1]))

    def check_hit(self, answer):
        for enemy in self.game.get_current_level().enemies:
            if enemy.check_hit(answer):
                self.old_direction = self.direction
                self.sound_hit.play()
                self.direction = vec2d(0, 0)
                self._state = ENEMY_STATE_HIT
                self.image = self.images[2]
                self._time_hit = pygame.time.get_ticks()
                self.hit_points -= 10
                if self.hit_points <= 0:
                    self.hit_points = 0
                    self._state = ENEMY_STATE_DEFEATED
                    self.game.get_current_level().on_level_complete()
                    self.direction = vec2d(0, 0)
                    self.game.get_current_level().on_level_complete()
                break;

    def defeat(self, enemies):
        if self.alive:
            self.alive = False
            self.loop = False
            self.enemies = enemies
            self._images = self.smoke_images
            self.death_sound.play()

    def on_fire(self):
        self.state = ENEMY_STATE_FIRING

    def on_explode(self):
        if not self.death_scream_done:
            self.death_scream_done = True
            self.sound_death.play()


class SpriteDarkBoss(SpriteBoss):
    images = SpriteEnemy.load_sliced_sprites(122, 110, 'enemies/dark_boss_strip.png')
    values = 5000
    attack_points = 115
    speed = 0.1
    hit_points = total_hit_points = 50
