from libraries.events import EVENT_CHANGE_LEVEL
from libraries.levels import StoryLevel, TitleScreen
from libraries.literals import GAME_LEVEL_TITLE, GAME_LEVEL_STORY
from libraries.utils import post_event


class ModuleBase(object):
    def __init__(self, game):
        self.game = game
        self.modes = {
            GAME_LEVEL_TITLE: TitleScreen(game),
            GAME_LEVEL_STORY: StoryLevel(game),
        }

    def on_start(self):
        post_event(event=EVENT_CHANGE_LEVEL, mode=GAME_LEVEL_TITLE)
