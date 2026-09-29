"""Tests for the training-curves plot (no display)."""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from bppm_dem_sm.visualization.training_curves import plot_training_history

_HISTORY = {"loss": [1.0, 0.5, 0.25], "val_loss": [1.1, 0.6, 0.3]}


def test_plot_training_history_from_dict():
    fig = plot_training_history(_HISTORY, show=False)
    assert fig is not None
    plt.close(fig)


def test_plot_training_history_from_json_path(tmp_path):
    history_path = tmp_path / "model.history.json"
    history_path.write_text(json.dumps(_HISTORY), encoding="utf-8")

    fig = plot_training_history(history_path, show=False)
    assert fig is not None
    plt.close(fig)


def test_plot_training_history_from_keras_like_object():
    class _StubHistory:
        history = _HISTORY

    fig = plot_training_history(_StubHistory(), show=False)
    assert fig is not None
    plt.close(fig)


def test_plot_training_history_saves_figure(tmp_path):
    save_path = tmp_path / "training_curves.png"
    fig = plot_training_history(_HISTORY, save_path=save_path, show=False)
    assert save_path.is_file()
    plt.close(fig)
