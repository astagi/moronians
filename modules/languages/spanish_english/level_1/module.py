from libraries.events import EVENT_CHANGE_LEVEL
from libraries.levels import PlayLevel, TitleScreen
from libraries.literals import GAME_LEVEL_TITLE, GAME_LEVEL_STORY
from libraries.maps import Map1, Map2, Map3, Map4
from libraries.sprites import (EnemyArachnid, EnemyEyePod, EnemyFlyingBot, EnemyRedSlime,
    PowerUpApple, PowerUpShield, SpriteDarkBoss)
from libraries.stages import StoryStage, StagePlanetTravel
from libraries.utils import hollow_text, outlined_text, post_event, check_event, Timer

from modules.classes import ModuleBase

from .generators import pair_generator, word_list_spanish_english
from .literals import (GAME_LEVEL_TRAVEL, GAME_LEVEL_STORY, GAME_LEVEL_TITLE,
    GAME_LEVEL_SPANISH_ENGLISH_LEVEL, GAME_LEVEL_SPANISH_ENGLISH_BOSS,
    TEXT_PLANET_01_NAME)


class Module(ModuleBase):
    def __init__(self, game):
        self.game = game
        self.modes = {
            GAME_LEVEL_TITLE: TitleScreen(game, next_level=GAME_LEVEL_STORY),
            GAME_LEVEL_STORY: StoryStage(game, next_level=GAME_LEVEL_TRAVEL),
            GAME_LEVEL_TRAVEL: StageFirenius(game, next_level=GAME_LEVEL_SPANISH_ENGLISH_LEVEL),
            GAME_LEVEL_SPANISH_ENGLISH_LEVEL: SpanishEnglishLevel(game=game, player=game.player),
            GAME_LEVEL_SPANISH_ENGLISH_BOSS: SpanishEnglishBossLevel(game=game, player=game.player),
        }


class StageFirenius(StagePlanetTravel):
    planet_name = TEXT_PLANET_01_NAME
    background_file = 'assets/backgrounds/planet_1_0.png'


class SpanishEnglishLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.player = player
        self.enemy_class = EnemyRedSlime
        self.stage_score_value = 100
        self.question_function = lambda: pair_generator(word_list_spanish_english)
        self.enemy_count = 8
        self.next_level = GAME_LEVEL_SPANISH_ENGLISH_BOSS


class SpanishEnglishBossLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.boss_level = True
        self.player = player
        self.boss_class = SpriteDarkBoss
        self.stage_score_value = 100
        self.question_function = lambda: pair_generator(word_list_spanish_english)
        self.enemy_attack_points = 5
        self.next_level = GAME_LEVEL_TITLE
