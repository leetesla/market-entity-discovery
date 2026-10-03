# Directional Change V0 — BTCUSDT 1m, January 2025

This is the first real-data result for the event/intrinsic-time representation branch of Market Entity Discovery.

GitHub Actions validation:
https://github.com/leetesla/market-entity-discovery/actions/runs/37134215950

## Data

- BTCUSDT USD-M futures
- Binance Public Data / Binance Vision
- 1 minute
- January 2025
- 44,640 observations
- Directional Change computed on close price
- thresholds: 0.25%, 0.5%, 1%, 2%, 4%

The use of 1m close is a first approximation. It still loses intra-minute path information; tick/trade data should be tested later.

## First result: scale emerges naturally

| Reversal threshold | Events | Median bars between confirmations | Approx. median clock time |
|---|---:|---:|---:|
| 0.25% | 1,849 | 13 | 13 min |
| 0.5% | 633 | 36 | 36 min |
| 1% | 194 | 96 | 1 h 36 min |
| 2% | 52 | 269 | 4 h 29 min |
| 4% | 16 | 1,219 | 20 h 19 min |

This is the main reason Directional Change is useful here: the same price stream is represented simultaneously at several intrinsic scales without choosing 5m, 15m, 1h, or 4h bars as the primary ontology.

An exploratory log-log fit on this single month gives approximately:

    event_count ∝ threshold^-1.73

with a very high in-sample log-log fit. This is only a one-month diagnostic, not a claimed market scaling law. It must be repeated across months and symbols.

## Multi-scale market state

For each minute we encode the confirmed Directional Change regime at:

    [0.25%, 0.5%, 1%, 2%, 4%]

For example:

    DUUUU

means:

- 0.25% scale: downward regime
- 0.5% scale: upward
- 1% scale: upward
- 2% scale: upward
- 4% scale: upward

So it can be read as a small-scale pullback inside larger-scale upward structure.

After all five thresholds had received their first confirmation, the month contained all 32 possible binary multi-scale states.

That is useful as a negative result: a state code by itself is too permissive to be promoted to a Market Entity. Duration, transition context, recurrence, and out-of-sample stability still matter.

## First glimpse of Market Grammar

The most frequent compressed transition was:

    UUUUU -> DUUUU    186 times

When all five scales were upward and the state changed, 186 of 193 outgoing changes (96.4%) began by flipping only the smallest 0.25% scale.

That is mechanically expected from nested thresholds, but it gives us an interpretable primitive:

    all-scales-up
    -> micro pullback starts

The interesting branch comes next.

From DUUUU there were 186 outgoing state changes:

    DUUUU -> DDUUU    94  (50.5%)
    DUUUU -> UUUUU    91  (48.9%)
    DUUUU -> DDDUU     1  (0.5%)

So after a smallest-scale pullback starts, this month almost perfectly splits between:

    pullback deepens to the next scale
    vs
    smallest scale recovers and all scales align upward again

The bearish mirror also appears:

    DDDDD -> UDDDD

occurred 100 times out of 113 outgoing state changes from DDDDD (88.5%).

Then from UDDDD:

    UDDDD -> UUDDD    53%
    UDDDD -> DDDDD    47%

This is the first concrete version of what we earlier called Market Grammar:

    large-scale state
    -> small-scale reversal
    -> either recovery or propagation into the next scale

These are transition frequencies, not trading probabilities and not evidence of predictive edge.

## Why this is more interesting than another indicator

The representation has converted one continuous price series into:

    price
    -> causal reversal events
    -> multi-scale states
    -> state transitions

This gives explicit objects that can become entities:

1. a single Directional Change event;
2. an overshoot;
3. a multi-scale state;
4. a state run with duration;
5. a transition;
6. a transition sequence;
7. eventually a transition sequence under context.

So instead of looking only for 24 bars that resemble another 24 bars, we can search for a variable-length sequence such as:

    UUUUU
    -> DUUUU
    -> DDUUU
    -> UDUUU
    -> UUUUU

The actual number of minutes spent in each state may vary.

## Causality guardrail

The code stores both extremum_time and confirmation_time.

A pivot extremum is only known retrospectively. The live state changes at confirmation, never back at the extremum.

This prevents a common ZigZag/pivot backtest error where historical turning points are treated as if they were known in real time.

## Current verdict

Directional Change is worth keeping as Baseline C.

It already provides something the fixed 5m mSTUMP baseline does not naturally provide:

    explicit nested market states
    + variable-length state durations
    + causal transition sequences

But this is not yet a validated new Market Entity.

## Next scientific step

1. Use several consecutive months.
2. Discover state/transition motifs on Train only.
3. Freeze them.
4. Test state frequencies, run durations, and transition probabilities on Validation/Test.
5. Compare against shuffled/surrogate sequences.
6. Compare Directional Change entities with the bar/mSTUMP entities.
7. Only after that attach future return, MFE/MAE, volatility, or trading outcomes.
