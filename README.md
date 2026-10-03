# Market Entity Discovery

V0 research project for discovering recurrent, out-of-sample market entities from multivariate time series before attaching trading outcomes to them.

## V0 question

> Can we discover recurrent market structures using only historical multivariate market data, freeze those structures, and recognize them again in later unseen data?

This repository deliberately does **not** optimize PnL yet. The first milestone is recurrence and out-of-sample stability.

## Data source

V0 uses the official **Binance Public Data / Binance Vision** archive, initially **BTCUSDT USD-M futures 5m klines**.

The kline archive includes OHLC, total volume, trade count, and taker-buy base/quote volume. That lets us build a coarse candle-level aggressive-flow proxy without downloading every trade:

```text
delta_proxy = 2 * taker_buy_base_volume - volume
delta_ratio = delta_proxy / volume
```

This is **not** footprint/tick-level delta; it is a 5m aggregate proxy.

### Initial features

1. `log_return`
2. `range_pct`
3. `body_pct`
4. `log_volume`
5. `delta_ratio`
6. `cvd_12_ratio` — rolling signed-volume / rolling total-volume

We intentionally do not use both `delta` and `ΔCVD` as separate features because per-bar `ΔCVD` is algebraically the same quantity as per-bar delta.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[stumpy]'
```

STUMPY is the production baseline. A small exact NumPy fallback is included only for tests/smoke checks.

## 1. Download data

Download three months of BTCUSDT 5m USD-M futures klines from Binance Vision:

```bash
python scripts/download_binance.py \
  --symbol BTCUSDT \
  --interval 5m \
  --start 2025-01 \
  --end 2025-03 \
  --market futures_um
```

The merged local file is written to `data/processed/BTCUSDT-5m.csv` and is ignored by git.

## 2. Run V0

```bash
python scripts/run_v0.py \
  --csv data/processed/BTCUSDT-5m.csv \
  --window 24 \
  --backend stumpy \
  --max-rows 6000
```

`m=24` on 5m bars is a **2-hour probe scale**, not an assumption that market entities naturally last two hours.

Outputs:

```text
experiments/btcusdt_5m_m24/
├── summary.json
├── entities.json
├── matrix_profile.npy
└── matrix_profile_index.npy
```

Discovery occurs on the training period only. Validation and test periods are used only to match the frozen training entities. Gaps equal to the window size are inserted between splits to prevent overlapping windows from leaking across boundaries.

## 3. Offline smoke test

No internet or STUMPY required:

```bash
PYTHONPATH=src python scripts/smoke_synthetic.py
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Current V0 algorithm

```text
Binance 5m klines
      ↓
stationary-ish features
      ↓
chronological train / validation / test + gaps
      ↓
multivariate Matrix Profile on TRAIN only
      ↓
low-profile seeds → recurrent occurrence sets
      ↓
freeze entity prototypes + thresholds
      ↓
match in VALIDATION / TEST or leave unmatched
      ↓
out-of-sample recurrence metrics
```

The first baseline uses all six dimensions. Sub-dimensional discovery (LAMA), learned representations (TS2Vec), multi-scale windows, transition graphs, and outcome analysis come later so they can be compared against the same V0 protocol.

## Important limitations

- Kline `delta_ratio` is a coarse taker-flow proxy, not order-level delta.
- Matrix Profile uses window-wise z-normalized shape similarity, so V0 emphasizes morphology. Scale/context features will be evaluated separately instead of being silently discarded.
- `mstump` is quadratic in sequence length. V0 intentionally caps the first smoke experiment; larger-scale discovery needs chunking/approximation or another candidate-generation stage.
- An algorithmic cluster is not automatically a "market entity". Recurrence, temporal stability, null-model comparison, and out-of-sample survival are required before promotion.

## Next experiments

1. Run BTCUSDT 5m `m=24` baseline and inspect discovered occurrences.
2. Add recurrence/stability metrics by train sub-period.
3. Add a block-shuffle null model.
4. Add LAMA as a sub-dimensional baseline.
5. Compare learned representations only after the non-learning baseline is stable.
