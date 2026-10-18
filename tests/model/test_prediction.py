"""Tests for RNNSR prediction: the GRU stand-in plus the SR model's noise (Eq. 4)."""

from __future__ import annotations

import numpy as np
import pytest

from bppm_dem_sm.config import ExperimentConfig, PredictionOptions, StochasticOptions
from bppm_dem_sm.data_processing import frames as data_io
from bppm_dem_sm.model import prediction
from bppm_dem_sm.model.sr import SRModel
from bppm_dem_sm.model.sr.fitting import fit_and_save_sr

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
        pos, _, _ = data_io.load_frames_stacked(train_dir)
        vel = data_io.load_velocities_stacked(train_dir)
        fit_and_save_sr(pos, vel, config)
    return config


def _single_cell_model(sigma):
    """Return an SR model whose only cell, (0, 0, 0), has the given sigma vector."""
    return SRModel(cell_size=1.0, origin=np.zeros(3), sigma_by_cell={(0, 0, 0): np.asarray(sigma)})


# --- Tests -------------------------------------------------------------------


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
