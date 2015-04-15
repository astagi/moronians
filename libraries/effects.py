import pygame


class BaseEffect(object):
    """
    DisplayText effects base class
    """
    def on_setup(self, action):
        self.action = action


class Blink(BaseEffect):
    def __init__(self, delay=1000, sound_file=None):
        self.delay = delay
        if sound_file:
            self.sound = pygame.mixer.Sound(sound_file)
        else:
            self.sound = None
        self._last_time = 0

    def on_update(self, time_passed):
        if self.action._active:
            if pygame.time.get_ticks() > self._last_time + self.delay:
                self._last_time = pygame.time.get_ticks()
                self.action._visible = not self.action._visible
                if self.action._visible and self.sound:
                    self.sound.play()


class TypeWriter(BaseEffect):
    """
    Display one letter at a time with a delay and an optional sound effect
    """
    def __init__(self, delay, sound_file=None):
        self.delay = delay
        if sound_file:
            self.sound = pygame.mixer.Sound(sound_file)
        else:
            self.sound = None
        self._letter_index = 0
        self._last_letter_time = 0

    def on_setup(self, action):
        super(TypeWriter, self).on_setup(action)
        self.original_string = action.string
        action.string = ''
        self._letter_index = 0
        self._last_letter_time = 0

    def on_update(self, time_passed):
        if self.action._visible:
            if not self._last_letter_time:
                self._last_letter_time = self.action._start_time

            if pygame.time.get_ticks() > self._last_letter_time + self.delay:
                self._last_letter_time = pygame.time.get_ticks()
                self._letter_index += 1
                if self._letter_index > len(self.original_string):
                    self._letter_index = len(self.original_string)
                else:
                    if self.sound:
                        self.sound.play()
                self.action.string = self.original_string[0:self._letter_index]
