"""Menu, gameplay, and results screens."""

from __future__ import annotations

import math
import random

import pygame

from . import config
from .effects import FloatText, MissMark, RingBurst
from .stats import RecordResult, RunStats
from .targets import Target, spawn_target
from .ui import Button, draw_text, draw_wrapped, get_font, lerp_color


class Scene:
    def __init__(self, app):
        self.app = app

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass


class MenuScene(Scene):
    CARD_WIDTH = 350
    CARD_HEIGHT = 196
    CARD_GAP = 24
    CARD_TOP = 232

    def __init__(self, app):
        super().__init__(app)
        total = (
            len(config.MODES) * self.CARD_WIDTH
            + (len(config.MODES) - 1) * self.CARD_GAP
        )
        left = (config.WIDTH - total) // 2
        self.left = left

        self.cards: list[tuple[pygame.Rect, dict]] = []
        for index, mode in enumerate(config.MODES):
            rect = pygame.Rect(
                left + index * (self.CARD_WIDTH + self.CARD_GAP),
                self.CARD_TOP,
                self.CARD_WIDTH,
                self.CARD_HEIGHT,
            )
            self.cards.append((rect, mode))

        self.duration_rects: list[tuple[pygame.Rect, int]] = []
        pill_width, pill_height = 92, 46
        pill_left = left + 132
        for index, duration in enumerate(config.DURATIONS):
            rect = pygame.Rect(
                pill_left + index * (pill_width + 12),
                488,
                pill_width,
                pill_height,
            )
            self.duration_rects.append((rect, duration))

        self.start_button = Button(
            (0, 0, 300, 62), "START TRAINING", accent=True, font_size=24
        )
        self.start_button.rect.center = (config.WIDTH // 2, 590)

    def on_enter(self) -> None:
        pygame.mouse.set_visible(True)

    def _duration_index(self) -> int:
        try:
            return config.DURATIONS.index(self.app.selected_duration)
        except ValueError:
            return 0

    def _start(self) -> None:
        self.app.start_run(self.app.selected_mode, self.app.selected_duration)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.quit()
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.app.selected_mode = config.MODE_IDS[event.key - pygame.K_1]
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                step = -1 if event.key == pygame.K_LEFT else 1
                index = (self._duration_index() + step) % len(config.DURATIONS)
                self.app.selected_duration = config.DURATIONS[index]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._start()
            elif event.key == pygame.K_s:
                self.app.audio.toggle()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, mode in self.cards:
                if rect.collidepoint(event.pos):
                    self.app.selected_mode = mode["id"]
                    return
            for rect, duration in self.duration_rects:
                if rect.collidepoint(event.pos):
                    self.app.selected_duration = duration
                    return
            if self.start_button.rect.collidepoint(event.pos):
                self._start()

    def update(self, dt: float) -> None:
        self.start_button.update(pygame.mouse.get_pos())

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.app.background, (0, 0))
        mouse = pygame.mouse.get_pos()

        title_font = get_font(64, True)
        aim = title_font.render("AIM", True, config.ACCENT)
        trainer = title_font.render(" TRAINER", True, config.WHITE)
        total = aim.get_width() + trainer.get_width()
        x = (config.WIDTH - total) // 2
        surface.blit(aim, (x, 58))
        surface.blit(trainer, (x + aim.get_width(), 58))

        draw_text(
            surface,
            "Sharpen your flicks. Track clean. Beat your best.",
            18,
            (config.WIDTH // 2, 150),
            config.MUTED,
            anchor="center",
        )

        draw_text(
            surface,
            "SELECT MODE",
            14,
            (self.left, 196),
            config.MUTED,
            bold=True,
            anchor="midleft",
        )

        for rect, mode in self.cards:
            selected = mode["id"] == self.app.selected_mode
            hovered = rect.collidepoint(mouse)
            fill = config.PANEL_LIGHT if selected else config.PANEL
            if hovered and not selected:
                fill = lerp_color(fill, config.WHITE, 0.05)
            pygame.draw.rect(surface, fill, rect, border_radius=16)

            border = config.BORDER
            if selected:
                border = config.ACCENT
            elif hovered:
                border = lerp_color(config.BORDER, config.WHITE, 0.25)
            pygame.draw.rect(
                surface,
                border,
                rect,
                2 if selected else 1,
                border_radius=16,
            )

            name_color = config.ACCENT if selected else config.WHITE
            draw_text(
                surface,
                mode["name"].upper(),
                27,
                (rect.x + 26, rect.y + 26),
                name_color,
                bold=True,
            )
            draw_wrapped(
                surface,
                mode["tagline"],
                16,
                config.MUTED,
                rect.x + 26,
                rect.y + 78,
                rect.width - 52,
                line_height=24,
            )

            best = self.app.stats.best(mode["id"])
            if best > 0:
                draw_text(
                    surface,
                    f"BEST  {best:,}",
                    14,
                    (rect.x + 26, rect.bottom - 40),
                    config.MUTED,
                    bold=True,
                )
            else:
                draw_text(
                    surface,
                    "NO RUNS YET",
                    14,
                    (rect.x + 26, rect.bottom - 40),
                    config.DIM,
                    bold=True,
                )

            if selected:
                pygame.draw.circle(
                    surface, config.ACCENT, (rect.right - 27, rect.y + 28), 5
                )

        draw_text(
            surface,
            "DURATION",
            14,
            (self.left, 511),
            config.MUTED,
            bold=True,
            anchor="midleft",
        )
        for rect, duration in self.duration_rects:
            selected = duration == self.app.selected_duration
            hovered = rect.collidepoint(mouse)
            fill = config.ACCENT if selected else config.PANEL
            if hovered and not selected:
                fill = config.PANEL_LIGHT
            pygame.draw.rect(surface, fill, rect, border_radius=12)
            if not selected:
                pygame.draw.rect(surface, config.BORDER, rect, 1, border_radius=12)
            color = (8, 12, 20) if selected else (
                config.WHITE if hovered else config.MUTED
            )
            draw_text(
                surface,
                f"{duration}s",
                20,
                rect.center,
                color,
                bold=True,
                anchor="center",
            )

        self.start_button.draw(surface)

        draw_text(
            surface,
            "Left click to shoot   ·   Hold LMB to track   ·   1-3 pick mode   ·   S sound   ·   Esc quit",
            14,
            (config.WIDTH // 2, 682),
            config.DIM,
            anchor="center",
        )
        draw_text(
            surface,
            "v1.0.0",
            12,
            (32, 682),
            config.DIM,
            bold=True,
            anchor="midleft",
        )

        if not self.app.audio.enabled:
            status, color = "SOUND N/A", config.DIM
        elif self.app.audio.muted:
            status, color = "SOUND OFF", config.DIM
        else:
            status, color = "SOUND ON", config.ACCENT_SOFT
        draw_text(
            surface,
            status,
            12,
            (config.WIDTH - 32, 682),
            color,
            bold=True,
            anchor="midright",
        )


class GameScene(Scene):
    COUNTDOWN = 3.0
    GO_TIME = 0.55

    def __init__(self, app, mode: str, duration: int):
        super().__init__(app)
        self.mode = mode
        self.duration = float(duration)
        self.rng = random.Random()
        self.stats = RunStats(mode=mode, duration=float(duration))
        self.target: Target | None = None
        self.effects: list = []
        self.phase = "countdown"
        self.countdown = self.COUNTDOWN
        self.last_count = int(math.ceil(self.countdown))
        self.go_timer = 0.0
        self.go_started = False
        self.elapsed = 0.0
        self.time_left = float(duration)
        self.spawn_time = 0.0
        self.finished = False
        self.firing = False
        self.on_target = False

    def on_enter(self) -> None:
        pygame.mouse.set_visible(False)

    def on_exit(self) -> None:
        pygame.mouse.set_visible(True)

    def _begin(self) -> None:
        self.phase = "playing"
        self.elapsed = 0.0
        self.time_left = self.duration
        self._spawn_target()

    def _spawn_target(self) -> None:
        avoid = [pygame.mouse.get_pos()]
        if self.target is not None:
            avoid.append((self.target.x, self.target.y))
        self.target = spawn_target(self.mode, self.rng, avoid)
        self.spawn_time = self.elapsed

    def _update_effects(self, dt: float) -> None:
        for effect in self.effects:
            effect.update(dt)
        self.effects = [effect for effect in self.effects if not effect.done()]

    def _update_tracking(self, dt: float) -> None:
        mouse = pygame.mouse.get_pos()
        self.firing = pygame.mouse.get_pressed(3)[0]
        self.on_target = bool(self.target and self.target.contains(mouse))
        if self.firing:
            self.stats.fire_time += dt
            if self.on_target:
                self.stats.on_target_time += dt
        self.stats.score = int(self.stats.on_target_time * 100)

    def _shoot(self, pos) -> None:
        self.stats.shots += 1
        target = self.target
        if target is not None and target.contains(pos):
            bullseye = target.is_bullseye(pos)
            self.stats.hits += 1
            self.stats.reaction_times.append(max(0.0, self.elapsed - self.spawn_time))
            if bullseye:
                self.stats.bullseyes += 1
            gain = 150 if bullseye else 100
            self.stats.score += gain
            color = config.YELLOW if bullseye else config.ACCENT
            self.effects.append(
                RingBurst(
                    pos[0],
                    pos[1],
                    color,
                    radius=target.radius,
                    duration=0.35,
                )
            )
            self.effects.append(
                FloatText(
                    pos[0],
                    pos[1] - 26,
                    f"+{gain}",
                    config.YELLOW if bullseye else config.WHITE,
                    size=22,
                )
            )
            self.app.audio.play("bullseye" if bullseye else "hit")
            self._spawn_target()
        else:
            self.stats.misses += 1
            self.stats.score = max(0, self.stats.score - 25)
            self.effects.append(MissMark(pos[0], pos[1]))
            self.app.audio.play("miss")

    def _finish(self) -> None:
        if self.finished:
            return
        self.finished = True
        self.phase = "done"
        if self.mode == "tracking":
            self.stats.score = int(self.stats.on_target_time * 100)
        record = self.app.stats.record(self.stats)
        self.app.show_results(self.stats, record)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.phase == "playing":
                self._finish()
            else:
                self.app.show_menu()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.phase == "playing" and self.mode in ("flick", "moving"):
                self._shoot(event.pos)

    def update(self, dt: float) -> None:
        self._update_effects(dt)

        if self.phase == "countdown":
            self.countdown -= dt
            if self.countdown > 0:
                current = int(math.ceil(self.countdown))
                if current < self.last_count:
                    self.last_count = current
                    self.app.audio.play("beep")
            else:
                if not self.go_started:
                    self.go_started = True
                    self.go_timer = self.GO_TIME
                    self.app.audio.play("go")
                self.go_timer -= dt
                if self.go_timer <= 0:
                    self._begin()
            return

        if self.phase != "playing":
            return

        self.elapsed += dt
        self.time_left = max(0.0, self.duration - self.elapsed)
        if self.target is not None:
            self.target.update(dt)
        if self.mode == "tracking":
            self._update_tracking(dt)
        if self.time_left <= 0.0:
            self._finish()

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.app.background, (0, 0))

        if self.target is not None and self.phase != "done":
            highlight = self.mode == "tracking" and self.firing and self.on_target
            self.target.draw(surface, highlight=highlight)

        for effect in self.effects:
            effect.draw(surface)

        self._draw_hud(surface)

        if self.phase == "countdown":
            surface.blit(self.app.dim, (0, 0))
            if self.countdown > 0:
                number = max(1, int(math.ceil(self.countdown)))
                draw_text(
                    surface,
                    str(number),
                    150,
                    (config.WIDTH // 2, config.HEIGHT // 2 - 16),
                    config.WHITE,
                    bold=True,
                    anchor="center",
                )
                draw_text(
                    surface,
                    "GET READY",
                    18,
                    (config.WIDTH // 2, config.HEIGHT // 2 + 92),
                    config.MUTED,
                    bold=True,
                    anchor="center",
                )
            else:
                draw_text(
                    surface,
                    "GO",
                    140,
                    (config.WIDTH // 2, config.HEIGHT // 2),
                    config.ACCENT,
                    bold=True,
                    anchor="center",
                )

        self._draw_crosshair(surface)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        strip = pygame.Surface((config.WIDTH, config.HUD_HEIGHT), pygame.SRCALPHA)
        strip.fill((8, 12, 22, 195))
        surface.blit(strip, (0, 0))
        pygame.draw.line(
            surface,
            config.BORDER,
            (0, config.HUD_HEIGHT),
            (config.WIDTH, config.HUD_HEIGHT),
        )

        fraction = 0.0
        if self.duration > 0:
            fraction = max(0.0, min(1.0, self.time_left / self.duration))
        bar_color = config.RED if self.time_left <= 5 else config.ACCENT
        pygame.draw.rect(
            surface,
            (30, 40, 60),
            (0, config.HUD_HEIGHT - 3, config.WIDTH, 3),
        )
        pygame.draw.rect(
            surface,
            bar_color,
            (0, config.HUD_HEIGHT - 3, int(config.WIDTH * fraction), 3),
        )

        draw_text(
            surface,
            config.MODE_NAMES[self.mode].upper(),
            20,
            (32, 14),
            config.ACCENT,
            bold=True,
        )
        draw_text(
            surface,
            f"{int(self.duration)} SECOND RUN",
            12,
            (32, 44),
            config.MUTED,
            bold=True,
        )
        draw_text(
            surface,
            f"{max(0.0, self.time_left):0.1f}",
            36,
            (config.WIDTH // 2, config.HUD_HEIGHT // 2),
            config.WHITE,
            bold=True,
            anchor="center",
        )
        draw_text(
            surface,
            f"{self.stats.score:,}",
            28,
            (config.WIDTH - 32, 10),
            config.ACCENT,
            bold=True,
            anchor="topright",
        )
        draw_text(
            surface,
            f"ACCURACY {self.stats.accuracy:.0f}%",
            13,
            (config.WIDTH - 32, 48),
            config.MUTED,
            bold=True,
            anchor="topright",
        )

        hint = (
            "HOLD LEFT MOUSE TO TRACK"
            if self.mode == "tracking"
            else "LEFT CLICK TO SHOOT"
        )
        draw_text(
            surface,
            hint,
            12,
            (config.WIDTH // 2, config.HEIGHT - 24),
            config.DIM,
            bold=True,
            anchor="center",
        )
        draw_text(
            surface,
            "ESC  END RUN",
            12,
            (32, config.HEIGHT - 24),
            config.DIM,
            bold=True,
            anchor="midleft",
        )

    def _draw_crosshair(self, surface: pygame.Surface) -> None:
        x, y = pygame.mouse.get_pos()
        if self.mode == "tracking" and self.firing:
            color = config.GREEN if self.on_target else config.RED
        else:
            color = config.ACCENT

        pygame.draw.circle(surface, color, (x, y), 10, 1)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            pygame.draw.line(
                surface,
                color,
                (x + dx * 14, y + dy * 14),
                (x + dx * 21, y + dy * 21),
                2,
            )
        pygame.draw.circle(surface, config.WHITE, (x, y), 2)


class ResultsScene(Scene):
    def __init__(self, app, stats: RunStats, record: RecordResult):
        super().__init__(app)
        self.stats = stats
        self.record = record
        self.panel = pygame.Rect(0, 0, 820, 560)
        self.panel.center = (config.WIDTH // 2, 350)

        widths = (210, 210, 130)
        gap = 16
        total = sum(widths) + gap * (len(widths) - 1)
        left = config.WIDTH // 2 - total // 2
        y = self.panel.bottom - 116
        self.buttons = [
            Button((left, y, widths[0], 54), "PLAY AGAIN", accent=True, font_size=20),
            Button(
                (left + widths[0] + gap, y, widths[1], 54),
                "CHANGE MODE",
                font_size=20,
            ),
            Button(
                (left + widths[0] + widths[1] + gap * 2, y, widths[2], 54),
                "QUIT",
                font_size=20,
            ),
        ]

    def on_enter(self) -> None:
        pygame.mouse.set_visible(True)

    def _play_again(self) -> None:
        self.app.start_run(self.stats.mode, int(self.stats.duration))

    def _stat_items(self) -> list[tuple[str, str]]:
        if self.stats.mode == "tracking":
            return [
                ("ACCURACY", f"{self.stats.accuracy:.1f}%"),
                ("ON TARGET", f"{self.stats.on_target_time:.1f}s"),
                ("FIRE TIME", f"{self.stats.fire_time:.1f}s"),
            ]
        return [
            ("ACCURACY", f"{self.stats.accuracy:.1f}%"),
            ("AVG REACTION", self._ms(self.stats.avg_reaction_ms)),
            ("BEST REACTION", self._ms(self.stats.best_reaction_ms)),
            ("HITS", f"{self.stats.hits}"),
            ("MISSES", f"{self.stats.misses}"),
            ("BULLSEYE RATE", f"{self.stats.bullseye_rate:.0f}%"),
        ]

    @staticmethod
    def _ms(value) -> str:
        return "n/a" if value is None else f"{value:.0f} ms"

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._play_again()
            elif event.key == pygame.K_m:
                self.app.show_menu()
            elif event.key == pygame.K_ESCAPE:
                self.app.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttons[0].rect.collidepoint(event.pos):
                self._play_again()
            elif self.buttons[1].rect.collidepoint(event.pos):
                self.app.show_menu()
            elif self.buttons[2].rect.collidepoint(event.pos):
                self.app.quit()

    def update(self, dt: float) -> None:
        mouse = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.app.background, (0, 0))
        surface.blit(self.app.dim, (0, 0))

        pygame.draw.rect(surface, config.PANEL, self.panel, border_radius=20)
        pygame.draw.rect(surface, config.BORDER, self.panel, 1, border_radius=20)

        panel = self.panel
        mode_name = config.MODE_NAMES[self.stats.mode].upper()
        draw_text(
            surface,
            f"{mode_name}   ·   {int(self.stats.duration)} SECOND RUN",
            14,
            (panel.centerx, panel.top + 30),
            config.MUTED,
            bold=True,
            anchor="center",
        )

        if self.record.new_best:
            draw_text(
                surface,
                "NEW PERSONAL BEST",
                16,
                (panel.centerx, panel.top + 62),
                config.YELLOW,
                bold=True,
                anchor="center",
            )

        score_color = config.ACCENT if self.record.new_best else config.WHITE
        draw_text(
            surface,
            f"{self.stats.score:,}",
            84,
            (panel.centerx, panel.top + 130),
            score_color,
            bold=True,
            anchor="center",
        )

        best_text = f"PERSONAL BEST  {self.record.best:,}"
        if self.record.new_best:
            gained = max(0, self.record.best - self.record.previous_best)
            best_text += f"   (+{gained:,})"
        draw_text(
            surface,
            best_text,
            14,
            (panel.centerx, panel.top + 192),
            config.MUTED,
            bold=True,
            anchor="center",
        )

        pygame.draw.line(
            surface,
            config.BORDER,
            (panel.left + 90, panel.top + 224),
            (panel.right - 90, panel.top + 224),
            1,
        )

        items = self._stat_items()
        columns = 3
        row_count = math.ceil(len(items) / columns)
        first_label_y = panel.top + (290 if row_count == 1 else 252)
        row_gap = 76
        x_positions = (panel.centerx - 250, panel.centerx, panel.centerx + 250)
        for index, (label, value) in enumerate(items):
            column = index % columns
            row = index // columns
            x = x_positions[column]
            y = first_label_y + row * row_gap
            draw_text(
                surface,
                label,
                12,
                (x, y),
                config.DIM,
                bold=True,
                anchor="center",
            )
            draw_text(
                surface,
                value,
                26,
                (x, y + 22),
                config.WHITE,
                bold=True,
                anchor="center",
            )

        for button in self.buttons:
            button.draw(surface)

        draw_text(
            surface,
            "ENTER  play again      M  change mode      ESC  quit",
            12,
            (panel.centerx, panel.bottom - 32),
            config.DIM,
            bold=True,
            anchor="center",
        )
