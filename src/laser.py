import pygame

from src.settings import CYAN, LASER_SPEED, YELLOW


class Laser(pygame.sprite.Sprite):

    def __init__(self, pos, piercing=False, color=None, kind=None, velocity=None, damage=None):
        super().__init__()
        self.kind = kind or ("beam" if piercing else "bolt")
        self.color = color or (YELLOW if piercing else CYAN)
        self.piercing = piercing or self.kind in ("beam", "disk")
        self.blast_radius = 0
        self.age = 0.0
        self.hit_ids = set()

        if self.kind == "beam":
            self.image = pygame.Surface((14, 38), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (*self.color, 45), (0, 0, 14, 38), border_radius=7)
            pygame.draw.rect(self.image, self.color, (4, 1, 6, 34), border_radius=3)
            pygame.draw.line(self.image, (255, 255, 255), (7, 4), (7, 28), 2)
            self.remaining_hits = 5
            default_velocity = (0, -LASER_SPEED)
            default_damage = 1
        elif self.kind == "pulse":
            self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (*self.color, 45), (14, 14), 14)
            pygame.draw.circle(self.image, self.color, (14, 14), 10)
            pygame.draw.circle(self.image, (245, 255, 255), (14, 14), 5)
            self.remaining_hits = 1
            self.blast_radius = 72
            default_velocity = (0, -520)
            default_damage = 2
        elif self.kind == "disk":
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (*self.color, 40), (15, 15), 15)
            pygame.draw.circle(self.image, self.color, (15, 15), 11, width=4)
            pygame.draw.line(self.image, (255, 245, 235), (5, 15), (25, 15), 2)
            pygame.draw.line(self.image, self.color, (15, 5), (15, 25), 2)
            self.remaining_hits = 3
            default_velocity = velocity or (180, -470)
            default_damage = 1.5
        else:
            self.image = pygame.Surface((10, 24), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (*self.color, 45), (0, 0, 10, 24), border_radius=5)
            pygame.draw.rect(self.image, self.color, (3, 1, 4, 20), border_radius=2)
            self.remaining_hits = 1
            default_velocity = velocity or (0, -LASER_SPEED)
            default_damage = 0.7 if self.kind == "twin" else 1

        self.rect = self.image.get_rect(midbottom=pos)
        self.pos = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2(velocity or default_velocity)
        self.damage = default_damage if damage is None else damage
        self.wall_bounces = 0

    def register_hit(self, target):
        target_id = id(target)
        if target_id in self.hit_ids:
            return False
        self.hit_ids.add(target_id)
        self.remaining_hits -= 1
        if self.kind == "disk" and self.remaining_hits > 0:
            self.velocity.x *= -1
            self.velocity.y *= -1
        if self.remaining_hits <= 0:
            self.kill()
        return True

    def update(self, dt=1 / 60):
        self.age += dt
        self.pos += self.velocity * dt
        if self.kind == "disk":
            if self.pos.x < 16 or self.pos.x > 944:
                self.velocity.x *= -1
                self.pos.x = max(16, min(944, self.pos.x))
                self.wall_bounces += 1
            if self.pos.y < 82 or self.pos.y > 625:
                self.velocity.y *= -1
                self.pos.y = max(82, min(625, self.pos.y))
                self.wall_bounces += 1
            if self.wall_bounces > 6 or self.age > 5:
                self.kill()
        elif self.rect.bottom < 0 or self.rect.top > 640 or self.rect.right < 0 or self.rect.left > 960:
            self.kill()
        self.rect.center = self.pos
