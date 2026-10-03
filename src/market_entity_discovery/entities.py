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
    train_occurrences: list[int]

    def to_dict(self) -> dict:
        return asdict(self)


def _greedy_non_overlapping(indices: Iterable[int], min_gap: int) -> list[int]:
    kept: list[int] = []
    for idx in sorted(set(int(i) for i in indices)):
        if not kept or idx - kept[-1] >= min_gap:
            kept.append(idx)
    return kept


def discover_entities(
    values: np.ndarray,
    m: int,
    mp: MatrixProfileResult,
    max_entities: int = 12,
    distance_multiplier: float = 1.6,
    min_support: int = 3,
) -> list[Entity]:
    windows = z_normalized_windows(values, m)
    flat = windows.reshape(len(windows), -1)
    candidates = np.argsort(mp.profile)
    consumed: list[int] = []
    entities: list[Entity] = []

    for seed in candidates:
        nn = int(mp.index[seed])
        if nn < 0 or not np.isfinite(mp.profile[seed]):
            continue
        if any(abs(int(seed) - x) < m or abs(nn - x) < m for x in consumed):
            continue

        proto = flat[seed]
        distances = np.linalg.norm(flat - proto, axis=1)
        threshold = float(mp.profile[seed] * distance_multiplier)
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
    train_w = z_normalized_windows(train_values, m).reshape(-1, train_values.shape[1] * m)
    target_w = z_normalized_windows(target_values, m).reshape(-1, target_values.shape[1] * m)
    result: dict[str, list[int]] = {}
    for e in entities:
        proto = train_w[e.prototype_index]
        d = np.linalg.norm(target_w - proto, axis=1)
        hits = _greedy_non_overlapping(np.flatnonzero(d <= e.threshold), m)
        result[e.entity_id] = hits
    return result
