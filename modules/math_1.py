

from ..maps import Map1, Map2, Map3, Map4
from ..sprites import (EnemyArachnid, EnemyEyePod, EnemyFlyingBot, EnemyRedSlime,
    PowerUpApple, PowerUpShield, SpriteDarkBoss, SpriteSpaceship)
GAME_LEVEL_ADDITION_LEVEL,
    GAME_LEVEL_SUBSTRACT_LEVEL, GAME_LEVEL_MULTIPLICATION_LEVEL, GAME_LEVEL_DIVISION_LEVEL,

SubstractionLevel


AdditionLevel, AdditionBossLevel, DivisionLevel, MultiplicationLevel



word_list_spanish_english = [
#    (chr(32), 'airplane'),
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


OPERATOR_ADD = 1
OPERATOR_SUB = 2
OPERATOR_MUL = 3
OPERATOR_DIV = 4


def formula_generator(operation, digits_1=1, digits_2=1, range_1=None, range_2=None, even_1=False, even_2=False, big_endian=False):
    if range_1:
        low_limit_1, high_limit_1 = range_1
    else:
        low_limit_1 = 10 ** (digits_1 - 1)
        high_limit_1 = 10 ** digits_1 - 1

    if range_2:
        low_limit_2, high_limit_2 = range_2
    else:
        low_limit_2 = 10 ** (digits_2 - 1)
        high_limit_2 = 10 ** digits_2 - 1

    if operation == OPERATOR_DIV and low_limit_2 == 0:
        # Avoid generating a div by zero
        low_limit_2 = 1

    first_number = randint(low_limit_1, high_limit_1)
    second_number = randint(low_limit_2, high_limit_2)

    if even_1 and first_number % 2 != 0:
        first_number += 1

    if even_2 and second_number % 2 != 0:
        second_number += 1

    if big_endian and second_number > first_number:
        return formula_generator(operation, digits_1, digits_2, range_1, range_2, even_1, even_2, big_endian)

    if operation == OPERATOR_ADD:
        return '%d + %d' % (first_number, second_number), str(first_number + second_number)
    elif operation == OPERATOR_SUB:
        return '%d - %d' % (first_number, second_number), str(first_number - second_number)
    elif operation == OPERATOR_MUL:
        return '%d * %d' % (first_number, second_number), str(first_number * second_number)
    elif operation == OPERATOR_DIV:
        return '%d / %d' % (first_number, second_number), str(first_number / second_number)


class AdditionLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.player = player
        self.enemy_class = EnemyEyePod
        self.stage_score_value = 100
        self.question_function = lambda: formula_generator(OPERATOR_ADD, digits_1=1, digits_2=1)
        self.enemy_count = 8
        self.next_level = GAME_LEVEL_ADDITION_BOSS


class AdditionBossLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.boss_level = True
        self.player = player
        self.boss_class = SpriteDarkBoss
        self.stage_score_value = 100
        self.question_function = lambda: formula_generator(OPERATOR_ADD, digits_1=1, digits_2=1)
        self.enemy_attack_points = 5
        self.next_level = GAME_LEVEL_SUBSTRACT_LEVEL


class SubstractionLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.player = player
        self.enemy_class = EnemyRedSlime
        self.stage_score_value = 150
        self.question_function = lambda: formula_generator(OPERATOR_SUB, digits_1=1, digits_2=1, big_endian=True)
        self.enemy_count = 6
        self.next_level = GAME_LEVEL_MULTIPLICATION_LEVEL


class MultiplicationLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.player = player
        self.enemy_class = EnemyArachnid
        self.stage_score_value = 200
        self.question_function = lambda: formula_generator(OPERATOR_MUL, digits_1=1, digits_2=1, even_1=True, even_2=True)
        self.enemy_count = 4
        self.next_level = GAME_LEVEL_DIVISION_LEVEL


class DivisionLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map4()
        self.player = player
        self.enemy_class = EnemyFlyingBot
        self.stage_score_value = 250
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(1,2), even_1=True, even_2=True, big_endian=True)
        self.enemy_count = 2
        self.next_level = GAME_LEVEL_TITLE
