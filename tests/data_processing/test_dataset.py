"""Tests for supervised sliding-window dataset construction."""

from __future__ import annotations

import numpy as np

from bppm_dem_sm.data_processing.dataset import (
    build_supervised_dataset,
    local_mean_positions,
    train_test_split,
)


def test_build_supervised_dataset_shapes():
    T, N, frames_in = 5, 3, 2
    pos = np.arange(T * N * 3, dtype=np.float32).reshape(T, N, 3)
    rad = np.ones((T, N, 1), dtype=np.float32)

    X, y = build_supervised_dataset(pos, rad, frames_in)

    assert X.shape == ((T - frames_in) * N, frames_in, 4)
    assert y.shape == ((T - frames_in) * N, 3)


def test_build_supervised_dataset_targets_match_next_frame():
    T, N, frames_in = 3, 2, 2
    pos = np.arange(T * N * 3, dtype=np.float32).reshape(T, N, 3)
    rad = np.zeros((T, N, 1), dtype=np.float32)

    X, y = build_supervised_dataset(pos, rad, frames_in)

    # Only one window (t0=0, t1=2): targets should be pos[2].
    assert np.allclose(y, pos[2])
    # Each window's last input frame should be pos[1] (x, y, z only).
    assert np.allclose(X[:, -1, :3], pos[1])


def test_local_mean_positions_subtracts_velocity_displacement():
    pos = np.ones((2, 3, 3), dtype=np.float32)
    vel = np.full((2, 3, 3), 2.0, dtype=np.float32)

    out = local_mean_positions(pos, vel, dt_rnn=0.05)

    # Eq. 1: x_bar = x - v * dt_RNN = 1 - 2 * 0.05
    assert out.dtype == np.float32
    assert np.allclose(out, 0.9)


def test_train_test_split_sizes_and_reproducible_with_seed():
    X = np.arange(20).reshape(10, 2)
    y = np.arange(10)

    Xtr1, ytr1, Xval1, yval1 = train_test_split(X, y, val_fraction=0.2, seed=0)
    assert Xtr1.shape[0] == 8
    assert Xval1.shape[0] == 2

    Xtr2, ytr2, Xval2, yval2 = train_test_split(X, y, val_fraction=0.2, seed=0)
    assert np.array_equal(ytr1, ytr2)
    assert np.array_equal(yval1, yval2)
