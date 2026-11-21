"""Central configuration for Aim Trainer."""

from __future__ import annotations

WIDTH = 1280
HEIGHT = 720
FPS = 120
TITLE = "Aim Trainer"

DURATIONS = (15, 30, 60)
DEFAULT_DURATION = 30

TARGET_RADIUS = 44
BULLSEYE_RADIUS = 14
SPAWN_MARGIN = 70
MIN_SPAWN_DISTANCE = 240
HUD_HEIGHT = 78
PLAY_TOP = HUD_HEIGHT + 24

# Palette
BG_TOP = (10, 14, 26)
BG_BOTTOM = (24, 32, 54)
WHITE = (238, 243, 255)
MUTED = (134, 148, 178)
DIM = (72, 84, 110)
ACCENT = (0, 200, 255)
ACCENT_SOFT = (0, 120, 165)
GREEN = (74, 222, 128)
RED = (255, 99, 99)
YELLOW = (250, 204, 21)
PANEL = (24, 32, 50)
PANEL_LIGHT = (34, 44, 68)
BORDER = (48, 60, 88)

MODES = (
    {
        "id": "flick",
        "name": "Flick",
        "tagline": "Static targets. Click them before they blink.",
    },
    {
        "id": "moving",
        "name": "Moving",
        "tagline": "Targets drift and bounce. Lead your shots.",
    },
    {
        "id": "tracking",
        "name": "Tracking",
        "tagline": "Hold fire and keep the crosshair on target.",
    },
)

MODE_IDS = tuple(mode["id"] for mode in MODES)
MODE_NAMES = {mode["id"]: mode["name"] for mode in MODES}
