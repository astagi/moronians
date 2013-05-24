from libraries.events import EVENT_CHANGE_LEVEL
from libraries.literals import GAME_LEVEL_TITLE, GAME_LEVEL_STORY
from libraries.utils import post_event


class ModuleBase(object):
    """
    Teaching module definion base class
    Must override __init__ method
    """
    def on_start(self):
        post_event(event=EVENT_CHANGE_LEVEL, mode=GAME_LEVEL_TITLE)
