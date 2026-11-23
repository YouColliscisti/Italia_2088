import pygame

from src.settings import CYAN, GRAY, GREEN, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE, YELLOW
from src.ui_helpers import draw_centered_text, draw_glass_panel, render_multiline_text


def display_intro(surface, title_font, sub_font):
    draw_centered_text(surface, "ITALIA 2008—2088", title_font, YELLOW, (SCREEN_WIDTH // 2, 245))
    draw_centered_text(surface, "NEON REBELLION", title_font, CYAN, (SCREEN_WIDTH // 2, 292))


def display_main_menu(surface, font, title_font, sub_font):
    draw_centered_text(surface, "ITALIA 2008—2088", title_font, YELLOW, (SCREEN_WIDTH // 2, 110))
    draw_centered_text(surface, "NEON REBELLION", title_font, CYAN, (SCREEN_WIDTH // 2, 153))
    return []


def draw_character_selection(surface, font, title_font, sub_font, completed_stories_list, character_images=None, difficulty="Normal"):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((3, 5, 15, 215))
    surface.blit(overlay, (0, 0))
    draw_centered_text(surface, "CHOOSE YOUR OPERATIVE", title_font, YELLOW, (SCREEN_WIDTH // 2, 34))
    draw_centered_text(surface, f"LIBERATED STORIES {len(completed_stories_list)}/4", sub_font, GREEN, (SCREEN_WIDTH // 2, 70))

    card_w, card_h = 440, 205
    positions = [(30, 100), (490, 100), (30, 320), (490, 320)]
    characters = [
        (1, "BEATRICE", "PIERCING BEAM", "A needle interceptor firing beams that penetrate up to five targets.", CYAN),
        (2, "SIMON", "TWIN SPREAD + HYPER DASH", "Split-wing runner with angled twin neon lasers and evasive dash.", YELLOW),
        (3, "SOFIA", "PULSE CHARGES + AEGIS", "Armored gunship firing splash-damage pulses behind a rechargeable shield.", GREEN),
        (4, "ELIAS", "RICOCHET DISKS + ANARCHY", "Heavy launcher with energy disks that rebound between ships and walls.", RED),
    ]
    mouse = pygame.mouse.get_pos()
    rects = []
    for (cid, name, ability, description, color), (x, y) in zip(characters, positions):
        rect = pygame.Rect(x, y, card_w, card_h)
        rects.append((rect, cid))
        hover = rect.collidepoint(mouse)
        completed = cid in completed_stories_list
        draw_glass_panel(surface, rect, border_color=WHITE if hover else color, bg_alpha=240)
        if character_images and character_images.get(cid):
            surface.blit(character_images[cid], (x + 18, y + 52))
        tx = x + 122
        surface.blit(font.render(f"[{cid}] {name}", True, color), (tx, y + 20))
        status = "STORY LIBERATED" if completed else ability
        surface.blit(sub_font.render(status, True, GREEN if completed else WHITE), (tx, y + 54))
        line_y = y + 86
        for line in render_multiline_text(description, sub_font, GRAY, card_w - 142):
            surface.blit(line, (tx, line_y))
            line_y += 20
        if completed:
            surface.blit(sub_font.render(ability, True, color), (tx, y + 158))

    difficulty_rect = pygame.Rect(315, 543, 330, 38)
    draw_glass_panel(surface, difficulty_rect, border_color=CYAN if difficulty_rect.collidepoint(mouse) else GRAY)
    draw_centered_text(surface, f"DIFFICULTY: {difficulty.upper()}  [D / CLICK]", sub_font, WHITE, difficulty_rect.center)
    draw_centered_text(surface, "CLICK / 1—4 TO DEPLOY  •  ESC FOR MAIN MENU", sub_font, CYAN, (SCREEN_WIDTH // 2, 610))
    return rects, difficulty_rect


def display_backstory(surface, font, title_font, sub_font, portrait, operative_name, story):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((2, 4, 14, 242))
    surface.blit(overlay, (0, 0))
    draw_centered_text(surface, "OPERATIVE DOSSIER // RESISTANCE ARCHIVE", title_font, YELLOW, (SCREEN_WIDTH // 2, 42))
    panel = pygame.Rect(70, 82, 820, 480)
    draw_glass_panel(surface, panel, border_color=CYAN, bg_alpha=245)
    if portrait:
        portrait_large = pygame.transform.smoothscale(portrait, (112, 112))
        surface.blit(portrait_large, (102, 112))
    surface.blit(font.render(operative_name, True, CYAN), (240, 116))
    for index, line in enumerate(render_multiline_text(story["role"], sub_font, GREEN, 610)):
        surface.blit(line, (240, 153 + index * 19))

    sections = (("BACKGROUND", story["background"], 215), ("PERSONAL MOTIVATION", story["motivation"], 323),
                ("RESISTANCE CONNECTION", story["connection"], 420))
    for label, text, y in sections:
        surface.blit(sub_font.render(label, True, YELLOW), (102, y))
        line_y = y + 25
        for line in render_multiline_text(text, sub_font, WHITE, 750):
            surface.blit(line, (102, line_y))
            line_y += 20
    draw_centered_text(surface, "SPACE / CLICK TO OPEN PROLOGUE  •  ESC TO SKIP", sub_font, CYAN, (SCREEN_WIDTH // 2, 600))


def display_pause(surface, font, title_font, sub_font):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 8, 205))
    surface.blit(overlay, (0, 0))
    draw_centered_text(surface, "SYSTEM PAUSED", title_font, YELLOW, (SCREEN_WIDTH // 2, 145))
    draw_centered_text(surface, "ESC / P TO RESUME", sub_font, GRAY, (SCREEN_WIDTH // 2, 188))
    actions = (("RESUME", "resume"), ("SAVE GAME", "save"), ("SAVE & MAIN MENU", "main_menu"), ("QUIT GAME", "quit"))
    rects = []
    for index, (label, action) in enumerate(actions):
        rect = pygame.Rect(330, 225 + index * 68, 300, 48)
        draw_glass_panel(surface, rect, border_color=CYAN if rect.collidepoint(pygame.mouse.get_pos()) else (RED if action == "quit" else GRAY))
        draw_centered_text(surface, label, font, WHITE, rect.center)
        rects.append((rect, action))
    return rects


def display_game_over(surface, title_font, sub_font, score=0, reason=""):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((25, 0, 10, 220))
    surface.blit(overlay, (0, 0))
    draw_centered_text(surface, "CONNECTION SEVERED", title_font, RED, (SCREEN_WIDTH // 2, 225))
    draw_centered_text(surface, reason or "OPERATIVE SHIP DESTROYED", sub_font, YELLOW, (SCREEN_WIDTH // 2, 278))
    draw_centered_text(surface, f"RUN SCORE: {score:06d}", sub_font, WHITE, (SCREEN_WIDTH // 2, 315))
    draw_centered_text(surface, "R: RETRY MISSION  •  M: MAIN MENU  •  Q: QUIT", sub_font, YELLOW, (SCREEN_WIDTH // 2, 370))


def display_victory(surface, font, sub_font, completed_count, score=0, character_name=""):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 22, 18, 230))
    surface.blit(overlay, (0, 0))
    draw_centered_text(surface, "ITALIA LIBERATA", font, GREEN, (SCREEN_WIDTH // 2, 210))
    draw_centered_text(surface, f"{character_name.upper()} // STORY COMPLETE", sub_font, CYAN, (SCREEN_WIDTH // 2, 260))
    draw_centered_text(surface, f"FINAL SCORE {score:06d}  •  STORIES {completed_count}/4", sub_font, WHITE, (SCREEN_WIDTH // 2, 305))
    draw_centered_text(surface, "SPACE / CLICK: CHOOSE ANOTHER OPERATIVE", sub_font, YELLOW, (SCREEN_WIDTH // 2, 370))
