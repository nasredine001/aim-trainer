"""Shared fonts, drawing helpers, and widgets."""

from __future__ import annotations

import pygame

from . import config

_FONT_NAMES = "bahnschrift,segoeui,arial"
_font_cache: dict[tuple[int, bool], pygame.font.Font] = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (int(size), bool(bold))
    font = _font_cache.get(key)
    if font is None:
        font = pygame.font.SysFont(_FONT_NAMES, int(size), bold=bold)
        _font_cache[key] = font
    return font


def draw_text(
    surface: pygame.Surface,
    text,
    size: int,
    pos,
    color=config.WHITE,
    *,
    bold: bool = False,
    anchor: str = "topleft",
    alpha: int = 255,
) -> pygame.Rect:
    image = get_font(size, bold).render(str(text), True, color)
    if alpha < 255:
        image.set_alpha(alpha)
    rect = image.get_rect(**{anchor: pos})
    surface.blit(image, rect)
    return rect


def lerp_color(first, second, t: float):
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(first, second))


def wrap_lines(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if current and font.size(trial)[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    surface: pygame.Surface,
    text: str,
    size: int,
    color,
    x: int,
    y: int,
    max_width: int,
    *,
    line_height: int | None = None,
    bold: bool = False,
    alpha: int = 255,
) -> int:
    font = get_font(size, bold)
    lines = wrap_lines(text, font, max_width)
    step = line_height or int(size * 1.45)
    for index, line in enumerate(lines):
        draw_text(
            surface,
            line,
            size,
            (x, y + index * step),
            color,
            bold=bold,
            alpha=alpha,
        )
    return y + len(lines) * step


class Button:
    def __init__(self, rect, label: str, *, accent: bool = False, font_size: int = 22):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.accent = accent
        self.font_size = font_size
        self.hovered = False

    def update(self, mouse_pos) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        fill = config.ACCENT if self.accent else config.PANEL_LIGHT
        if self.hovered:
            fill = lerp_color(fill, config.WHITE, 0.16)
        pygame.draw.rect(surface, fill, self.rect, border_radius=12)
        if not self.accent:
            pygame.draw.rect(surface, config.BORDER, self.rect, 1, border_radius=12)
        text_color = (8, 12, 20) if self.accent else config.WHITE
        draw_text(
            surface,
            self.label,
            self.font_size,
            self.rect.center,
            text_color,
            bold=True,
            anchor="center",
        )

    def clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )
