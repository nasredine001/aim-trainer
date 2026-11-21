"""Target entity and spawn helpers."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from . import config


@dataclass
class Target:
    x: float
    y: float
    radius: float = config.TARGET_RADIUS
    vx: float = 0.0
    vy: float = 0.0
    age: float = 0.0

    def contains(self, point) -> bool:
        dx = point[0] - self.x
        dy = point[1] - self.y
        return dx * dx + dy * dy <= self.radius * self.radius

    def is_bullseye(self, point) -> bool:
        dx = point[0] - self.x
        dy = point[1] - self.y
        return dx * dx + dy * dy <= config.BULLSEYE_RADIUS**2

    def update(self, dt: float) -> None:
        self.age += dt
        if self.vx == 0.0 and self.vy == 0.0:
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        left = config.SPAWN_MARGIN + self.radius
        right = config.WIDTH - config.SPAWN_MARGIN - self.radius
        top = config.PLAY_TOP + self.radius
        bottom = config.HEIGHT - config.SPAWN_MARGIN - self.radius

        if self.x < left:
            self.x = left
            self.vx = abs(self.vx)
        elif self.x > right:
            self.x = right
            self.vx = -abs(self.vx)
        if self.y < top:
            self.y = top
            self.vy = abs(self.vy)
        elif self.y > bottom:
            self.y = bottom
            self.vy = -abs(self.vy)

    def draw(self, surface: pygame.Surface, highlight: bool = False) -> None:
        growth = min(1.0, self.age / 0.14)
        growth = 1.0 - (1.0 - growth) ** 3
        radius = max(5, int(self.radius * growth))
        center = (int(self.x), int(self.y))

        if highlight:
            glow_size = radius * 2 + 28
            glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(
                glow,
                (*config.GREEN, 40),
                (radius + 14, radius + 14),
                radius + 8,
            )
            surface.blit(glow, (center[0] - radius - 14, center[1] - radius - 14))
            pygame.draw.circle(surface, config.GREEN, center, radius + 6, 2)

        pygame.draw.circle(surface, (15, 23, 37), center, radius)
        pygame.draw.circle(surface, config.ACCENT, center, radius, 3)
        pygame.draw.circle(surface, (70, 90, 124), center, int(radius * 0.66), 2)

        bullseye = max(2, int(config.BULLSEYE_RADIUS * growth))
        pygame.draw.circle(surface, (255, 99, 99), center, bullseye)
        pygame.draw.circle(surface, (255, 186, 186), center, max(1, int(bullseye * 0.55)))
        pygame.draw.circle(surface, config.WHITE, center, max(1, int(bullseye * 0.22)))


def spawn_target(mode: str, rng: random.Random, avoid=()) -> Target:
    """Spawn a target away from the cursor (and the previous target)."""
    radius = config.TARGET_RADIUS
    left = config.SPAWN_MARGIN + radius
    right = config.WIDTH - config.SPAWN_MARGIN - radius
    top = config.PLAY_TOP + radius
    bottom = config.HEIGHT - config.SPAWN_MARGIN - radius

    x = rng.uniform(left, right)
    y = rng.uniform(top, bottom)
    for _ in range(80):
        candidate_x = rng.uniform(left, right)
        candidate_y = rng.uniform(top, bottom)
        if all(
            math.hypot(candidate_x - ax, candidate_y - ay)
            >= config.MIN_SPAWN_DISTANCE
            for ax, ay in avoid
        ):
            x, y = candidate_x, candidate_y
            break

    target = Target(x, y)
    if mode in ("moving", "tracking"):
        angle = rng.uniform(0.0, math.tau)
        if mode == "moving":
            speed = rng.uniform(140.0, 240.0)
        else:
            speed = rng.uniform(170.0, 260.0)
        target.vx = math.cos(angle) * speed
        target.vy = math.sin(angle) * speed
    return target
