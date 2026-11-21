"""Headless end-to-end test: menu -> run -> results.

SDL's dummy drivers let this run without a display or sound card.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import pygame
except ImportError:  # pragma: no cover - exercised only without pygame
    pygame = None


@unittest.skipIf(pygame is None, "pygame is not installed")
class SmokeTest(unittest.TestCase):
    def test_menu_then_run_then_results(self):
        from aimtrainer.app import App

        with tempfile.TemporaryDirectory() as temp_dir:
            app = App(muted=True, stats_path=Path(temp_dir) / "stats.json")
            try:
                app.scene.update(1 / 60)
                app.scene.draw(app.screen)
                self.assertEqual(type(app.scene).__name__, "MenuScene")

                app.start_run("flick", 5)
                scene = app.scene
                for _ in range(240):
                    scene.update(1 / 60)
                self.assertEqual(scene.phase, "playing")
                self.assertIsNotNone(scene.target)

                target = scene.target
                scene._shoot((target.x, target.y))
                self.assertEqual(scene.stats.hits, 1)
                self.assertGreater(scene.stats.score, 0)
                self.assertGreater(len(scene.stats.reaction_times), 0)

                for _ in range(400):
                    if app.scene is not scene:
                        break
                    scene.update(1 / 60)

                self.assertIsNot(app.scene, scene)
                self.assertEqual(type(app.scene).__name__, "ResultsScene")
                app.scene.draw(app.screen)
            finally:
                app.shutdown()


if __name__ == "__main__":
    unittest.main()
