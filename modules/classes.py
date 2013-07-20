from libraries.events import EVENT_CHANGE_LEVEL
from libraries.utils import post_event


class ModuleBase(object):
    """
    Teaching module definion base class
    Must override __init__ method
    """
    def on_start(self):
        post_event(event=EVENT_CHANGE_LEVEL, mode=self.first_game_level)
