from libraries.events import EVENT_CHANGE_LEVEL
from libraries.levels import PlayLevel
from libraries.literals import GAME_LEVEL_TITLE, GAME_LEVEL_STORY
from libraries.maps import Map1, Map2, Map3, Map4
from libraries.sprites import (EnemyArachnid, EnemyEyePod, EnemyFlyingBot,
    EnemyRedSlime, SpriteDarkBoss)
from libraries.stages import StoryStage, StageTitle, StagePlanetTravel
from libraries.utils import hollow_text, outlined_text, post_event, check_event

from modules.classes import ModuleBase

from .generators import formula_generator
from .literals import GAME_LEVEL_ADDITION_LEVEL1, GAME_LEVEL_ADDITION_LEVEL2, GAME_LEVEL_ADDITION_LEVEL3, GAME_LEVEL_ADDITION_BOSS
from .literals import GAME_LEVEL_SUBSTRACTION_LEVEL1, GAME_LEVEL_SUBSTRACTION_LEVEL2, GAME_LEVEL_SUBSTRACTION_LEVEL3, GAME_LEVEL_SUBSTRACTION_BOSS
from .literals import GAME_LEVEL_MULTIPLICATION_LEVEL1, GAME_LEVEL_MULTIPLICATION_LEVEL2, GAME_LEVEL_MULTIPLICATION_LEVEL3, GAME_LEVEL_MULTIPLICATION_BOSS
from .literals import GAME_LEVEL_DIVISION_LEVEL1, GAME_LEVEL_DIVISION_LEVEL2, GAME_LEVEL_DIVISION_LEVEL3, GAME_LEVEL_DIVISION_BOSS
from .literals import GAME_LEVEL_BLUE_PLANET, TEXT_PLANET_BLUE_NAME
from .literals import GAME_LEVEL_RED_PLANET, TEXT_PLANET_RED_NAME
from .literals import OPERATOR_ADD, OPERATOR_SUB, OPERATOR_MUL, OPERATOR_DIV


class Module(ModuleBase):
    first_game_level = GAME_LEVEL_TITLE

    def __init__(self, game):
        self.game = game
        self.modes = {
            GAME_LEVEL_TITLE: StageTitle(game=game, next_stage=GAME_LEVEL_RED_PLANET),

            #GAME_LEVEL_TITLE: StageTitle(game=game, next_stage=GAME_LEVEL_STORY),

            GAME_LEVEL_STORY: StoryStage(game, next_stage=GAME_LEVEL_BLUE_PLANET),
            GAME_LEVEL_BLUE_PLANET: StageBluePlanet(game, next_stage=GAME_LEVEL_ADDITION_LEVEL1),
            GAME_LEVEL_ADDITION_LEVEL1: AdditionLevel1(game=game, player=game.player, next_level=GAME_LEVEL_ADDITION_LEVEL2),
            GAME_LEVEL_ADDITION_LEVEL2: AdditionLevel2(game=game, player=game.player, next_level=GAME_LEVEL_ADDITION_LEVEL3),
            GAME_LEVEL_ADDITION_LEVEL3: AdditionLevel3(game=game, player=game.player, next_level=GAME_LEVEL_ADDITION_BOSS),
            GAME_LEVEL_ADDITION_BOSS: AdditionBossLevel(game=game, player=game.player, next_level=GAME_LEVEL_RED_PLANET),

            GAME_LEVEL_RED_PLANET: StageRedPlanet(game, next_stage=GAME_LEVEL_SUBSTRACTION_LEVEL1),
            GAME_LEVEL_SUBSTRACTION_LEVEL1: SubstractionLevel1(game=game, player=game.player, next_level=GAME_LEVEL_SUBSTRACTION_LEVEL2),
            GAME_LEVEL_SUBSTRACTION_LEVEL2: SubstractionLevel2(game=game, player=game.player, next_level=GAME_LEVEL_SUBSTRACTION_LEVEL3),
            GAME_LEVEL_SUBSTRACTION_LEVEL3: SubstractionLevel3(game=game, player=game.player, next_level=GAME_LEVEL_SUBSTRACTION_BOSS),
            GAME_LEVEL_SUBSTRACTION_BOSS: SubstractionBossLevel(game=game, player=game.player, next_level=GAME_LEVEL_RED_PLANET),

            GAME_LEVEL_MULTIPLICATION_LEVEL1: MultiplicationLevel1(game=game, player=game.player),
            GAME_LEVEL_MULTIPLICATION_LEVEL2: MultiplicationLevel2(game=game, player=game.player),
            GAME_LEVEL_MULTIPLICATION_LEVEL3: MultiplicationLevel3(game=game, player=game.player),
            GAME_LEVEL_MULTIPLICATION_BOSS: MultiplicationBossLevel(game=game, player=game.player, next_level=GAME_LEVEL_RED_PLANET),

            GAME_LEVEL_DIVISION_LEVEL1: DivisionLevel1(game=game, player=game.player),
            GAME_LEVEL_DIVISION_LEVEL2: DivisionLevel2(game=game, player=game.player),
            GAME_LEVEL_DIVISION_LEVEL3: DivisionLevel3(game=game, player=game.player),
            GAME_LEVEL_DIVISION_BOSS: DivisionBossLevel(game=game, player=game.player, next_level=GAME_LEVEL_RED_PLANET),
        }


class StageBluePlanet(StagePlanetTravel):
    planet_name = TEXT_PLANET_BLUE_NAME
    background_file = 'assets/backgrounds/planet_blue.png'


class StageRedPlanet(StagePlanetTravel):
    planet_name = TEXT_PLANET_RED_NAME
    background_file = 'assets/backgrounds/planet_red.png'


class AdditionLevel1(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.player = player
        self.enemy_class = EnemyEyePod
        self.stage_score_value = 100
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 6), range_2=(0, 6))
        self.enemy_count = 4


class AdditionLevel2(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.player = player
        self.enemy_class = EnemyEyePod
        self.stage_score_value = 200
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 9), range_2=(0, 6))
        self.enemy_count = 8


class AdditionLevel3(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.player = player
        self.enemy_class = EnemyEyePod
        self.stage_score_value = 300
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 9), range_2=(0, 9))
        self.enemy_count = 16


class AdditionBossLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.boss_level = True
        self.player = player
        self.boss_class = SpriteDarkBoss
        self.stage_score_value = 400
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 6), range_2=(0, 6))
        self.enemy_attack_points = 5


class SubstractionLevel1(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.player = player
        self.enemy_class = EnemyRedSlime
        self.stage_score_value = 500
        self.question_function = lambda: formula_generator(OPERATOR_SUB, range_1=(0, 6), range_2=(0, 6), big_endian=True)
        self.enemy_count = 5


class SubstractionLevel2(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.player = player
        self.enemy_class = EnemyRedSlime
        self.stage_score_value = 600
        self.question_function = lambda: formula_generator(OPERATOR_SUB, range_1=(0, 9), range_2=(0, 6), big_endian=True)
        self.enemy_count = 10


class SubstractionLevel3(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.player = player
        self.enemy_class = EnemyRedSlime
        self.stage_score_value = 700
        self.question_function = lambda: formula_generator(OPERATOR_SUB, range_1=(0, 9), range_2=(0, 9), big_endian=True)
        self.enemy_count = 15


class SubstractionBossLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.boss_level = True
        self.player = player
        self.boss_class = SpriteDarkBoss
        self.stage_score_value = 800
        self.question_function = lambda: formula_generator(OPERATOR_SUB, range_1=(0, 6), range_2=(0, 6), big_endian=True)
        self.enemy_attack_points = 5


class MultiplicationLevel1(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.player = player
        self.enemy_class = EnemyArachnid
        self.stage_score_value = 200
        self.question_function = lambda: formula_generator(OPERATOR_MUL, digits_1=1, digits_2=1, even_1=True, even_2=True)
        self.enemy_count = 4


class MultiplicationLevel2(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.player = player
        self.enemy_class = EnemyArachnid
        self.stage_score_value = 200
        self.question_function = lambda: formula_generator(OPERATOR_MUL, digits_1=1, digits_2=1, even_1=True, even_2=True)
        self.enemy_count = 4


class MultiplicationLevel3(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.player = player
        self.enemy_class = EnemyArachnid
        self.stage_score_value = 200
        self.question_function = lambda: formula_generator(OPERATOR_MUL, digits_1=1, digits_2=1, even_1=True, even_2=True)
        self.enemy_count = 4


class MultiplicationBossLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.boss_level = True
        self.player = player
        self.boss_class = SpriteDarkBoss
        self.stage_score_value = 400
        self.question_function = lambda: formula_generator(OPERATOR_MUL, digits_1=1, digits_2=1, even_1=True, even_2=True)
        self.enemy_attack_points = 5


class DivisionLevel1(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map4()
        self.player = player
        self.enemy_class = EnemyFlyingBot
        self.stage_score_value = 250
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(1, 2), even_1=True, even_2=True, big_endian=True)
        self.enemy_count = 2


class DivisionLevel2(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map4()
        self.player = player
        self.enemy_class = EnemyFlyingBot
        self.stage_score_value = 250
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(1, 2), even_1=True, even_2=True, big_endian=True)
        self.enemy_count = 2


class DivisionLevel3(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map4()
        self.player = player
        self.enemy_class = EnemyFlyingBot
        self.stage_score_value = 250
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(1, 2), even_1=True, even_2=True, big_endian=True)
        self.enemy_count = 2


class DivisionBossLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.boss_level = True
        self.player = player
        self.boss_class = SpriteDarkBoss
        self.stage_score_value = 400
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(1, 2), even_1=True, even_2=True, big_endian=True)
        self.enemy_attack_points = 5
