from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np

from .profile import MatrixProfileResult, z_normalized_windows


@dataclass
class Entity:
    entity_id: str
    prototype_index: int
    nearest_neighbor_index: int
    seed_distance: float
    threshold: float
    background_median_distance: float
    compactness_ratio: float
    train_occurrences: list[int]

    def to_dict(self) -> dict:
        return asdict(self)


def _greedy_non_overlapping(indices: Iterable[int], min_gap: int) -> list[int]:
    kept: list[int] = []
    for idx in sorted(set(int(i) for i in indices)):
        if not kept or idx - kept[-1] >= min_gap:
            kept.append(idx)
    return kept


def _mean_dimension_distance(windows: np.ndarray, prototype: np.ndarray) -> np.ndarray:
    """Mean z-normalized Euclidean distance across dimensions.

    This matches the distance semantics used by the final row of STUMPY's
    multidimensional matrix profile when all dimensions are included.
    """
    per_dimension = np.linalg.norm(windows - prototype[None, :, :], axis=2)
    return per_dimension.mean(axis=1)


def discover_entities(
    values: np.ndarray,
    m: int,
    mp: MatrixProfileResult,
    max_entities: int = 12,
    distance_multiplier: float = 1.6,
    min_support: int = 3,
) -> list[Entity]:
    windows = z_normalized_windows(values, m)
    candidates = np.argsort(mp.profile)
    consumed: list[int] = []
    entities: list[Entity] = []

    for seed in candidates:
        nn = int(mp.index[seed])
        if nn < 0 or not np.isfinite(mp.profile[seed]):
            continue
        if any(abs(int(seed) - x) < m or abs(nn - x) < m for x in consumed):
            continue

        proto = windows[seed]
        distances = _mean_dimension_distance(windows, proto)
        threshold = float(mp.profile[seed] * distance_multiplier)
        background_median = float(np.median(distances[np.isfinite(distances)]))
        compactness_ratio = threshold / background_median if background_median > 0 else float("inf")
        member_candidates = np.flatnonzero(distances <= threshold)
        members = _greedy_non_overlapping(member_candidates, m)
        if len(members) < min_support:
            continue

        entity = Entity(
            entity_id=f"E{len(entities)+1:03d}",
            prototype_index=int(seed),
            nearest_neighbor_index=nn,
            seed_distance=float(mp.profile[seed]),
            threshold=threshold,
            background_median_distance=background_median,
            compactness_ratio=compactness_ratio,
            train_occurrences=members,
        )
        entities.append(entity)
        consumed.extend(members)
        if len(entities) >= max_entities:
            break
    return entities


def match_entities(
    train_values: np.ndarray,
    target_values: np.ndarray,
    m: int,
    entities: list[Entity],
) -> dict[str, list[int]]:
    if not entities or len(target_values) < m:
        return {e.entity_id: [] for e in entities}
    train_w = z_normalized_windows(train_values, m)
    target_w = z_normalized_windows(target_values, m)
    result: dict[str, list[int]] = {}
    for e in entities:
        proto = train_w[e.prototype_index]
        d = _mean_dimension_distance(target_w, proto)
        hits = _greedy_non_overlapping(np.flatnonzero(d <= e.threshold), m)
        result[e.entity_id] = hits
    return result
