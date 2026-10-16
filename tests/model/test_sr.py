"""Tests for the stochastic random (SR) model and its use in prediction."""

from __future__ import annotations

import numpy as np
import pytest

from bppm_dem_sm.model.rnn import prediction
from bppm_dem_sm.model import sr as sm
from bppm_dem_sm.config import ExperimentConfig, PredictionOptions, StochasticOptions

from helpers import write_frame

# --- Helpers -----------------------------------------------------------------


class _IdentityModel:
    """Stub GRU stand-in: 'predicts' the last input frame's (x, y, z) unchanged."""

    input_shape = (None, 2, 4)
    output_shape = (None, 3)

    def predict(self, x_in, batch_size=32, verbose=0):
        return x_in[:, -1, :3]


def _make_predict_config(tmp_path, *, stochastic_enabled, seed=0, save_sr=True):
    """Build a one-step autoregressive config with a +/-x SR training set.

    When ``save_sr`` is set, the SR model is fitted on the training frames and
    saved next to ``model_path``, as training would.
    """
    ids = np.arange(8)
    pos0 = np.zeros((8, 3))
    r = np.full(8, 0.5)

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    write_frame(data_dir / "frame_00000.parquet", ids, pos0, r)
    write_frame(data_dir / "frame_00001.parquet", ids, pos0, r)

    train_dir = tmp_path / "train"
    train_dir.mkdir(parents=True)
    v = np.zeros((8, 3))
    v[::2, 0] = 1.0
    v[1::2, 0] = -1.0
    write_frame(train_dir / "frame_00000.parquet", ids, pos0, r, v=v)
    write_frame(train_dir / "frame_00001.parquet", ids, pos0 + v, r, v=v)
    write_frame(train_dir / "frame_00002.parquet", ids, pos0 + 2 * v, r, v=v)

    config = ExperimentConfig(
        data_dir=data_dir,
        train_data_dir=train_dir,
        model_path=tmp_path / "models" / "m.keras",
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
    if save_sr:
        sm.fit_sr_from_config(config).save(sm.sr_path_for(config.model_path))
    return config


def _single_cell_model(sigma):
    """Return an SR model whose only cell, (0, 0, 0), has the given sigma vector."""
    return sm.SRModel(cell_size=1.0, origin=np.zeros(3), sigma_by_cell={(0, 0, 0): np.asarray(sigma)})


# --- Tests -------------------------------------------------------------------


def test_fit_sr_zero_for_uniform_motion():
    rng = np.random.default_rng(0)
    pos = rng.uniform(0, 1, size=(3, 20, 3))
    vel = np.tile(np.array([0.1, 0.0, -0.2]), (3, 20, 1))

    model = sm.fit_sr(pos, vel, cell_size=1.0, min_particles_per_cell=5)

    assert np.allclose(model.sigma_at(pos[0]), 0.0, atol=1e-6)


def test_fit_sr_matches_known_variance_per_axis():
    # 10 particles in a single cell; half move at +1, half at -1 along x.
    pos = np.full((1, 10, 3), 0.1)
    vel = np.zeros((1, 10, 3))
    vel[0, :5, 0] = 1.0
    vel[0, 5:, 0] = -1.0

    model = sm.fit_sr(pos, vel, cell_size=10.0, min_particles_per_cell=5)

    # Eq. 2 per axis: x velocities are +/-1 around a zero mean, y and z are 0.
    assert model.sigma_at(pos[0, :1])[0] == pytest.approx([1.0, 0.0, 0.0], abs=1e-6)


def test_fit_sr_from_config_uses_dem_velocity_not_displacement(tmp_path):
    # Positions never move, but the DEM velocity columns carry +/-2 along y,
    # which Eq. 2 must pick up. 0.5 is exact in float32, the loaded dtype.
    ids = np.arange(10)
    pos0 = np.full((10, 3), 0.5)
    v = np.zeros((10, 3))
    v[:5, 1] = 2.0
    v[5:, 1] = -2.0
    write_frame(tmp_path / "frame_00000.parquet", ids, pos0, np.full(10, 0.5), v=v)
    write_frame(tmp_path / "frame_00001.parquet", ids, pos0, np.full(10, 0.5), v=v)

    config = ExperimentConfig(
        train_data_dir=tmp_path,
        stochastic=StochasticOptions(velocity_cell_size=10.0, velocity_min_particles_per_cell=5),
    )
    model = sm.fit_sr_from_config(config)

    assert model.sigma_at(pos0[:1])[0] == pytest.approx([0.0, 2.0, 0.0], abs=1e-6)


def test_sigma_at_returns_zero_outside_known_cells():
    pos = np.zeros((1, 6, 3))
    vel = np.zeros((1, 6, 3))
    vel[0, :, 0] = [1.0, -1.0, 2.0, -2.0, 0.5, -0.5]

    model = sm.fit_sr(pos, vel, cell_size=1.0, min_particles_per_cell=6)

    far_away = np.array([[1000.0, 1000.0, 1000.0]])
    assert np.all(model.sigma_at(far_away)[0] == 0.0)


def test_cell_below_min_particles_excluded():
    pos = np.zeros((1, 3, 3))
    vel = np.array([[[1.0, 0, 0], [-1.0, 0, 0], [2.0, 0, 0]]])

    model = sm.fit_sr(pos, vel, cell_size=1.0, min_particles_per_cell=10)

    assert model.sigma_by_cell == {}
    assert np.all(model.sigma_at(pos[0])[0] == 0.0)


def test_fit_sr_requires_frames():
    with pytest.raises(ValueError):
        sm.fit_sr(np.zeros((0, 3, 3)), np.zeros((0, 3, 3)), cell_size=1.0)


def test_sample_is_per_axis():
    model = _single_cell_model([1.0, 0.0, 0.0])
    v_tilde = model.sample(np.zeros((50, 3)), np.random.default_rng(0))
    assert not np.allclose(v_tilde[:, 0], 0.0)
    assert np.allclose(v_tilde[:, 1:], 0.0)


def test_sample_zero_sigma_gives_zero_velocity():
    v_tilde = _single_cell_model(np.zeros(3)).sample(np.zeros((5, 3)), np.random.default_rng(1))
    assert v_tilde.shape == (5, 3)
    assert np.allclose(v_tilde, 0.0)


def test_sample_reproducible_with_seed():
    model = _single_cell_model(np.full(3, 0.5))
    v1 = model.sample(np.zeros((5, 3)), np.random.default_rng(42))
    v2 = model.sample(np.zeros((5, 3)), np.random.default_rng(42))
    assert np.allclose(v1, v2)
    assert not np.allclose(v1, 0.0)


def test_save_load_roundtrip(tmp_path):
    model = sm.SRModel(
        cell_size=0.5,
        origin=np.array([-1.0, 0.0, 2.0]),
        sigma_by_cell={(0, 1, 2): np.array([0.1, 0.2, 0.3]), (3, -1, 0): np.array([1.0, 0.0, 0.5])},
    )
    path = sm.sr_path_for(tmp_path / "models" / "m.keras")
    model.save(path)

    assert path.name == "m.sr.npz"
    loaded = sm.SRModel.load(path)
    assert loaded.cell_size == model.cell_size
    assert np.allclose(loaded.origin, model.origin)
    assert set(loaded.sigma_by_cell) == set(model.sigma_by_cell)
    for key, sigma in model.sigma_by_cell.items():
        assert np.allclose(loaded.sigma_by_cell[key], sigma)


def test_save_load_roundtrip_empty_model(tmp_path):
    path = tmp_path / "empty.sr.npz"
    sm.SRModel(cell_size=1.0, origin=np.zeros(3), sigma_by_cell={}).save(path)
    assert sm.SRModel.load(path).sigma_by_cell == {}


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


def test_predict_frames_leaves_positions_unchanged_when_disabled(tmp_path):
    config = _make_predict_config(tmp_path, stochastic_enabled=False, save_sr=False)
    out = prediction.predict_frames(config, model=_IdentityModel())
    assert np.allclose(out[["x", "y", "z"]].to_numpy(), 0.0)


def test_predict_frames_perturbs_positions_after_gru_when_enabled(tmp_path):
    config = _make_predict_config(tmp_path, stochastic_enabled=True, seed=123)
    out = prediction.predict_frames(config, model=_IdentityModel())
    assert not np.allclose(out[["x", "y", "z"]].to_numpy(), 0.0)


def test_predict_frames_adds_v_tilde_times_dt(tmp_path):
    # Eq. 4: x = x_bar + v_tilde * dt_step, with x_bar = 0 from the identity stub.
    config = _make_predict_config(tmp_path, stochastic_enabled=True, seed=5, save_sr=False)
    model = _single_cell_model(np.full(3, 2.0))
    model.cell_size = 100.0

    out = prediction.predict_frames(config, model=_IdentityModel(), sr_model=model)

    expected = model.sample(np.zeros((8, 3)), np.random.default_rng(5)) * 0.05
    assert np.allclose(out[["x", "y", "z"]].to_numpy(), expected)


def test_predict_frames_requires_saved_sr_when_enabled(tmp_path):
    config = _make_predict_config(tmp_path, stochastic_enabled=True, save_sr=False)
    with pytest.raises(FileNotFoundError, match="do_train"):
        prediction.predict_frames(config, model=_IdentityModel())


def test_predict_frames_stochastic_reproducible_with_same_seed(tmp_path):
    config1 = _make_predict_config(tmp_path / "a", stochastic_enabled=True, seed=99)
    out1 = prediction.predict_frames(config1, model=_IdentityModel())

    config2 = _make_predict_config(tmp_path / "b", stochastic_enabled=True, seed=99)
    out2 = prediction.predict_frames(config2, model=_IdentityModel())

    assert np.allclose(out1[["x", "y", "z"]].to_numpy(), out2[["x", "y", "z"]].to_numpy())
