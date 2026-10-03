from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable

import pandas as pd

KLINE_COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "num_trades",
    "taker_buy_base_volume",
    "taker_buy_quote_volume",
    "ignore",
]


def monthly_kline_url(
    symbol: str,
    interval: str,
    year: int,
    month: int,
    market: str = "futures_um",
) -> str:
    """Build an official Binance Vision monthly kline URL."""
    symbol = symbol.upper()
    ym = f"{year:04d}-{month:02d}"
    filename = f"{symbol}-{interval}-{ym}.zip"
    if market == "futures_um":
        base = "https://data.binance.vision/data/futures/um/monthly/klines"
    elif market == "spot":
        base = "https://data.binance.vision/data/spot/monthly/klines"
    else:
        raise ValueError(f"Unsupported market: {market}")
    return f"{base}/{symbol}/{interval}/{filename}"


def _timestamp_unit(values: pd.Series) -> str:
    # Binance Spot switched historical archive timestamps to microseconds in 2025.
    median = pd.to_numeric(values, errors="coerce").dropna().median()
    if pd.isna(median):
        return "ms"
    return "us" if median > 100_000_000_000_000 else "ms"


def parse_kline_csv_bytes(raw: bytes) -> pd.DataFrame:
    """Parse headerless (or headered) Binance kline CSV bytes."""
    df = pd.read_csv(io.BytesIO(raw), header=None)
    if df.empty:
        return pd.DataFrame(columns=KLINE_COLUMNS)

    first = str(df.iloc[0, 0]).lower()
    if "open" in first and "time" in first:
        df = df.iloc[1:].reset_index(drop=True)

    if df.shape[1] < len(KLINE_COLUMNS):
        raise ValueError(f"Expected >=12 kline columns, found {df.shape[1]}")
    df = df.iloc[:, : len(KLINE_COLUMNS)]
    df.columns = KLINE_COLUMNS

    numeric = [c for c in KLINE_COLUMNS if c != "ignore"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["open_time", "open", "high", "low", "close", "volume"])

    unit = _timestamp_unit(df["open_time"])
    df["timestamp"] = pd.to_datetime(df["open_time"], unit=unit, utc=True)
    return df.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)


def download_month(
    out_dir: str | Path,
    symbol: str,
    interval: str,
    year: int,
    month: int,
    market: str = "futures_um",
    timeout: int = 60,
) -> Path:
    """Download one official Binance Vision monthly archive and extract the CSV."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    url = monthly_kline_url(symbol, interval, year, month, market)
    zip_path = out_dir / url.rsplit("/", 1)[-1]
    csv_path = zip_path.with_suffix(".csv")
    if csv_path.exists():
        return csv_path

    with urllib.request.urlopen(url, timeout=timeout) as response:
        payload = response.read()
    zip_path.write_bytes(payload)
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if len(csv_names) != 1:
            raise ValueError(f"Expected one CSV in {zip_path.name}, found {csv_names}")
        csv_path.write_bytes(zf.read(csv_names[0]))
    return csv_path


def load_months(paths: Iterable[str | Path]) -> pd.DataFrame:
    frames = []
    for path in paths:
        frames.append(parse_kline_csv_bytes(Path(path).read_bytes()))
    if not frames:
        return pd.DataFrame(columns=KLINE_COLUMNS + ["timestamp"])
    return (
        pd.concat(frames, ignore_index=True)
        .sort_values("timestamp")
        .drop_duplicates("timestamp")
        .reset_index(drop=True)
    )
