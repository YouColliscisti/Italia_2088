import random
import pygame

class Particle(pygame.sprite.Sprite):

    def __init__(self, pos, color, velocity=None, lifetime=0.55, radius=None, fragment=False):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.color = color
        self.velocity = pygame.Vector2(velocity or (random.uniform(-190, 190), random.uniform(-190, 190)))
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.radius = radius or random.randint(2, 5)
        self.fragment = fragment
        size = self.radius * 4 + 8
        self.base_image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        pygame.draw.circle(self.base_image, (*self.color, 35), (center, center), self.radius * 2)
        if fragment:
            length = self.radius * 3
            pygame.draw.polygon(self.base_image, (*self.color, 255), [
                (center - length, center - 1), (center + length, center - self.radius // 2 - 1),
                (center + self.radius, center + self.radius), (center - self.radius, center + 2),
            ])
            pygame.draw.line(self.base_image, (245, 255, 255, 220), (center - length, center), (center + length, center), 1)
        else:
            pygame.draw.circle(self.base_image, (*self.color, 230), (center, center), self.radius)
            pygame.draw.circle(self.base_image, (250, 255, 255, 230), (center, center), max(1, self.radius // 2))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt=1 / 60):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self.pos += self.velocity * dt
        if self.fragment:
            self.velocity.y += 75 * dt
        self.velocity *= max(0.0, 1.0 - 1.5 * dt)
        self.rect.center = self.pos
        self.image = self.base_image.copy()
        self.image.set_alpha(max(0, min(255, int(255 * self.lifetime / self.max_lifetime))))


class Shockwave(pygame.sprite.Sprite):
    def __init__(self, pos, color, radius=160, lifetime=0.42, width=5):
        super().__init__()
        self.center = pygame.Vector2(pos)
        self.color = color
        self.max_radius = radius
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.width = width
        size = radius * 2 + 12
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.center)
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        progress = 1.0 - self.lifetime / self.max_lifetime
        radius = max(2, int(self.max_radius * (0.12 + 0.88 * progress)))
        alpha = int(230 * (1.0 - progress))
        center = self.image.get_rect().center
        pygame.draw.circle(self.image, (*self.color, max(0, alpha // 3)), center, radius + 5, self.width + 5)
        pygame.draw.circle(self.image, (*self.color, max(0, alpha)), center, radius, self.width)

    def update(self, dt=1 / 60):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self._redraw()


class FloatingText(pygame.sprite.Sprite):
    def __init__(self, pos, text, color, font=None, lifetime=1.0):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        font = font or pygame.font.SysFont("Consolas", 16, bold=True)
        self.base_image = font.render(text, True, color)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt=1 / 60):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        self.pos.y -= 32 * dt
        self.rect.center = self.pos
        self.image = self.base_image.copy()
        self.image.set_alpha(int(255 * min(1.0, self.lifetime / (self.max_lifetime * 0.6))))


class VisualEffectsManager:
    def __init__(self):
        self.group = pygame.sprite.Group()

    def add_floating_text(self, x, y, text, color=(0, 255, 200)):
        self.group.add(FloatingText((x, y), text, color))

    def add_particle_burst(self, x, y, color=(0, 255, 200), count=12):
        for _ in range(count):
            self.group.add(Particle((x, y), color))

    def update(self, dt=1 / 60):
        self.group.update(dt)

    def draw(self, surface):
        self.group.draw(surface)
