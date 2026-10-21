"""Tests for the RNNModel wrapper and load_rnn's delegation (no TensorFlow needed)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from pm_dem_sm.model.rnn import RNNModel
from pm_dem_sm.model.rnn import loading

# --- Helpers -----------------------------------------------------------------


class _StubNetwork:
    """Keras-network stand-in returning extra columns, as a wider output layer would."""

    input_shape = (None, 2, 4)
    output_shape = (None, 4)

    def predict(self, x, batch_size=32, verbose=0):
        self.batch_size = batch_size
        return x[:, -1, :].astype(np.float64)

    def save(self, path):
        Path(path).write_bytes(b"stub")


# --- Tests -------------------------------------------------------------------


def test_predict_returns_float32_xyz_per_particle():
    network = _StubNetwork()
    windows = np.arange(2 * 2 * 4, dtype=np.float64).reshape(2, 2, 4)

    xyz = RNNModel(network).predict(windows, batch_size=7)

    assert xyz.shape == (2, 3)
    assert xyz.dtype == np.float32
    assert np.allclose(xyz, windows[:, -1, :3])
    assert network.batch_size == 7


def test_shapes_come_from_the_network():
    model = RNNModel(_StubNetwork())
    assert model.input_shape == (None, 2, 4)
    assert model.output_shape == (None, 4)


def test_save_creates_parent_dirs(tmp_path):
    path = tmp_path / "models" / "m.keras"
    RNNModel(_StubNetwork()).save(path)
    assert path.read_bytes() == b"stub"


def test_load_rnn_loads_the_resolved_path(tmp_path, monkeypatch):
    keras_path = tmp_path / "m.keras"
    keras_path.write_bytes(b"")
    seen = []
    monkeypatch.setattr(loading.RNNModel, "load", lambda path: seen.append(path) or "loaded")

    assert loading.load_rnn(tmp_path / "m") == "loaded"
    assert seen == [keras_path]
