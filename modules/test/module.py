from libraries.actors import (
    ActorEnemyArachnid, ActorEnemyEyePod, ActorEnemyFlyingBot,
    ActorEnemyRedSlime, ActorEnemyBossHorizontal
)
from libraries.maps import Map1, Map2, Map3, Map4
from libraries.stages import BossLevel, PlayLevel, StageEnd, StagePlanetTravel, StageTitle, StoryStage
from libraries.utils import hollow_text, outlined_text, post_event, check_event

from modules.classes import ModuleBase

from modules.math.level_1.generators import formula_generator
from modules.math.level_1.literals import OPERATOR_ADD, OPERATOR_SUB, OPERATOR_MUL, OPERATOR_DIV

GAME_LEVEL_TITLE = 5
GAME_LEVEL_STORY = 2
GAME_LEVEL_TRAVEL = 3
GAME_LEVEL_1 = 201
GAME_LEVEL_BOSS = 202
GAME_LEVEL_END = 300


class StageBluePlanet(StagePlanetTravel):
    planet_name = 'BLUE PLANET'
    background_file = 'assets/backgrounds/planet_blue.png'


class LevelAddition1(PlayLevel):
    def __init__(self, *args, **kwargs):
        super(LevelAddition1, self).__init__(*args, **kwargs)
        self.map = Map1()
        self.enemy_class = ActorEnemyEyePod
        self.stage_score_value = 100
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 6), range_2=(0, 6))
        self.enemy_count = 5


class ActorEnemyBossHorizontalCustom(ActorEnemyBossHorizontal):
    total_hit_points = 500


class AdditionBossLevel(BossLevel):
    def __init__(self, *args, **kwargs):
        super(AdditionBossLevel, self).__init__(*args, **kwargs)
        self.map = Map1()
        self.boss_level = True
        self.boss_class = ActorEnemyBossHorizontalCustom
        self.stage_score_value = 400
        self.question_function = lambda: formula_generator(OPERATOR_ADD, range_1=(0, 12), range_2=(0, 6))
        self.enemy_attack_points = 5


class Module(object):
    initial_stage = GAME_LEVEL_TITLE
    stages = {
        GAME_LEVEL_TITLE: StageTitle(next_stage=GAME_LEVEL_STORY),
        GAME_LEVEL_STORY: StoryStage(next_stage=GAME_LEVEL_TRAVEL),
        GAME_LEVEL_TRAVEL: StageBluePlanet(next_stage=GAME_LEVEL_1),
        GAME_LEVEL_1: LevelAddition1(next_stage=GAME_LEVEL_BOSS),
        GAME_LEVEL_BOSS: AdditionBossLevel(next_stage=GAME_LEVEL_END),
        GAME_LEVEL_END: StageEnd(next_stage=GAME_LEVEL_TITLE)
    }



