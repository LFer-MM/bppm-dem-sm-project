"""Tests for model artifact path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from bppm_dem_sm.model.prediction import _resolve_model_path


def test_resolve_model_path_finds_keras_file(tmp_path):
    keras_path = tmp_path / "model.keras"
    keras_path.write_bytes(b"")
    assert _resolve_model_path(keras_path) == keras_path
    assert _resolve_model_path(tmp_path / "model") == keras_path


def test_resolve_model_path_finds_saved_model_dir(tmp_path):
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "saved_model.pb").write_bytes(b"")
    assert _resolve_model_path(tmp_path / "model.keras") == model_dir


def test_resolve_model_path_raises_when_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        _resolve_model_path(tmp_path / "does_not_exist.keras")
