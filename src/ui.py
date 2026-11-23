from pathlib import Path

import pygame
from PIL import Image

from src.ui_briefing import display_mission_briefing, display_story_dialogue
from src.ui_helpers import Button, render_multiline_text
from src.ui_hud import (
    display_ability, display_boss_health, display_health, display_hud,
    display_mission_progress, display_objective_progress, display_shield,
)
from src.ui_screen import display_backstory, display_game_over, display_pause, display_victory, draw_character_selection


class UI:
    def __init__(self, surface):
        self.display_surface = surface
        self.font = pygame.font.SysFont("Consolas", 20, bold=True)
        self.title_font = pygame.font.SysFont("Consolas", 38, bold=True)
        self.sub_font = pygame.font.SysFont("Consolas", 15)
        self.small_font = pygame.font.SysFont("Consolas", 13)
        self.last_card_rects = []
        self.difficulty_rect = None
        self.pause_button_rects = []
        self.map_image = None
        self.character_gif_frames = {}
        self.gif_timers = {}
        self.gif_indices = {}
        self.gif_durations = {}
        assets = Path(__file__).resolve().parent.parent / "assets"

        try:
            loaded = pygame.image.load(str(assets / "italy_map.png")).convert_alpha()
            self.map_image = pygame.transform.smoothscale(loaded, (190, 195))
        except (pygame.error, FileNotFoundError):
            self.map_image = None

        for cid, filename in {1: "Beatrice.gif", 2: "Simon.gif", 3: "Sofia.gif", 4: "Elias.gif"}.items():
            frames = []
            try:
                with Image.open(assets / filename) as source:
                    durations = []
                    for index in range(source.n_frames):
                        source.seek(index)
                        durations.append(max(80, source.info.get("duration", 120)))
                        rgba = source.convert("RGBA")
                        image = pygame.image.frombytes(rgba.tobytes(), rgba.size, "RGBA").convert_alpha()
                        frames.append(pygame.transform.smoothscale(image, (88, 88)))
                self.gif_durations[cid] = durations
            except (OSError, pygame.error):
                frames = []
            self.character_gif_frames[cid] = frames
            self.gif_indices[cid] = 0
            self.gif_timers[cid] = pygame.time.get_ticks()

    @staticmethod
    def Button(*args, **kwargs):
        return Button(*args, **kwargs)

    def draw_character_selection(self, completed_stories, difficulty="Normal"):
        now = pygame.time.get_ticks()
        images = {}
        for cid, frames in self.character_gif_frames.items():
            if frames:
                duration = self.gif_durations.get(cid, [120] * len(frames))[self.gif_indices[cid]]
                if now - self.gif_timers[cid] >= duration:
                    self.gif_indices[cid] = (self.gif_indices[cid] + 1) % len(frames)
                    self.gif_timers[cid] = now
                images[cid] = frames[self.gif_indices[cid]]
            else:
                images[cid] = None
        self.last_card_rects, self.difficulty_rect = draw_character_selection(
            self.display_surface, self.font, self.title_font, self.sub_font,
            completed_stories, images, difficulty,
        )

    def display_hud(self, score, high_score, level, max_levels, is_boss_level, ultimate_ready, objective_text=""):
        display_hud(self.display_surface, self.font, self.sub_font, score, high_score, level, max_levels, is_boss_level, ultimate_ready, objective_text)

    def display_objective_progress(self, mission):
        display_objective_progress(self.display_surface, self.sub_font, mission)

    def display_mission_progress(self, current_kills, required_kills):
        display_mission_progress(self.display_surface, self.font, self.sub_font, current_kills, required_kills)

    def display_health(self, current_health, max_health):
        display_health(self.display_surface, self.sub_font, current_health, max_health)

    def display_player_status(self, player, charge, threshold):
        self.display_health(player.health, player.max_health)
        display_shield(self.display_surface, self.sub_font, player)
        display_ability(self.display_surface, self.sub_font, player, charge, threshold)

    def display_boss_health(self, boss):
        display_boss_health(self.display_surface, self.sub_font, boss)

    def display_mission_briefing(self, level, city_name, description, objective, char_name, route=None):
        display_mission_briefing(self.display_surface, self.font, self.sub_font, self.map_image,
                                 level, city_name, description, objective, char_name, route)

    def display_backstory(self, character_id, story, operative_name):
        frames = self.character_gif_frames.get(character_id, [])
        portrait = frames[self.gif_indices[character_id]] if frames else None
        display_backstory(self.display_surface, self.font, self.title_font, self.sub_font, portrait, operative_name, story)

    def display_story_dialogue(self, speaker, message, city_title):
        display_story_dialogue(self.display_surface, self.font, self.sub_font, speaker, message, city_title)

    def display_pause(self):
        self.pause_button_rects = display_pause(self.display_surface, self.font, self.title_font, self.sub_font)

    def display_game_over(self, score=0, reason=""):
        display_game_over(self.display_surface, self.title_font, self.sub_font, score, reason)

    def display_victory(self, completed_count, score=0, character_name=""):
        display_victory(self.display_surface, self.font, self.sub_font, completed_count, score, character_name)

    def draw_launch_button(self, button):
        button.draw(self.display_surface)

    def render_multiline_text(self, text, font, color, max_width):
        return render_multiline_text(text, font, color, max_width)
