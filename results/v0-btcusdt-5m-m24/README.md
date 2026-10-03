# Discovered entities — BTCUSDT 5m / m=24

This directory stores the **actual candidate entities discovered by the first real-data V0 run**, rather than only a narrative summary.

Experiment:

- Data: BTCUSDT USD-M futures 5m, Binance Vision, January 2025
- Rows used: first 2,500 feature rows
- Window: 24 bars = 2 hours
- Backend: STUMPY `mstump`
- Discovery: train only
- Matching: frozen entities applied to validation and test

## E001

- Train support: 7
- Validation support: 3
- Test support: 4
- Compactness ratio: 0.731
- Train coverage: 11.2%
- Validation coverage: 15.1%
- Test coverage: 20.2%

Current status: **candidate worth inspecting visually and statistically**.

## E002

- Train support: 43
- Validation support: 12
- Test support: 13
- Compactness ratio: 0.895
- Train coverage: 68.8%
- Validation coverage: 60.5%
- Test coverage: 65.5%

Current status: **probably too broad/generic**. Its recurrence is high, but it matches a large fraction of windows.

These are candidate entities, not established market entities or trading signals. The next step is to render the prototype and every occurrence, then run stability and null-model tests.
