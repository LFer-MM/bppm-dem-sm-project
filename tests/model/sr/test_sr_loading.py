"""Tests for locating and loading the SR model saved next to the GRU."""

from __future__ import annotations

import numpy as np
import pytest

from pm_dem_sm.model.sr import SRModel
from pm_dem_sm.model.sr.loading import load_sr, sr_path_for


def test_sr_path_for_sits_next_to_the_gru(tmp_path):
    assert sr_path_for(tmp_path / "m.keras") == tmp_path / "m.sr.npz"
    assert sr_path_for(tmp_path / "m.h5") == tmp_path / "m.sr.npz"
    assert sr_path_for(tmp_path / "m") == tmp_path / "m.sr.npz"


def test_load_sr_reads_the_paired_file(tmp_path):
    model = SRModel(cell_size=0.5, origin=np.zeros(3), sigma_by_cell={(0, 0, 0): np.array([1.0, 2.0, 3.0])})
    model.save(tmp_path / "m.sr.npz")

    loaded = load_sr(tmp_path / "m.keras")

    assert loaded.cell_size == 0.5
    assert np.allclose(loaded.sigma_by_cell[(0, 0, 0)], [1.0, 2.0, 3.0])


def test_load_sr_raises_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="do_train"):
        load_sr(tmp_path / "m.keras")
