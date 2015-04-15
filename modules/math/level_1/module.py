from libraries.actors import (
    ActorEnemyArachnid, ActorEnemyEyePod, ActorEnemyFlyingBot,
    ActorEnemyRedSlime, ActorEnemyBossHorizontal, ActorEnemyBossVertical,
    ActorEnemyBossBounce
)

#from libraries.events import EVENT_CHANGE_LEVEL
from libraries.stages import PlayLevel
from libraries.maps import Map1, Map2, Map3, Map4
from libraries.stages import BossLevel, StageEnd, StoryStage, StageTitle, StagePlanetTravel
from libraries.utils import hollow_text, outlined_text, post_event, check_event

from modules.classes import ModuleBase

from .generators import formula_generator
from .literals import GAME_LEVEL_ADDITION_LEVEL1, GAME_LEVEL_ADDITION_LEVEL2, GAME_LEVEL_ADDITION_LEVEL3, GAME_LEVEL_ADDITION_BOSS
from .literals import GAME_LEVEL_SUBSTRACTION_LEVEL1, GAME_LEVEL_SUBSTRACTION_LEVEL2, GAME_LEVEL_SUBSTRACTION_LEVEL3, GAME_LEVEL_SUBSTRACTION_BOSS
from .literals import GAME_LEVEL_MULTIPLICATION_LEVEL1, GAME_LEVEL_MULTIPLICATION_LEVEL2, GAME_LEVEL_MULTIPLICATION_LEVEL3, GAME_LEVEL_MULTIPLICATION_BOSS
from .literals import GAME_LEVEL_DIVISION_LEVEL1, GAME_LEVEL_DIVISION_LEVEL2, GAME_LEVEL_DIVISION_LEVEL3, GAME_LEVEL_DIVISION_BOSS
from .literals import GAME_LEVEL_BLUE_PLANET, TEXT_PLANET_BLUE_NAME
from .literals import GAME_LEVEL_RED_PLANET, TEXT_PLANET_RED_NAME
from .literals import GAME_LEVEL_GREEN_PLANET, TEXT_PLANET_GREEN_NAME
from .literals import GAME_LEVEL_SAND_PLANET, TEXT_PLANET_SAND_NAME
from .literals import OPERATOR_ADD, OPERATOR_SUB, OPERATOR_MUL, OPERATOR_DIV
from .literals import GAME_LEVEL_TITLE, GAME_LEVEL_STORY, GAME_LEVEL_END


class StageBluePlanet(StagePlanetTravel):
    planet_name = TEXT_PLANET_BLUE_NAME
    background_file = 'assets/backgrounds/planet_blue.png'


class StageRedPlanet(StagePlanetTravel):
    planet_name = TEXT_PLANET_RED_NAME
    background_file = 'assets/backgrounds/planet_red.png'


class StageGreenPlanet(StagePlanetTravel):
    planet_name = TEXT_PLANET_GREEN_NAME
    background_file = 'assets/backgrounds/planet_green.png'


class StageSandPlanet(StagePlanetTravel):
    planet_name = TEXT_PLANET_SAND_NAME
    background_file = 'assets/backgrounds/planet_sand.png'


class AdditionLevel1(PlayLevel):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.enemy_class = ActorEnemyEyePod
        self.stage_score_value = 100
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 6), range_2=(0, 6))
        self.enemy_count = 4


class AdditionLevel2(PlayLevel):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.enemy_class = ActorEnemyEyePod
        self.stage_score_value = 200
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 9), range_2=(0, 6))
        self.enemy_count = 8


class AdditionLevel3(PlayLevel):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.enemy_class = ActorEnemyEyePod
        self.stage_score_value = 300
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 9), range_2=(0, 9))
        self.enemy_count = 16


class AdditionBossLevel(BossLevel):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.boss_level = True
        self.boss_class = ActorEnemyBossHorizontal
        self.stage_score_value = 400
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 12), range_2=(0, 6))
        self.enemy_attack_points = 5


class SubstractionLevel1(PlayLevel):
    level_song = 'assets/music/8-Bit Ninja.mp3'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.enemy_class = ActorEnemyRedSlime
        self.stage_score_value = 500
        self.question_function = lambda: formula_generator(OPERATOR_SUB, range_1=(0, 6), range_2=(0, 6), big_endian=True)
        self.enemy_count = 5


class SubstractionLevel2(PlayLevel):
    level_song = 'assets/music/8-Bit Ninja.mp3'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.enemy_class = ActorEnemyRedSlime
        self.stage_score_value = 600
        self.question_function = lambda: formula_generator(OPERATOR_SUB, range_1=(0, 9), range_2=(0, 6), big_endian=True)
        self.enemy_count = 10


class SubstractionLevel3(PlayLevel):
    level_song = 'assets/music/8-Bit Ninja.mp3'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.enemy_class = ActorEnemyRedSlime
        self.stage_score_value = 700
        self.question_function = lambda: formula_generator(OPERATOR_SUB, range_1=(0, 9), range_2=(0, 9), big_endian=True)
        self.enemy_count = 15


class SubstractionBossLevel(BossLevel):
    level_song = 'assets/music/CPU Showdown_1.mp3'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.boss_class = ActorEnemyBossVertical
        self.stage_score_value = 800
        self.question_function = lambda: formula_generator(OPERATOR_SUB, range_1=(0, 15), range_2=(0, 6), big_endian=True)
        self.enemy_attack_points = 5


class MultiplicationLevel1(PlayLevel):
    level_song = 'assets/music/hiphop.mp3'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.enemy_class = ActorEnemyArachnid
        self.stage_score_value = 900
        self.question_function = lambda: formula_generator(OPERATOR_MUL, range_1=(0, 6), range_2=(0, 6))
        self.enemy_count = 6


class MultiplicationLevel2(PlayLevel):
    level_song = 'assets/music/hiphop.mp3'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.enemy_class = ActorEnemyArachnid
        self.stage_score_value = 1000
        self.question_function = lambda: formula_generator(OPERATOR_MUL, range_1=(0, 9), range_2=(0, 6))
        self.enemy_count = 12


class MultiplicationLevel3(PlayLevel):
    level_song = 'assets/music/hiphop.mp3'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.enemy_class = ActorEnemyArachnid
        self.stage_score_value = 1100
        self.question_function = lambda: formula_generator(OPERATOR_MUL, range_1=(0, 9), range_2=(0, 9))
        self.enemy_count = 18


class MultiplicationBossLevel(BossLevel):
    level_song = 'assets/music/FoxSynergy - Resistor v1.0.mp3'

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.boss_class = ActorEnemyBossBounce
        self.stage_score_value = 1200
        self.question_function = lambda: formula_generator(OPERATOR_MUL, digits_1=1, digits_2=1, even_1=True, even_2=True)
        self.enemy_attack_points = 5


class DivisionLevel1(PlayLevel):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map4()
        self.enemy_class = ActorEnemyFlyingBot
        self.stage_score_value = 250
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(1, 2), even_1=True, even_2=True, big_endian=True)
        self.enemy_count = 2


class DivisionLevel2(PlayLevel):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map4()
        self.enemy_class = ActorEnemyFlyingBot
        self.stage_score_value = 250
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(1, 2), even_1=True, even_2=True, big_endian=True)
        self.enemy_count = 2


class DivisionLevel3(PlayLevel):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map4()
        self.enemy_class = ActorEnemyFlyingBot
        self.stage_score_value = 250
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(1, 2), even_1=True, even_2=True, big_endian=True)
        self.enemy_count = 2


class DivisionBossLevel(BossLevel):
    def __init__(self, **kwargs):
        super(DivisionBossLevel, self).__init__(**kwargs)
        self.map = Map1()
        self.boss_class = ActorEnemyBossHorizontal
        self.stage_score_value = 400
        self.question_function = lambda: formula_generator(OPERATOR_DIV, digits_1=1, range_2=(1, 2), even_1=True, even_2=True, big_endian=True)
        self.enemy_attack_points = 5


class Module(object):
    initial_stage = GAME_LEVEL_TITLE

    stages = {
        GAME_LEVEL_TITLE: StageTitle(next_stage=GAME_LEVEL_STORY),
        GAME_LEVEL_STORY: StoryStage(next_stage=GAME_LEVEL_BLUE_PLANET),
        GAME_LEVEL_BLUE_PLANET: StageBluePlanet(next_stage=GAME_LEVEL_ADDITION_LEVEL1),
        GAME_LEVEL_ADDITION_LEVEL1: AdditionLevel1(next_stage=GAME_LEVEL_ADDITION_LEVEL2),
        GAME_LEVEL_ADDITION_LEVEL2: AdditionLevel2(next_stage=GAME_LEVEL_ADDITION_LEVEL3),
        GAME_LEVEL_ADDITION_LEVEL3: AdditionLevel3(next_stage=GAME_LEVEL_ADDITION_BOSS),
        GAME_LEVEL_ADDITION_BOSS: AdditionBossLevel(next_stage=GAME_LEVEL_RED_PLANET),

        GAME_LEVEL_RED_PLANET: StageRedPlanet(next_stage=GAME_LEVEL_SUBSTRACTION_LEVEL1),
        GAME_LEVEL_SUBSTRACTION_LEVEL1: SubstractionLevel1(next_stage=GAME_LEVEL_SUBSTRACTION_LEVEL2),
        GAME_LEVEL_SUBSTRACTION_LEVEL2: SubstractionLevel2(next_stage=GAME_LEVEL_SUBSTRACTION_LEVEL3),
        GAME_LEVEL_SUBSTRACTION_LEVEL3: SubstractionLevel3(next_stage=GAME_LEVEL_SUBSTRACTION_BOSS),
        GAME_LEVEL_SUBSTRACTION_BOSS: SubstractionBossLevel(next_stage=GAME_LEVEL_GREEN_PLANET),

        GAME_LEVEL_GREEN_PLANET: StageGreenPlanet(next_stage=GAME_LEVEL_MULTIPLICATION_LEVEL1),
        GAME_LEVEL_MULTIPLICATION_LEVEL1: MultiplicationLevel1(next_stage=GAME_LEVEL_MULTIPLICATION_LEVEL2),
        GAME_LEVEL_MULTIPLICATION_LEVEL2: MultiplicationLevel2(next_stage=GAME_LEVEL_MULTIPLICATION_LEVEL3),
        GAME_LEVEL_MULTIPLICATION_LEVEL3: MultiplicationLevel3(next_stage=GAME_LEVEL_MULTIPLICATION_BOSS),
        GAME_LEVEL_MULTIPLICATION_BOSS: MultiplicationBossLevel(next_stage=GAME_LEVEL_END),

        GAME_LEVEL_SAND_PLANET: StageSandPlanet(next_stage=GAME_LEVEL_DIVISION_LEVEL1),
        GAME_LEVEL_DIVISION_LEVEL1: DivisionLevel1(next_stage=GAME_LEVEL_DIVISION_LEVEL2),
        GAME_LEVEL_DIVISION_LEVEL2: DivisionLevel2(next_stage=GAME_LEVEL_DIVISION_LEVEL3),
        GAME_LEVEL_DIVISION_LEVEL3: DivisionLevel3(next_stage=GAME_LEVEL_DIVISION_BOSS),
        GAME_LEVEL_DIVISION_BOSS: DivisionBossLevel(next_stage=GAME_LEVEL_TITLE),

        GAME_LEVEL_END: StageEnd(next_stage=GAME_LEVEL_TITLE)
    }


