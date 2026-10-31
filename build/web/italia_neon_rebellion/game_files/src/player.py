import math
import pygame

from src.effects import Particle
from src.laser import Laser
from src.settings import CYAN, GREEN, PLAYER_HEALTH, PLAYER_SPEED, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE, YELLOW


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, lasers_group=None, particles_group=None, character_id=1, sound=None):
        super().__init__()
        self.character_id = character_id
        self.lasers_group = lasers_group
        self.particles_group = particles_group
        self.sound = sound
        self.primary_color = {1: CYAN, 2: YELLOW, 3: GREEN, 4: RED}.get(character_id, CYAN)
        self.base_image = pygame.Surface((58, 58), pygame.SRCALPHA)
        self._draw_ship()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)

        self.max_health = 150 if character_id == 3 else PLAYER_HEALTH
        self.health = self.max_health
        self.max_shield = 45 if character_id == 3 else 0
        self.shield = self.max_shield
        self.shield_recharge_delay = 0.0
        self.temporary_shield_time = 0.0
        self.invulnerable_time = 0.0
        self.shoot_cooldown = {1: 0.17, 2: 0.16, 3: 0.30, 4: 0.32}[character_id]
        self.shoot_timer = 0.0
        self.shot_counter = 0
        self.auto_fire = True
        self.dash_cooldown = 0.0
        self.dash_time = 0.0
        self.dash_direction = pygame.Vector2(0, -1)
        self.trail_timer = 0.0
        self.last_mouse = pygame.Vector2(pygame.mouse.get_pos())
        self.mouse_active = False

    def _draw_ship(self):
        """Distinct silhouettes, not palette swaps."""
        self.base_image.fill((0, 0, 0, 0))
        color = self.primary_color
        if self.character_id == 1:  # Beatrice: long, precise needle interceptor
            pygame.draw.polygon(self.base_image, (*color, 45), [(29, 0), (13, 54), (45, 54)])
            pygame.draw.polygon(self.base_image, color, [(29, 2), (20, 42), (8, 55), (27, 48), (29, 56), (31, 48), (50, 55), (38, 42)])
            pygame.draw.polygon(self.base_image, (235, 255, 255), [(29, 13), (25, 34), (33, 34)])
            pygame.draw.line(self.base_image, YELLOW, (29, 4), (29, 45), 2)
        elif self.character_id == 2:  # Simon: split-wing twin cannon runner
            pygame.draw.polygon(self.base_image, (*color, 45), [(8, 8), (0, 52), (29, 40), (58, 52), (50, 8)])
            pygame.draw.polygon(self.base_image, color, [(10, 5), (3, 47), (23, 35), (20, 12)])
            pygame.draw.polygon(self.base_image, color, [(48, 5), (55, 47), (35, 35), (38, 12)])
            pygame.draw.polygon(self.base_image, (255, 250, 210), [(29, 17), (20, 43), (29, 37), (38, 43)])
            pygame.draw.rect(self.base_image, CYAN, (7, 16, 4, 20), border_radius=2)
            pygame.draw.rect(self.base_image, CYAN, (47, 16, 4, 20), border_radius=2)
        elif self.character_id == 3:  # Sofia: broad armored Aegis platform
            pygame.draw.polygon(self.base_image, (*color, 45), [(29, 0), (0, 23), (7, 55), (51, 55), (58, 23)])
            pygame.draw.polygon(self.base_image, color, [(29, 3), (7, 20), (3, 43), (18, 50), (29, 42), (40, 50), (55, 43), (51, 20)])
            pygame.draw.rect(self.base_image, (205, 255, 230), (19, 15, 20, 22), border_radius=7)
            pygame.draw.arc(self.base_image, CYAN, (8, 4, 42, 47), 0, math.pi, 3)
            pygame.draw.line(self.base_image, WHITE, (9, 34), (49, 34), 2)
        else:  # Elias: heavy asymmetric anarchy disk launcher
            pygame.draw.polygon(self.base_image, (*color, 45), [(27, 0), (0, 43), (17, 57), (52, 51), (58, 19)])
            pygame.draw.polygon(self.base_image, color, [(27, 2), (8, 24), (0, 45), (22, 40), (29, 56), (37, 39), (57, 45), (48, 17)])
            pygame.draw.circle(self.base_image, (50, 20, 35), (30, 27), 13)
            pygame.draw.circle(self.base_image, YELLOW, (30, 27), 9, width=3)
            pygame.draw.polygon(self.base_image, WHITE, [(30, 16), (34, 26), (44, 28), (34, 31), (30, 40), (27, 31), (17, 28), (27, 25)])

    @property
    def ready(self):
        return self.shoot_timer <= 0

    @property
    def dash_ready(self):
        return self.character_id == 2 and self.dash_cooldown <= 0

    def update(self, dt=1 / 60):
        self.shoot_timer = max(0.0, self.shoot_timer - dt)
        self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.invulnerable_time = max(0.0, self.invulnerable_time - dt)
        self.shield_recharge_delay = max(0.0, self.shield_recharge_delay - dt)
        if self.temporary_shield_time > 0:
            self.temporary_shield_time -= dt
            if self.temporary_shield_time <= 0 and self.character_id != 3:
                self.shield = 0
                self.max_shield = 0
        if self.character_id == 3 and self.shield_recharge_delay <= 0:
            self.shield = min(self.max_shield, self.shield + 12 * dt)

        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        if direction.length_squared() > 0:
            direction = direction.normalize()
        current_mouse = pygame.Vector2(pygame.mouse.get_pos())
        if current_mouse.distance_squared_to(self.last_mouse) > 4:
            self.mouse_active = True
        self.last_mouse = current_mouse

        if self.dash_time > 0:
            self.dash_time -= dt
            self.pos += self.dash_direction * 930 * dt
            self.trail_timer -= dt
            if self.trail_timer <= 0 and self.particles_group is not None:
                self.trail_timer = 0.025
                self.particles_group.add(Particle(self.pos, self.primary_color, (0, 0), 0.25, 5))
        elif direction.length_squared() > 0:
            self.pos += direction * PLAYER_SPEED * dt
            self.mouse_active = False
        elif self.mouse_active:
            self.pos = self.pos.lerp(current_mouse, 1.0 - math.exp(-20 * dt))
        self.pos.x = max(self.rect.width / 2, min(SCREEN_WIDTH - self.rect.width / 2, self.pos.x))
        self.pos.y = max(70 + self.rect.height / 2, min(SCREEN_HEIGHT - self.rect.height / 2 - 12, self.pos.y))
        self.rect.center = self.pos

        if self.auto_fire or pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]:
            self.shoot()
        self.image = self.base_image.copy()
        if self.invulnerable_time > 0 and int(self.invulnerable_time * 18) % 2 == 0:
            self.image.set_alpha(95)
        if self.shield > 0:
            pygame.draw.circle(self.image, (*CYAN, 170), self.image.get_rect().center, 28, width=2)

    def shoot(self):
        if not self.ready or self.lasers_group is None:
            return False
        self.shoot_timer = self.shoot_cooldown
        self.shot_counter += 1
        x, y = self.rect.midtop
        if self.character_id == 1:
            self.lasers_group.add(Laser((x, y), piercing=True, color=self.primary_color, kind="beam"))
        elif self.character_id == 2:
            self.lasers_group.add(Laser((x - 10, y + 5), color=self.primary_color, kind="twin", velocity=(-105, -760)))
            self.lasers_group.add(Laser((x + 10, y + 5), color=self.primary_color, kind="twin", velocity=(105, -760)))
        elif self.character_id == 3:
            self.lasers_group.add(Laser((x, y), color=self.primary_color, kind="pulse"))
        else:
            direction = -1 if self.shot_counter % 2 else 1
            self.lasers_group.add(Laser((x, y), color=self.primary_color, kind="disk", velocity=(direction * 190, -470)))
        if self.sound:
            self.sound.play_laser()
        return True

    def trigger_dash(self):
        if not self.dash_ready:
            return False
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        if direction.length_squared() == 0:
            direction = pygame.Vector2(pygame.mouse.get_pos()) - self.pos
        if direction.length_squared() == 0:
            direction = pygame.Vector2(0, -1)
        self.dash_direction = direction.normalize()
        self.dash_time = 0.18
        self.dash_cooldown = 2.4
        self.invulnerable_time = 0.3
        return True

    def take_damage(self, amount):
        if self.invulnerable_time > 0 or self.dash_time > 0 or self.health <= 0:
            return False
        self.invulnerable_time = 0.5
        self.shield_recharge_delay = 4.0
        remaining = amount
        if self.shield > 0:
            absorbed = min(self.shield, remaining)
            self.shield -= absorbed
            remaining -= absorbed
        self.health = max(0, self.health - remaining)
        return True

    def heal(self, amount):
        previous = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - previous

    def activate_shield(self, duration_ms=6000):
        if self.character_id != 3:
            self.max_shield = max(self.max_shield, 40)
        self.shield = self.max_shield
        self.temporary_shield_time = duration_ms / 1000

    def update_ship_design(self):
        self._draw_ship()
        self.image = self.base_image.copy()
