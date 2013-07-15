# -*- coding: utf-8 -*-
from random import choice


word_list_spanish_english = [
    (u'avión', 'airplane'),
    (u'rojo', 'red'),
    (u'azul', 'blue'),
    (u'ayer', 'yesterday'),
    (u'jugar', 'play'),
    (u'foto', 'photo'),
    (u'padre', 'father'),
    (u'madre', 'mother'),
    (u'hoy', 'today'),
    (u'ahora', 'now'),
    (u'alto', 'tall'),
    (u'corto', 'short'),
    (u'largo', 'long'),
    (u'perro', 'dog'),
    (u'gato', 'cat'),
    (u'carro', 'carr'),
    (u'año', 'year'),
    (u'casa', 'house'),
    (u'aire', 'air'),
    (u'cielo', 'sky'),
    (u'nube', 'cloud'),
    (u'bote', 'boat'),
    (u'mar', 'sea'),
    (u'oceano', 'ocean'),
]


def pair_generator(word_list):
    return choice(word_list)
