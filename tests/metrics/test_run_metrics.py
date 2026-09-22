"""Integration tests for compute_metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from bppm_dem_sm.metrics import run_metrics
from bppm_dem_sm.config import MetricsOptions, PipelineConfig, PredictionOptions


def _write_frame(path, ids, xyz, r):
    pd.DataFrame(
        {"id": ids, "x": xyz[:, 0], "y": xyz[:, 1], "z": xyz[:, 2], "r": r}
    ).to_parquet(path, index=False)


def _write_gt_frames(data_dir, seed=0):
    data_dir.mkdir(parents=True, exist_ok=True)
    ids = np.arange(8)
    r = np.array([0.1] * 4 + [0.2] * 4)
    rng = np.random.default_rng(seed)
    pos0 = rng.uniform(-1, 1, size=(8, 3))
    v = rng.normal(0, 0.1, size=(8, 3))
    dt = 0.05
    for step in range(3):
        _write_frame(data_dir / f"frame_{step:05d}.parquet", ids, pos0 + step * v * dt, r)
    return ids, r


def _write_pred_frames(pred_frames_dir, start_idx, seed=1):
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
    data_dir = tmp_path / "data"
    _write_gt_frames(data_dir)

    out_dir = tmp_path / "out"
    if with_pred:
        _write_pred_frames(out_dir / "pred_frames", start_idx=10)

    return PipelineConfig(
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


def test_compute_metrics_gt_only(tmp_path):
    config = _base_config(tmp_path, with_pred=False)
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
    config = _base_config(tmp_path, with_pred=True)
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
    _write_frame(data_dir / "frame_00000.parquet", ids, np.zeros((4, 3)), r)

    config = PipelineConfig(
        data_dir=data_dir,
        prediction=PredictionOptions(pred_out_dir=tmp_path / "out"),
        metrics=MetricsOptions(cell_size=100.0, min_particles_per_cell=2),
    )
    metrics = run_metrics.compute_metrics(config)
    assert "velocity_gt" not in metrics
    assert "gt" in metrics
