import pygame

from src.settings import CYAN, GRAY, GREEN, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE, YELLOW
from src.ui_helpers import draw_glass_panel, render_multiline_text


CITY_MARKERS = {
    "milan": (0.39, 0.12), "venice": (0.60, 0.15), "rome": (0.51, 0.55),
    "turin": (0.30, 0.12), "bologna": (0.47, 0.30), "florence": (0.46, 0.39),
    "naples": (0.60, 0.72), "omnia": (0.51, 0.55),
    "milano": (0.39, 0.12), "venezia": (0.60, 0.15), "roma": (0.51, 0.55),
    "torino": (0.30, 0.12), "firenze": (0.46, 0.39), "napoli": (0.60, 0.72),
    "core central": (0.51, 0.55),
}


def marker_for_city(city):
    lowered = city.lower()
    for name, point in CITY_MARKERS.items():
        if name in lowered:
            return point
    return None


def display_mission_briefing(surface, font, sub_font, map_image, level, city_name, description, objective, char_name, route=None):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((3, 5, 15, 225))
    surface.blit(overlay, (0, 0))
    title = font.render(f"MISSION {level:02d} // {city_name.upper()}", True, YELLOW)
    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 42)))

    panel = pygame.Rect(48, 82, 585, 405)
    draw_glass_panel(surface, panel, border_color=CYAN)
    surface.blit(font.render(f"OPERATIVE: {char_name.upper()}", True, GREEN), (72, 110))
    surface.blit(sub_font.render("SITUATION", True, YELLOW), (72, 158))
    y = 184
    for line in render_multiline_text(description, sub_font, WHITE, panel.width - 48):
        surface.blit(line, (72, y))
        y += 22
    y += 20
    surface.blit(sub_font.render("PRIMARY OBJECTIVE", True, YELLOW), (72, y))
    y += 27
    for line in render_multiline_text(objective, sub_font, CYAN, panel.width - 48):
        surface.blit(line, (72, y))
        y += 22
    surface.blit(sub_font.render("LOADOUT: auto-fire enabled  //  F to toggle", True, GRAY), (72, 430))

    map_panel = pygame.Rect(655, 82, 257, 405)
    draw_glass_panel(surface, map_panel, border_color=YELLOW)
    surface.blit(sub_font.render("CAMPAIGN // ITALIA", True, YELLOW), (682, 110))
    if map_image:
        map_rect = map_image.get_rect(center=(map_panel.centerx, 280))
        surface.blit(map_image, map_rect)
        route = route or [city_name]
        points = []
        for stage, route_city in enumerate(route, 1):
            marker = marker_for_city(route_city)
            if marker:
                points.append((stage, (map_rect.x + int(marker[0] * map_rect.width), map_rect.y + int(marker[1] * map_rect.height))))
        for index in range(1, len(points)):
            previous_stage, previous = points[index - 1]
            stage, current = points[index]
            if stage <= level:
                pygame.draw.line(surface, GREEN, previous, current, 2)
        for stage, point in points:
            if stage < level:
                color, radius = GREEN, 5
            elif stage == level:
                color, radius = YELLOW, 10
            else:
                color, radius = GRAY, 4
            pygame.draw.circle(surface, (5, 10, 20), point, radius + 2)
            pygame.draw.circle(surface, color, point, radius, width=2 if stage == level else 0)
            if stage == level:
                pygame.draw.circle(surface, WHITE, point, 3)
                number = sub_font.render(str(stage), True, YELLOW)
                surface.blit(number, (point[0] + 11, point[1] - 9))
    else:
        surface.blit(sub_font.render("[MAP OFFLINE]", True, GRAY), (710, 280))
    surface.blit(sub_font.render(city_name.upper(), True, WHITE), (678, 400))
    surface.blit(sub_font.render("GREEN: LIBERATED", True, GREEN), (678, 425))
    surface.blit(sub_font.render("YELLOW: CURRENT", True, YELLOW), (678, 445))
    surface.blit(sub_font.render("GRAY: LOCKED", True, GRAY), (678, 465))


def display_story_dialogue(surface, font, sub_font, speaker, message, city_title):
    box = pygame.Rect(90, SCREEN_HEIGHT - 190, SCREEN_WIDTH - 180, 160)
    draw_glass_panel(surface, box, border_color=YELLOW, bg_alpha=245)
    surface.blit(sub_font.render(f"ENCRYPTED COMMUNIQUE // {city_title}", True, CYAN), (box.x + 22, box.y + 15))
    surface.blit(font.render(f"{speaker}:", True, YELLOW), (box.x + 22, box.y + 43))
    y = box.y + 74
    for line in render_multiline_text(message, sub_font, WHITE, box.width - 44):
        surface.blit(line, (box.x + 22, y))
        y += 21
    prompt = sub_font.render("SPACE / CLICK TO CONTINUE", True, GRAY)
    surface.blit(prompt, (box.right - prompt.get_width() - 18, box.bottom - 24))
