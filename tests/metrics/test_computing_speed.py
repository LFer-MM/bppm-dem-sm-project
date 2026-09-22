"""Tests for the computing-speed metric (config, computation, pipeline wiring)."""

from __future__ import annotations

import pytest

from bppm_dem_sm.metrics import run_metrics
from bppm_dem_sm.config import ComputingSpeedOptions, PipelineConfig
from bppm_dem_sm.pipeline import run_pipeline


def test_computing_speed_options_defaults():
    config = PipelineConfig()
    assert isinstance(config.computing_speed, ComputingSpeedOptions)
    assert config.computing_speed.dem_reference_seconds == pytest.approx(86400.0)
    assert config.computing_speed.dem_data_acquisition_seconds == pytest.approx(0.0)


def test_computing_speed_options_roundtrip():
    config = PipelineConfig().with_overrides(dem_reference_seconds=3600.0)
    assert config.computing_speed.dem_reference_seconds == 3600.0

    restored = PipelineConfig.from_dict(config.to_dict())
    assert restored.computing_speed == config.computing_speed


def test_compute_computing_speed_both_timings_present_no_dem_acquisition():
    config = PipelineConfig(computing_speed=ComputingSpeedOptions(dem_reference_seconds=1000.0))
    cs = run_metrics.compute_computing_speed({"train_seconds": 80.0, "predict_seconds": 20.0}, config)

    assert cs["all_steps_seconds"] == pytest.approx(100.0)
    assert cs["all_steps_speedup"] == pytest.approx(10.0)
    assert cs["prediction_only_speedup"] == pytest.approx(50.0)


def test_compute_computing_speed_includes_dem_data_acquisition():
    config = PipelineConfig(
        computing_speed=ComputingSpeedOptions(
            dem_reference_seconds=1000.0, dem_data_acquisition_seconds=400.0
        )
    )
    cs = run_metrics.compute_computing_speed({"train_seconds": 80.0, "predict_seconds": 20.0}, config)

    assert cs["dem_data_acquisition_seconds"] == pytest.approx(400.0)
    assert cs["all_steps_seconds"] == pytest.approx(500.0)  # 400 + 80 + 20
    assert cs["all_steps_speedup"] == pytest.approx(2.0)  # 1000 / 500
    assert cs["prediction_only_speedup"] == pytest.approx(50.0)  # unaffected


def test_compute_computing_speed_dem_data_acquisition_ignored_without_full_timing():
    config = PipelineConfig(
        computing_speed=ComputingSpeedOptions(
            dem_reference_seconds=1000.0, dem_data_acquisition_seconds=400.0
        )
    )
    cs = run_metrics.compute_computing_speed({"predict_seconds": 25.0}, config)

    assert cs["train_seconds"] is None
    assert cs["all_steps_seconds"] is None
    assert cs["all_steps_speedup"] is None
    assert cs["prediction_only_speedup"] == pytest.approx(40.0)


def test_compute_computing_speed_predict_only():
    config = PipelineConfig(computing_speed=ComputingSpeedOptions(dem_reference_seconds=1000.0))
    cs = run_metrics.compute_computing_speed({"predict_seconds": 25.0}, config)

    assert cs["train_seconds"] is None
    assert cs["all_steps_seconds"] is None
    assert cs["all_steps_speedup"] is None
    assert cs["prediction_only_speedup"] == pytest.approx(40.0)


def test_compute_computing_speed_no_timing():
    config = PipelineConfig()
    cs = run_metrics.compute_computing_speed({}, config)

    assert cs["train_seconds"] is None
    assert cs["predict_seconds"] is None
    assert cs["prediction_only_speedup"] is None
    assert cs["all_steps_speedup"] is None


def test_run_pipeline_records_timing_and_computing_speed(monkeypatch):
    monkeypatch.setattr("bppm_dem_sm.pipeline.silence_tensorflow", lambda: None)
    monkeypatch.setattr(
        "bppm_dem_sm.pipeline.training.train_and_save", lambda config: (object(), {"loss": [1.0]})
    )
    monkeypatch.setattr(
        "bppm_dem_sm.pipeline.prediction.predict_frames", lambda config, model=None: None
    )
    monkeypatch.setattr("bppm_dem_sm.pipeline.run_metrics.compute_metrics", lambda config: {})

    config = PipelineConfig(
        do_train=True,
        do_predict=True,
        do_metrics=True,
        do_visualization=False,
    ).with_overrides(show_plots=False, save_figures=False)

    results = run_pipeline(config)

    assert "timing" in results
    assert results["timing"]["train_seconds"] >= 0.0
    assert results["timing"]["predict_seconds"] >= 0.0
    assert "computing_speed" in results["metrics"]
    cs = results["metrics"]["computing_speed"]
    assert cs["all_steps_speedup"] is not None
    assert cs["prediction_only_speedup"] is not None


def test_run_pipeline_no_timing_key_when_stages_skipped(monkeypatch):
    monkeypatch.setattr("bppm_dem_sm.pipeline.silence_tensorflow", lambda: None)
    results = run_pipeline(
        PipelineConfig(do_train=False, do_predict=False, do_metrics=False, do_visualization=False)
    )
    assert "timing" not in results
