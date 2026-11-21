"""Run statistics and JSON-backed personal bests."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def default_stats_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "stats.json"


@dataclass
class RunStats:
    """Everything measured during a single training run."""

    mode: str
    duration: float
    score: int = 0
    shots: int = 0
    hits: int = 0
    misses: int = 0
    bullseyes: int = 0
    reaction_times: list[float] = field(default_factory=list)
    on_target_time: float = 0.0
    fire_time: float = 0.0

    @property
    def accuracy(self) -> float:
        if self.mode == "tracking":
            if self.fire_time <= 1e-9:
                return 0.0
            return 100.0 * self.on_target_time / self.fire_time
        if self.shots == 0:
            return 0.0
        return 100.0 * self.hits / self.shots

    @property
    def avg_reaction_ms(self) -> Optional[float]:
        if not self.reaction_times:
            return None
        return 1000.0 * sum(self.reaction_times) / len(self.reaction_times)

    @property
    def best_reaction_ms(self) -> Optional[float]:
        if not self.reaction_times:
            return None
        return 1000.0 * min(self.reaction_times)

    @property
    def bullseye_rate(self) -> float:
        if self.hits == 0:
            return 0.0
        return 100.0 * self.bullseyes / self.hits

    def as_history_entry(self) -> dict:
        return {
            "mode": self.mode,
            "score": int(self.score),
            "accuracy": round(self.accuracy, 2),
            "hits": self.hits,
            "shots": self.shots,
            "bullseyes": self.bullseyes,
            "avg_reaction_ms": (
                None if self.avg_reaction_ms is None else round(self.avg_reaction_ms, 1)
            ),
            "duration": self.duration,
            "played_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }


@dataclass
class RecordResult:
    new_best: bool
    previous_best: int
    best: int


class StatsStore:
    """Loads and saves personal bests plus the most recent runs."""

    MAX_HISTORY = 50

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path is not None else default_stats_path()
        self.data = self._load()

    def _empty(self) -> dict:
        return {"version": 1, "best": {}, "history": []}

    def _load(self) -> dict:
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except (OSError, ValueError):
            return self._empty()

        if not isinstance(raw, dict):
            return self._empty()

        best: dict[str, int] = {}
        raw_best = raw.get("best")
        if isinstance(raw_best, dict):
            for mode, value in raw_best.items():
                if isinstance(mode, str) and isinstance(value, (int, float)):
                    best[mode] = max(0, int(value))

        history = raw.get("history")
        if not isinstance(history, list):
            history = []

        return {
            "version": 1,
            "best": best,
            "history": history[-self.MAX_HISTORY :],
        }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(self.path.suffix + ".tmp")
        with temp.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2)
        temp.replace(self.path)

    def best(self, mode: str) -> int:
        return int(self.data["best"].get(mode, 0))

    def history(self, mode: str | None = None, limit: int = 5) -> list[dict]:
        runs = self.data.get("history", [])
        if mode is not None:
            runs = [
                run
                for run in runs
                if isinstance(run, dict) and run.get("mode") == mode
            ]
        return runs[-limit:][::-1]

    def record(self, stats: RunStats) -> RecordResult:
        previous = self.best(stats.mode)
        new_best = stats.score > previous
        if new_best:
            self.data["best"][stats.mode] = int(stats.score)

        self.data["history"].append(stats.as_history_entry())
        self.data["history"] = self.data["history"][-self.MAX_HISTORY :]

        try:
            self._save()
        except OSError:
            # A read-only folder should never crash a training run.
            pass

        return RecordResult(
            new_best=new_best,
            previous_best=previous,
            best=max(previous, int(stats.score)),
        )
