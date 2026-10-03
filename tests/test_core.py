from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from market_entity_discovery.binance_data import monthly_kline_url, parse_kline_csv_bytes
from market_entity_discovery.features import build_features
from market_entity_discovery.profile import compute_multivariate_profile
from market_entity_discovery.split import chronological_split


class CoreTests(unittest.TestCase):
    def test_binance_url(self):
        self.assertEqual(
            monthly_kline_url("BTCUSDT", "5m", 2025, 1),
            "https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-2025-01.zip",
        )

    def test_parse_official_kline_shape(self):
        raw = (
            b"1499040000000,0.01634790,0.80000000,0.01575800,0.01577100,"
            b"148976.11427815,1499040299999,2434.19055334,308,1756.87402397,28.46694368,0\n"
        )
        df = parse_kline_csv_bytes(raw)
        self.assertEqual(len(df), 1)
        self.assertEqual(str(df.loc[0, "timestamp"]), "2017-07-03 00:00:00+00:00")

    def test_delta_ratio(self):
        n = 20
        df = pd.DataFrame(
            {
                "open": np.full(n, 100.0),
                "high": np.full(n, 101.0),
                "low": np.full(n, 99.0),
                "close": np.linspace(100, 102, n),
                "volume": np.full(n, 100.0),
                "taker_buy_base_volume": np.full(n, 60.0),
            }
        )
        feat = build_features(df, cvd_window=3)
        self.assertTrue(np.allclose(feat["delta_ratio"], 0.2))
        self.assertTrue(np.allclose(feat["cvd_12_ratio"], 0.2))

    def test_chronological_split_gap(self):
        s = chronological_split(1000, gap=24)
        self.assertGreaterEqual(s.validation.start - s.train.stop, 24)
        self.assertGreaterEqual(s.test.start - s.validation.stop, 24)

    def test_numpy_profile_repeated_pattern(self):
        rng = np.random.default_rng(1)
        x = rng.normal(0, 0.1, (220, 3))
        motif = np.c_[
            np.sin(np.linspace(0, 2 * np.pi, 24)),
            np.linspace(-1, 1, 24),
            np.cos(np.linspace(0, 2 * np.pi, 24)),
        ]
        x[30:54] = motif
        x[140:164] = motif
        mp = compute_multivariate_profile(x, 24, backend="numpy", max_numpy_windows=500)
        i = int(np.argmin(mp.profile))
        j = int(mp.index[i])
        self.assertLess(min(abs(i - 30), abs(i - 140)), 3)
        self.assertLess(min(abs(j - 30), abs(j - 140)), 3)


if __name__ == "__main__":
    unittest.main()
