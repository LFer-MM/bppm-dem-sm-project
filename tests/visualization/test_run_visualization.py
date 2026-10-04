"""Tests for the Visualization stage orchestrator (no display, no real disk writes)."""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from bppm_dem_sm.config import ExperimentConfig, MetricsOptions, PredictionOptions
from bppm_dem_sm.metrics import computing_speed as cs_module
from bppm_dem_sm.metrics import run_metrics
from bppm_dem_sm.visualization import run_visualization

from helpers import write_frame, write_frames


def test_generate_visualizations_empty_run_returns_no_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(cs_module, "REPORTS_DIR", tmp_path / "reports")
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    config = ExperimentConfig(
        data_dir=data_dir,
        prediction=PredictionOptions(pred_out_dir=tmp_path / "out"),
        model_path=tmp_path / "models" / "no_such_model.keras",
    ).with_overrides(show_plots=False, save_figures=False)

    artifacts = run_visualization.generate_visualizations(config)
    assert artifacts == {}


@pytest.mark.filterwarnings("ignore:FigureCanvasAgg is non-interactive.*:UserWarning")
def test_generate_visualizations_full_run_reloads_persisted_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr(cs_module, "REPORTS_DIR", tmp_path / "reports")

    data_dir = tmp_path / "data"
    write_frames(data_dir, n_frames=3, seed=0)

    out_dir = tmp_path / "out"
    write_frames(out_dir / "pred_frames", n_frames=2, start_idx=10, seed=1, prefix="pred_frame")

    model_path = tmp_path / "models" / "model.keras"
    model_path.parent.mkdir(parents=True)
    model_path.touch()
    history_path = model_path.with_suffix(".history.json")
    history_path.write_text(json.dumps({"loss": [1.0, 0.5], "val_loss": [1.1, 0.6]}), encoding="utf-8")

    config = ExperimentConfig(
        data_dir=data_dir,
        prediction=PredictionOptions(pred_out_dir=out_dir),
        model_path=model_path,
        metrics=MetricsOptions(cell_size=100.0, min_particles_per_cell=2, n_radial_bins=2, n_axial_bins=2),
    ).with_overrides(show_plots=True, save_figures=False)

    # Populate every file generate_visualizations reads, exactly as do_metrics would.
    run_metrics.compute_metrics(config)

    artifacts = run_visualization.generate_visualizations(config)

    assert "training_curves_figure" in artifacts
    plt.close(artifacts["training_curves_figure"])

    assert "grid_figure" in artifacts
    assert "sr_grid_figure" in artifacts
    plt.close(artifacts["grid_figure"])
    plt.close(artifacts["sr_grid_figure"])

    assert "metrics" in artifacts
    assert "gt" in artifacts["metrics"]

    assert "animation" in artifacts


def test_plot_frame_grid_and_plot_sr_grid_use_different_cell_sizes(tmp_path):
    frame_path = tmp_path / "frame_00000.parquet"
    ids = np.arange(8)
    write_frame(frame_path, ids, np.zeros((8, 3)), np.array([0.1] * 4 + [0.2] * 4))

    config = ExperimentConfig(
        metrics=MetricsOptions(cell_size=1.0),
    ).with_overrides(velocity_cell_size=2.0)
    assert config.metrics.cell_size != config.stochastic.velocity_cell_size

    fig1 = run_visualization.plot_frame_grid(frame_path, config, show=False)
    fig2 = run_visualization.plot_sr_grid(frame_path, config, show=False)

    assert fig1.axes[0].get_title() == "Particle Positions with Grid (cell size = 1.0 m)"
    assert fig2.axes[0].get_title() == "Particle Positions with Grid (cell size = 2.0 m)"
    plt.close(fig1)
    plt.close(fig2)
