#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from market_entity_discovery.binance_data import download_month, load_months


def month_range(start: str, end: str):
    sy, sm = map(int, start.split("-"))
    ey, em = map(int, end.split("-"))
    y, m = sy, sm
    while (y, m) <= (ey, em):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--interval", default="5m")
    p.add_argument("--start", default="2025-01")
    p.add_argument("--end", default="2025-03")
    p.add_argument("--market", choices=["futures_um", "spot"], default="futures_um")
    p.add_argument("--out", default="data/raw/binance")
    p.add_argument("--merged", default="data/processed/BTCUSDT-5m.csv")
    args = p.parse_args()

    paths = []
    for year, month in month_range(args.start, args.end):
        path = download_month(args.out, args.symbol, args.interval, year, month, args.market)
        print(f"downloaded: {path}")
        paths.append(path)

    df = load_months(paths)
    merged = Path(args.merged)
    merged.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(merged, index=False)
    print(f"merged {len(df):,} rows -> {merged}")


if __name__ == "__main__":
    main()
