from __future__ import absolute_import

import os
from random import randint

import pygame

from .literals import COLOR_ALMOST_BLACK, COLOR_WHITE, TEAM_BAD, TEAM_GOOD
from .utils import outlined_text
from .vec2d import vec2d

INTERVAL_INVINCIBLE = 1000


class Actor(object):
    animation_death_file = None
    animation_death_dimensions = (0, 0)
    animation_death_fps = 8
    animation_loop = True
    animation_active = True
    animation_normal_files = []
    animation_normal_dimensions = [(0, 0)]
    attack_points = 1
    total_hit_points = 100
    invincible = False
    fps = 1
    sound_hit = None
    sound_hit_file = None
    sound_die = None
    sound_die_file = None
    speed = 0.05
    team = None

    speed = 0
    scale = 1
    rotation = 0
    flip_x = False
    flip_y = False
    can_overflow = True

    @staticmethod
    def load_sliced_sprites(width, height, filename, origin_y=0):
        images = []
        master_image = pygame.image.load(os.path.join('assets', filename))  # .convert_alpha()

        master_width, master_height = master_image.get_size()
        for i in xrange(int(master_width / width)):
            images.append(master_image.subsurface((i * width, origin_y, width, height)))
        return images

    def __init__(self, game):
        self.game = game
        self._visible = False
        self._strobe = False

    def change_animation(self, images):
        self.images = images
        self._frame = -1
        self._last_update = 0
        self.rect = self.images[0].get_rect()
        self.size = self.images[0].get_size()
        self.image = self.images[0]

    def destroy(self):
        if self in self.stage.actors:
            self.stage.actors.remove(self)

    def hide(self):
        self._visible = False
        self._strobe = False

    def is_alive(self):
        return self.hit_points > 0

    def on_animate(self, time_passed, force=False):
        if self.animation_active or force:
            t = pygame.time.get_ticks()
            if t - self._last_update > self._animation_delay or force:
                self._frame += 1
                if self._frame >= len(self.images):
                    if self.animation_loop:
                        self._frame = 0
                    else:
                        self._frame -= 1

                    self.on_animation_finished()

                self.image = self.images[self._frame]
                self._last_update = t

    def on_animation_finished(self):
        pass

    def on_blit(self):
        if self._visible:
            temp = pygame.transform.rotozoom(self.image, self.rotation, self.scale)
            if self.flip_x or self.flip_y:
                temp = pygame.transform.flip(temp, self.flip_x, self.flip_y)
            self.game.surface.blit(temp, self.pos)

    def on_calculate_movement(self):
        if self.destination:
            if int(self.pos.x) != int(self.destination.x) or int(self.pos.y) != int(self.destination.y):
                self.set_destination(self.destination.x, self.destination.y, self.speed)
            else:
                self.speed = 0

    def on_collision(self, foreign_actor):
        self.on_hit(foreign_actor.attack_points)

    def on_death(self):
        self.hit_points = 0
        self.direction = vec2d(0, 0)

        if self.sound_die:
            self.sound_die.play()

        self.animation_loop = False
        if self.animation_death_fps:
            self.set_animation_fps(self.animation_death_fps)

        if self.animation_death:
            self.change_animation(self.animation_death)

    def on_execute(self):
        pass

    def on_event(self, event):
        pass

    def on_hit(self, attack_points):
        self.hit_points -= attack_points
        if self.sound_hit:
            self.sound_hit.play()

        if self.hit_points <= 0:
            self.hit_points = 0
            self.on_death()

    def on_setup(self, stage):
        self.stage = stage

        self.direction = vec2d(0, 0).normalized()
        self.pos = self.destination = vec2d(0, 0)

        if self.sound_die_file:
            self.sound_die = pygame.mixer.Sound(self.sound_die_file)
        if self.sound_hit_file:
            self.sound_hit = pygame.mixer.Sound(self.sound_hit_file)

        if self.animation_death_file:
            self.animation_death = Actor.load_sliced_sprites(*self.animation_death_dimensions, filename=self.animation_death_file)

        self.animation_normal = []

        for filename, dimensions in zip(self.animation_normal_files, self.animation_normal_dimensions):
            self.animation_normal.append(Actor.load_sliced_sprites(*dimensions, filename=filename))

        self._invincible_initial_time = 0
        self.change_animation(self.animation_normal[0])
        self.hit_points = self.total_hit_points
        self.set_animation_fps(self.fps)

    def on_update(self, time_passed, force=False):
        if self._strobe:
            self._visible = not self._visible

        if self.is_alive():
            self.on_calculate_movement()

        displacement = vec2d(
            self.direction.x * self.speed * time_passed,
            self.direction.y * self.speed * time_passed
        )

        self.pos += displacement

        # TODO: cache this value
        bounds_rect = self.game.surface.get_rect()

        if not self.can_overflow:
            if self.pos.x < bounds_rect.left:
                self.pos.x = bounds_rect.left
            elif self.pos.x + self.size[0] > bounds_rect.right:
                self.pos.x = bounds_rect.right - self.size[0]

            if self.pos.y < bounds_rect.top:
                self.pos.y = bounds_rect.top
            elif self.pos.y + self.size[1] > bounds_rect.bottom:
                self.pos.y = bounds_rect.bottom - self.size[1]

        self.rect.topleft = [self.pos.x, self.pos.y]

        for local_actor in self.stage.actors:
            for foreign_actor in self.stage.actors:
                if not local_actor == foreign_actor and hasattr(foreign_actor, 'rect') and hasattr(local_actor, 'rect'):
                    if pygame.sprite.collide_mask(local_actor, foreign_actor) and local_actor.is_alive() and foreign_actor.is_alive():
                        if local_actor.team != foreign_actor.team:
                            if not local_actor.invincible:
                                local_actor.on_collision(foreign_actor)

                            if not foreign_actor.invincible:
                                foreign_actor.on_collision(local_actor)

        self.on_animate(time_passed, force)

    def set_animation_fps(self, fps):
        self._animation_delay = 1000 / fps

    def set_destination(self, x_position, y_position, speed):
        self.speed = speed
        self.destination = vec2d(x_position, y_position)
        self.direction = (self.destination - vec2d(self.pos)).normalized()

    def set_direction(self, vector):
        self.direction = vector

    def set_flip_x(self, flip):
        self.flip_x = flip

    def set_flip_y(self, flip):
        self.flip_y = flip

    def set_invincible(self, offset):
        self._invincible_initial_time = pygame.time.get_ticks() + offset
        self.invincible = True

    def set_position(self, x_position, y_position):
        self.pos = vec2d(x_position, y_position)

    def set_rotation(self, degrees):
        self.rotation = degrees

    def set_scale(self, scale):
        self.scale = scale

    def show(self):
        self._visible = True
        if self not in self.stage.actors:
            self.stage.actors.append(self)

    def strobe_start(self):
        self._strobe = True

    def strobe_stop(self):
        self._strobe = False
        self._visible = True


class ActorSpaceship(Actor):
    animation_normal_files = ['enemies/bio_ship.png']
    animation_normal_dimensions = [(48, 62)]


class ActorTracktorBeam(Actor):
    animation_normal_files = ['enemies/tractor_beam.png']
    animation_normal_dimensions = [(12, 100)]


class ActorBook01(Actor):
    animation_normal_files = ['players/W_Book01.png']
    animation_normal_dimensions = [(34, 34)]

class ActorBook02(Actor):
    animation_normal_files = ['players/W_Book02.png']
    animation_normal_dimensions = [(34, 34)]


class ActorBook03(Actor):
    animation_normal_files = ['players/W_Book04.png']
    animation_normal_dimensions = [(34, 34)]


class ActorBook04(Actor):
    animation_normal_files = ['players/W_Book05.png']
    animation_normal_dimensions = [(34, 34)]


class ActorBook05(Actor):
    animation_normal_files = ['players/W_Book06.png']
    animation_normal_dimensions = [(34, 34)]


class ActorHumanShip(Actor):
    animation_normal_files = ['players/human_ship.png']
    animation_normal_dimensions = [(60, 48)]


class ActorPlayer(Actor):
    animation_normal_files = ['players/boy_walk_down_stripe.png', 'players/boy_walk_up_stripe.png', 'players/boy_walk_right_stripe.png']
    animation_normal_dimensions = [(34, 34), (34, 34), (34, 34)]
    animation_death_file = 'players/boy_death_stripe.png'
    animation_death_dimensions = (34, 34)
    attack_points = 10
    answer = []
    can_overflow = False
    fps = 8
    hit_score_penalty = 100
    score = 0
    sound_hit_file = 'assets/players/04.ogg'
    sound_die_file = 'assets/players/falldown.wav'
    speed = 0.08
    team = TEAM_GOOD

    def __init__(self, *args, **kwargs):
        super(ActorPlayer, self).__init__(*args, **kwargs)
        self.music_win = 'assets/players/141695__copyc4t__levelup.wav'
        self.scroll = pygame.image.load('assets/players/I_Scroll02.png').convert_alpha()
        self.scroll_speed = 0.008
        self.thought_image = pygame.image.load('assets/players/thought.png').convert_alpha()

    def on_blit(self):
        super(ActorPlayer, self).on_blit()

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

    def on_calculate_movement(self):
        super(ActorPlayer, self).on_calculate_movement()
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

            self.set_direction(vec2d(direction_x, direction_y).normalized())

    def on_collision(self, foreign_actor):
        super(ActorPlayer, self).on_collision(foreign_actor)

        if self.is_alive() and not self.invincible:
            displacement = vec2d(
                foreign_actor.direction.x * 50,
                foreign_actor.direction.y * 50
            )

            self.pos += displacement
            self.rect.topleft = [self.pos.x, self.pos.y]

            self.set_invincible(INTERVAL_INVINCIBLE)
            self.score -= self.hit_score_penalty
            if self.score < 0:
                self.score = 0

    def on_death(self):
        super(ActorPlayer, self).on_death()
        self.answer = []
        self.stage.on_game_over()
        self._time_death = pygame.time.get_ticks()
        self.accept_input = False
        self.set_animation_fps(15)

    def on_event(self, event):
        if event.type == pygame.KEYDOWN and not self.game.paused:
            if event.key == pygame.K_RETURN and self.answer:
                self.game.get_current_stage().player_shot(self, ''.join(self.answer))
                self.answer = []
            elif event.key == pygame.K_BACKSPACE:
                self.answer = self.answer[0: -1]
            elif event.key <= 127 and event.key >= 32:
                self.answer.append(chr(event.key))

            if event.key == pygame.K_DOWN:
                self.change_animation(self.animation_normal[0])
            elif event.key == pygame.K_UP:
                self.change_animation(self.animation_normal[1])
            elif event.key == pygame.K_RIGHT:
                self.set_flip_x(False)
                self.change_animation(self.animation_normal[2])
            elif event.key == pygame.K_LEFT:
                self.set_flip_x(True)
                self.change_animation(self.animation_normal[2])

    def on_setup(self, stage):
        super(ActorPlayer, self).on_setup(stage)
        self.pos = (
            self.game.surface.get_size()[0] / 2 - self.size[0] / 2,
            self.game.surface.get_size()[1] / 2 - self.size[1] / 2
        )
        self._sound_die_played = False
        self.result_font = self.game.font
        self.has_scroll = False

    def on_update(self, time_passed, force=False):
        super(ActorPlayer, self).on_update(time_passed=time_passed)

        if not self.game.running:
            self._invincible_initial_time += time_passed

        if self.is_alive():
            if self.direction:
                self.animation_active = True
            else:
                self.animation_active = False
                self._frame = 0

        if self.has_scroll:
            if not self.scroll_position[1] < self.scroll_original_position[1] - 40:
                displacement = vec2d(
                    self.scroll_direction.x * self.scroll_speed * time_passed,
                    self.scroll_direction.y * self.scroll_speed * time_passed
                )
                self.scroll_position += displacement

        if not self.is_alive():
            if pygame.time.get_ticks() > self._time_death + 1400:
                self.image = pygame.transform.rotozoom(self.animation_normal[0][0], 90, 1)
                if not self._sound_die_played:
                    self.sound_die.play()
                    self._sound_die_played = True

        if self.invincible:
            if pygame.time.get_ticks() > self._invincible_initial_time:
                self.invincible = False

        if self.invincible:
            self.strobe_start()
        else:
            self.strobe_stop()

    def on_win_scroll(self):
        if not self.has_scroll:
            self.has_scroll = True
            pygame.mixer.music.load(self.music_win)
            pygame.mixer.music.play()
            self.scroll_direction = (vec2d(self.pos[0], 0) - vec2d(self.pos)).normalized()
            self.scroll_position = ((self.pos[0] + self.size[0] / 2) - self.scroll.get_size()[0] / 2, self.pos[1] - 80)
            self.scroll_original_position = self.scroll_position
            self._time_win_time = pygame.time.get_ticks()

    def reset_scroll(self):
        self.has_scroll = False


class ActorEnemy(Actor):
    animation_death_file = 'enemies/smoke_puff_strip.png'
    animation_death_dimensions = (32, 32)
    attack_points = 1
    can_overflow = False
    total_hit_points = 1
    sound_die_file = 'assets/sounds/8bit_bomb_explosion.wav'
    team = TEAM_BAD

    def __init__(self, *args, **kwargs):
        self.answer = kwargs.pop('answer', None)
        self.font = kwargs.pop('font', None)
        self.init_position = kwargs.pop('init_position', None)
        self.question = kwargs.pop('question', None)
        self.speed = kwargs.pop('speed', None) or self.speed

        super(ActorEnemy, self).__init__(*args, **kwargs)

    def check_hit(self, answer):
        if answer == self.answer and self.is_alive():
            return True
        else:
            return False

    def on_animation_finished(self):
        # Remove dead actor after their death animation finishes
        if not self.is_alive():
            if self in self.stage.enemies:
                self.stage.enemies.remove(self)
                self.destroy()

    def on_blit(self):
        super(ActorEnemy, self).on_blit()

        if self.is_alive() and self.question:
            # If enemy is alive show it's question
            text_size = self.font.size(self.question)
            label = outlined_text(self.font, self.question, COLOR_WHITE, COLOR_ALMOST_BLACK)

            self.game.surface.blit(label, (self.pos.x + self.size[0] / 2 - text_size[0] / 2, self.pos.y - 11))

    def on_calculate_movement(self):
        # Follow player
        self.set_direction((self.game.player.pos - self.pos).normalized())

    def on_setup(self, stage):
        super(ActorEnemy, self).on_setup(stage)

        if self.init_position:
            self.pos = vec2d(self.init_position)


class ActorEnemyEyePod(ActorEnemy):
    animation_normal_files = ['enemies/eye_pod_strip.png']
    animation_normal_dimensions = [(32, 32)]
    attack_points = 5
    fps = 8
    score_value = 100
    speed = 0.005


class ActorEnemyRedSlime(ActorEnemy):
    animation_normal_files = ['enemies/redslime_strip.png']
    animation_normal_dimensions = [(32, 32)]
    attack_points = 10
    fps = 10
    score_value = 150
    speed = 0.01


class ActorEnemyArachnid(ActorEnemy):
    animation_normal_files = ['enemies/aracnid_strip.png']
    animation_normal_dimensions = [(32, 32)]
    attack_points = 15
    fps = 12
    score_value = 200
    speed = 0.025


class ActorEnemyFlyingBot(ActorEnemy):
    animation_normal_files = ['enemies/flying_bot_strip.png']
    animation_normal_dimensions = [(32, 32)]
    attack_points = 20
    fps = 14
    score_value = 300
    speed = 0.05


class ActorEnemyBoss(ActorEnemy):
    animation_death_fps = 0.01
    enemy_class = ActorEnemyEyePod
    fps = 1
    invincible = True
    sound_die_file = 'assets/enemies/zombie-17.wav'
    sound_hit_file = 'assets/enemies/zombie-5.wav'
    spawned_enemy_speed = ActorEnemyEyePod.speed * 8
    # Calculate initial direction

    def __init__(self, *args, **kwargs):
        super(ActorEnemyBoss, self).__init__(*args, **kwargs)
        self._move_time = 0
        self.original_speed = self.speed

    def on_calculate_movement(self):
        bounds_rect = self.game.surface.get_rect()

        if self.rect.left <= bounds_rect.left:
            self.direction.x *= -1
        elif self.rect.right >= bounds_rect.right:
            self.direction.x *= -1
        elif self.rect.top <= bounds_rect.top:
            self.direction.y *= -1
        elif self.rect.bottom >= bounds_rect.bottom:
            self.direction.y *= -1

    def check_hit(self, answer):
        for enemy in self.stage.enemies:
            # Remove myself from enemy list
            if enemy != self:
                if enemy.check_hit(answer):
                    self.on_hit(attack_points=self.game.player.attack_points)
                    break

    def on_animation_finished(self):
        if self.is_alive():
            self.speed = self.original_speed
            self.change_animation(self.animation_normal[0])
            self.set_animation_fps(self.fps)
            self._move_time = pygame.time.get_ticks()

    def on_death(self):
        super(ActorEnemyBoss, self).on_death()
        self.stage.on_level_complete()

    def on_fire(self):
        self.speed = 0
        self.change_animation(self.animation_shoot)
        self.set_animation_fps(3)

        self._time_fire = pygame.time.get_ticks()
        self.stage.spawn_enemy(self.enemy_class, origin_point=(self.pos[0] + self.image.get_size()[0] / 2, self.pos[1] + self.image.get_size()[1]), speed=self.spawned_enemy_speed)
        self._last_shot = pygame.time.get_ticks()

    def on_hit(self, attack_points):
        super(ActorEnemyBoss, self).on_hit(attack_points)
        self.speed = 0
        self.change_animation(self.animation_hit)
        self.set_animation_fps(3)
        self._last_shot = pygame.time.get_ticks()

    def on_setup(self, stage):
        super(ActorEnemyBoss, self).on_setup(stage)

        self.init_position = (randint(0, self.stage.screen_size[0]), 0)
        self.pos = vec2d(self.init_position)
        self.animation_shoot = Actor.load_sliced_sprites(*self.animation_shoot_dimensions, filename=self.animation_shoot_file)
        self.animation_hit = Actor.load_sliced_sprites(*self.animation_hit_dimensions, filename=self.animation_hit_file)
        self._last_shot = pygame.time.get_ticks()
        self.direction = self.default_direction

    def on_update(self, time_passed, force=False):
        super(ActorEnemyBoss, self).on_update(time_passed=time_passed)

        if self.is_alive():
            if pygame.time.get_ticks() > self._last_shot + self.firing_delay:
                self.on_fire()


class ActorEnemyBossHorizontal(ActorEnemyBoss):
    animation_hit_file = 'enemies/dark_boss_hit.png'
    animation_hit_dimensions = (122, 110)
    animation_normal_files = ['enemies/dark_boss_walk.png']
    animation_normal_dimensions = [(122, 110)]
    animation_shoot_file = 'enemies/dark_boss_shoot.png'
    animation_shoot_dimensions = (122, 110)
    attack_points = 20
    default_direction = vec2d(1, 0)  # Horizontal

    enemy_class = ActorEnemyEyePod
    firing_animation_delay = 150
    firing_delay = 1200
    speed = 0.1
    total_hit_points = 150
    values = 5000



class ActorEnemyBossVertical(ActorEnemyBoss):
    animation_hit_file = 'enemies/boss_genie_hit.png'
    animation_hit_dimensions = (80, 96)
    animation_normal_files = ['enemies/boss_genie_walk.png']
    animation_normal_dimensions = [(80, 96)]
    animation_shoot_file = 'enemies/boss_genie_shoot.png'
    animation_shoot_dimensions = (80, 96)
    attack_points = 20
    default_direction = vec2d(0, 1)  # Down
    enemy_class = ActorEnemyRedSlime
    firing_animation_delay = 150
    firing_delay = 1100
    speed = 0.1
    total_hit_points = 150
    values = 10000


class ActorEnemyBossBounce(ActorEnemyBoss):
    animation_hit_file = 'enemies/boss_phantom_hit.png'
    animation_hit_dimensions = (100, 100)
    animation_normal_files = ['enemies/boss_phantom_walk.png']
    animation_normal_dimensions = [(100, 100)]
    animation_shoot_file = 'enemies/boss_phantom_shoot.png'
    animation_shoot_dimensions = (100, 100)

    default_direction = vec2d(1, 1)  # Down

    enemy_class = ActorEnemyArachnid
    firing_animation_delay = 150
    firing_delay = 1000
    values = 20000
    attack_points = 20
    speed = 0.1
    total_hit_points = 150
