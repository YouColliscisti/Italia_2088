import random
import pygame
from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH

class DynamicBackground:
    PALETTES = {
        1: ((5, 10, 26), (22, 50, 85), (35, 190, 230)),
        2: ((14, 9, 24), (65, 42, 90), (240, 190, 55)),
        3: ((5, 18, 20), (20, 65, 65), (55, 210, 150)),
        4: ((20, 7, 18), (80, 25, 60), (255, 75, 100)),
    }

    def __init__(self):
        self.scroll_y = 0.0
        rng = random.Random(2088)
        self.stars = [(rng.randrange(SCREEN_WIDTH), rng.randrange(SCREEN_HEIGHT), rng.choice((1, 1, 2)), rng.uniform(12, 42)) for _ in range(85)]
        self.buildings = []
        x = 0
        while x < SCREEN_WIDTH:
            width = rng.randint(45, 95)
            self.buildings.append((x, width, rng.randint(90, 260), rng.randint(2, 5)))
            x += width + rng.randint(5, 16)

    def update(self, dt=1 / 60):
        self.scroll_y = (self.scroll_y + 65 * dt) % 80
        for index, (x, y, size, speed) in enumerate(self.stars):
            y += speed * dt
            if y > SCREEN_HEIGHT:
                y = 0
            self.stars[index] = (x, y, size, speed)

    def draw(self, surface, level=1, character_id=1):
        base, building_color, neon = self.PALETTES.get(character_id, self.PALETTES[1])
        surface.fill(base)
        for x, y, size, _ in self.stars:
            pygame.draw.rect(surface, tuple(min(255, c + 45) for c in building_color), (int(x), int(y), size, size))

        horizon = SCREEN_HEIGHT - 150
        for index, (x, width, height, windows) in enumerate(self.buildings):
            top = horizon - height + (index % 3) * 15
            pygame.draw.rect(surface, building_color, (x, top, width, height + 160))
            pygame.draw.line(surface, tuple(min(255, c + 25) for c in building_color), (x, top), (x + width, top), 2)
            if index % 4 == 0:
                pygame.draw.line(surface, neon, (x + width // 2, top - 24), (x + width // 2, top), 2)
            for row in range(3, windows + 3):
                for col in range(2):
                    wx = x + 10 + col * max(16, (width - 20) // 2)
                    wy = top + row * 25
                    if wx + 5 < x + width and wy < SCREEN_HEIGHT:
                        window_color = neon if (index + row + col + level) % 4 == 0 else tuple(max(0, c - 5) for c in building_color)
                        pygame.draw.rect(surface, window_color, (wx, wy, 5, 9))

        grid_color = tuple(min(255, c + 15) for c in building_color)
        for y in range(-80, SCREEN_HEIGHT + 80, 80):
            draw_y = y + self.scroll_y
            pygame.draw.line(surface, grid_color, (0, draw_y), (SCREEN_WIDTH, draw_y), 1)
        for x in range(0, SCREEN_WIDTH + 1, 120):
            pygame.draw.line(surface, grid_color, (SCREEN_WIDTH // 2, 330), (x, SCREEN_HEIGHT), 1)
        shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 10, 70))
        surface.blit(shade, (0, 0))
