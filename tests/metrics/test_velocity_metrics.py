"""Tests for velocity-distribution and granular-temperature metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from bppm_dem_sm.metrics import velocity_metrics as vm


def _frame(ids, xyz, r):
    """Build a frame table from ids, an ``(N, 3)`` position array, and radii."""
    return pd.DataFrame(
        {"id": ids, "x": xyz[:, 0], "y": xyz[:, 1], "z": xyz[:, 2], "r": r}
    )


def test_velocity_speed_by_species_splits_correctly():
    ids = np.arange(4)
    pos0 = np.zeros((4, 3))
    v = np.array([[3.0, 4.0, 0.0], [0.0, 0.0, 5.0], [1.0, 0.0, 0.0], [0.0, 2.0, 0.0]])
    r = np.array([0.1, 0.1, 0.2, 0.2])  # first two small, last two large
    dt = 1.0

    df_t = _frame(ids, pos0, r)
    df_t1 = _frame(ids, pos0 + v * dt, r)

    speeds = vm.velocity_speed_by_species(df_t, df_t1, dt, tracer_radius=0.2)
    assert np.allclose(sorted(speeds["small"]), [5.0, 5.0])
    assert np.allclose(sorted(speeds["large"]), [1.0, 2.0])


def test_velocity_speed_by_species_handles_out_of_order_ids():
    ids_t = np.array([2, 0, 1])
    ids_t1 = np.array([0, 1, 2])
    pos0 = np.zeros((3, 3))
    r = np.array([0.1, 0.1, 0.1])
    df_t = _frame(ids_t, pos0, r)
    df_t1 = _frame(ids_t1, pos0, r)  # zero velocity regardless of order

    speeds = vm.velocity_speed_by_species(df_t, df_t1, dt=1.0, tracer_radius=99.0)
    assert np.allclose(speeds["small"], [0.0, 0.0, 0.0])
    assert speeds["large"].size == 0


def test_mismatched_ids_raise():
    df_t = _frame(np.array([1, 2]), np.zeros((2, 3)), np.array([0.1, 0.1]))
    df_t1 = _frame(np.array([1, 3]), np.zeros((2, 3)), np.array([0.1, 0.1]))
    with pytest.raises(ValueError):
        vm.velocity_speed_by_species(df_t, df_t1, dt=1.0, tracer_radius=0.1)


def test_granular_temperature_matches_known_variance():
    # 10 particles in one cell; half move at +v, half at -v along x -> mean v = 0.
    ids = np.arange(10)
    pos0 = np.tile(np.array([0.1, 0.1, 0.1]), (10, 1))
    v = np.zeros((10, 3))
    v[:5, 0] = 1.0
    v[5:, 0] = -1.0
    r = np.full(10, 0.1)
    dt = 1.0

    df_t = _frame(ids, pos0, r)
    df_t1 = _frame(ids, pos0 + v * dt, r)

    temps = vm.granular_temperature_by_cell(df_t, df_t1, dt, cell_size=10.0, min_particles_per_cell=5)
    # sigma_v^2 = mean(||v_i||^2) = 1.0 (mean v is 0); T_g = sigma_v^2 / 3.
    assert temps.shape == (1,)
    assert temps[0] == pytest.approx(1.0 / 3.0, rel=1e-6)


def test_granular_temperature_excludes_sparse_cells():
    ids = np.arange(3)
    pos0 = np.zeros((3, 3))
    v = np.array([[1.0, 0, 0], [-1.0, 0, 0], [2.0, 0, 0]])
    r = np.full(3, 0.1)
    dt = 1.0

    df_t = _frame(ids, pos0, r)
    df_t1 = _frame(ids, pos0 + v * dt, r)

    temps = vm.granular_temperature_by_cell(df_t, df_t1, dt, cell_size=1.0, min_particles_per_cell=10)
    assert temps.size == 0


def test_granular_temperature_zero_for_uniform_motion():
    ids = np.arange(6)
    pos0 = np.random.default_rng(0).uniform(0, 1, size=(6, 3))
    v = np.tile(np.array([0.2, -0.1, 0.05]), (6, 1))
    r = np.full(6, 0.1)
    dt = 1.0

    df_t = _frame(ids, pos0, r)
    df_t1 = _frame(ids, pos0 + v * dt, r)

    temps = vm.granular_temperature_by_cell(df_t, df_t1, dt, cell_size=10.0, min_particles_per_cell=5)
    assert np.allclose(temps, 0.0, atol=1e-10)
