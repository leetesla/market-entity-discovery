from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .entities import discover_entities, match_entities
from .features import FEATURE_COLUMNS, build_features
from .profile import compute_multivariate_profile
from .split import chronological_split


def run_v0(
    klines: pd.DataFrame,
    out_dir: str | Path,
    window_size: int = 24,
    backend: str = "auto",
    max_rows: int | None = 6000,
    max_entities: int = 12,
) -> dict:
    features = build_features(klines)
    if max_rows and len(features) > max_rows:
        features = features.iloc[:max_rows].reset_index(drop=True)

    split = chronological_split(len(features), gap=window_size)
    train = features.iloc[split.train]
    val = features.iloc[split.validation]
    test = features.iloc[split.test]

    train_values = train[FEATURE_COLUMNS].to_numpy(float)
    val_values = val[FEATURE_COLUMNS].to_numpy(float)
    test_values = test[FEATURE_COLUMNS].to_numpy(float)

    mp = compute_multivariate_profile(train_values, window_size, backend=backend)
    entities = discover_entities(
        train_values,
        window_size,
        mp,
        max_entities=max_entities,
    )
    val_hits = match_entities(train_values, val_values, window_size, entities)
    test_hits = match_entities(train_values, test_values, window_size, entities)

    def occurrence_times(frame: pd.DataFrame, indices: list[int]) -> list[str]:
        if "timestamp" not in frame.columns:
            return []
        return [str(frame.iloc[i]["timestamp"]) for i in indices if 0 <= i < len(frame)]

    rows = []
    for e in entities:
        train_support = len(e.train_occurrences)
        validation_support = len(val_hits[e.entity_id])
        test_support = len(test_hits[e.entity_id])
        rows.append(
            {
                **e.to_dict(),
                "prototype_time": occurrence_times(train, [e.prototype_index])[0] if "timestamp" in train.columns else None,
                "nearest_neighbor_time": occurrence_times(train, [e.nearest_neighbor_index])[0] if "timestamp" in train.columns else None,
                "train_occurrence_times": occurrence_times(train, e.train_occurrences),
                "validation_occurrences": val_hits[e.entity_id],
                "validation_occurrence_times": occurrence_times(val, val_hits[e.entity_id]),
                "test_occurrences": test_hits[e.entity_id],
                "test_occurrence_times": occurrence_times(test, test_hits[e.entity_id]),
                "train_support": train_support,
                "validation_support": validation_support,
                "test_support": test_support,
                "train_nonoverlap_coverage": train_support * window_size / len(train),
                "validation_nonoverlap_coverage": validation_support * window_size / len(val),
                "test_nonoverlap_coverage": test_support * window_size / len(test),
            }
        )

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_json(out / "entities.json", orient="records", indent=2)
    np.save(out / "matrix_profile.npy", mp.profile)
    np.save(out / "matrix_profile_index.npy", mp.index)

    summary = {
        "rows": len(features),
        "window_size": window_size,
        "backend": mp.backend,
        "feature_columns": FEATURE_COLUMNS,
        "split_rows": {
            "train": len(train),
            "validation": len(val),
            "test": len(test),
        },
        "entity_count": len(entities),
        "entities_with_validation_recurrence": sum(bool(val_hits[e.entity_id]) for e in entities),
        "entities_with_test_recurrence": sum(bool(test_hits[e.entity_id]) for e in entities),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
