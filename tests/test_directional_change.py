from __future__ import annotations

import unittest

import numpy as np

from market_entity_discovery.directional_change import (
    directional_state_series,
    extract_directional_changes,
    multiscale_directional_change,
    multiscale_state_summary,
)


class DirectionalChangeTests(unittest.TestCase):
    def test_known_zigzag(self):
        prices = [100, 99, 98, 99, 100, 101, 100, 99, 98, 99, 100]
        events = extract_directional_changes(prices, 0.02)

        self.assertEqual([e.direction for e in events], ["UPTURN", "DOWNTURN", "UPTURN"])
        self.assertEqual([e.extremum_index for e in events], [2, 5, 8])
        self.assertEqual([e.confirmation_index for e in events], [4, 8, 10])

        for event in events:
            self.assertLessEqual(event.extremum_index, event.confirmation_index)

    def test_state_changes_only_on_confirmation(self):
        prices = [100, 99, 98, 99, 100, 101, 100, 99, 98, 99, 100]
        events = extract_directional_changes(prices, 0.02)
        state = directional_state_series(len(prices), events)

        self.assertTrue(np.all(state[:4] == 0))
        self.assertTrue(np.all(state[4:8] == 1))
        self.assertTrue(np.all(state[8:10] == -1))
        self.assertEqual(int(state[10]), 1)

    def test_overshoot_annotation(self):
        prices = [100, 99, 98, 99, 100, 101, 102, 100, 99, 98, 99, 100]
        events = extract_directional_changes(prices, 0.02)
        first = events[0]
        self.assertEqual(first.direction, "UPTURN")
        self.assertEqual(first.overshoot_end_price, 102.0)
        self.assertGreater(first.overshoot_pct or 0, 0)

    def test_multiscale_states(self):
        prices = np.r_[
            np.linspace(100, 110, 20),
            np.linspace(110, 95, 30),
            np.linspace(95, 108, 25),
        ]
        thresholds = [0.01, 0.03]
        event_map, states = multiscale_directional_change(prices, thresholds)
        self.assertEqual(states.shape, (len(prices), 2))
        self.assertTrue(all(len(event_map[t]) >= 2 for t in thresholds))

        summary = multiscale_state_summary(states, thresholds)
        self.assertGreater(summary["valid_rows"], 0)
        self.assertGreaterEqual(summary["unique_states"], 1)

    def test_reject_bad_threshold(self):
        with self.assertRaises(ValueError):
            extract_directional_changes([100, 101, 102], 0)


if __name__ == "__main__":
    unittest.main()
