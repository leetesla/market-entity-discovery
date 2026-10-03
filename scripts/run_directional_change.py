#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from market_entity_discovery.directional_change import (
    multiscale_directional_change,
    multiscale_state_summary,
    summarize_events,
)


def threshold_key(x: float) -> str:
    pct = x * 100.0
    return f"dc_{pct:g}pct".replace(".", "_")


def main() -> None:
    p = argparse.ArgumentParser(description="Multi-scale Directional Change representation")
    p.add_argument("--csv", required=True)
    p.add_argument("--out", default="experiments/btcusdt_1m_directional_change")
    p.add_argument(
        "--thresholds",
        default="0.0025,0.005,0.01,0.02,0.04",
        help="Comma-separated fractional reversal thresholds (0.005 = 0.5%%)",
    )
    p.add_argument("--price-column", default="close")
    p.add_argument("--max-rows", type=int, default=0, help="0 means all rows")
    args = p.parse_args()

    thresholds = sorted(float(x.strip()) for x in args.thresholds.split(",") if x.strip())

    df = pd.read_csv(args.csv)
    if args.price_column not in df:
        raise SystemExit(f"Missing price column: {args.price_column}")

    if "timestamp" in df:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)

    if args.max_rows and len(df) > args.max_rows:
        df = df.iloc[: args.max_rows].reset_index(drop=True)

    prices = pd.to_numeric(df[args.price_column], errors="coerce")
    good = prices.notna() & np.isfinite(prices) & (prices > 0)
    if not good.all():
        df = df.loc[good].reset_index(drop=True)
        prices = pd.to_numeric(df[args.price_column], errors="raise")

    event_map, states = multiscale_directional_change(prices.to_numpy(float), thresholds)

    rows: list[dict] = []
    for threshold in thresholds:
        for event in event_map[threshold]:
            row = event.to_dict()
            if "timestamp" in df:
                row["extremum_time"] = str(df.iloc[event.extremum_index]["timestamp"])
                row["confirmation_time"] = str(df.iloc[event.confirmation_index]["timestamp"])
                if event.overshoot_end_index is not None:
                    row["overshoot_end_time"] = str(df.iloc[event.overshoot_end_index]["timestamp"])
                else:
                    row["overshoot_end_time"] = None
            rows.append(row)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(rows).to_csv(out / "events.csv", index=False)

    state_df = pd.DataFrame()
    if "timestamp" in df:
        state_df["timestamp"] = df["timestamp"].astype(str)
    state_df["close"] = prices.to_numpy(float)
    for j, threshold in enumerate(thresholds):
        state_df[threshold_key(threshold)] = states[:, j]
    state_df.to_csv(out / "states.csv", index=False)

    by_threshold = {
        str(threshold): {
            "threshold_pct": threshold * 100.0,
            **summarize_events(event_map[threshold]),
        }
        for threshold in thresholds
    }
    intrinsic = multiscale_state_summary(states, thresholds)

    summary = {
        "input_csv": args.csv,
        "rows": len(df),
        "price_column": args.price_column,
        "thresholds": thresholds,
        "by_threshold": by_threshold,
        "intrinsic_state_summary": intrinsic,
        "causality_note": (
            "State changes only at confirmation_index. extremum_time is historical and "
            "must not be used as if it were known before confirmation_time."
        ),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "transitions.json").write_text(
        json.dumps(intrinsic, indent=2), encoding="utf-8"
    )

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
