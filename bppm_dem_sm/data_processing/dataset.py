"""Supervised sliding-window dataset construction for the RNN surrogate."""

from __future__ import annotations

import numpy as np


def build_supervised_dataset(pos, rad, frames_in):
    """Build sliding-window ``(X, y)``: ``frames_in`` steps of ``x, y, z, r`` -> next ``x, y, z``.

    Args:
        pos: Position tensor of shape ``(T, N, 3)``.
        rad: Radius tensor of shape ``(T, N, 1)``.
        frames_in: Number of input frames in each supervised window.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]: ``X`` of shape
        ``((T - frames_in) * N, frames_in, 4)`` and ``y`` of shape
        ``((T - frames_in) * N, 3)``.
    """
    Xs, Ys = [], []
    for t0 in range(pos.shape[0] - frames_in):
        t1 = t0 + frames_in
        x_seq = np.concatenate([pos[t0:t1], rad[t0:t1]], axis=-1)  # (frames_in, N, 4)
        Xs.append(np.transpose(x_seq, (1, 0, 2)))  # (N, frames_in, 4)
        Ys.append(pos[t1])  # (N, 3)
    return np.concatenate(Xs), np.concatenate(Ys)


def train_test_split(X, y, val_fraction=0.1, seed=0):
    """Shuffle and split arrays into train/validation subsets.

    Args:
        X: Feature array (first axis is samples).
        y: Target array aligned with ``X``.
        val_fraction: Fraction of samples reserved for validation.
        seed: RNG seed for the shuffle.

    Returns:
        tuple: ``(X_train, y_train, X_val, y_val)``.
    """
    idx = np.arange(X.shape[0])
    np.random.default_rng(seed).shuffle(idx)
    split = int((1.0 - val_fraction) * len(idx))
    tr, te = idx[:split], idx[split:]
    return X[tr], y[tr], X[te], y[te]
