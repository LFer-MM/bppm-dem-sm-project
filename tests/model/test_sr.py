"""Tests for the stochastic random (SR) velocity perturbation module."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from bppm_dem_sm.model.rnn import prediction
from bppm_dem_sm.model import sr as sm
from bppm_dem_sm.config import ExperimentConfig, PredictionOptions, StochasticOptions


def _write_frame(path, ids, xyz):
    pd.DataFrame(
        {
            "id": ids,
            "x": xyz[:, 0],
            "y": xyz[:, 1],
            "z": xyz[:, 2],
        }
    ).to_parquet(path, index=False)


def test_build_velocity_std_field_zero_for_uniform_motion(tmp_path):
    ids = np.arange(20)
    rng = np.random.default_rng(0)
    pos0 = rng.uniform(0, 1, size=(20, 3))
    velocity = np.array([0.1, 0.0, -0.2])
    dt = 0.05

    _write_frame(tmp_path / "frame_00000.parquet", ids, pos0)
    _write_frame(tmp_path / "frame_00001.parquet", ids, pos0 + velocity * dt)
    _write_frame(tmp_path / "frame_00002.parquet", ids, pos0 + 2 * velocity * dt)

    field = sm.build_velocity_std_field(
        tmp_path, "frame_*.parquet", dt=dt, cell_size=1.0, min_particles_per_cell=5
    )

    sigmas = field.sigma_at(pos0)
    assert np.allclose(sigmas, 0.0, atol=1e-6)


def test_build_velocity_std_field_matches_known_variance(tmp_path):
    # 10 particles in a single cell; half move at +v, half at -v along x.
    ids = np.arange(10)
    pos0 = np.tile(np.array([0.1, 0.1, 0.1]), (10, 1))
    v = np.zeros((10, 3))
    v[:5, 0] = 1.0
    v[5:, 0] = -1.0
    dt = 1.0

    _write_frame(tmp_path / "frame_00000.parquet", ids, pos0)
    _write_frame(tmp_path / "frame_00001.parquet", ids, pos0 + v * dt)

    field = sm.build_velocity_std_field(
        tmp_path, "frame_*.parquet", dt=dt, cell_size=10.0, min_particles_per_cell=5
    )

    # mean velocity is 0, so sigma_v = sqrt(mean(||v_i||^2)) = sqrt(1.0) = 1.0
    sigma = field.sigma_at(pos0[:1])[0]
    assert sigma == pytest.approx(1.0, rel=1e-6)


def test_sigma_at_returns_zero_outside_known_cells(tmp_path):
    ids = np.arange(6)
    pos0 = np.zeros((6, 3))
    v = np.zeros((6, 3))
    v[:, 0] = np.array([1.0, -1.0, 2.0, -2.0, 0.5, -0.5])
    dt = 1.0

    _write_frame(tmp_path / "frame_00000.parquet", ids, pos0)
    _write_frame(tmp_path / "frame_00001.parquet", ids, pos0 + v * dt)

    field = sm.build_velocity_std_field(
        tmp_path, "frame_*.parquet", dt=dt, cell_size=1.0, min_particles_per_cell=6
    )
    far_away = np.array([[1000.0, 1000.0, 1000.0]])
    assert field.sigma_at(far_away)[0] == 0.0


def test_cell_below_min_particles_excluded(tmp_path):
    ids = np.arange(3)
    pos0 = np.zeros((3, 3))
    v = np.array([[1.0, 0, 0], [-1.0, 0, 0], [2.0, 0, 0]])
    dt = 1.0

    _write_frame(tmp_path / "frame_00000.parquet", ids, pos0)
    _write_frame(tmp_path / "frame_00001.parquet", ids, pos0 + v * dt)

    field = sm.build_velocity_std_field(
        tmp_path, "frame_*.parquet", dt=dt, cell_size=1.0, min_particles_per_cell=10
    )
    assert field.sigma_by_cell == {}
    assert field.sigma_at(pos0)[0] == 0.0


def test_build_velocity_std_field_requires_two_frames(tmp_path):
    _write_frame(tmp_path / "frame_00000.parquet", np.arange(3), np.zeros((3, 3)))
    with pytest.raises(ValueError):
        sm.build_velocity_std_field(tmp_path, "frame_*.parquet", dt=0.05, cell_size=1.0)


def test_sample_stochastic_displacement_zero_sigma_gives_zero_displacement():
    field = sm.VelocityStdField(cell_size=1.0, origin=np.zeros(3), sigma_by_cell={(0, 0, 0): 0.0})
    positions = np.zeros((5, 3))
    rng = np.random.default_rng(1)
    disp = sm.sample_stochastic_displacement(positions, field, dt_rnn=0.05, rng=rng)
    assert disp.shape == (5, 3)
    assert np.allclose(disp, 0.0)


def test_sample_stochastic_displacement_reproducible_with_seed():
    field = sm.VelocityStdField(cell_size=1.0, origin=np.zeros(3), sigma_by_cell={(0, 0, 0): 0.5})
    positions = np.zeros((5, 3))
    disp1 = sm.sample_stochastic_displacement(positions, field, 0.05, np.random.default_rng(42))
    disp2 = sm.sample_stochastic_displacement(positions, field, 0.05, np.random.default_rng(42))
    assert np.allclose(disp1, disp2)
    assert not np.allclose(disp1, 0.0)


def test_stochastic_options_default_disabled():
    config = ExperimentConfig()
    assert config.stochastic.enabled is False
    assert isinstance(config.stochastic, StochasticOptions)


def test_experiment_config_roundtrip_with_stochastic():
    config = ExperimentConfig().with_overrides(enabled=True, stochastic_seed=7)
    assert config.stochastic.enabled is True
    assert config.stochastic.stochastic_seed == 7

    data = config.to_dict()
    restored = ExperimentConfig.from_dict(data)
    assert restored.stochastic == config.stochastic


class _IdentityModel:
    """Stub GRU stand-in: 'predicts' the last input frame's (x, y, z) unchanged."""

    input_shape = (None, 2, 4)
    output_shape = (None, 3)

    def predict(self, x_in, batch_size=32, verbose=0):
        return x_in[:, -1, :3]


def _write_full_frame(path, ids, xyz, r):
    pd.DataFrame(
        {"id": ids, "x": xyz[:, 0], "y": xyz[:, 1], "z": xyz[:, 2], "r": r}
    ).to_parquet(path, index=False)


def _make_predict_config(tmp_path, *, stochastic_enabled, seed=0):
    ids = np.arange(8)
    pos0 = np.zeros((8, 3))
    r = np.full(8, 0.5)

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    _write_full_frame(data_dir / "frame_00000.parquet", ids, pos0, r)
    _write_full_frame(data_dir / "frame_00001.parquet", ids, pos0, r)

    train_dir = tmp_path / "train"
    train_dir.mkdir(parents=True)
    v = np.zeros((8, 3))
    v[::2, 0] = 1.0
    v[1::2, 0] = -1.0
    _write_full_frame(train_dir / "frame_00000.parquet", ids, pos0, r)
    _write_full_frame(train_dir / "frame_00001.parquet", ids, pos0 + v, r)
    _write_full_frame(train_dir / "frame_00002.parquet", ids, pos0 + 2 * v, r)

    return ExperimentConfig(
        data_dir=data_dir,
        train_data_dir=train_dir,
        frames_in=2,
        prediction=PredictionOptions(
            start_frame=0,
            autoregressive=True,
            predict_until_end=False,
            max_steps=1,
            dt_step=0.05,
            pred_out_dir=tmp_path / "out",
        ),
        stochastic=StochasticOptions(
            enabled=stochastic_enabled,
            velocity_cell_size=10.0,
            velocity_min_particles_per_cell=5,
            stochastic_seed=seed,
        ),
    )


def test_predict_frames_leaves_positions_unchanged_when_disabled(tmp_path):
    config = _make_predict_config(tmp_path, stochastic_enabled=False)
    out = prediction.predict_frames(config, model=_IdentityModel())
    assert np.allclose(out[["x", "y", "z"]].to_numpy(), 0.0)


def test_predict_frames_perturbs_positions_after_gru_when_enabled(tmp_path):
    config = _make_predict_config(tmp_path, stochastic_enabled=True, seed=123)
    out = prediction.predict_frames(config, model=_IdentityModel())
    assert not np.allclose(out[["x", "y", "z"]].to_numpy(), 0.0)


def test_predict_frames_stochastic_reproducible_with_same_seed(tmp_path):
    config1 = _make_predict_config(tmp_path / "a", stochastic_enabled=True, seed=99)
    out1 = prediction.predict_frames(config1, model=_IdentityModel())

    config2 = _make_predict_config(tmp_path / "b", stochastic_enabled=True, seed=99)
    out2 = prediction.predict_frames(config2, model=_IdentityModel())

    assert np.allclose(out1[["x", "y", "z"]].to_numpy(), out2[["x", "y", "z"]].to_numpy())
