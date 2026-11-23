import random

import pygame

from src.settings import GRAY, ORANGE, SCREEN_HEIGHT, WHITE


class SpaceDebris(pygame.sprite.Sprite):
    """area shockwave"""
    def __init__(self, pos, velocity=None):
        super().__init__()
        self.image = pygame.Surface((38, 38), pygame.SRCALPHA)
        points = [(5, 19), (18, 2), (34, 11), (27, 34), (9, 30)]
        pygame.draw.polygon(self.image, GRAY, points)
        pygame.draw.polygon(self.image, WHITE, points, 1)
        pygame.draw.line(self.image, (65, 75, 95), (12, 12), (27, 27), 3)
        pygame.draw.circle(self.image, ORANGE, (20, 19), 5)
        pygame.draw.circle(self.image, (255, 235, 180), (20, 19), 2)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity or (0, random.uniform(75, 125)))
        self.health = 3
        self.score_value = 35
        self.explosion_radius = 165
        self.explosion_damage = 4
        self.detonated = False

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def update(self, dt=1 / 60):
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        if self.rect.top > SCREEN_HEIGHT + 40 or self.rect.bottom < -100 or self.rect.right < -80 or self.rect.left > 1040:
            self.kill()
