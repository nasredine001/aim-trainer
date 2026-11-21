"""Application shell: window, scene switching, and the main loop."""

from __future__ import annotations

import pygame

from . import config
from .audio import SAMPLE_RATE, Audio
from .scenes import GameScene, MenuScene, ResultsScene
from .stats import RecordResult, RunStats, StatsStore
from .ui import lerp_color


def _make_background() -> pygame.Surface:
    surface = pygame.Surface((config.WIDTH, config.HEIGHT))
    for y in range(config.HEIGHT):
        color = lerp_color(config.BG_TOP, config.BG_BOTTOM, y / (config.HEIGHT - 1))
        pygame.draw.line(surface, color, (0, y), (config.WIDTH, y))

    grid = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    for x in range(0, config.WIDTH, 64):
        pygame.draw.line(grid, (255, 255, 255, 5), (x, 0), (x, config.HEIGHT))
    for y in range(0, config.HEIGHT, 64):
        pygame.draw.line(grid, (255, 255, 255, 5), (0, y), (config.WIDTH, y))
    surface.blit(grid, (0, 0))
    return surface


def _make_icon() -> pygame.Surface:
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(icon, config.ACCENT, (16, 16), 9, 2)
    pygame.draw.circle(icon, config.WHITE, (16, 16), 2)
    for start, end in (
        ((16, 2), (16, 8)),
        ((16, 24), (16, 30)),
        ((2, 16), (8, 16)),
        ((24, 16), (30, 16)),
    ):
        pygame.draw.line(icon, config.ACCENT, start, end, 2)
    return icon


class App:
    def __init__(self, muted: bool = False, stats_path=None):
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(config.TITLE)
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_icon(_make_icon())

        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = Audio(muted=muted)
        self.stats = StatsStore(stats_path)
        self.background = _make_background()
        self.dim = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        self.dim.fill((4, 8, 16, 150))

        self.selected_mode = config.MODE_IDS[0]
        self.selected_duration = config.DEFAULT_DURATION
        self.scene = None
        self.set_scene(MenuScene(self))

    def set_scene(self, scene) -> None:
        if self.scene is not None:
            self.scene.on_exit()
        self.scene = scene
        self.scene.on_enter()

    def show_menu(self) -> None:
        self.set_scene(MenuScene(self))

    def start_run(self, mode: str, duration: int) -> None:
        self.selected_mode = mode
        self.selected_duration = int(duration)
        self.set_scene(GameScene(self, mode, int(duration)))

    def show_results(self, stats: RunStats, record: RecordResult) -> None:
        self.set_scene(ResultsScene(self, stats, record))

    def quit(self) -> None:
        self.running = False

    def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(config.FPS) / 1000.0, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    break
                self.scene.handle_event(event)
            if not self.running:
                break

            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()

    def shutdown(self) -> None:
        pygame.mouse.set_visible(True)
        try:
            pygame.mixer.quit()
        except pygame.error:
            pass
        pygame.quit()
