from __future__ import absolute_import

from random import randint

import pygame


class SpritePowerUp(object):
    def __init__(self, game):
        self.game = game
        self.active = False
        self.sound = pygame.mixer.Sound(self.sound_file)
        self.image = pygame.image.load(self.image_file)
        self.effect_active = False
        self._time_initial = 0

    def on_update(self, time_passed):
        if not self.game.running:
            self._time_initial += time_passed

        self.effect()

        if self.game.running:
            if not self.active:
                if self.chance():
                    self._time_initial = pygame.time.get_ticks()
                    self.active = True
                    surface_size = self.game.surface.get_size()
                    self.pos = (randint(0, surface_size[0] - self.image.get_size()[0]), randint(0, surface_size[1] - self.image.get_size()[0]))
                    self.rect = self.image.get_rect()
                    self.size = self.image.get_size()
                    self.rect.topleft = [self.pos[0], self.pos[1]]
            if self.active:
                if pygame.time.get_ticks() > self._time_initial + 6000:
                    self.active = False
                else:
                    if pygame.sprite.collide_mask(self, self.game.player):
                        self.active = False
                        self.sound.play()
                        self.collision()

    def on_blit(self):
        if self.active:
            self.game.surface.blit(self.image, self.pos)

    def effect(self):
        pass


class PowerUpApple(SpritePowerUp):
    chance = lambda self: randint(0, 500) == 0
    image_file = 'assets/powerups/I_C_Apple.png'
    sound_file = 'assets/powerups/15.ogg'

    def collision(self):
        self.game.player.hit_points += 20
        if self.game.player.hit_points > self.game.player.total_hit_points:
            self.game.player.hit_points = self.game.player.total_hit_points


class PowerUpShield(SpritePowerUp):
    chance = lambda self: randint(0, 500) == 0
    image_file = 'assets/powerups/E_Metal04.png'
    sound_file = 'assets/powerups/16.ogg'

    def collision(self):
        self.effect_active = True
        self.game.player.set_invincible(5000)


class PowerUpEnemyFreeze(SpritePowerUp):
    chance = lambda self: randint(0, 500) == 0
    image_file = 'assets/powerups/S_Ice02.png'
    sound_file = 'assets/powerups/75.ogg'

    def collision(self):
        self.effect_active = True
        self._time_initial = pygame.time.get_ticks()
        self.game.player._invincible_initial_time = pygame.time.get_ticks() + 5000
