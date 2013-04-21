from __future__ import absolute_import

import pygame

from .vec2d import vec2d


class Actor(pygame.sprite.Sprite):
    def __init__(self, stage):
        pygame.sprite.Sprite.__init__(self)
        self._visible = False
        self.image = pygame.image.load(self.image_file).convert_alpha()
        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.stage = stage
        self.pos = self.destination = vec2d(0, 0)
        self.direction = vec2d(0, 0).normalized()
        self.speed = 0
        self._strobe = False

    def set_position(self, x_position, y_position):
        self.pos = vec2d(x_position, y_position)

    def set_destination(self, x_position, y_position, speed):
        self.speed = speed
        self.destination = vec2d(x_position, y_position)
        self.direction = (self.destination - vec2d(self.pos)).normalized()

    def show(self):
        self._visible = True

    def hide(self):
        self._visible = False
        self._strobe = False

    def strobe_start(self):
        self._strobe = True

    def strobe_stop(self):
        self._strobe = False

    def on_blit(self):
        if self._visible:
            self.stage.canvas.blit(self.image, self.pos)

    def on_update(self, time_passed):
        if self._strobe:
            self._visible = not self._visible

        if int(self.pos.x) != int(self.destination.x) or int(self.pos.y) != int(self.destination.y):
            self.set_destination(self.destination.x, self.destination.y, self.speed)
            displacement = vec2d(
                self.direction.x * self.speed * time_passed,
                self.direction.y * self.speed * time_passed
            )
            self.pos += displacement


class ActorSpaceship(Actor):
    image_file = 'assets/enemies/bio_ship.png'


class ActorTracktorBeam(Actor):
    image_file = 'assets/enemies/tractor_beam.png'


class ActorBook01(Actor):
    image_file = 'assets/players/W_Book01.png'


class ActorBook02(Actor):
    image_file = 'assets/players/W_Book02.png'


class ActorBook03(Actor):
    image_file = 'assets/players/W_Book04.png'


class ActorBook04(Actor):
    image_file = 'assets/players/W_Book05.png'


class ActorBook05(Actor):
    image_file = 'assets/players/W_Book06.png'


class ActorHumanShip(Actor):
    image_file = 'assets/players/human_ship.png'
