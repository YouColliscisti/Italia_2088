import pygame

from src.settings import CYAN, GREEN, SCREEN_HEIGHT, WHITE


class BasePowerUp(pygame.sprite.Sprite):
    color = CYAN
    label = "SHIELD"

    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*self.color, 45), (15, 15), 15)
        pygame.draw.circle(self.image, self.color, (15, 15), 12)
        pygame.draw.circle(self.image, WHITE, (15, 15), 12, width=2)
        self._draw_icon()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.speed = 105

    def _draw_icon(self):
        pass

    def update(self, dt=1 / 60):
        self.pos.y += self.speed * dt
        self.rect.center = self.pos
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def apply_effect(self, player):
        raise NotImplementedError


class HealthPowerUp(BasePowerUp):
    color = GREEN
    label = "+30 HP"

    def _draw_icon(self):
        pygame.draw.rect(self.image, WHITE, (13, 7, 4, 16))
        pygame.draw.rect(self.image, WHITE, (7, 13, 16, 4))

    def apply_effect(self, player):
        return player.heal(30)


class ShieldPowerUp(BasePowerUp):
    color = CYAN
    label = "SHIELD RESTORED"

    def _draw_icon(self):
        pygame.draw.polygon(self.image, WHITE, [(15, 6), (23, 10), (21, 20), (15, 25), (9, 20), (7, 10)], width=2)

    def apply_effect(self, player):
        player.activate_shield(6000)
        return True
