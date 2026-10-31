import math
import random
import pygame

from src.debris import SpaceDebris
from src.effects import FloatingText, Shockwave
from src.settings import CYAN, GREEN, ORANGE, PURPLE, RED, SCREEN_WIDTH, WHITE, YELLOW


MISSION_BLUEPRINTS = {
    1: {"kind": "HACK", "name": "GHOST IN THE NODE", "objective": "Hack 3 data nodes before the trace window closes. Stay inside each uplink ring.", "target": 3, "time": 75},
    2: {"kind": "ESCORT", "name": "SUPPLY LINE", "objective": "Escort the resistance supply drone to the northern extraction gate. Keep its hull intact.", "target": 1},
    3: {"kind": "STORM", "name": "KINETIC WEATHER", "objective": "Survive the kinetic storm. Dodge falling scrap or detonate it to clear nearby hostiles.", "target": 1, "time": 35},
    4: {"kind": "SHIELDS", "name": "GHOST PROTOCOL", "objective": "Destroy 3 stealth shield generators concealing the corporate sector.", "target": 3},
    5: {"kind": "SALVAGE", "name": "MEMORY HUNT", "objective": "Destroy couriers and recover 5 encrypted data cores before they fall off-grid.", "target": 5},
    6: {"kind": "SABOTAGE", "name": "CASCADE FAILURE", "objective": "Sabotage 4 armored reactors while their security fleet counterattacks.", "target": 4},
    7: {"kind": "DEFENSE", "name": "LAST UPLINK", "objective": "Protect the resistance uplink until the liberation broadcast completes.", "target": 1, "time": 40},
    8: {"kind": "BOSS", "name": "OMNIA CORE", "objective": "Break all three Omnia Core combat phases and liberate Italia.", "target": 1},
}


class MissionTarget(pygame.sprite.Sprite):
    def __init__(self, pos, kind):
        super().__init__()
        self.kind = kind
        self.pos = pygame.Vector2(pos)
        self.shootable = kind in ("SHIELD", "REACTOR")
        self.max_health = {"SHIELD": 7, "REACTOR": 11}.get(kind, 999)
        self.health = self.max_health
        self.hack_progress = 0.0
        self.hacked = False
        self.age = random.uniform(0, math.tau)
        self.image = pygame.Surface((62, 62), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self._redraw()

    def _redraw(self):
        self.image.fill((0, 0, 0, 0))
        color = GREEN if self.hacked else {"NODE": CYAN, "SHIELD": PURPLE, "REACTOR": ORANGE}[self.kind]
        pygame.draw.circle(self.image, (*color, 35), (31, 31), 30)
        if self.kind == "NODE":
            pygame.draw.rect(self.image, color, (17, 13, 28, 36), width=3, border_radius=4)
            for y in (21, 29, 37):
                pygame.draw.line(self.image, WHITE, (23, y), (39, y), 2)
        elif self.kind == "SHIELD":
            pygame.draw.polygon(self.image, color, [(31, 5), (53, 17), (49, 44), (31, 57), (13, 44), (9, 17)], width=4)
            pygame.draw.circle(self.image, WHITE, (31, 31), 8, width=2)
        else:
            pygame.draw.rect(self.image, color, (12, 9, 38, 44), width=4, border_radius=6)
            pygame.draw.circle(self.image, color, (31, 31), 13)
            pygame.draw.circle(self.image, WHITE, (31, 31), 5)
        self._color = color

    def update(self, dt=1 / 60):
        self.age += dt
        self._redraw()

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        return self.health <= 0


class SupplyDrone(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((54, 44), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(27, 0), (52, 20), (42, 42), (12, 42), (2, 20)])
        pygame.draw.rect(self.image, WHITE, (17, 13, 20, 18), width=2, border_radius=3)
        pygame.draw.line(self.image, CYAN, (7, 22), (47, 22), 2)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 540))
        self.pos = pygame.Vector2(self.rect.center)
        self.max_hull = 110
        self.hull = self.max_hull
        self.elapsed = 0.0
        self.duration = 34.0
        self.progress = 0.0

    def update(self, dt=1 / 60):
        self.elapsed = min(self.duration, self.elapsed + dt)
        self.progress = self.elapsed / self.duration
        self.pos.y = 540 - 405 * self.progress
        self.pos.x = SCREEN_WIDTH // 2 + math.sin(self.progress * math.pi * 3) * 175
        self.rect.center = self.pos

    def damage(self, amount):
        self.hull = max(0, self.hull - amount)


class ResistanceUplink(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((72, 72), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*CYAN, 40), (36, 36), 35)
        pygame.draw.polygon(self.image, CYAN, [(36, 4), (55, 60), (17, 60)], width=4)
        pygame.draw.circle(self.image, WHITE, (36, 32), 8)
        pygame.draw.arc(self.image, GREEN, (9, 9, 54, 54), math.pi, math.tau, 3)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 465))
        self.max_hull = 140
        self.hull = self.max_hull

    def damage(self, amount):
        self.hull = max(0, self.hull - amount)


class DataCore(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (*YELLOW, 45), [(14, 0), (28, 14), (14, 28), (0, 14)])
        pygame.draw.polygon(self.image, YELLOW, [(14, 3), (25, 14), (14, 25), (3, 14)], width=3)
        pygame.draw.rect(self.image, WHITE, (10, 10, 8, 8))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.age = 0.0

    def update(self, dt=1 / 60):
        self.age += dt
        self.pos.y += 42 * dt
        self.rect.center = self.pos
        if self.age > 12 or self.rect.top > 650:
            self.kill()


class MissionController:
    def __init__(self, level, number):
        self.level = level
        self.number = number
        self.blueprint = MISSION_BLUEPRINTS[number]
        self.kind = self.blueprint["kind"]
        self.name = self.blueprint["name"]
        self.objective_text = self.blueprint["objective"]
        self.objects_group = pygame.sprite.Group()
        self.targets_group = pygame.sprite.Group()
        self.friendly_group = pygame.sprite.Group()
        self.items_group = pygame.sprite.Group()
        self.completed = False
        self.failed = False
        self.elapsed = 0.0
        self.total_time = self.blueprint.get("time")
        self.time_remaining = float(self.total_time) if self.total_time else None
        self.storm_timer = 0.0
        self.cores_collected = 0
        self.hacked_count = 0
        self.escort = None
        self.uplink = None
        self._setup()

    def _setup(self):
        positions = {
            "HACK": [(220, 205), (480, 300), (740, 195)],
            "SHIELDS": [(205, 190), (480, 275), (755, 190)],
            "SABOTAGE": [(175, 185), (380, 270), (585, 185), (790, 270)],
        }
        if self.kind in positions:
            target_kind = {"HACK": "NODE", "SHIELDS": "SHIELD", "SABOTAGE": "REACTOR"}[self.kind]
            for pos in positions[self.kind]:
                target = MissionTarget(pos, target_kind)
                self.objects_group.add(target)
                self.targets_group.add(target)
        elif self.kind == "ESCORT":
            self.escort = SupplyDrone()
            self.objects_group.add(self.escort)
            self.friendly_group.add(self.escort)
        elif self.kind == "DEFENSE":
            self.uplink = ResistanceUplink()
            self.objects_group.add(self.uplink)
            self.friendly_group.add(self.uplink)

    def update(self, dt):
        if self.completed or self.failed:
            return
        self.elapsed += dt
        if self.time_remaining is not None:
            self.time_remaining = max(0.0, self.time_remaining - dt)
        self.objects_group.update(dt)
        self.items_group.update(dt)

        if self.kind == "HACK":
            player_pos = pygame.Vector2(self.level.player.rect.center)
            for node in self.targets_group:
                if node.hacked:
                    continue
                if player_pos.distance_to(node.pos) <= 92:
                    node.hack_progress = min(1.0, node.hack_progress + dt / 3.0)
                else:
                    node.hack_progress = max(0.0, node.hack_progress - dt * 0.025)
                if node.hack_progress >= 1.0:
                    node.hacked = True
                    self.hacked_count += 1
                    self.level.score += 250
                    self.level.text_group.add(FloatingText(node.pos, "NODE LIBERATED", GREEN, self.level.ui.sub_font))
            if self.hacked_count >= 3:
                self.complete()
            elif self.time_remaining <= 0:
                self.fail("TRACE COMPLETE // HACK WINDOW LOST")
        elif self.kind == "ESCORT":
            if self.escort.hull <= 0:
                self.fail("SUPPLY DRONE DESTROYED")
            elif self.escort.progress >= 1.0:
                self.complete()
        elif self.kind == "STORM":
            self.storm_timer -= dt
            if self.storm_timer <= 0 and self.time_remaining > 0:
                self.storm_timer = max(0.30, 0.62 - self.elapsed * 0.005)
                velocity = (random.uniform(-65, 65), random.uniform(190, 285))
                self.level.debris_group.add(SpaceDebris((random.randint(35, 925), -45), velocity))
            if self.time_remaining <= 0:
                self.complete()
        elif self.kind == "DEFENSE":
            if self.uplink.hull <= 0:
                self.fail("RESISTANCE UPLINK DESTROYED")
            elif self.time_remaining <= 0:
                self.complete()
        self._collect_cores()
        self._hostile_collisions()

    def _collect_cores(self):
        if self.kind != "SALVAGE":
            return
        for _ in pygame.sprite.spritecollide(self.level.player, self.items_group, True):
            self.cores_collected += 1
            self.level.score += 175
            self.level.sound.play_pickup()
            self.level.text_group.add(FloatingText(self.level.player.rect.center, f"DATA CORE {self.cores_collected}/5", YELLOW, self.level.ui.sub_font))
        if self.cores_collected >= 5:
            self.complete()

    def _hostile_collisions(self):
        for friendly in list(self.friendly_group):
            hits = pygame.sprite.spritecollide(friendly, self.level.enemy_lasers_group, True)
            if hits:
                friendly.damage(10 * len(hits))
            for enemy in pygame.sprite.spritecollide(friendly, self.level.enemies_group, False):
                friendly.damage(24)
                if enemy is not self.level.boss and enemy.alive():
                    self.level.create_explosion(enemy.rect.center, RED, scale=enemy.explosion_scale)
                    enemy.kill()

    def handle_player_laser(self, laser):
        for target in pygame.sprite.spritecollide(laser, self.targets_group, False):
            if not target.shootable or not target.alive() or not laser.register_hit(target):
                continue
            destroyed = target.take_damage(laser.damage)
            if laser.kind == "pulse":
                self.level.detonate_pulse(laser, target.rect.center, primary=target)
            if destroyed and target.alive():
                self.destroy_target(target)

    def destroy_target(self, target):
        position = target.rect.center
        self.level.score += 300
        self.level.create_explosion(position, ORANGE if target.kind == "REACTOR" else PURPLE, scale=1.5)
        self.level.particles_group.add(Shockwave(position, YELLOW, radius=115))
        target.kill()
        if not self.targets_group:
            self.complete()

    def on_enemy_destroyed(self, enemy):
        if self.kind == "SALVAGE" and self.cores_collected + len(self.items_group) < 5:
            self.items_group.add(DataCore(enemy.rect.center))

    def complete(self):
        if self.completed or self.failed:
            return
        self.completed = True
        self.level.complete_mission()

    def fail(self, reason):
        if self.failed or self.completed:
            return
        self.failed = True
        self.level.mission_failed(reason)

    @property
    def progress_text(self):
        if self.kind == "HACK":
            return f"DATA NODES {self.hacked_count}/3"
        if self.kind == "ESCORT":
            return f"ESCORT {int(self.escort.progress * 100)}% // DRONE {self.escort.hull}"
        if self.kind == "STORM":
            return f"SURVIVE {math.ceil(self.time_remaining)}s"
        if self.kind == "SHIELDS":
            return f"SHIELD GENERATORS {len(self.targets_group)} REMAIN"
        if self.kind == "SALVAGE":
            return f"DATA CORES {self.cores_collected}/5"
        if self.kind == "SABOTAGE":
            return f"REACTORS {len(self.targets_group)} REMAIN"
        if self.kind == "DEFENSE":
            return f"UPLINK {math.ceil(self.time_remaining)}s // INTEGRITY {self.uplink.hull}"
        return "DESTROY OMNIA CORE"

    @property
    def progress_ratio(self):
        if self.kind == "HACK":
            return min(1.0, (self.hacked_count + sum(n.hack_progress for n in self.targets_group if not n.hacked)) / 3)
        if self.kind == "ESCORT":
            return self.escort.progress
        if self.kind in ("STORM", "DEFENSE"):
            return 1.0 - self.time_remaining / self.total_time
        if self.kind == "SHIELDS":
            return 1.0 - len(self.targets_group) / 3
        if self.kind == "SALVAGE":
            return self.cores_collected / 5
        if self.kind == "SABOTAGE":
            return 1.0 - len(self.targets_group) / 4
        return 0.0

    def draw_details(self, surface):
        for target in self.targets_group:
            if target.kind == "NODE" and not target.hacked:
                pygame.draw.circle(surface, CYAN, target.rect.center, 92, width=1)
                if target.hack_progress > 0:
                    rect = pygame.Rect(0, 0, 74, 74)
                    rect.center = target.rect.center
                    pygame.draw.arc(surface, GREEN, rect, -math.pi / 2, -math.pi / 2 + math.tau * target.hack_progress, 5)
            if target.shootable and target.health < target.max_health:
                width = 58
                x, y = target.rect.centerx - width // 2, target.rect.bottom + 5
                pygame.draw.rect(surface, (45, 30, 50), (x, y, width, 5))
                pygame.draw.rect(surface, ORANGE, (x, y, int(width * target.health / target.max_health), 5))
        for friendly in self.friendly_group:
            width = 92
            x, y = friendly.rect.centerx - width // 2, friendly.rect.top - 13
            pygame.draw.rect(surface, (35, 40, 50), (x, y, width, 7))
            pygame.draw.rect(surface, GREEN, (x, y, int(width * friendly.hull / friendly.max_hull), 7))
