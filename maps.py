import pygame
from pygame import *

class Map(object):
    def __init__(self):
        pass


class Map1(Map):
    def __init__(self):
        self.tileset = pygame.image.load('assets/tilesets/TileA4.png')

        p = pygame.Rect(288, 0, 32, 32) #area of source image containing pavement
        g = pygame.Rect(416, 0, 32, 32) #area of source image containing grass
        s = pygame.Rect(288, 160, 32, 32) #area of source image containing sand/dirt
        b = pygame.Rect(288, 320, 32, 32) #area of source image containing bush

        self.grid = [[p,p,p,p,p,p,p,p,p,p,p,p,p,p,p,p],\
                     [p,b,b,b,b,b,p,p,p,p,b,b,b,b,b,p],\
                     [p,b,b,g,g,g,g,p,p,g,g,g,g,b,b,p],\
                     [p,b,g,g,g,g,g,p,p,g,g,g,g,g,b,p],\
                     [p,b,g,g,g,p,p,p,p,p,p,g,g,g,b,p],\
                     [p,b,g,s,g,p,s,s,s,s,p,g,s,g,b,p],\
                     [s,s,s,s,s,s,s,g,g,s,s,s,s,s,s,s],\
                     [s,s,s,s,s,s,s,g,g,s,s,s,s,s,s,s],\
                     [p,b,g,s,g,p,s,s,s,s,p,g,s,g,b,p],\
                     [p,b,g,g,g,p,p,p,p,p,p,g,g,g,b,p],\
                     [p,b,g,g,g,g,g,p,p,g,g,g,g,g,b,p],\
                     [p,b,b,g,g,g,g,p,p,g,g,g,g,b,b,p],\
                     [p,b,b,b,b,b,p,p,p,p,b,b,b,b,b,p],\
                     [p,p,p,p,p,p,p,p,p,p,p,p,p,p,p,p]]


class Map2(Map):
    def __init__(self):
        self.tileset = pygame.image.load('assets/tilesets/TileA4.png')

        p = pygame.Rect(128, 230, 32, 32) #area of source image containing pavement
        g = pygame.Rect(160, 230, 32, 32) #area of source image containing grass
        s = pygame.Rect(128, 416, 32, 32) #area of source image containing sand/dirt
        b = pygame.Rect(288, 320, 32, 32) #area of source image containing bush

        self.grid = [[p,p,p,p,p,p,p,p,p,p,p,p,p,p,p,p],\
                     [p,b,b,b,b,b,p,p,p,p,b,b,b,b,b,p],\
                     [p,b,b,g,g,g,g,p,p,g,g,g,g,b,b,p],\
                     [p,b,g,g,g,g,g,p,p,g,g,g,g,g,b,p],\
                     [p,b,g,g,g,p,p,p,p,p,p,g,g,g,b,p],\
                     [p,b,g,s,g,p,s,s,s,s,p,g,s,g,b,p],\
                     [s,s,s,s,s,s,s,g,g,s,s,s,s,s,s,s],\
                     [s,s,s,s,s,s,s,g,g,s,s,s,s,s,s,s],\
                     [p,b,g,s,g,p,s,s,s,s,p,g,s,g,b,p],\
                     [p,b,g,g,g,p,p,p,p,p,p,g,g,g,b,p],\
                     [p,b,g,g,g,g,g,p,p,g,g,g,g,g,b,p],\
                     [p,b,b,g,g,g,g,p,p,g,g,g,g,b,b,p],\
                     [p,b,b,b,b,b,p,p,p,p,b,b,b,b,b,p],\
                     [p,p,p,p,p,p,p,p,p,p,p,p,p,p,p,p]]


class Map1(Map):
    def __init__(self):
        self.tileset = pygame.image.load('assets/tilesets/TileA4.png')

        p = pygame.Rect(450, 96, 32, 32) #area of source image containing pavement
        g = pygame.Rect(160, 230, 32, 32) #area of source image containing grass
        s = pygame.Rect(128, 416, 32, 32) #area of source image containing sand/dirt
        b = pygame.Rect(288, 320, 32, 32) #area of source image containing bush
        x = pygame.Rect(320, 416, 32, 32) #area of source image containing bush

        self.grid = [[x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x],\
                     [x,b,b,b,b,b,x,x,x,x,b,b,b,b,b,x],\
                     [x,b,b,p,p,p,p,x,x,p,p,p,p,b,b,x],\
                     [x,b,p,p,p,p,p,p,p,p,p,p,p,p,b,x],\
                     [x,b,p,p,p,p,p,p,p,p,p,p,p,p,b,x],\
                     [x,b,p,p,p,p,p,p,p,p,p,p,p,p,b,x],\
                     [x,b,p,p,p,p,p,p,p,p,p,p,p,p,b,x],\
                     [x,b,p,p,p,p,p,p,p,p,p,p,p,p,b,x],\
                     [x,b,p,p,p,p,p,p,p,p,p,p,p,p,b,x],\
                     [x,b,p,p,p,p,p,p,p,p,p,p,p,p,b,x],\
                     [x,b,p,p,p,p,p,p,p,p,p,p,p,p,b,x],\
                     [x,b,b,p,p,p,p,x,x,p,p,p,p,b,b,x],\
                     [x,b,b,b,b,b,x,x,x,x,b,b,b,b,b,x],\
                     [x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x]]
