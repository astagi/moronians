import os

import pygame

from literals import SEX_MALE
from vec2d import vec2d


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, game, sex=SEX_MALE):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.result_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 12)
        self.thought_image = pygame.image.load('assets/players/thought.png').convert_alpha()
        self.scroll = pygame.image.load('assets/players/I_Scroll02.png').convert_alpha()
        self.has_won = False
        self.win_sound = pygame.mixer.Sound('assets/players/141695__copyc4t__levelup.wav')
        self.scroll_speed = 0.008

        if sex == SEX_MALE:
            self.image = pygame.image.load('assets/players/boy.png').convert_alpha()
        else:
            self.image = pygame.image.load('assets/players/girl.png').convert_alpha()

        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.pos = (
            self.game.screen.get_size()[0] / 2 - self.size[0] / 2,
            self.game.screen.get_size()[1] / 2 - self.size[1] / 2
        )

    def update(self, time_passed):
        if self.has_won:
            if not self.scroll_position[1] < self.pos[1] - 40:
                displacement = vec2d(
                    self.scroll_direction.x * self.scroll_speed * time_passed,
                    self.scroll_direction.y * self.scroll_speed * time_passed
                )
                self.scroll_position += displacement
            else:
                if self.win_time + 8000 < pygame.time.get_ticks():
                    raise LevelComplete

    def blit(self):
        self.game.screen.blit(self.image, self.pos)
        if self.has_won:
            self.game.screen.blit(self.scroll, self.scroll_position)

    def result(self, result):
        if len(result) != 0:
            thought_size = self.thought_image.get_size()
            self.game.screen.blit(self.thought_image, (self.pos[0] + thought_size[1] / 2, self.pos[1] - 20))

            text_size = self.result_font.size(result)
            label = textOutline(self.result_font, result, COLOR_WHITE, COLOR_ALMOST_BLACK)
            self.game.screen.blit(label, (self.pos[0] + self.size[0] / 2 - text_size[0] / 2, self.pos[1] - 30))

    def win(self):
        if not self.has_won:
            pygame.mixer.music.stop()
            self.has_won = True
            self.win_sound.play()
            self.scroll_direction = (vec2d(self.pos[0], 0) - vec2d(self.pos)).normalized()
            self.scroll_position = self.pos
            self.win_time = pygame.time.get_ticks()
            self.game.can_be_paused = False


class EnemySprite(pygame.sprite.Sprite):
    @staticmethod
    def load_sliced_sprites(w, h, filename):
        images = []
        master_image = pygame.image.load(os.path.join('assets', filename)).convert_alpha()

        master_width, master_height = master_image.get_size()
        for i in xrange(int(master_width / w)):
            images.append(master_image.subsurface((i * w, 0, w , h)))
        return images

    @staticmethod
    def is_all_defeated(enemies):
        return enemies == []

    @staticmethod
    def player_shot(value, enemies):
        for enemy in enemies:
            if enemy.result == value:
                enemy.defeat(enemies)

    def __init__(self, game, font, text, init_position, speed, images, fps):
        pygame.sprite.Sprite.__init__(self)
        self._images = images
        self.speed = speed
        self._start = pygame.time.get_ticks()
        self._delay = 1000 / fps
        self._last_update = 0
        self._frame = 0
        self.font = font
        self.text = text
        self.result = eval(text)
        self.rect = self._images[0].get_rect()
        self.size = self._images[0].get_size()
        self.game = game
        self.alive = True
        self.loop = True

        self.pos = vec2d(init_position)
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

        # Calculate direction to the center of the screen
        self.direction = (vec2d(self.game.screen.get_size()[0] / 2,self.game.screen.get_size()[1] / 2) - vec2d(init_position)).normalized()

        # Call update to set our first image.
        self.update(pygame.time.get_ticks(), force=True)

    def update(self, time_passed, force=False):
        if not self.game.paused:
            t = pygame.time.get_ticks()
            if t - self._last_update > self._delay or force:
                self._frame += 1
                if self._frame >= len(self._images):
                    if self.loop:
                        self._frame = 0
                    else:
                        self._frame -= 1
                        self.enemies.remove(self)

                self.image = self._images[self._frame]
                self._last_update = t

            if self.alive:
                displacement = vec2d(
                    self.direction.x * self.speed * time_passed,
                    self.direction.y * self.speed * time_passed
                )

                self.pos += displacement

    def blitme(self):
        self.game.screen.blit(self.image, (self.pos.x, self.pos.y))
        if self.alive:
            # If enemy is alive show it's formula
            text_size = self.font.size(self.text)
            label = textOutline(self.font, self.text, COLOR_WHITE, COLOR_ALMOST_BLACK)

            self.game.screen.blit(label, (self.pos.x + self.size[0] / 2 - text_size[0] / 2, self.pos.y - 11))

    def defeat(self, enemies):
        self.alive = False
        self.loop = False
        self.enemies = enemies
        self._images = self.smoke_images
        self.death_sound.play()
