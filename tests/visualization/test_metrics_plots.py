"""Tests for the metrics comparison plots (no display)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from bppm_dem_sm.config import ComputingSpeedOptions, ExperimentConfig
from bppm_dem_sm.metrics import computing_speed as cs_module
from bppm_dem_sm.metrics import run_metrics
from bppm_dem_sm.visualization import metrics_plots

from helpers import metrics_config


def test_plot_functions_run_without_error(tmp_path):
    config = metrics_config(tmp_path, with_pred=True)
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
