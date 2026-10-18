"""Tests for the SR model's lookup, Gaussian draw, and .npz format."""

from __future__ import annotations

import numpy as np

from bppm_dem_sm.model.sr import SRModel

# --- Helpers -----------------------------------------------------------------


def _single_cell_model(sigma):
    """Return an SR model whose only cell, (0, 0, 0), has the given sigma vector."""
    return SRModel(cell_size=1.0, origin=np.zeros(3), sigma_by_cell={(0, 0, 0): np.asarray(sigma)})


# --- Tests -------------------------------------------------------------------


def test_sigma_at_returns_zero_outside_known_cells():
    model = _single_cell_model([1.0, 2.0, 3.0])
    assert np.allclose(model.sigma_at(np.zeros((1, 3)))[0], [1.0, 2.0, 3.0])
    assert np.all(model.sigma_at(np.array([[1000.0, 1000.0, 1000.0]]))[0] == 0.0)


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
    model = SRModel(
        cell_size=0.5,
        origin=np.array([-1.0, 0.0, 2.0]),
        sigma_by_cell={(0, 1, 2): np.array([0.1, 0.2, 0.3]), (3, -1, 0): np.array([1.0, 0.0, 0.5])},
    )
    path = tmp_path / "models" / "m.sr.npz"
    model.save(path)

    loaded = SRModel.load(path)
    assert loaded.cell_size == model.cell_size
    assert np.allclose(loaded.origin, model.origin)
    assert set(loaded.sigma_by_cell) == set(model.sigma_by_cell)
    for key, sigma in model.sigma_by_cell.items():
        assert np.allclose(loaded.sigma_by_cell[key], sigma)


def test_save_load_roundtrip_empty_model(tmp_path):
    path = tmp_path / "empty.sr.npz"
    SRModel(cell_size=1.0, origin=np.zeros(3), sigma_by_cell={}).save(path)
    assert SRModel.load(path).sigma_by_cell == {}
