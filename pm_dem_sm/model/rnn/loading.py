"""Locating and loading a saved GRU, including legacy SavedModel exports.

Reading the artifact itself is :meth:`~pm_dem_sm.model.rnn.model.RNNModel.load`;
this module owns which path to read, trying alternate suffixes, and the
error when none exists -- as :mod:`pm_dem_sm.model.sr.loading` does for
the SR model.
"""

from __future__ import annotations

from pathlib import Path

from .model import RNNModel

# --- Public functions --------------------------------------------------------


def load_rnn(path) -> RNNModel:
    """Load a saved GRU from a ``.keras``/``.h5`` file or legacy SavedModel directory.

    Args:
        path: Path to a ``.keras``/``.h5`` file or SavedModel directory;
            alternate suffixes are tried when it does not exist as given.

    Returns:
        RNNModel: The loaded model.

    Raises:
        FileNotFoundError: If no Keras file or SavedModel directory is found.
    """
    return RNNModel.load(_resolve_model_path(Path(path)))


# --- Private helper functions ------------------------------------------------


def _resolve_model_path(path: Path) -> Path:
    """Return an existing ``.keras``, ``.h5``, or SavedModel directory path.

    Args:
        path: Requested model path (file or directory); alternate suffixes are tried.

    Returns:
        pathlib.Path: Resolved artifact path that exists on disk.

    Raises:
        FileNotFoundError: If no Keras file or SavedModel directory is found.
    """
    candidates = [path]
    if path.suffix in {".keras", ".h5"}:
        candidates.append(path.with_suffix(""))
    else:
        candidates.extend([path.with_suffix(".keras"), path.with_suffix(".h5")])

    for candidate in candidates:
        if candidate.is_dir() and (candidate / "saved_model.pb").exists():
            return candidate
        if candidate.is_file() and candidate.suffix in {".keras", ".h5"}:
            return candidate

    raise FileNotFoundError(f"No Keras or SavedModel artifact found for: {path}")
