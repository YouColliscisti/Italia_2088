import math
import random
import pygame

from src.backgrounds import DynamicBackground
from src.collision_handler import process_collisions
from src.debris import SpaceDebris
from src.effects import FloatingText, Particle, Shockwave
from src.enemy import BossEnemy, CruiserEnemy, ThemeEnemy
from src.missions import MissionController
from src.music import MusicManager
from src.player import Player
from src.powerup import HealthPowerUp, ShieldPowerUp
from src.save_manager import SaveManager
from src.settings import (
    CYAN, DIFFICULTY_SETTINGS, ENEMY_SPAWN_TIME, GREEN, MAX_LEVELS, ORANGE,
     SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_KILLS_PER_LEVEL, WHITE, YELLOW,
)
from src.story_data import BACKSTORIES, BRIEFINGS, CHARACTER_NAMES, DIALOGUE_DATA, PROLOGUE_EVENTS
from src.ui import UI, Button


class Level:
    def __init__(self, surface, character_id=1, difficulty="Normal", new_game=True, save_manager=None, sound=None):
        self.display_surface = surface
        self.ui = UI(surface)
        self.bg = DynamicBackground()
        self.sound = sound or MusicManager()
        self.save_mgr = save_manager or SaveManager()
        self.character_id = character_id
        self.difficulty = difficulty if difficulty in DIFFICULTY_SETTINGS else "Normal"
        self.launch_btn = Button(SCREEN_WIDTH // 2 - 155, SCREEN_HEIGHT - 92, 310, 50, "LAUNCH MISSION", self.ui.font, "launch")

        self.player_group = pygame.sprite.GroupSingle()
        self.lasers_group = pygame.sprite.Group()
        self.enemy_lasers_group = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.debris_group = pygame.sprite.Group()
        self.powerups_group = pygame.sprite.Group()
        self.particles_group = pygame.sprite.Group()
        self.text_group = pygame.sprite.Group()
        self.mission = None

        self.high_score = self.save_mgr.load_high_score()
        self.shake_duration = 0.0
        self.ultimate_threshold = 10
        self.enemy_timer = 0.0
        self.input_cooldown = 0.0
        self.notice = ""
        self.notice_time = 0.0
        self.boss_enraged_announced = False
        self.failure_reason = ""
        self.restart(new_game=new_game)
        if new_game:
            self.save_game()

    @property
    def required_kills(self):
        """Retained for compatibility; mission completion is now objective-driven."""
        return TARGET_KILLS_PER_LEVEL + (self.current_level - 1) * 2

    def get_completed_stories_count(self):
        return self.save_mgr.get_completed_stories_count()

    def save_game(self):
        self.high_score = max(self.high_score, self.score)
        success = self.save_mgr.save_game(self.character_id, self.difficulty, self.current_level, self.score, self.player)
        self.set_notice("GAME SAVED" if success else "SAVE FAILED")
        return success

    def set_notice(self, text, duration=1.8):
        self.notice = text
        self.notice_time = duration

    def handle_event(self, event):
        if self.input_cooldown > 0:
            return None
        advance = (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)) or (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)

        if self.in_backstory:
            if advance:
                self.in_backstory = False
                self.in_prologue = True
                self.input_cooldown = 0.2
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.in_backstory = False
                self.in_prologue = True
        elif self.in_prologue:
            if advance:
                self.prologue_index += 1
                self.input_cooldown = 0.2
                if self.prologue_index >= len(PROLOGUE_EVENTS[self.character_id]):
                    self.in_prologue = False
                    self.in_briefing = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.in_prologue = False
                self.in_briefing = True
        elif self.in_briefing:
            if self.launch_btn.is_clicked(event) or (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)):
                self.in_briefing = False
                self.in_dialogue = True
                self.input_cooldown = 0.2
        elif self.in_dialogue:
            if advance:
                self.in_dialogue = False
                self.enemy_timer = 0.5
                self.input_cooldown = 0.2
        elif self.paused:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.paused = False
                elif event.key == pygame.K_s:
                    self.save_game()
                elif event.key == pygame.K_m:
                    self.save_game()
                    return "MENU"
                elif event.key == pygame.K_q:
                    return "QUIT"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, action in self.ui.pause_button_rects:
                    if rect.collidepoint(event.pos):
                        if action == "resume":
                            self.paused = False
                        elif action == "save":
                            self.save_game()
                        elif action == "main_menu":
                            self.save_game()
                            return "MENU"
                        elif action == "quit":
                            return "QUIT"
        elif self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.retry_level()
                elif event.key == pygame.K_m:
                    return "MENU"
                elif event.key == pygame.K_q:
                    return "QUIT"
        elif self.victory:
            if advance or (event.type == pygame.KEYDOWN and event.key == pygame.K_m):
                return "SELECT_CHARACTER"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                return "QUIT"
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.paused = True
            elif event.key == pygame.K_f:
                self.player.auto_fire = not self.player.auto_fire
                self.set_notice(f"AUTO-FIRE {'ON' if self.player.auto_fire else 'OFF'}")
            elif event.key in (pygame.K_e, pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.trigger_ability()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.trigger_ability()
        return None

    def trigger_ability(self):
        if self.character_id == 2:
            if not self.player.trigger_dash():
                self.set_notice("DASH RECHARGING", 0.8)
        elif self.character_id == 4:
            self.trigger_ultimate()

    def trigger_ultimate(self):
        if self.character_id != 4:
            return False
        if self.ultimate_kills < self.ultimate_threshold:
            self.set_notice("ANARCHY BLAST NOT CHARGED", 0.8)
            return False
        self.ultimate_kills = 0
        self.trigger_shake(0.65)
        self.sound.play_ultimate()
        for enemy in list(self.enemies_group):
            if enemy is self.boss:
                if enemy.take_damage(18) and enemy.alive():
                    self.destroy_enemy(enemy)
                else:
                    self.create_explosion(enemy.rect.center, YELLOW, count=20, play_sound=False)
            else:
                self.destroy_enemy(enemy, ultimate=True)
        self.enemy_lasers_group.empty()
        for radius in range(20, 190, 20):
            self.particles_group.add(Particle((SCREEN_WIDTH // 2 + radius, SCREEN_HEIGHT // 2), YELLOW, (0, 0), 0.5, 4))
        self.particles_group.add(Shockwave(self.player.rect.center, CYAN, radius=420, lifetime=0.65, width=8))
        self.text_group.add(FloatingText((SCREEN_WIDTH // 2, 205), "ANARCHY BLAST!", CYAN, self.ui.font, 1.3))
        return True

    def trigger_shake(self, duration):
        self.shake_duration = max(self.shake_duration, duration)

    def create_explosion(self, pos, color, count=None, scale=1.0, play_sound=True):
        """Layered neon sparks, glowing fragments, and expanding pressure rings."""
        if play_sound:
            self.sound.play_explosion()
        total = int((count if count is not None else 24) * scale)
        palette = (color, CYAN, YELLOW, WHITE)
        for index in range(total):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(85, 270) * math.sqrt(scale)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles_group.add(Particle(
                pos, palette[index % len(palette)], velocity,
                lifetime=random.uniform(0.42, 0.90) * min(1.6, scale),
                radius=random.randint(2, 5) + int(scale > 2), fragment=index % 3 == 0,
            ))
        if scale >= 1.7:
            self.particles_group.add(Shockwave(pos, color, radius=int(75 + 28 * scale), lifetime=0.45))
        if scale >= 4:
            self.particles_group.add(Shockwave(pos, YELLOW, radius=280, lifetime=0.8, width=7))

    def detonate_debris(self, debris):
        """Damage nearby ships and recursively detonate volatile scrap."""
        if debris.detonated:
            return
        debris.detonated = True
        position = pygame.Vector2(debris.rect.center)
        radius = debris.explosion_radius
        self.score += debris.score_value
        debris.kill()
        self.create_explosion(position, ORANGE, scale=1.45)
        self.particles_group.add(Shockwave(position, ORANGE, radius=radius, lifetime=0.48, width=6))
        for enemy in list(self.enemies_group):
            if position.distance_to(enemy.rect.center) <= radius:
                if enemy.take_damage(debris.explosion_damage) and enemy.alive():
                    self.destroy_enemy(enemy)
        for other in list(self.debris_group):
            if other is not debris and not other.detonated and position.distance_to(other.rect.center) <= radius * 0.78:
                self.detonate_debris(other)

    def detonate_pulse(self, laser, pos, primary=None):
        """Sofia's pulse charge deals secondary damage in a compact radius."""
        position = pygame.Vector2(pos)
        self.particles_group.add(Shockwave(position, GREEN, radius=laser.blast_radius, lifetime=0.28, width=4))
        for enemy in list(self.enemies_group):
            if enemy is not primary and position.distance_to(enemy.rect.center) <= laser.blast_radius:
                if enemy.take_damage(1) and enemy.alive():
                    self.destroy_enemy(enemy)
        for debris in list(self.debris_group):
            if position.distance_to(debris.rect.center) <= laser.blast_radius:
                self.detonate_debris(debris)

    def _clear_combat(self):
        for group in (self.lasers_group, self.enemy_lasers_group, self.enemies_group, self.debris_group,
                      self.powerups_group, self.particles_group, self.text_group):
            group.empty()
        if self.mission:
            for group in (self.mission.objects_group, self.mission.targets_group, self.mission.friendly_group, self.mission.items_group):
                group.empty()
        self.boss = None

    def _spawn_player(self):
        self.player_group.empty()
        self.player = Player(
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80), self.lasers_group,
            self.particles_group, self.character_id, self.sound,
        )
        self.player_group.add(self.player)

    def setup_mission(self):
        self.mission = MissionController(self, self.current_level)
        self.boss_enraged_announced = False

    def restart(self, new_game=True):
        saved = self.save_mgr.load_game_data()
        self.score = 0 if new_game else saved["score"]
        self.current_level = 1 if new_game else saved["level"]
        self.level_start_score = self.score
        self.level_kills = 0
        self.ultimate_kills = 0
        self.game_over = False
        self.victory = False
        self.paused = False
        self.boss = None
        self.failure_reason = ""
        self.in_backstory = new_game
        self.in_prologue = False
        self.prologue_index = 0
        self.in_briefing = not new_game
        self.in_dialogue = False
        self.input_cooldown = 0.25
        self._clear_combat()
        self._spawn_player()
        self.setup_mission()

    def retry_level(self):
        self.score = self.level_start_score
        self.level_kills = 0
        self.ultimate_kills = 0
        self.game_over = False
        self.paused = False
        self.failure_reason = ""
        self._clear_combat()
        self._spawn_player()
        self.setup_mission()
        self.in_briefing = True
        self.in_dialogue = False
        self.in_backstory = self.in_prologue = False
        self.input_cooldown = 0.25

    def is_boss_level(self):
        return self.current_level == MAX_LEVELS

    def complete_mission(self):
        if self.game_over or self.victory or self.is_boss_level():
            return
        self.set_notice("OBJECTIVE COMPLETE", 1.4)
        self.advance_level()

    def mission_failed(self, reason):
        self.failure_reason = reason
        self.game_over = True
        self.trigger_shake(0.4)
        self.save_mgr.record_high_score(self.score)

    def advance_level(self):
        self.current_level += 1
        self.level_start_score = self.score
        self.level_kills = 0
        self._clear_combat()
        self.setup_mission()
        self.in_briefing = True
        self.in_dialogue = False
        self.player.heal(20)
        if self.character_id == 3:
            self.player.shield = self.player.max_shield
        self.save_game()

    def spawn_enemy_check(self, dt):
        self.enemy_timer -= dt
        if self.enemy_timer > 0:
            return
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        self.enemy_timer = max(0.38, ENEMY_SPAWN_TIME - (self.current_level - 1) * 0.07) * settings["spawn"]
        if self.mission.kind == "STORM":
            self.enemy_timer *= 1.65
        self.spawn_enemy()

    def spawn_enemy(self):
        if not self.is_active_gameplay:
            return
        if self.is_boss_level():
            if not self.boss:
                hp = DIFFICULTY_SETTINGS[self.difficulty]["boss_health"]
                self.boss = BossEnemy(self.enemy_lasers_group, hp, target=self.player)
                self.enemies_group.add(self.boss)
            return
        if len(self.enemies_group) >= 12:
            return
        x = random.randint(55, SCREEN_WIDTH - 55)
        stage_boost = self.current_level * 0.45
        enemy_cls = ThemeEnemy if random.random() < 0.68 else CruiserEnemy
        enemy = enemy_cls(
            (x, -45), self.current_level, stage_boost, self.character_id,
            self.enemy_lasers_group, DIFFICULTY_SETTINGS[self.difficulty]["enemy_health"],
        )
        self.enemies_group.add(enemy)
        if random.random() < 0.15 and len(self.debris_group) < 5 and self.mission.kind != "STORM":
            self.debris_group.add(SpaceDebris((random.randint(50, SCREEN_WIDTH - 50), -60)))

    @property
    def is_active_gameplay(self):
        return not (self.game_over or self.victory or self.paused or self.in_backstory or self.in_briefing
                    or self.in_dialogue or self.in_prologue)

    def destroy_enemy(self, enemy, ultimate=False):
        if not enemy.alive():
            return
        position = enemy.rect.center
        is_boss = enemy is self.boss
        scale = enemy.explosion_scale
        self.score += enemy.score_value // 2 if ultimate else enemy.score_value
        self.high_score = max(self.high_score, self.score)
        if not is_boss:
            self.level_kills += 1
            if self.character_id == 4 and not ultimate:
                self.ultimate_kills = min(self.ultimate_threshold, self.ultimate_kills + 1)
        enemy.kill()
        self.create_explosion(position, YELLOW if is_boss else CYAN, scale=scale, play_sound=not ultimate)
        if not is_boss:
            self.mission.on_enemy_destroyed(enemy)
            if len(self.powerups_group) < 3 and random.random() < 0.13:
                powerup_cls = HealthPowerUp if self.player.health < self.player.max_health * 0.75 and random.random() < 0.65 else ShieldPowerUp
                self.powerups_group.add(powerup_cls(position))
        if is_boss:
            self.boss = None
            self.enemy_lasers_group.empty()
            self.victory = True
            self.save_mgr.record_high_score(self.score, keep_active=False)
            self.save_mgr.mark_story_completed(self.character_id)

    def damage_player(self, amount):
        scaled = amount * DIFFICULTY_SETTINGS[self.difficulty]["damage"]
        if self.player.take_damage(scaled):
            self.sound.play_hit()
            self.trigger_shake(0.16)
            if self.player.health <= 0:
                self.failure_reason = "OPERATIVE SHIP DESTROYED"
                self.game_over = True
                self.create_explosion(self.player.rect.center, YELLOW, scale=2.5)
                self.save_mgr.record_high_score(self.score)

    def update(self, dt):
        self.input_cooldown = max(0.0, self.input_cooldown - dt)
        self.notice_time = max(0.0, self.notice_time - dt)
        self.shake_duration = max(0.0, self.shake_duration - dt)
        self.bg.update(dt)
        if self.is_active_gameplay:
            self.spawn_enemy_check(dt)
            self.player_group.update(dt)
            self.lasers_group.update(dt)
            self.enemy_lasers_group.update(dt)
            self.enemies_group.update(dt)
            self.debris_group.update(dt)
            self.powerups_group.update(dt)
            self.mission.update(dt)
            self.particles_group.update(dt)
            self.text_group.update(dt)
            process_collisions(self)
            if self.boss and self.boss.enraged and not self.boss_enraged_announced:
                self.boss_enraged_announced = True
                self.set_notice("OMNIA CORE // ENRAGED MODE", 2.8)
                self.trigger_shake(0.65)
        elif self.game_over or self.victory:
            self.particles_group.update(dt)
            self.text_group.update(dt)

    def draw(self):
        render = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg.draw(render, self.current_level, self.character_id)
        self.mission.objects_group.draw(render)
        self.mission.items_group.draw(render)
        self.mission.draw_details(render)
        for group in (self.particles_group, self.debris_group, self.powerups_group, self.enemies_group,
                      self.lasers_group, self.enemy_lasers_group, self.player_group, self.text_group):
            group.draw(render)
        offset = (random.randint(-5, 5), random.randint(-5, 5)) if self.shake_duration > 0 else (0, 0)
        self.display_surface.fill((2, 3, 10))
        self.display_surface.blit(render, offset)

        self.ui.display_hud(self.score, self.high_score, self.current_level, MAX_LEVELS, self.is_boss_level(),
                            self.ultimate_kills >= self.ultimate_threshold, self.mission.objective_text)
        self.ui.display_objective_progress(self.mission)
        if self.player:
            self.ui.display_player_status(self.player, self.ultimate_kills, self.ultimate_threshold)
        if self.boss and self.boss.alive():
            self.ui.display_boss_health(self.boss)

        if self.in_backstory:
            self.ui.display_backstory(self.character_id, BACKSTORIES[self.character_id], CHARACTER_NAMES[self.character_id])
        elif self.in_prologue:
            speaker, message = PROLOGUE_EVENTS[self.character_id][self.prologue_index]
            self.ui.display_story_dialogue(speaker, message, f"PROLOGUE // {CHARACTER_NAMES[self.character_id]}")
        elif self.in_briefing:
            city, description = BRIEFINGS[self.character_id][self.current_level]
            route = [BRIEFINGS[self.character_id][stage][0] for stage in range(1, MAX_LEVELS + 1)]
            self.ui.display_mission_briefing(self.current_level, city, description, self.mission.objective_text,
                                             CHARACTER_NAMES[self.character_id], route)
            self.launch_btn.draw(self.display_surface)
        elif self.in_dialogue:
            speaker, message = DIALOGUE_DATA.get(self.current_level, ("COMMAND", "Engage!"))
            self.ui.display_story_dialogue(speaker, message, self.mission.name)
        elif self.paused:
            self.ui.display_pause()
        elif self.game_over:
            self.ui.display_game_over(self.score, self.failure_reason)
        elif self.victory:
            self.ui.display_victory(self.get_completed_stories_count(), self.score, CHARACTER_NAMES[self.character_id])
        if self.notice_time > 0 and not (self.in_backstory or self.in_prologue or self.in_briefing or self.in_dialogue):
            notice = self.ui.font.render(self.notice, True, WHITE)
            notice_y = 210 if self.boss else 135
            self.display_surface.blit(notice, notice.get_rect(center=(SCREEN_WIDTH // 2, notice_y)))

    def run(self, dt=1 / 60):
        self.update(dt)
        self.draw()
        return None
