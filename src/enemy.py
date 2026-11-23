import math
import random

import pygame

from src.settings import CYAN, PURPLE, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE, YELLOW

class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, pos, velocity=(0, 280), color=RED, target=None, tracking=0.0):
        super().__init__()
        size = 26 if tracking else 22
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        pygame.draw.circle(self.image, (*color, 45), (center, center), center)
        pygame.draw.circle(self.image, color, (center, center), 8 if tracking else 6)
        pygame.draw.circle(self.image, WHITE, (center, center), 3)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.target = target
        self.tracking = tracking
        self.age = 0.0

    def update(self, dt=1 / 60):
        self.age += dt
        if self.tracking and self.target is not None and self.target.alive() and self.age < 4.5:
            speed = self.velocity.length()
            desired = pygame.Vector2(self.target.rect.center) - self.pos
            if desired.length_squared() > 1:
                desired = desired.normalize() * speed
                self.velocity = self.velocity.lerp(desired, min(1.0, self.tracking * dt))
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        if (self.rect.top > SCREEN_HEIGHT + 50 or self.rect.bottom < -80 or self.rect.right < -80
                or self.rect.left > SCREEN_WIDTH + 80 or self.age > 8):
            self.kill()


class BaseEnemy(pygame.sprite.Sprite):
    score_value = 100
    explosion_scale = 1.0

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        return self.health <= 0


class ThemeEnemy(BaseEnemy):
    def __init__(self, pos, level=1, stage=1, character_id=1, lasers_group=None, health_multiplier=1.0):
        super().__init__()
        self.level = level
        self.character_id = character_id
        self.lasers_group = lasers_group
        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        accent = {1: CYAN, 2: YELLOW, 3: (80, 220, 150), 4: (255, 110, 65)}.get(character_id, CYAN)
        pygame.draw.polygon(self.image, (85, 35, 115), [(24, 46), (2, 8), (15, 13), (24, 2), (33, 13), (46, 8)])
        pygame.draw.circle(self.image, accent, (24, 23), 10)
        pygame.draw.circle(self.image, WHITE, (24, 23), 4)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.origin_x = self.pos.x
        self.speed = 72 + level * 7 + stage * 2
        self.health = max(1, round((2 + level // 3) * health_multiplier))
        self.max_health = self.health
        self.age = random.uniform(0, math.tau)
        self.shoot_timer = random.uniform(1.2, 2.8)
        self.score_value = 100 + level * 10

    def update(self, dt=1 / 60):
        self.age += dt
        self.pos.y += self.speed * dt
        self.pos.x = self.origin_x + math.sin(self.age * 2.1) * 34
        self.rect.center = self.pos
        self.shoot_timer -= dt
        if self.level >= 2 and self.shoot_timer <= 0 and self.lasers_group is not None and self.rect.top > 0:
            self.shoot_timer = random.uniform(2.2, 3.4)
            self.lasers_group.add(EnemyLaser(self.rect.midbottom, (0, 260 + self.level * 8)))
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class CruiserEnemy(BaseEnemy):
    explosion_scale = 1.9

    def __init__(self, pos, level=1, stage=1, character_id=1, lasers_group=None, health_multiplier=1.0):
        super().__init__()
        self.level = level
        self.lasers_group = lasers_group
        self.image = pygame.Surface((66, 58), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (45, 75, 115), [(33, 56), (2, 25), (12, 5), (25, 17), (33, 2), (41, 17), (54, 5), (64, 25)])
        pygame.draw.rect(self.image, (100, 125, 155), (19, 19, 28, 25), border_radius=6)
        pygame.draw.circle(self.image, YELLOW, (33, 29), 7)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.speed = 48 + level * 4 + stage
        self.health = max(2, round((5 + level // 2) * health_multiplier))
        self.max_health = self.health
        self.shoot_timer = random.uniform(1.4, 2.5)
        self.score_value = 180 + level * 15

    def update(self, dt=1 / 60):
        self.pos.y += self.speed * dt
        self.rect.center = self.pos
        self.shoot_timer -= dt
        if self.level >= 3 and self.shoot_timer <= 0 and self.lasers_group is not None and self.rect.top > 0:
            self.shoot_timer = random.uniform(2.0, 2.8)
            self.lasers_group.add(EnemyLaser((self.rect.left + 12, self.rect.bottom - 5), (-25, 240)))
            self.lasers_group.add(EnemyLaser((self.rect.right - 12, self.rect.bottom - 5), (25, 240)))
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class BossEnemy(BaseEnemy):
    """Three phases"""

    explosion_scale = 4.8

    def __init__(self, lasers_group, max_health=125, target=None):
        super().__init__()
        self.lasers_group = lasers_group
        self.target = target
        self.name = "OMNIA CORE"
        self.image = pygame.Surface((190, 120), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, -60))
        self.pos = pygame.Vector2(self.rect.center)
        self.max_health = max_health
        self.health = max_health
        self.direction = 1
        self.shoot_timer = 1.0
        self.age = 0.0
        self.phase = 1
        self.enraged = False
        self.attack_index = 0
        self.spiral_angle = 0.0
        self.score_value = 2500
        self._draw_boss()

    def _draw_boss(self):
        self.image.fill((0, 0, 0, 0))
        colors = {1: (130, 45, 180), 2: (225, 95, 45), 3: (225, 35, 85)}
        core_colors = {1: CYAN, 2: YELLOW, 3: RED}
        main = colors[self.phase]
        core = core_colors[self.phase]
        pygame.draw.polygon(self.image, main, [(0, 55), (35, 18), (65, 28), (95, 0), (125, 28), (155, 18), (190, 55), (150, 103), (40, 103)])
        pygame.draw.rect(self.image, (65, 75, 105), (55, 28, 80, 66), border_radius=12)
        if self.phase >= 2:
            for angle in range(0, 360, 45):
                radians = math.radians(angle + self.age * 45)
                start = (95 + math.cos(radians) * 31, 60 + math.sin(radians) * 31)
                end = (95 + math.cos(radians) * 43, 60 + math.sin(radians) * 43)
                pygame.draw.line(self.image, core, start, end, 4 if self.enraged else 2)
        pygame.draw.circle(self.image, core, (95, 60), 26)
        pygame.draw.circle(self.image, WHITE, (95, 60), 11)
        pygame.draw.line(self.image, YELLOW, (22, 60), (52, 60), 3)
        pygame.draw.line(self.image, YELLOW, (138, 60), (168, 60), 3)

    def update(self, dt=1 / 60):
        self.age += dt
        ratio = self.health / self.max_health
        self.phase = 3 if ratio < 0.45 else (2 if ratio < 0.72 else 1)
        self.enraged = self.phase == 3
        if self.pos.y < 125:
            self.pos.y += 75 * dt
        else:
            phase_speed = {1: 105, 2: 145, 3: 195}[self.phase]
            self.pos.x += self.direction * phase_speed * dt
            if self.pos.x < 115 or self.pos.x > SCREEN_WIDTH - 115:
                self.direction *= -1
                self.pos.x = max(115, min(SCREEN_WIDTH - 115, self.pos.x))
        self.rect.center = self.pos
        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and self.pos.y >= 100:
            self.shoot_pattern()
            self.shoot_timer = {1: 1.25, 2: 0.82, 3: 0.43}[self.phase]
        self._draw_boss()

    def _radial_burst(self, count, speed):
        self.spiral_angle += 0.37
        for index in range(count):
            angle = self.spiral_angle + math.tau * index / count
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.lasers_group.add(EnemyLaser(self.rect.center, velocity, PURPLE if self.enraged else YELLOW))

    def _fan(self, count, speed):
        origin = self.rect.midbottom
        spread = 165 if self.enraged else 110
        for index in range(count):
            factor = 0 if count == 1 else index / (count - 1) - 0.5
            self.lasers_group.add(EnemyLaser(origin, (factor * spread * 2, speed), RED if self.enraged else YELLOW))

    def _tracking_wave(self):
        for offset in (-55, 0, 55):
            self.lasers_group.add(EnemyLaser(
                (self.rect.centerx + offset, self.rect.bottom), (offset * 0.5, 215),
                PURPLE, target=self.target, tracking=1.65,
            ))

    def shoot_pattern(self):
        self.attack_index += 1
        if self.phase == 1:
            self._fan(3, 250)
        elif self.phase == 2:
            if self.attack_index % 2:
                self._fan(5, 265)
            else:
                self._radial_burst(9, 215)
        elif self.attack_index % 3 == 0:
            self._tracking_wave()
            self._fan(7, 285)
        else:
            self._radial_burst(14 if self.attack_index % 2 else 18, 245)
