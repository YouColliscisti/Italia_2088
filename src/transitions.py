import pygame
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT

class ScreenTransition:
    def __init__(self, surface):
        self.surface = surface
        self.alpha = 0
        self.fading_out = False
        self.fading_in = False
        self.speed = 12
        self.callback = None

    def start_fade_out(self, callback=None):
        self.fading_out = True
        self.fading_in = False
        self.alpha = 0
        self.callback = callback

    def start_fade_in(self):
        self.fading_in = True
        self.fading_out = False
        self.alpha = 255

    def update(self):
        if self.fading_out:
            self.alpha += self.speed
            if self.alpha >= 255:
                self.alpha = 255
                self.fading_out = False
                if self.callback:
                    self.callback()
                self.start_fade_in()
        elif self.fading_in:
            self.alpha -= self.speed
            if self.alpha <= 0:
                self.alpha = 0
                self.fading_in = False

    def draw(self):
        if self.alpha > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 7, 15, self.alpha))
            self.surface.blit(overlay, (0, 0))

    def is_active(self):
        return