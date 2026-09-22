"""Tests for particle radius count aggregation."""

from __future__ import annotations

import pandas as pd

from bppm_dem_sm.data_processing.integrity import particle_radius_counts_per_file


def test_particle_radius_counts_per_file(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    pd.DataFrame({"r": [0.1, 0.1, 0.2]}).to_parquet(d / "a.parquet", index=False)
    df = particle_radius_counts_per_file(str(d), size_column="r")
    assert df.shape[0] == 1
    assert df.to_numpy().sum() > 0


def test_particle_radius_counts_empty_dir_returns_empty_dataframe(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    df = particle_radius_counts_per_file(str(empty), size_column="r")
    assert df.empty
