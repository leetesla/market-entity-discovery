from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSplit:
    train: slice
    validation: slice
    test: slice


def chronological_split(
    n: int,
    train_fraction: float = 0.60,
    validation_fraction: float = 0.20,
    gap: int = 24,
) -> TimeSplit:
    if n <= 2 * gap + 20:
        raise ValueError("Series too short for requested split and gap")
    train_end = int(n * train_fraction)
    validation_start = train_end + gap
    validation_end = int(n * (train_fraction + validation_fraction))
    test_start = validation_end + gap
    if validation_start >= validation_end or test_start >= n:
        raise ValueError("Invalid split fractions/gap for series length")
    return TimeSplit(
        train=slice(0, train_end),
        validation=slice(validation_start, validation_end),
        test=slice(test_start, n),
    )
