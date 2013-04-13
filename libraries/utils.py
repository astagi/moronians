from __future__ import absolute_import

import pygame

from .events import MORONIAN_CUSTOM_EVENT


def aspect_scale(img,(bx,by)):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio """
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.scale(img, (int(sx), int(sy)))


def hollow_text(font, message, fontcolor):
    notcolor = [c^0xFF for c in fontcolor]
    base = font.render(message, 0, fontcolor, notcolor)
    size = base.get_width() + 2, base.get_height() + 2
    img = pygame.Surface(size, 16)
    img.fill(notcolor)
    base.set_colorkey(0)
    img.blit(base, (0, 0))
    img.blit(base, (2, 0))
    img.blit(base, (0, 2))
    img.blit(base, (2, 2))
    base.set_colorkey(0)
    base.set_palette_at(1, notcolor)
    img.blit(base, (1, 1))
    img.set_colorkey(notcolor)
    return img


def outlined_text(font, message, fontcolor, outlinecolor):
    base = font.render(message, 0, fontcolor)
    outline = hollow_text(font, message, outlinecolor)
    img = pygame.Surface(outline.get_size(), 16)
    img.blit(base, (1, 1))
    img.blit(outline, (0, 0))
    img.set_colorkey(0)
    return img


def post_event(event, **kwargs):
    pygame.event.post(pygame.event.Event(MORONIAN_CUSTOM_EVENT, event=event, **kwargs))


def check_event(event):
    if event.type == MORONIAN_CUSTOM_EVENT:
        return event.dict


class Timer(object):
    _registry = []

    @classmethod
    def check_expired(cls):
        for timer in cls._registry:
            if timer.initial + timer.interval > pygame.time.get_ticks():
                cls._registry.remove(timer)
                callback(*args, **kwargs)

    def __init__(self, interval, callback, *arg, **kwargs):
        self.initial = pygame.time.get_ticks()
        self.interval = interval
        self.args = args
        self.kwargs = kwargs

        self.__class__._registry.append(self)
