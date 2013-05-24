from random import choice


word_list_spanish_english = [
    ('avion', 'airplane'),
    ('rojo', 'red'),
    ('azul', 'blue'),
    ('ayer', 'yesterday'),
    ('jugar', 'play'),
    ('foto', 'photo'),
    ('padre', 'father'),
    ('madre', 'mother'),
    ('abuelo', 'grandfather'),
    ('abuela', 'grandmother'),
]


def pair_generator(word_list):
    return choice(word_list)
