"""Tests for GRU training's model + history persistence (no TensorFlow needed)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from bppm_dem_sm.config import ExperimentConfig, PredictionOptions, TrainingOptions
from bppm_dem_sm.model.rnn import training

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
        self.fit_targets = np.concatenate([y, validation_data[1]])
        return _StubHistory({"loss": [1.0, 0.5], "val_loss": [1.1, 0.6]})

    def save(self, path):
        Path(path).touch()


# --- Tests -------------------------------------------------------------------


def test_train_and_save_persists_model_and_history_json(tmp_path, monkeypatch):
    ids = np.arange(4)
    pos = np.zeros((4, 3))
    r = np.full(4, 0.1)

    train_dir = tmp_path / "train"
    train_dir.mkdir()
    for i in range(3):
        write_frame(train_dir / f"frame_{i:05d}.parquet", ids, pos, r, v=np.zeros((4, 3)))

    stub_model = _StubModel()
    monkeypatch.setattr(training, "build_model", lambda *a, **k: stub_model)

    config = ExperimentConfig(
        train_data_dir=train_dir,
        frames_in=2,
        model_path=tmp_path / "models" / "test_model.keras",
    )

    model, history = training.train_and_save(config)

    assert model is stub_model
    assert history.history == {"loss": [1.0, 0.5], "val_loss": [1.1, 0.6]}
    assert (tmp_path / "models" / "test_model.keras").is_file()

    history_path = tmp_path / "models" / "test_model.history.json"
    assert history_path.is_file()
    saved = json.loads(history_path.read_text(encoding="utf-8"))
    assert saved == {"loss": [1.0, 0.5], "val_loss": [1.1, 0.6]}


def test_train_and_save_trains_on_local_mean_positions(tmp_path, monkeypatch):
    ids = np.arange(4)
    r = np.full(4, 0.1)
    v = np.full((4, 3), 2.0)

    train_dir = tmp_path / "train"
    train_dir.mkdir()
    for i in range(3):
        write_frame(train_dir / f"frame_{i:05d}.parquet", ids, np.full((4, 3), float(i)), r, v=v)

    stub_model = _StubModel()
    monkeypatch.setattr(training, "build_model", lambda *a, **k: stub_model)

    config = ExperimentConfig(
        train_data_dir=train_dir,
        frames_in=2,
        model_path=tmp_path / "m.keras",
        prediction=PredictionOptions(dt_step=0.05),
    )
    training.train_and_save(config)

    # Target is frame 2's local mean component (Eq. 1): 2 - 2.0 * 0.05.
    assert np.allclose(stub_model.fit_targets, 1.9)


def test_train_and_save_requires_velocity_for_local_mean(tmp_path, monkeypatch):
    train_dir = tmp_path / "train"
    train_dir.mkdir()
    for i in range(3):
        write_frame(train_dir / f"frame_{i:05d}.parquet", np.arange(4), np.zeros((4, 3)), np.full(4, 0.1))

    monkeypatch.setattr(training, "build_model", lambda *a, **k: _StubModel())
    config = ExperimentConfig(train_data_dir=train_dir, frames_in=2, model_path=tmp_path / "m.keras")

    with pytest.raises(ValueError, match="velocity"):
        training.train_and_save(config)

    raw = config.with_overrides(training=TrainingOptions(local_mean_conversion=False))
    training.train_and_save(raw)
