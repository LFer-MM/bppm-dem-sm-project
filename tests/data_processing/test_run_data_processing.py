"""Tests for the Data Processing stage orchestrator (convert + integrity)."""

from __future__ import annotations

import pandas as pd

from bppm_dem_sm.config import ExperimentConfig
from bppm_dem_sm.data_processing import run_data_processing


def test_process_frames_converts_and_reports_integrity(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    pd.DataFrame({"id": [0, 1], "x": [0.0, 1.0], "r": [0.1, 0.2]}).to_csv(
        raw_dir / "frame_00000.csv", index=False
    )

    data_dir = tmp_path / "processed"
    config = ExperimentConfig(raw_data_dir=raw_dir, data_dir=data_dir)

    result = run_data_processing.process_frames(config)

    assert (data_dir / "frame_00000.parquet").is_file()
    assert result["data_dir"] == data_dir
    assert result["integrity_report"].shape[0] == 1
