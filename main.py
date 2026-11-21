"""Aim Trainer - entry point.

Run with:

    python main.py
"""

from __future__ import annotations

import argparse
import sys


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Aim Trainer - a pygame aim trainer with flick, moving, and tracking modes."
    )
    parser.add_argument(
        "--mute",
        action="store_true",
        help="start with sound disabled",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    try:
        import pygame
    except ImportError:
        print(
            "pygame is required. Install it with:\n\n"
            "    python -m pip install -r requirements.txt\n"
        )
        return 1

    from aimtrainer.app import App

    try:
        app = App(muted=args.mute)
    except pygame.error as exc:
        print(f"Could not open a game window: {exc}")
        return 1

    try:
        app.run()
    finally:
        app.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
