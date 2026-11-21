"""Short-lived hit, miss, and floating-score effects."""

from __future__ import annotations

import pygame

from . import config
from .ui import get_font


class RingBurst:
    def __init__(
        self,
        x: float,
        y: float,
        color,
        radius: float = 44.0,
        duration: float = 0.35,
    ):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.radius = radius
        self.duration = duration
        self.age = 0.0

    def update(self, dt: float) -> None:
        self.age += dt

    def done(self) -> bool:
        return self.age >= self.duration

    def draw(self, surface: pygame.Surface) -> None:
        t = min(1.0, self.age / self.duration)
        radius = max(3, int(self.radius * (0.6 + 0.8 * t)))
        width = max(1, int(4 * (1.0 - t)))
        alpha = int(230 * (1.0 - t))
        size = radius * 2 + width * 2 + 8
        layer = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            layer,
            (*self.color, alpha),
            (size // 2, size // 2),
            radius,
            width,
        )
        surface.blit(layer, (int(self.x - size / 2), int(self.y - size / 2)))


class MissMark:
    def __init__(self, x: float, y: float, duration: float = 0.38):
        self.x = float(x)
        self.y = float(y)
        self.duration = duration
        self.age = 0.0

    def update(self, dt: float) -> None:
        self.age += dt

    def done(self) -> bool:
        return self.age >= self.duration

    def draw(self, surface: pygame.Surface) -> None:
        t = min(1.0, self.age / self.duration)
        alpha = int(210 * (1.0 - t))
        size = 44
        half = 10
        layer = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        color = (*config.RED, alpha)
        pygame.draw.line(
            layer,
            color,
            (center - half, center - half),
            (center + half, center + half),
            2,
        )
        pygame.draw.line(
            layer,
            color,
            (center - half, center + half),
            (center + half, center - half),
            2,
        )
        surface.blit(layer, (int(self.x - size / 2), int(self.y - size / 2)))


class FloatText:
    def __init__(
        self,
        x: float,
        y: float,
        text: str,
        color,
        size: int = 22,
        duration: float = 0.65,
        rise: float = 42.0,
    ):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.size = size
        self.duration = duration
        self.rise = rise
        self.age = 0.0

    def update(self, dt: float) -> None:
        self.age += dt

    def done(self) -> bool:
        return self.age >= self.duration

    def draw(self, surface: pygame.Surface) -> None:
        t = min(1.0, self.age / self.duration)
        alpha = int(255 * (1.0 - t))
        y = self.y - self.rise * t
        image = get_font(self.size, True).render(self.text, True, self.color)
        image.set_alpha(alpha)
        rect = image.get_rect(center=(int(self.x), int(y)))
        surface.blit(image, rect)
