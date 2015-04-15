import pygame
from pygame import *

from .literals import MAP_TILE_SET


class Map(object):
    def __init__(self):
        pass

    def blit(self, surface):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                location = (x * 32, y * 32)
                surface.blit(self.tileset, location, self.grid[y][x])


class Map1(Map):
    def __init__(self):
        self.tileset = pygame.image.load(MAP_TILE_SET)

        i = pygame.Rect(321, 353, 32, 32)  # area of source image containing bush
        q = pygame.Rect(320, 384, 32, 32)  # area of source image containing bush
        x = pygame.Rect(320, 416, 32, 32)  # area of source image containing bush
        p = pygame.Rect(448, 352, 32, 32)  # Purple vines
        o = pygame.Rect(448, 416, 32, 32)  # Falling purple vines

        self.grid = [[i, i, i, i, i, i, i, i, i, i, i, i, i, i, i, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [i, p, p, p, p, p, p, p, p, p, p, p, p, p, p, i],
                     [q, p, p, p, p, p, p, p, p, p, p, p, p, p, p, q],
                     [x, o, o, o, o, o, o, o, o, o, o, o, o, o, o, x]]


class Map2(Map):
    def __init__(self):
        self.tileset = pygame.image.load(MAP_TILE_SET)

        p = pygame.Rect(128, 230, 32, 32)  # area of source image containing pavement
        g = pygame.Rect(160, 230, 32, 32)  # area of source image containing grass
        s = pygame.Rect(128, 416, 32, 32)  # area of source image containing sand/dirt
        b = pygame.Rect(128, 384, 32, 32)  # area of source image containing bush

        self.grid = [[p, p, p, p, p, p, p, p, p, p, p, p, p, p, p, p],
                     [p, b, b, b, b, b, p, p, p, p, b, b, b, b, b, p],
                     [p, b, b, g, g, g, g, p, p, g, g, g, g, b, b, p],
                     [p, b, g, g, g, g, g, p, p, g, g, g, g, g, b, p],
                     [p, b, g, g, g, p, p, p, p, p, p, g, g, g, b, p],
                     [p, b, g, s, g, p, s, s, s, s, p, g, s, g, b, p],
                     [s, s, s, s, s, s, s, g, g, s, s, s, s, s, s, s],
                     [s, s, s, s, s, s, s, g, g, s, s, s, s, s, s, s],
                     [p, b, g, s, g, p, s, s, s, s, p, g, s, g, b, p],
                     [p, b, g, g, g, p, p, p, p, p, p, g, g, g, b, p],
                     [p, b, g, g, g, g, g, p, p, g, g, g, g, g, b, p],
                     [p, b, b, g, g, g, g, p, p, g, g, g, g, b, b, p],
                     [p, b, b, b, b, b, p, p, p, p, b, b, b, b, b, p],
                     [p, p, p, p, p, p, p, p, p, p, p, p, p, p, p, p]]


class Map3(Map):
    def __init__(self):
        self.tileset = pygame.image.load(MAP_TILE_SET)

        p = pygame.Rect(450, 96, 32, 32)  # area of source image containing pavement
        b = pygame.Rect(288, 320, 32, 32)  # area of source image containing bush
        x = pygame.Rect(384, 32, 32, 32)  # area of source image containing bush

        self.grid = [[x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x],
                     [x, b, b, b, b, b, x, x, x, x, b, b, b, b, b, x],
                     [x, b, b, p, p, p, p, x, x, p, p, p, p, b, b, x],
                     [x, b, p, p, p, p, p, p, p, p, p, p, p, p, b, x],
                     [x, b, p, p, p, p, p, p, p, p, p, p, p, p, b, x],
                     [x, b, p, p, p, p, p, p, p, p, p, p, p, p, b, x],
                     [x, b, p, p, p, p, p, p, p, p, p, p, p, p, b, x],
                     [x, b, p, p, p, p, p, p, p, p, p, p, p, p, b, x],
                     [x, b, p, p, p, p, p, p, p, p, p, p, p, p, b, x],
                     [x, b, p, p, p, p, p, p, p, p, p, p, p, p, b, x],
                     [x, b, p, p, p, p, p, p, p, p, p, p, p, p, b, x],
                     [x, b, b, p, p, p, p, x, x, p, p, p, p, b, b, x],
                     [x, b, b, b, b, b, x, x, x, x, b, b, b, b, b, x],
                     [x, x, x, x, x, x, x, x, x, x, x, x, x, x, x, x]]


class Map4(Map):
    def __init__(self):
        self.tileset = pygame.image.load(MAP_TILE_SET)

        p = pygame.Rect(288, 0, 32, 32)  # area of source image containing pavement
        g = pygame.Rect(416, 0, 32, 32)  # area of source image containing grass
        s = pygame.Rect(288, 160, 32, 32)  # area of source image containing sand/dirt
        b = pygame.Rect(288, 320, 32, 32)  # area of source image containing bush

        self.grid = [[p, p, p, p, p, p, p, p, p, p, p, p, p, p, p, p],
                     [p, b, b, b, b, b, p, p, p, p, b, b, b, b, b, p],
                     [p, b, b, g, g, g, g, p, p, g, g, g, g, b, b, p],
                     [p, b, g, g, g, g, g, p, p, g, g, g, g, g, b, p],
                     [p, b, g, g, g, p, p, p, p, p, p, g, g, g, b, p],
                     [p, b, g, s, g, p, s, s, s, s, p, g, s, g, b, p],
                     [s, s, s, s, s, s, s, g, g, s, s, s, s, s, s, s],
                     [s, s, s, s, s, s, s, g, g, s, s, s, s, s, s, s],
                     [p, b, g, s, g, p, s, s, s, s, p, g, s, g, b, p],
                     [p, b, g, g, g, p, p, p, p, p, p, g, g, g, b, p],
                     [p, b, g, g, g, g, g, p, p, g, g, g, g, g, b, p],
                     [p, b, b, g, g, g, g, p, p, g, g, g, g, b, b, p],
                     [p, b, b, b, b, b, p, p, p, p, b, b, b, b, b, p],
                     [p, p, p, p, p, p, p, p, p, p, p, p, p, p, p, p]]
