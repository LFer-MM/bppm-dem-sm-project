"""Tests for RNNSR training: the GRU and the SR model fitted on the same frames."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bppm_dem_sm.config import ExperimentConfig, StochasticOptions
from bppm_dem_sm.model import training
from bppm_dem_sm.model.rnn import training as rnn_training
from bppm_dem_sm.model.sr import SRModel

from helpers import write_frame

# --- Helpers -----------------------------------------------------------------


class _StubHistory:
    """Minimal stand-in for a Keras ``History``."""
    def __init__(self, history):
        self.history = history


class _StubModel:
    """Keras-model stand-in: fixed loss history, empty file on ``save``."""
    def summary(self):
        pass

    def fit(self, X, y, validation_data=None, epochs=1, batch_size=1, verbose=1):
        return _StubHistory({"loss": [1.0], "val_loss": [1.1]})

    def save(self, path):
        Path(path).touch()


# --- Tests -------------------------------------------------------------------


def test_train_and_save_persists_gru_history_and_sr(tmp_path, monkeypatch):
    ids = np.arange(4)
    train_dir = tmp_path / "train"
    train_dir.mkdir()
    for i in range(3):
        write_frame(train_dir / f"frame_{i:05d}.parquet", ids, np.zeros((4, 3)), np.full(4, 0.1))

    stub_model = _StubModel()
    monkeypatch.setattr(rnn_training, "build_rnn", lambda *a, **k: stub_model)

    config = ExperimentConfig(train_data_dir=train_dir, frames_in=2, model_path=tmp_path / "models" / "m.keras")
    model, history = training.train_and_save(config)

    assert model is stub_model
    assert history.history == {"loss": [1.0], "val_loss": [1.1]}
    for name in ("m.keras", "m.history.json", "m.sr.npz"):
        assert (tmp_path / "models" / name).is_file()


def test_train_and_save_fits_sr_on_dem_velocity_not_displacement(tmp_path, monkeypatch):
    # Positions never move, but the DEM velocity columns carry +/-2 along y,
    # which Eq. 2 must pick up. 0.5 is exact in float32, the loaded dtype.
    ids = np.arange(10)
    pos0 = np.full((10, 3), 0.5)
    v = np.zeros((10, 3))
    v[:5, 1] = 2.0
    v[5:, 1] = -2.0
    train_dir = tmp_path / "train"
    train_dir.mkdir()
    for i in range(3):
        write_frame(train_dir / f"frame_{i:05d}.parquet", ids, pos0, np.full(10, 0.5), v=v)

    monkeypatch.setattr(rnn_training, "build_rnn", lambda *a, **k: _StubModel())

    config = ExperimentConfig(
        train_data_dir=train_dir,
        frames_in=2,
        model_path=tmp_path / "m.keras",
        stochastic=StochasticOptions(velocity_cell_size=10.0, velocity_min_particles_per_cell=5),
    )
    training.train_and_save(config)

    sr_model = SRModel.load(tmp_path / "m.sr.npz")
    assert sr_model.sigma_at(pos0[:1])[0] == pytest.approx([0.0, 2.0, 0.0], abs=1e-6)
