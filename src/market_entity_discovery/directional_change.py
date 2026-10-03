from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class DCEvent:
    threshold: float
    direction: str  # UPTURN or DOWNTURN
    extremum_index: int
    confirmation_index: int
    extremum_price: float
    confirmation_price: float
    confirmation_bars: int
    overshoot_end_index: int | None = None
    overshoot_end_price: float | None = None
    overshoot_bars: int | None = None
    overshoot_pct: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def extract_directional_changes(prices: Iterable[float], threshold: float) -> list[DCEvent]:
    """Extract causal Directional Change events from a price series.

    A UPTURN is confirmed only after price rises by the threshold from the
    running low. A DOWNTURN is confirmed only after price falls by the
    threshold from the running high.

    The extremum occurs before (or at) confirmation, so event timestamps should
    distinguish the historical extremum from the causal confirmation time.
    """
    p = np.asarray(list(prices), dtype=float)
    if p.ndim != 1 or len(p) < 2:
        return []
    if not np.all(np.isfinite(p)) or np.any(p <= 0):
        raise ValueError("prices must be finite and strictly positive")
    if not (0 < threshold < 1):
        raise ValueError("threshold must be between 0 and 1")

    events: list[DCEvent] = []
    mode = 0  # 0 unknown, +1 upward regime after UPTURN, -1 downward regime

    high_price = low_price = float(p[0])
    high_idx = low_idx = 0

    for i in range(1, len(p)):
        price = float(p[i])

        if mode == 0:
            if price > high_price:
                high_price, high_idx = price, i
            if price < low_price:
                low_price, low_idx = price, i

            up_trigger = price >= low_price * (1.0 + threshold)
            down_trigger = price <= high_price * (1.0 - threshold)

            if up_trigger:
                events.append(
                    DCEvent(
                        threshold=threshold,
                        direction="UPTURN",
                        extremum_index=low_idx,
                        confirmation_index=i,
                        extremum_price=low_price,
                        confirmation_price=price,
                        confirmation_bars=i - low_idx,
                    )
                )
                mode = 1
                high_price, high_idx = price, i
            elif down_trigger:
                events.append(
                    DCEvent(
                        threshold=threshold,
                        direction="DOWNTURN",
                        extremum_index=high_idx,
                        confirmation_index=i,
                        extremum_price=high_price,
                        confirmation_price=price,
                        confirmation_bars=i - high_idx,
                    )
                )
                mode = -1
                low_price, low_idx = price, i

        elif mode == 1:
            if price > high_price:
                high_price, high_idx = price, i

            if price <= high_price * (1.0 - threshold):
                events.append(
                    DCEvent(
                        threshold=threshold,
                        direction="DOWNTURN",
                        extremum_index=high_idx,
                        confirmation_index=i,
                        extremum_price=high_price,
                        confirmation_price=price,
                        confirmation_bars=i - high_idx,
                    )
                )
                mode = -1
                low_price, low_idx = price, i

        else:
            if price < low_price:
                low_price, low_idx = price, i

            if price >= low_price * (1.0 + threshold):
                events.append(
                    DCEvent(
                        threshold=threshold,
                        direction="UPTURN",
                        extremum_index=low_idx,
                        confirmation_index=i,
                        extremum_price=low_price,
                        confirmation_price=price,
                        confirmation_bars=i - low_idx,
                    )
                )
                mode = 1
                high_price, high_idx = price, i

    annotated: list[DCEvent] = []
    for i, event in enumerate(events):
        if i + 1 >= len(events):
            annotated.append(event)
            continue

        end = events[i + 1]
        end_idx = end.extremum_index
        end_price = end.extremum_price
        bars = max(0, end_idx - event.confirmation_index)

        if event.direction == "UPTURN":
            overshoot = max(0.0, end_price / event.confirmation_price - 1.0)
        else:
            overshoot = max(0.0, 1.0 - end_price / event.confirmation_price)

        annotated.append(
            replace(
                event,
                overshoot_end_index=end_idx,
                overshoot_end_price=end_price,
                overshoot_bars=bars,
                overshoot_pct=float(overshoot),
            )
        )
    return annotated


def directional_state_series(length: int, events: list[DCEvent]) -> np.ndarray:
    """Return causal regime state: 0 unknown, +1 after UPTURN, -1 after DOWNTURN."""
    state = np.zeros(length, dtype=np.int8)
    current = 0
    start = 0

    for event in events:
        idx = int(event.confirmation_index)
        state[start:idx] = current
        current = 1 if event.direction == "UPTURN" else -1
        start = idx
    state[start:] = current
    return state


def multiscale_directional_change(
    prices: Iterable[float], thresholds: Iterable[float]
) -> tuple[dict[float, list[DCEvent]], np.ndarray]:
    p = np.asarray(list(prices), dtype=float)
    threshold_list = [float(x) for x in thresholds]
    if not threshold_list:
        raise ValueError("at least one threshold is required")
    if len(set(threshold_list)) != len(threshold_list):
        raise ValueError("thresholds must be unique")

    event_map: dict[float, list[DCEvent]] = {}
    columns = []
    for threshold in threshold_list:
        events = extract_directional_changes(p, threshold)
        event_map[threshold] = events
        columns.append(directional_state_series(len(p), events))
    states = np.column_stack(columns)
    return event_map, states


def summarize_events(events: list[DCEvent]) -> dict:
    if not events:
        return {
            "event_count": 0,
            "upturn_count": 0,
            "downturn_count": 0,
            "median_confirmation_bars": None,
            "median_overshoot_bars": None,
            "median_overshoot_pct": None,
            "median_interconfirmation_bars": None,
        }

    confirmation_bars = np.asarray([e.confirmation_bars for e in events], dtype=float)
    os_bars = np.asarray([e.overshoot_bars for e in events if e.overshoot_bars is not None], dtype=float)
    os_pct = np.asarray([e.overshoot_pct for e in events if e.overshoot_pct is not None], dtype=float)
    confirms = np.asarray([e.confirmation_index for e in events], dtype=float)
    inter = np.diff(confirms)

    return {
        "event_count": len(events),
        "upturn_count": sum(e.direction == "UPTURN" for e in events),
        "downturn_count": sum(e.direction == "DOWNTURN" for e in events),
        "median_confirmation_bars": float(np.median(confirmation_bars)),
        "median_overshoot_bars": float(np.median(os_bars)) if len(os_bars) else None,
        "median_overshoot_pct": float(np.median(os_pct)) if len(os_pct) else None,
        "median_interconfirmation_bars": float(np.median(inter)) if len(inter) else None,
    }


def multiscale_state_summary(states: np.ndarray, thresholds: Iterable[float], top_n: int = 20) -> dict:
    states = np.asarray(states, dtype=np.int8)
    thresholds = [float(x) for x in thresholds]
    if states.ndim != 2 or states.shape[1] != len(thresholds):
        raise ValueError("states shape must be (time, len(thresholds))")

    valid_mask = np.all(states != 0, axis=1)
    valid = states[valid_mask]
    if len(valid) == 0:
        return {
            "valid_rows": 0,
            "unique_states": 0,
            "top_states": [],
            "top_transitions": [],
        }

    def code(row: np.ndarray) -> str:
        return "".join("U" if x > 0 else "D" for x in row)

    state_codes = [code(row) for row in valid]
    counts: dict[str, int] = {}
    for s in state_codes:
        counts[s] = counts.get(s, 0) + 1

    top_states = [
        {"state": s, "count": c, "share": c / len(state_codes)}
        for s, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]
    ]

    compressed: list[str] = []
    for s in state_codes:
        if not compressed or s != compressed[-1]:
            compressed.append(s)

    transition_counts: dict[tuple[str, str], int] = {}
    for a, b in zip(compressed, compressed[1:]):
        transition_counts[(a, b)] = transition_counts.get((a, b), 0) + 1

    top_transitions = [
        {"from": a, "to": b, "count": c}
        for (a, b), c in sorted(
            transition_counts.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1])
        )[:top_n]
    ]

    return {
        "thresholds": thresholds,
        "state_code_order": "thresholds ascending as provided; U=post-UPTURN, D=post-DOWNTURN",
        "valid_rows": int(len(valid)),
        "unique_states": int(len(counts)),
        "compressed_state_changes": int(max(0, len(compressed) - 1)),
        "top_states": top_states,
        "top_transitions": top_transitions,
    }
