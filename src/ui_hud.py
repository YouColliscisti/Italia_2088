import pygame

from src.settings import CYAN, GRAY, GREEN, RED, WHITE, YELLOW
from src.ui_helpers import draw_glass_panel, render_multiline_text


def display_hud(surface, font, sub_font, score, high_score, level, max_levels, is_boss_level, ultimate_ready, objective_text=""):
    top = pygame.Rect(12, 10, surface.get_width() - 24, 58)
    draw_glass_panel(surface, top, border_color=(45, 85, 125), bg_alpha=190)
    surface.blit(sub_font.render(f"SCORE {score:06d}  //  BEST {high_score:06d}", True, WHITE), (26, 20))
    stage = sub_font.render(f"SECTOR {level}/{max_levels}", True, YELLOW)
    surface.blit(stage, (surface.get_width() - stage.get_width() - 26, 20))
    if objective_text:
        lines = render_multiline_text(objective_text, sub_font, CYAN, 520)
        surface.blit(lines[0], (26, 43))


def display_objective_progress(surface, sub_font, mission):
    text = mission.progress_text
    color = RED if mission.time_remaining is not None and mission.time_remaining < 12 else GREEN
    progress = sub_font.render(text, True, color)
    center_x = surface.get_width() // 2 + 105
    surface.blit(progress, (center_x - progress.get_width() // 2, 19))
    width = 185
    ratio = max(0.0, min(1.0, mission.progress_ratio))
    pygame.draw.rect(surface, (35, 50, 65), (center_x - width // 2, 46, width, 6), border_radius=3)
    if ratio > 0:
        pygame.draw.rect(surface, color, (center_x - width // 2, 46, int(width * ratio), 6), border_radius=3)


def display_mission_progress(surface, font, sub_font, current_kills, required_kills):
    """Compatibility helper for older callers."""
    text = "DESTROY THE CORE" if required_kills <= 0 else f"HOSTILES {current_kills}/{required_kills}"
    color = RED if required_kills <= 0 else GREEN
    progress = sub_font.render(text, True, color)
    surface.blit(progress, (surface.get_width() // 2 - progress.get_width() // 2, 20))


def display_health(surface, sub_font, current_health, max_health):
    x, y, width = 22, surface.get_height() - 43, 210
    surface.blit(sub_font.render(f"HULL {int(current_health)}/{max_health}", True, WHITE), (x, y - 19))
    pygame.draw.rect(surface, (45, 25, 40), (x, y, width, 15), border_radius=5)
    ratio = max(0, current_health) / max_health
    color = GREEN if ratio > 0.5 else (YELLOW if ratio > 0.25 else RED)
    if ratio > 0:
        pygame.draw.rect(surface, color, (x, y, int(width * ratio), 15), border_radius=5)
    pygame.draw.rect(surface, WHITE, (x, y, width, 15), width=1, border_radius=5)


def display_shield(surface, sub_font, player):
    if player.max_shield <= 0:
        return
    x, y, width = 245, surface.get_height() - 43, 120
    surface.blit(sub_font.render("SHIELD", True, CYAN), (x, y - 19))
    pygame.draw.rect(surface, (20, 40, 55), (x, y, width, 15), border_radius=5)
    ratio = max(0, player.shield) / player.max_shield
    if ratio:
        pygame.draw.rect(surface, CYAN, (x, y, int(width * ratio), 15), border_radius=5)
    pygame.draw.rect(surface, WHITE, (x, y, width, 15), width=1, border_radius=5)


def display_ability(surface, sub_font, player, charge, threshold):
    if player.character_id == 1:
        text, color = "PIERCING BEAM // PASSIVE", YELLOW
    elif player.character_id == 2:
        dash = "DASH READY" if player.dash_ready else f"DASH {player.dash_cooldown:.1f}s"
        text, color = f"TWIN SPREAD // {dash}", YELLOW if player.dash_ready else GRAY
    elif player.character_id == 3:
        text, color = "PULSE CHARGES // AEGIS SHIELD", GREEN
    else:
        text = "RICOCHET DISKS // ANARCHY READY [E]" if charge >= threshold else f"RICOCHET DISKS // CHARGE {charge}/{threshold}"
        color = RED if charge >= threshold else GRAY
    rendered = sub_font.render(text, True, color)
    surface.blit(rendered, (surface.get_width() - rendered.get_width() - 22, surface.get_height() - 36))


def display_boss_health(surface, sub_font, boss):
    width, height = 480, 18
    x = (surface.get_width() - width) // 2
    y = 84
    phase = "ENRAGED // PHASE III" if boss.phase == 3 else f"PHASE {boss.phase}"
    label = sub_font.render(f"{boss.name} // {phase}", True, RED if boss.enraged else YELLOW)
    surface.blit(label, (x, y - 21))
    pygame.draw.rect(surface, (50, 12, 28), (x, y, width, height), border_radius=5)
    ratio = max(0, boss.health) / boss.max_health
    if ratio:
        pygame.draw.rect(surface, RED, (x, y, int(width * ratio), height), border_radius=5)
    pygame.draw.rect(surface, YELLOW, (x, y, width, height), width=1, border_radius=5)
