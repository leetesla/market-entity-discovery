from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "log_return",
    "range_pct",
    "body_pct",
    "log_volume",
    "delta_ratio",
    "cvd_12_ratio",
]


def build_features(klines: pd.DataFrame, cvd_window: int = 12) -> pd.DataFrame:
    """Build stationary-ish 5m features from Binance klines.

    delta_ratio is a candle-level aggressive-flow proxy:
        (taker_buy - taker_sell) / total_volume
      = (2 * taker_buy_base_volume - volume) / volume

    cvd_12_ratio is the rolling signed-volume imbalance over 12 bars. We use it
    instead of ΔCVD because ΔCVD is algebraically the same as per-bar delta.
    """
    df = klines.copy()
    prev_close = df["close"].shift(1)
    df["log_return"] = np.log(df["close"] / prev_close)
    df["range_pct"] = (df["high"] - df["low"]) / prev_close
    df["body_pct"] = (df["close"] - df["open"]) / prev_close
    df["log_volume"] = np.log1p(df["volume"].clip(lower=0))

    signed_volume = 2.0 * df["taker_buy_base_volume"] - df["volume"]
    denom = df["volume"].replace(0, np.nan)
    df["delta_ratio"] = signed_volume / denom

    rolling_signed = signed_volume.rolling(cvd_window, min_periods=cvd_window).sum()
    rolling_volume = df["volume"].rolling(cvd_window, min_periods=cvd_window).sum().replace(0, np.nan)
    df["cvd_12_ratio"] = rolling_signed / rolling_volume

    return df.dropna(subset=FEATURE_COLUMNS).reset_index(drop=True)
