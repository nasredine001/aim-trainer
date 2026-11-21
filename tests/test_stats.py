"""Unit tests for run statistics and persistence."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aimtrainer.stats import RunStats, StatsStore


class RunStatsTests(unittest.TestCase):
    def test_flick_accuracy(self):
        stats = RunStats("flick", 30)
        stats.shots = 10
        stats.hits = 8
        self.assertAlmostEqual(stats.accuracy, 80.0)

    def test_tracking_accuracy(self):
        stats = RunStats("tracking", 30)
        stats.on_target_time = 6.0
        stats.fire_time = 8.0
        self.assertAlmostEqual(stats.accuracy, 75.0)

    def test_empty_run_is_safe(self):
        stats = RunStats("flick", 30)
        self.assertEqual(stats.accuracy, 0.0)
        self.assertIsNone(stats.avg_reaction_ms)
        self.assertIsNone(stats.best_reaction_ms)
        self.assertEqual(stats.bullseye_rate, 0.0)

    def test_reaction_statistics(self):
        stats = RunStats("flick", 30)
        stats.reaction_times = [0.30, 0.20, 0.40]
        self.assertAlmostEqual(stats.avg_reaction_ms, 300.0)
        self.assertAlmostEqual(stats.best_reaction_ms, 200.0)


class StatsStoreTests(unittest.TestCase):
    def test_record_persists_best_and_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "nested" / "stats.json"
            store = StatsStore(path)
            self.assertEqual(store.best("flick"), 0)

            stats = RunStats("flick", 30)
            stats.score = 1250
            stats.shots = 12
            stats.hits = 10
            stats.misses = 2
            stats.bullseyes = 4
            stats.reaction_times = [0.25, 0.30]

            result = store.record(stats)
            self.assertTrue(result.new_best)
            self.assertEqual(result.previous_best, 0)
            self.assertEqual(result.best, 1250)
            self.assertTrue(path.exists())

            reloaded = StatsStore(path)
            self.assertEqual(reloaded.best("flick"), 1250)
            history = reloaded.history("flick")
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["score"], 1250)

            worse = RunStats("flick", 30)
            worse.score = 900
            worse.shots = 5
            worse.hits = 4
            worse.misses = 1

            result = reloaded.record(worse)
            self.assertFalse(result.new_best)
            self.assertEqual(result.previous_best, 1250)
            self.assertEqual(result.best, 1250)
            self.assertEqual(reloaded.best("flick"), 1250)

    def test_corrupt_file_falls_back_to_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "stats.json"
            path.write_text("not json", encoding="utf-8")

            store = StatsStore(path)
            self.assertEqual(store.best("moving"), 0)
            self.assertEqual(store.history(), [])


if __name__ == "__main__":
    unittest.main()
