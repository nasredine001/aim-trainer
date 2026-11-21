"""Tiny synthesized sound effects, so the game ships with no asset files."""

from __future__ import annotations

import math
import struct

import pygame

SAMPLE_RATE = 44100


def _tone(freq: float, ms: float, volume: float = 0.35, sweep: float = 0.0) -> bytes:
    """Build a mono 16-bit sine blip with a short attack and a soft decay."""
    count = max(1, int(SAMPLE_RATE * ms / 1000.0))
    samples = bytearray()
    for index in range(count):
        progress = index / count
        envelope = min(1.0, index / 90.0) * (1.0 - progress) ** 1.6
        current_freq = freq + sweep * progress
        wave = math.sin(2.0 * math.pi * current_freq * index / SAMPLE_RATE)
        value = int(max(-1.0, min(1.0, wave * envelope * volume)) * 32767)
        samples += struct.pack("<h", value)
    return bytes(samples)


class Audio:
    def __init__(self, muted: bool = False):
        self.muted = muted
        self.enabled = False
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512
                )
            if pygame.mixer.get_init() != (SAMPLE_RATE, -16, 1):
                return
            self._sounds = {
                "hit": pygame.mixer.Sound(buffer=_tone(880, 70)),
                "bullseye": pygame.mixer.Sound(buffer=_tone(1240, 95, sweep=240)),
                "miss": pygame.mixer.Sound(buffer=_tone(170, 95, sweep=-70)),
                "beep": pygame.mixer.Sound(buffer=_tone(620, 85, volume=0.25)),
                "go": pygame.mixer.Sound(buffer=_tone(960, 150, volume=0.3, sweep=120)),
            }
            self.enabled = True
        except pygame.error:
            # No audio device (or an unsupported format) - play silently.
            self.enabled = False

    def play(self, name: str) -> None:
        if not self.enabled or self.muted:
            return
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()

    def toggle(self) -> bool:
        self.muted = not self.muted
        return self.muted
