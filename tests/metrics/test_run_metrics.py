"""Integration tests for compute_metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from bppm_dem_sm.metrics import run_metrics
from bppm_dem_sm.config import ExperimentConfig, MetricsOptions, PredictionOptions

from helpers import metrics_config, write_frame


def test_compute_metrics_gt_only(tmp_path):
    config = metrics_config(tmp_path, with_pred=False)
    metrics = run_metrics.compute_metrics(config)

    assert {"gt", "radial_gt", "axial_gt", "velocity_gt"}.issubset(metrics)
    assert "pred" not in metrics
    assert "radial_pred" not in metrics
    assert "velocity_pred" not in metrics

    assert len(metrics["gt"]) == 3
    assert set(metrics["radial_gt"]["frame"]) == {0, 1, 2}
    speed = metrics["velocity_gt"]["speed"]
    assert set(speed) == {"small", "large"}
    assert metrics["velocity_gt"]["granular_temperature"].ndim == 1


def test_compute_metrics_with_pred(tmp_path):
    config = metrics_config(tmp_path, with_pred=True)
    metrics = run_metrics.compute_metrics(config)

    for key in ("gt", "pred", "radial_gt", "axial_gt", "radial_pred", "axial_pred", "velocity_gt", "velocity_pred"):
        assert key in metrics, key

    # GT and predicted radial profiles must share the same bin edges.
    gt_bins = sorted(metrics["radial_gt"]["bin_center"].unique())
    pred_bins = sorted(metrics["radial_pred"]["bin_center"].unique())
    assert gt_bins == pytest.approx(pred_bins)


def test_compute_metrics_skips_velocity_with_single_frame(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    ids = np.arange(4)
    r = np.array([0.1, 0.1, 0.2, 0.2])
    write_frame(data_dir / "frame_00000.parquet", ids, np.zeros((4, 3)), r)

    config = ExperimentConfig(
        data_dir=data_dir,
        prediction=PredictionOptions(pred_out_dir=tmp_path / "out"),
        metrics=MetricsOptions(cell_size=100.0, min_particles_per_cell=2),
    )
    metrics = run_metrics.compute_metrics(config)
    assert "velocity_gt" not in metrics
    assert "gt" in metrics


def test_compute_metrics_persists_velocity_and_granular_temperature(tmp_path):
    config = metrics_config(tmp_path, with_pred=True)
    run_metrics.compute_metrics(config)

    assert (config.data_dir / "velocity_speed.json").is_file()
    assert (config.data_dir / "granular_temperature.parquet").is_file()
    assert (config.prediction.pred_frames_dir / "velocity_speed.json").is_file()
    assert (config.prediction.pred_frames_dir / "granular_temperature.parquet").is_file()


def test_load_metrics_reconstructs_compute_metrics_shape(tmp_path):
    config = metrics_config(tmp_path, with_pred=True)
    computed = run_metrics.compute_metrics(config)
    loaded = run_metrics.load_metrics(config)

    assert set(loaded) == set(computed)
    pd.testing.assert_frame_equal(loaded["gt"], computed["gt"])
    pd.testing.assert_frame_equal(loaded["radial_gt"], computed["radial_gt"])
    assert set(loaded["velocity_gt"]["speed"]) == set(computed["velocity_gt"]["speed"])
    assert np.allclose(
        loaded["velocity_gt"]["granular_temperature"], computed["velocity_gt"]["granular_temperature"]
    )
