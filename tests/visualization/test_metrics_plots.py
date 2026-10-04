"""Tests for the metrics comparison plots (no display)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from bppm_dem_sm.config import ComputingSpeedOptions, ExperimentConfig, MetricsOptions, PredictionOptions
from bppm_dem_sm.metrics import computing_speed as cs_module
from bppm_dem_sm.metrics import run_metrics
from bppm_dem_sm.visualization import metrics_plots


def _write_frame(path, ids, xyz, r):
    """Write one parquet frame with ``id``, ``x``, ``y``, ``z``, ``r`` columns."""
    pd.DataFrame(
        {"id": ids, "x": xyz[:, 0], "y": xyz[:, 1], "z": xyz[:, 2], "r": r}
    ).to_parquet(path, index=False)


def _write_gt_frames(data_dir, seed=0):
    """Write 3 ground-truth frames of 8 bidisperse particles in linear motion."""
    data_dir.mkdir(parents=True, exist_ok=True)
    ids = np.arange(8)
    r = np.array([0.1] * 4 + [0.2] * 4)
    rng = np.random.default_rng(seed)
    pos0 = rng.uniform(-1, 1, size=(8, 3))
    v = rng.normal(0, 0.1, size=(8, 3))
    dt = 0.05
    for step in range(3):
        _write_frame(data_dir / f"frame_{step:05d}.parquet", ids, pos0 + step * v * dt, r)


def _write_pred_frames(pred_frames_dir, start_idx, seed=1):
    """Write 2 predicted frames numbered from ``start_idx``."""
    pred_frames_dir.mkdir(parents=True, exist_ok=True)
    ids = np.arange(8)
    r = np.array([0.1] * 4 + [0.2] * 4)
    rng = np.random.default_rng(seed)
    pos0 = rng.uniform(-1, 1, size=(8, 3))
    v = rng.normal(0, 0.1, size=(8, 3))
    dt = 0.05
    for step in range(2):
        idx = start_idx + step
        _write_frame(pred_frames_dir / f"pred_frame_{idx:05d}.parquet", ids, pos0 + step * v * dt, r)


def _base_config(tmp_path, with_pred):
    """Build a config over fresh GT frames, plus predicted frames if ``with_pred``."""
    data_dir = tmp_path / "data"
    _write_gt_frames(data_dir)

    out_dir = tmp_path / "out"
    if with_pred:
        _write_pred_frames(out_dir / "pred_frames", start_idx=10)

    return ExperimentConfig(
        data_dir=data_dir,
        prediction=PredictionOptions(pred_out_dir=out_dir),
        metrics=MetricsOptions(
            cell_size=100.0,
            min_particles_per_cell=2,
            metrics_dt=0.05,
            n_radial_bins=2,
            n_axial_bins=2,
        ),
    )


def test_plot_functions_run_without_error(tmp_path):
    config = _base_config(tmp_path, with_pred=True)
    metrics = run_metrics.compute_metrics(config)

    fig1 = metrics_plots.plot_lacey_comparison(metrics, config, show=False)
    fig2 = metrics_plots.plot_segregation_profile(metrics, config, show=False)
    fig3 = metrics_plots.plot_velocity_distribution(metrics, config, show=False)
    fig4 = metrics_plots.plot_granular_temperature(metrics, config, show=False)

    for fig in (fig1, fig2, fig3, fig4):
        assert fig is not None
        plt.close(fig)


def test_plot_velocity_and_granular_temperature_none_without_velocity(tmp_path):
    metrics = {"gt": pd.DataFrame({"time": [0.0], "lacey": [0.5]})}
    config = ExperimentConfig()
    assert metrics_plots.plot_velocity_distribution(metrics, config, show=False) is None
    assert metrics_plots.plot_granular_temperature(metrics, config, show=False) is None


def test_plot_computing_speed_none_when_missing():
    config = ExperimentConfig()
    assert metrics_plots.plot_computing_speed({}, config, show=False) is None
    assert metrics_plots.plot_computing_speed({"computing_speed": {}}, config, show=False) is None


def test_plot_computing_speed_none_when_no_speedup_available(tmp_path, monkeypatch):
    monkeypatch.setattr(cs_module, "REPORTS_DIR", tmp_path)
    config = ExperimentConfig()
    cs = cs_module.compute_computing_speed({}, config)
    assert metrics_plots.plot_computing_speed({"computing_speed": cs}, config, show=False) is None


def test_plot_computing_speed_renders_available_bars(tmp_path, monkeypatch):
    monkeypatch.setattr(cs_module, "REPORTS_DIR", tmp_path)
    config = ExperimentConfig(computing_speed=ComputingSpeedOptions(dem_reference_seconds=1000.0))
    cs = cs_module.compute_computing_speed({"train_seconds": 80.0, "predict_seconds": 20.0}, config)

    fig = metrics_plots.plot_computing_speed({"computing_speed": cs}, config, show=False)
    assert fig is not None
    plt.close(fig)
