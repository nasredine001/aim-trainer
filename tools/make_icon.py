"""Render the Aim Trainer app icon (assets/icon.png + assets/icon.ico)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from aimtrainer import config  # noqa: E402

ASSETS = ROOT / "assets"
SIZE = 256
SCALE = 4
BIG = SIZE * SCALE


def main() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))

    surface = pygame.Surface((BIG, BIG), pygame.SRCALPHA)
    center = BIG // 2

    # Soft outer glow
    pygame.draw.circle(
        surface, (*config.ACCENT, 28), (center, center), int(126 * SCALE)
    )

    # Badge body and rim
    pygame.draw.circle(surface, (14, 20, 34), (center, center), int(116 * SCALE))
    pygame.draw.circle(
        surface, config.ACCENT, (center, center), int(116 * SCALE), int(7 * SCALE)
    )

    # Crosshair rings
    pygame.draw.circle(
        surface, config.ACCENT, (center, center), int(70 * SCALE), int(8 * SCALE)
    )
    pygame.draw.circle(
        surface, (70, 90, 124), (center, center), int(44 * SCALE), int(4 * SCALE)
    )

    # Crosshair ticks
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        start = (center + dx * int(88 * SCALE), center + dy * int(88 * SCALE))
        end = (center + dx * int(108 * SCALE), center + dy * int(108 * SCALE))
        pygame.draw.line(surface, config.ACCENT, start, end, int(8 * SCALE))

    # Bullseye
    pygame.draw.circle(surface, (255, 99, 99), (center, center), int(24 * SCALE))
    pygame.draw.circle(surface, (255, 186, 186), (center, center), int(14 * SCALE))
    pygame.draw.circle(surface, config.WHITE, (center, center), int(5 * SCALE))

    icon = pygame.transform.smoothscale(surface, (SIZE, SIZE))

    ASSETS.mkdir(parents=True, exist_ok=True)
    png_path = ASSETS / "icon.png"
    pygame.image.save(icon, str(png_path))

    image = Image.open(png_path).convert("RGBA")
    image.save(
        ASSETS / "icon.ico",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )

    pygame.quit()
    print(f"Wrote {png_path}")
    print(f"Wrote {ASSETS / 'icon.ico'}")


if __name__ == "__main__":
    main()
