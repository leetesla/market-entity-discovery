# V0 real-data smoke validation

Date: 2026-10-03

## Data

Source: official Binance Public Data / Binance Vision archive.

Dataset used by the GitHub Actions smoke test:

- Market: BTCUSDT USD-M futures
- Interval: 5m
- Archive month: 2025-01
- Downloaded kline rows: 8,928
- V0 rows used in the smoke test: first 2,500 feature rows
- Window size: 24 bars (2 hours)
- Backend: STUMPY `mstump`
- Split: 1,500 train / 476 validation / 476 test, with a 24-bar gap between splits

Features:

1. `log_return`
2. `range_pct`
3. `body_pct`
4. `log_volume`
5. `delta_ratio`
6. `cvd_12_ratio`

## Important implementation finding

The first real-data run returned zero entities. This exposed a metric mismatch in our own code:

- STUMPY's final multidimensional Matrix Profile row uses the **average z-normalized Euclidean distance across dimensions**.
- Our first entity expansion/matching implementation used one flattened Euclidean distance across all dimensions.

That made the entity threshold inconsistent with the Matrix Profile seed distance.

After changing expansion/matching to use the same mean-per-dimension distance semantics as mSTUMP, the same real-data smoke test produced two candidate entities and both recurred in validation and test.

This is exactly why the real-data smoke workflow exists: it checks assumptions that synthetic tests may not expose.

## Real-data result after the fix

### E001

- Prototype: 2025-01-01 06:45 UTC
- Nearest neighbor: 2025-01-05 12:35 UTC
- Matrix Profile seed distance: 3.1631
- Match threshold: 5.0609
- Background median distance: 6.9273
- Compactness ratio: 0.731
- Train support: 7
- Validation support: 3
- Test support: 4
- Non-overlap coverage: 11.2% train / 15.1% validation / 20.2% test

Interpretation at this stage: **candidate worth inspecting**. It is substantially tighter than the background distance distribution and survives both out-of-sample splits. This is not yet evidence of a tradable market entity.

### E002

- Prototype: 2025-01-03 15:35 UTC
- Nearest neighbor: 2025-01-01 19:00 UTC
- Matrix Profile seed distance: 3.8792
- Match threshold: 6.2067
- Background median distance: 6.9324
- Compactness ratio: 0.895
- Train support: 43
- Validation support: 12
- Test support: 13
- Non-overlap coverage: 68.8% train / 60.5% validation / 65.5% test

Interpretation at this stage: **probably too broad/generic**. Its threshold is close to the background median and it covers most of the available non-overlapping windows. We should not promote this to a market entity simply because it recurs.

## What this validates

The current V0 now demonstrates, on real Binance data, that the pipeline can:

1. Download official historical market data.
2. Build causal features.
3. Split chronologically with leakage gaps.
4. Run multivariate Matrix Profile on training data only.
5. Freeze candidate prototypes and thresholds.
6. Match those candidates in unseen validation/test periods.
7. Record recurrence, timestamps, coverage, and compactness diagnostics.

## What it does not validate

It does **not** yet show that E001 or E002 is:

- semantically meaningful,
- stable across months/regimes,
- statistically stronger than a null model,
- useful for predicting future outcomes,
- or tradable.

## Next validation steps

1. Plot prototype + all occurrences for E001 and E002.
2. Add train sub-period temporal stability.
3. Add block-shuffle / surrogate null model.
4. Repeat across multiple months.
5. Reject candidates with excessive coverage or weak compactness.
6. Only after those checks, attach future return/MFE/MAE/volatility outcomes.
