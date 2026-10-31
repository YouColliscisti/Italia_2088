import pygame

from src.settings import CYAN, PANEL, WHITE, YELLOW


def draw_glass_panel(surface, rect, border_color=CYAN, bg_alpha=215, fill_color=PANEL):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*fill_color, bg_alpha), panel.get_rect(), border_radius=10)
    pygame.draw.rect(panel, border_color, panel.get_rect(), width=2, border_radius=10)
    pygame.draw.line(panel, (*border_color, 80), (12, 8), (rect.width - 12, 8), 1)
    surface.blit(panel, rect.topleft)


def render_multiline_text(text, font, color, max_width):

    lines = []
    for paragraph in str(text).splitlines() or [""]:
        words = paragraph.split()
        if not words:
            lines.append(font.render("", True, color))
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                lines.append(font.render(current, True, color))
                current = word
        lines.append(font.render(current, True, color))
    return lines


def draw_centered_text(surface, text, font, color, center):
    rendered = font.render(text, True, color)
    surface.blit(rendered, rendered.get_rect(center=center))
    return rendered


class Button:
    def __init__(self, x, y, width, height, text, font, action=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action or text.lower().replace(" ", "_")
        self.enabled = True

    def draw(self, surface, hover=None, color=YELLOW):
        if hover is None:
            hover = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())
        border = CYAN if hover else color
        if not self.enabled:
            border = (75, 85, 105)
        draw_glass_panel(surface, self.rect, border_color=border, bg_alpha=230)
        text_color = WHITE if self.enabled else (100, 110, 125)
        draw_centered_text(surface, self.text, self.font, text_color, self.rect.center)

    def is_clicked(self, event):
        return self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)
