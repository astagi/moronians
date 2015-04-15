from libraries.stages import BossLevel, PlayLevel
from libraries.maps import Map1, Map2, Map3, Map4
from libraries.actors import (
    ActorEnemyArachnid, ActorEnemyEyePod, ActorEnemyFlyingBot,
    ActorEnemyRedSlime, ActorEnemyBossHorizontal
)
from libraries.stages import StoryStage, StageTitle, StagePlanetTravel
from libraries.utils import hollow_text, outlined_text, post_event, check_event

from modules.classes import ModuleBase

from .generators import pair_generator, word_list_spanish_english
from .literals import (GAME_LEVEL_TRAVEL, GAME_LEVEL_STORY, GAME_LEVEL_TITLE,
    GAME_LEVEL_SPANISH_ENGLISH_LEVEL, GAME_LEVEL_SPANISH_ENGLISH_BOSS,
    TEXT_PLANET_01_NAME)


class StageYellonious(StagePlanetTravel):
    planet_name = TEXT_PLANET_01_NAME
    background_file = 'assets/backgrounds/planet_yellow.png'


class SpanishEnglishLevel(PlayLevel):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.enemy_class = ActorEnemyRedSlime
        self.stage_score_value = 100
        self.question_function = lambda: pair_generator(word_list_spanish_english)
        self.enemy_count = 8


class SpanishEnglishBossLevel(BossLevel):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.boss_class = ActorEnemyBossHorizontal
        self.stage_score_value = 100
        self.question_function = lambda: pair_generator(word_list_spanish_english)
        self.enemy_attack_points = 5


class Module(object):
    initial_stage = GAME_LEVEL_TITLE

    stages = {
        GAME_LEVEL_TITLE: StageTitle(next_stage=GAME_LEVEL_STORY),
        GAME_LEVEL_STORY: StoryStage(next_stage=GAME_LEVEL_TRAVEL),
        GAME_LEVEL_TRAVEL: StageYellonious(next_stage=GAME_LEVEL_SPANISH_ENGLISH_LEVEL),
        GAME_LEVEL_SPANISH_ENGLISH_LEVEL: SpanishEnglishLevel(next_stage=GAME_LEVEL_SPANISH_ENGLISH_BOSS),
        GAME_LEVEL_SPANISH_ENGLISH_BOSS: SpanishEnglishBossLevel(next_stage=GAME_LEVEL_TITLE),
    }



