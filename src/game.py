import pygame
from src.music import MusicManager
from src.backgrounds import DynamicBackground
from src.level import Level
from src.save_manager import SaveManager
from src.settings import (
    CYAN, DIFFICULTIES, FPS, GRAY, GREEN, RED, SCREEN_HEIGHT, SCREEN_WIDTH,
    TITLE, WHITE, YELLOW,
)
from src.ui import UI
from src.ui_helpers import draw_centered_text, draw_glass_panel

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.ui = UI(self.screen)
        self.sound = MusicManager()
        self.save_mgr = SaveManager()
        self.bg = DynamicBackground()
        self.state = "INTRO"
        self.selected_character = 1
        self.difficulty = "Normal"
        self.level = None
        self.running = True
        self.menu_rects = {
            "new": pygame.Rect(320, 260, 320, 54),
            "continue": pygame.Rect(320, 332, 320, 54),
            "quit": pygame.Rect(320, 404, 320, 54),
        }

        self.sound.play_music("assets/music.ogg", volume=0.35)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F10:
                    self.sound.toggle_mute()
                    continue
                self.handle_event(event)

            self.bg.update(dt)
            if self.state == "INTRO":
                self.draw_neon_intro()
            elif self.state == "MENU":
                self.draw_neon_main_menu()
            elif self.state == "CHARACTER_SELECT":
                self.bg.draw(self.screen, 1, self.selected_character)
                self.ui.draw_character_selection(self.save_mgr.get_completed_stories(), self.difficulty)
            elif self.state == "PLAYING" and self.level:
                result = self.level.run(dt)
                self.handle_level_result(result)
            pygame.display.flip()
        pygame.quit()

    def handle_event(self, event):
        if self.state == "INTRO":
            if event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.state = "MENU"
        elif self.state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for action, rect in self.menu_rects.items():
                    if rect.collidepoint(event.pos):
                        self.activate_menu(action)
                        break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.activate_menu("new")
                elif event.key == pygame.K_c:
                    self.activate_menu("continue")
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    self.running = False
        elif self.state == "CHARACTER_SELECT":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                elif event.key == pygame.K_d:
                    self.cycle_difficulty()
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.selected_character = event.key - pygame.K_0
                    self.start_level(new_game=True)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.ui.difficulty_rect and self.ui.difficulty_rect.collidepoint(event.pos):
                    self.cycle_difficulty()
                    return
                for rect, character_id in self.ui.last_card_rects:
                    if rect.collidepoint(event.pos):
                        self.selected_character = character_id
                        self.start_level(new_game=True)
                        break
        elif self.state == "PLAYING" and self.level:
            self.handle_level_result(self.level.handle_event(event))

    def handle_level_result(self, result):
        if result == "MENU":
            self.state = "MENU"
            self.level = None
            self.sound.play_music("assets/music.ogg", volume=0.35)
        elif result == "SELECT_CHARACTER":
            self.state = "CHARACTER_SELECT"
            self.level = None
            self.sound.play_music("assets/music.ogg", volume=0.35)
        elif result == "QUIT":
            self.running = False

    def activate_menu(self, action):
        if action == "new":
            self.save_mgr.reset_save_data()
            self.state = "CHARACTER_SELECT"
        elif action == "continue" and self.save_mgr.has_active_save():
            saved = self.save_mgr.load_game_data()
            self.selected_character = saved["character_id"]
            self.difficulty = saved["difficulty"]
            self.start_level(new_game=False)
        elif action == "quit":
            self.running = False

    def cycle_difficulty(self):
        index = DIFFICULTIES.index(self.difficulty)
        self.difficulty = DIFFICULTIES[(index + 1) % len(DIFFICULTIES)]

    def draw_neon_intro(self):
        self.bg.draw(self.screen, 8, 1)
        frame = pygame.Rect(150, 160, SCREEN_WIDTH - 300, 300)
        draw_glass_panel(self.screen, frame, border_color=CYAN, bg_alpha=225)
        draw_centered_text(self.screen, "ITALIA 2008—2088", self.ui.title_font, YELLOW, (SCREEN_WIDTH // 2, 245))
        draw_centered_text(self.screen, "NEON REBELLION", self.ui.title_font, CYAN, (SCREEN_WIDTH // 2, 295))
        draw_centered_text(self.screen, "AN UNDERGROUND RESISTANCE. FOUR STORIES. ONE FUTURE.", self.ui.sub_font, GRAY,
                           (SCREEN_WIDTH // 2, 355))
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            draw_centered_text(self.screen, "PRESS ANY KEY TO ACCESS THE RESISTANCE NETWORK", self.ui.sub_font, GREEN,
                               (SCREEN_WIDTH // 2, 410))

    def draw_neon_main_menu(self):
        self.bg.draw(self.screen, 1, self.selected_character)
        draw_centered_text(self.screen, "ITALIA 2008—2088", self.ui.title_font, YELLOW, (SCREEN_WIDTH // 2, 100))
        draw_centered_text(self.screen, "NEON REBELLION", self.ui.title_font, CYAN, (SCREEN_WIDTH // 2, 145))
        draw_centered_text(self.screen, "RESISTANCE COMMAND // SECURE UPLINK", self.ui.sub_font, GRAY,
                           (SCREEN_WIDTH // 2, 190))
        mouse = pygame.mouse.get_pos()
        has_save = self.save_mgr.has_active_save()
        labels = {"new": "NEW GAME  [N]", "continue": "CONTINUE  [C]", "quit": "QUIT  [Q]"}
        for action, rect in self.menu_rects.items():
            enabled = action != "continue" or has_save
            hover = enabled and rect.collidepoint(mouse)
            border = CYAN if hover else (YELLOW if action == "new" else (
                GREEN if action == "continue" and enabled else RED if action == "quit" else GRAY))
            draw_glass_panel(self.screen, rect, border_color=border, bg_alpha=230 if enabled else 120)
            draw_centered_text(self.screen, labels[action], self.ui.font, WHITE if enabled else GRAY, rect.center)
        data = self.save_mgr.load_game_data()
        footer = f"BEST {data['high_score']:06d}   //   STORIES {len(data['completed_stories'])}/4   //   F10 {'MUTED' if self.sound.muted else 'AUDIO ON'}"
        draw_centered_text(self.screen, footer, self.ui.sub_font, CYAN, (SCREEN_WIDTH // 2, 515))
        draw_centered_text(self.screen, "WASD / ARROWS + MOUSE  •  SPACE FIRE  •  F AUTO-FIRE  •  ESC PAUSE",
                           self.ui.small_font, GRAY, (SCREEN_WIDTH // 2, 590))

    def start_level(self, new_game=True):
        self.sound.stop_music()
        self.sound.play_music("assets/music.ogg", volume=0.45)
        self.level = Level(
            self.screen, character_id=self.selected_character, difficulty=self.difficulty,
            new_game=new_game, save_manager=self.save_mgr, sound=self.sound,
        )
        self.state = "PLAYING"
