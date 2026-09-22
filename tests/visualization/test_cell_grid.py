"""Tests for cell-grid visualization (no display)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bppm_dem_sm.visualization import cell_grid as vis


def test_plot_particles_with_grid_runs(tmp_path):
    p = tmp_path / "f.parquet"
    n = 20
    rng = np.random.default_rng(1)
    pd.DataFrame(
        {
            "x": rng.uniform(-1, 1, n),
            "y": rng.uniform(-1, 1, n),
            "r": np.where(np.arange(n) % 2 == 0, 0.1, 0.2),
        }
    ).to_parquet(p, index=False)

    fig = vis.plot_particles_with_grid(str(p), cell_size=0.5, use_equal_aspect=True, show=False)
    assert fig is not None
    plt.close(fig)
