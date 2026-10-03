#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from market_entity_discovery.binance_data import KLINE_COLUMNS
from market_entity_discovery.experiment import run_v0


def main() -> None:
    p = argparse.ArgumentParser(description="Market Entity Discovery V0")
    p.add_argument("--csv", default="data/processed/BTCUSDT-5m.csv")
    p.add_argument("--out", default="experiments/btcusdt_5m_m24")
    p.add_argument("--window", type=int, default=24)
    p.add_argument("--backend", choices=["auto", "stumpy", "numpy"], default="auto")
    p.add_argument("--max-rows", type=int, default=6000)
    p.add_argument("--max-entities", type=int, default=12)
    args = p.parse_args()

    df = pd.read_csv(args.csv)
    required = set(KLINE_COLUMNS[:-1])
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing kline columns: {sorted(missing)}")

    summary = run_v0(
        df,
        Path(args.out),
        window_size=args.window,
        backend=args.backend,
        max_rows=args.max_rows,
        max_entities=args.max_entities,
    )
    print(summary)


if __name__ == "__main__":
    main()
