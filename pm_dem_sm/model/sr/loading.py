"""Locating and loading the saved SR model paired with a GRU.

The ``.npz`` format itself is defined by :class:`~pm_dem_sm.model.sr.model.SRModel`
(``save``/``load``); this module owns where that file lives, next to the
GRU, and the error when it is missing.
"""

from __future__ import annotations

from pathlib import Path

from .model import SRModel


def sr_path_for(model_path) -> Path:
    """Return where the SR model paired with a saved GRU lives.

    Args:
        model_path: The GRU's path (``.keras``, ``.h5``, or SavedModel dir).

    Returns:
        pathlib.Path: ``<model_path stem>.sr.npz`` in the same directory.
    """
    return Path(model_path).with_suffix(".sr.npz")


def load_sr(model_path) -> SRModel:
    """Load the SR model saved next to the GRU at ``model_path``.

    Args:
        model_path: The GRU's path (``.keras``, ``.h5``, or SavedModel dir).

    Returns:
        SRModel: The fitted model.

    Raises:
        FileNotFoundError: If no SR model sits next to ``model_path``.
    """
    sr_path = sr_path_for(model_path)
    if not sr_path.is_file():
        raise FileNotFoundError(f"No SR model at {sr_path}; run training (do_train) to fit and save it")
    return SRModel.load(sr_path)
