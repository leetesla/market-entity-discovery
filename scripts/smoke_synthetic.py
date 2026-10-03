#!/usr/bin/env python3
from __future__ import annotations

import tempfile

import numpy as np
import pandas as pd

from market_entity_discovery.experiment import run_v0


def synthetic_klines(n: int = 900) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    ret = rng.normal(0, 0.001, n)
    motif = np.r_[np.linspace(-0.003, 0.003, 12), np.linspace(0.003, -0.001, 12)]
    for start in [80, 250, 450, 670, 820]:
        if start + len(motif) < n:
            ret[start : start + len(motif)] = motif
    close = 50_000 * np.exp(np.cumsum(ret))
    open_ = np.r_[close[0], close[:-1]]
    span = np.maximum(np.abs(close - open_), close * 0.0005)
    high = np.maximum(open_, close) + span * 0.3
    low = np.minimum(open_, close) - span * 0.3
    volume = 100 + 20 * rng.random(n)
    delta_ratio = np.clip(ret / 0.004, -0.8, 0.8)
    taker_buy = volume * (1 + delta_ratio) / 2
    ts = pd.date_range("2025-01-01", periods=n, freq="5min", tz="UTC")
    return pd.DataFrame(
        {
            "open_time": (ts.astype("int64") // 10**6).astype("int64"),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "close_time": (ts.astype("int64") // 10**6 + 299_999).astype("int64"),
            "quote_volume": volume * close,
            "num_trades": 100,
            "taker_buy_base_volume": taker_buy,
            "taker_buy_quote_volume": taker_buy * close,
            "ignore": 0,
            "timestamp": ts,
        }
    )


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as out:
        summary = run_v0(
            synthetic_klines(),
            out,
            window_size=24,
            backend="numpy",
            max_rows=900,
            max_entities=8,
        )
        print(summary)
        assert summary["entity_count"] >= 1
        assert summary["entities_with_test_recurrence"] >= 1
        print("smoke test: PASS")
