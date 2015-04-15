import pygame

from .events import EVENT_CHANGE_STAGE
from .literals import COLOR_WHITE
from .utils import LeftAlign, TopAlign, post_event


class Action(object):
    _visible = False

    def hide(self):
        self._visible = False

    def on_execute(self):
        self._start_time = pygame.time.get_ticks()
        self._active = True

    def on_setup(self, stage):
        self.stage = stage
        self._active = False

    def on_update(self, time_passed):
        pass

    def on_blit(self):
        pass

    def show(self):
        self._visible = True
        self.stage.actors.remove(self)


class DisplayText(Action):
    """
    Show a string at a specific position on a stage
    """
    def __init__(self, string, position, color=COLOR_WHITE, font=None, font_file=None, effect=None, horizontal_align=LeftAlign, size=None, vertical_align=TopAlign):
        super(DisplayText, self).__init__()

        self.color = color
        self.effect = effect
        if font_file:
            self.font = pygame.font.Font(font_file, size)
        else:
            self.font = font
        self.horizontal_align = horizontal_align
        self.position = position
        self.size = size
        self.string = string
        self.vertical_align = vertical_align

    def on_blit(self):
        if self._visible:
            self.stage.game.surface.blit(self.font.render(self.string, False, self.color), self.position)

    def on_update(self, time_passed):
        if self.effect:
            self.effect.on_update(time_passed)

    def on_setup(self, stage):
        super(DisplayText, self).on_setup(stage)
        if not self.font:
            self.font = self.stage.game.font

    def show(self):
        self.position = (
            self.horizontal_align(self, self.position[0]).get_result(),
            self.vertical_align(self, self.position[1]).get_result()
        )

        if self.effect:
            self.effect.on_setup(self)

        self._visible = True


class Background(Action):
    def __init__(self, *args, **kwargs):
        self.fit = kwargs.pop('fit', False)
        self.image_file = kwargs.pop('image_file')
        super(Background, self).__init__()

    def on_setup(self, stage):
        super(Background, self).on_setup(stage)
        self.image = pygame.image.load(self.image_file).convert()

        if self.fit:
            self.image = pygame.transform.scale(self.image, (self.stage.game.surface.get_size()[0], self.stage.game.surface.get_size()[1]))

    def on_blit(self):
        self.stage.game.surface.blit(self.image, (0, 0))

    def on_execute(self):
        if self not in self.stage.actors:
            self.stage.actors.append(self)


class PlaySound(Action):
    def __init__(self, sound_file):
        Action.__init__(self)
        self.sound = pygame.mixer.Sound(sound_file)

    def on_execute(self):
        Action.on_execute(self)
        if self._active:
            self.sound.play()
            self._active = False


class PlayMusic(Action):
    def __init__(self, music_file, loop=False):
        Action.__init__(self)
        self.loop = loop
        self.music_file = music_file

    def on_execute(self):
        super(PlayMusic, self).on_execute()
        Action.on_execute(self)
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.music_file)
        pygame.mixer.music.play(-1 if self.loop else 0)
        self._active = False


class End(Action):
    def __init__(self, stop_music=True):
        Action.__init__(self)
        self.stop_music = stop_music

    def on_execute(self):
        Action.on_execute(self)
        if self._active:
            post_event(event=EVENT_CHANGE_STAGE, stage=self.stage.next_stage)
            self._active = False
            if self.stop_music:
                pygame.mixer.music.stop()


class ActorCommand(Action):
    def __init__(self, actor, command):
        Action.__init__(self)
        self.actor = actor
        self.command = command

    def on_execute(self):
        super(ActorCommand, self).on_execute()
        if self.actor not in self.stage.actors:
            self.stage.actors.append(self.actor)

        self.command(self.actor)
        self.actor.on_execute()

    def on_setup(self, stage):
        super(ActorCommand, self).on_setup(stage)
        self.actor.on_setup(stage)
