from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class MatrixProfileResult:
    profile: np.ndarray
    index: np.ndarray
    backend: str


def z_normalized_windows(values: np.ndarray, m: int, eps: float = 1e-8) -> np.ndarray:
    """Return windows as (num_windows, dimensions, m), z-normalized per dimension."""
    values = np.asarray(values, dtype=float)
    if values.ndim != 2:
        raise ValueError("values must have shape (time, dimensions)")
    if m < 3 or m > len(values):
        raise ValueError("invalid window size")
    w = np.lib.stride_tricks.sliding_window_view(values, window_shape=m, axis=0)
    mu = w.mean(axis=2, keepdims=True)
    sigma = w.std(axis=2, keepdims=True)
    sigma = np.where(sigma < eps, 1.0, sigma)
    return (w - mu) / sigma


def _numpy_exact_profile(
    values: np.ndarray,
    m: int,
    exclusion_zone: int | None = None,
    max_windows: int = 2500,
) -> MatrixProfileResult:
    windows = z_normalized_windows(values, m)
    n_w = len(windows)
    if n_w > max_windows:
        raise RuntimeError(
            f"NumPy fallback limited to {max_windows} windows (got {n_w}). "
            "Install the 'stumpy' optional dependency for real data."
        )
    exclusion = exclusion_zone if exclusion_zone is not None else max(1, m // 2)
    flat = windows.reshape(n_w, -1)
    norms = np.sum(flat * flat, axis=1)
    profile = np.full(n_w, np.inf)
    index = np.full(n_w, -1, dtype=int)

    chunk = 256
    for start in range(0, n_w, chunk):
        stop = min(start + chunk, n_w)
        d2 = norms[start:stop, None] + norms[None, :] - 2.0 * flat[start:stop] @ flat.T
        d2 = np.maximum(d2, 0.0)
        for local_i, i in enumerate(range(start, stop)):
            lo = max(0, i - exclusion)
            hi = min(n_w, i + exclusion + 1)
            d2[local_i, lo:hi] = np.inf
        idx = np.argmin(d2, axis=1)
        profile[start:stop] = np.sqrt(d2[np.arange(stop - start), idx])
        index[start:stop] = idx
    return MatrixProfileResult(profile, index, "numpy_exact")


def compute_multivariate_profile(
    values: np.ndarray,
    m: int,
    backend: str = "auto",
    max_numpy_windows: int = 2500,
) -> MatrixProfileResult:
    if backend not in {"auto", "stumpy", "numpy"}:
        raise ValueError("backend must be auto, stumpy, or numpy")

    if backend in {"auto", "stumpy"}:
        try:
            import stumpy  # type: ignore
        except ImportError:
            if backend == "stumpy":
                raise RuntimeError("STUMPY is not installed. pip install '.[stumpy]'")
        else:
            P, I = stumpy.mstump(np.asarray(values, dtype=float).T, m)
            return MatrixProfileResult(
                profile=np.asarray(P[-1], dtype=float),
                index=np.asarray(I[-1], dtype=int),
                backend="stumpy_mstump",
            )

    return _numpy_exact_profile(values, m, max_windows=max_numpy_windows)
