from libraries.events import EVENT_CHANGE_LEVEL
from libraries.levels import StoryLevel, TitleScreen, PlayLevel
from libraries.literals import GAME_LEVEL_TITLE, GAME_LEVEL_STORY
from libraries.maps import Map1, Map2, Map3, Map4
from libraries.sprites import (EnemyArachnid, EnemyEyePod, EnemyFlyingBot, EnemyRedSlime,
    PowerUpApple, PowerUpShield, SpriteDarkBoss, SpriteSpaceship)
from libraries.utils import hollow_text, outlined_text, post_event, check_event, Timer

from modules.classes import ModuleBase

from .generators import pair_generator, word_list_spanish_english
from .literals import (GAME_LEVEL_ADDITION_BOSS, GAME_LEVEL_ADDITION_LEVEL,
    GAME_LEVEL_SUBSTRACT_LEVEL, GAME_LEVEL_MULTIPLICATION_LEVEL, GAME_LEVEL_DIVISION_LEVEL,
    OPERATOR_ADD, OPERATOR_SUB, OPERATOR_MUL, OPERATOR_DIV)


class Module(ModuleBase):
    def __init__(self, game):
        self.game = game
        self.modes = {
            GAME_LEVEL_TITLE: TitleScreen(game),
            GAME_LEVEL_STORY: StoryLevel(game),
            GAME_LEVEL_ADDITION_LEVEL: AdditionLevel(game=game, player=game.player),
            GAME_LEVEL_ADDITION_BOSS: AdditionBossLevel(game=game, player=game.player),
            GAME_LEVEL_SUBSTRACT_LEVEL: SubstractionLevel(game=game, player=game.player),
            GAME_LEVEL_MULTIPLICATION_LEVEL: MultiplicationLevel(game=game, player=game.player),
            GAME_LEVEL_DIVISION_LEVEL: DivisionLevel(game=game, player=game.player),
        }


class AdditionLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map1()
        self.player = player
        self.enemy_class = EnemyRedSlime
        self.stage_score_value = 100
        self.question_function = lambda: pair_generator(word_list_spanish_english)
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
        self.question_function = lambda: pair_generator(word_list_spanish_english)
        self.enemy_attack_points = 5
        self.next_level = GAME_LEVEL_SUBSTRACT_LEVEL


class SubstractionLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map2()
        self.player = player
        self.enemy_class = EnemyRedSlime
        self.stage_score_value = 150
        self.question_function = lambda: pair_generator(word_list_spanish_english)
        self.enemy_count = 6
        self.next_level = GAME_LEVEL_MULTIPLICATION_LEVEL


class MultiplicationLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map3()
        self.player = player
        self.enemy_class = EnemyArachnid
        self.stage_score_value = 200
        self.question_function = lambda: pair_generator(word_list_spanish_english)
        self.enemy_count = 4
        self.next_level = GAME_LEVEL_DIVISION_LEVEL


class DivisionLevel(PlayLevel):
    def __init__(self, player, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.map = Map4()
        self.player = player
        self.enemy_class = EnemyFlyingBot
        self.stage_score_value = 250
        self.question_function = lambda: pair_generator(word_list_spanish_english)
        self.enemy_count = 2
        self.next_level = GAME_LEVEL_TITLE
