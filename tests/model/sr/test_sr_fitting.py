"""Tests for fitting the SR model's sigma_v(x) (Eq. 2)."""

from __future__ import annotations

import numpy as np
import pytest

from pm_dem_sm.config import ExperimentConfig, StochasticOptions
from pm_dem_sm.model.sr import SRModel
from pm_dem_sm.model.sr.fitting import fit_and_save_sr, fit_sr


def test_fit_sr_zero_for_uniform_motion():
    rng = np.random.default_rng(0)
    pos = rng.uniform(0, 1, size=(3, 20, 3))
    vel = np.tile(np.array([0.1, 0.0, -0.2]), (3, 20, 1))

    model = fit_sr(pos, vel, cell_size=1.0, min_particles_per_cell=5)

    assert np.allclose(model.sigma_at(pos[0]), 0.0, atol=1e-6)


def test_fit_sr_matches_known_variance_per_axis():
    # 10 particles in a single cell; half move at +1, half at -1 along x.
    pos = np.full((1, 10, 3), 0.1)
    vel = np.zeros((1, 10, 3))
    vel[0, :5, 0] = 1.0
    vel[0, 5:, 0] = -1.0

    model = fit_sr(pos, vel, cell_size=10.0, min_particles_per_cell=5)

    # Eq. 2 per axis: x velocities are +/-1 around a zero mean, y and z are 0.
    assert model.sigma_at(pos[0, :1])[0] == pytest.approx([1.0, 0.0, 0.0], abs=1e-6)


def test_fit_sr_cell_outside_data_is_zero():
    pos = np.zeros((1, 6, 3))
    vel = np.zeros((1, 6, 3))
    vel[0, :, 0] = [1.0, -1.0, 2.0, -2.0, 0.5, -0.5]

    model = fit_sr(pos, vel, cell_size=1.0, min_particles_per_cell=6)

    far_away = np.array([[1000.0, 1000.0, 1000.0]])
    assert np.all(model.sigma_at(far_away)[0] == 0.0)


def test_cell_below_min_particles_excluded():
    pos = np.zeros((1, 3, 3))
    vel = np.array([[[1.0, 0, 0], [-1.0, 0, 0], [2.0, 0, 0]]])

    model = fit_sr(pos, vel, cell_size=1.0, min_particles_per_cell=10)

    assert model.sigma_by_cell == {}
    assert np.all(model.sigma_at(pos[0])[0] == 0.0)


def test_fit_sr_requires_frames():
    with pytest.raises(ValueError):
        fit_sr(np.zeros((0, 3, 3)), np.zeros((0, 3, 3)), cell_size=1.0)


def test_fit_and_save_sr_uses_config_and_saves_next_to_gru(tmp_path):
    pos = np.full((1, 10, 3), 0.5)
    vel = np.zeros((1, 10, 3))
    vel[0, :5, 1] = 2.0
    vel[0, 5:, 1] = -2.0
    config = ExperimentConfig(
        model_path=tmp_path / "models" / "m.keras",
        stochastic=StochasticOptions(velocity_cell_size=10.0, velocity_min_particles_per_cell=5),
    )

    model = fit_and_save_sr(pos, vel, config)

    assert model.cell_size == 10.0
    saved = SRModel.load(tmp_path / "models" / "m.sr.npz")
    assert saved.sigma_at(pos[0, :1])[0] == pytest.approx([0.0, 2.0, 0.0], abs=1e-6)
