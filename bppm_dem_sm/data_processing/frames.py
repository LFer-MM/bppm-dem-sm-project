"""Frame loading for the RNN surrogate."""

from __future__ import annotations

import glob
import os

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from ..config import FEATURE_COLS, ID_COL, TARGET_COLS, VELOCITY_COLS
from ..progress import track


def sorted_frame_files(frames_dir, pattern="frame_*.parquet"):
    """Return sorted parquet paths under ``frames_dir`` matching ``pattern``.

    Args:
        frames_dir: Directory containing frame parquet files.
        pattern: Glob pattern relative to ``frames_dir`` (default
            ``frame_*.parquet``).

    Returns:
        list[str]: Lexicographically sorted matching file paths.
    """
    return sorted(glob.glob(os.path.join(str(frames_dir), pattern)))


def load_frame(path, cols=None):
    """Read one parquet frame sorted by id.

    Args:
        path: Path to a single frame parquet file.
        cols: Optional column subset to read; ``None`` reads all columns.

    Returns:
        pandas.DataFrame: Frame rows sorted by particle ``id`` with a reset index.
    """
    return pd.read_parquet(path, columns=cols).sort_values(ID_COL).reset_index(drop=True)


def load_frames_stacked(frames_dir, pattern="frame_*.parquet", feature_cols=None):
    """Load all frames (sorted by id) and stack positions/radius over time.

    Args:
        frames_dir: Directory of parquet frames.
        pattern: Glob for frame files.
        feature_cols: Feature column names; defaults to ``FEATURE_COLS``
            (``x``, ``y``, ``z``, ``r``).

    Returns:
        tuple: ``(pos, rad, base_ids)`` where ``pos`` is ``(T, N, 3)``,
        ``rad`` is ``(T, N, 1)``, and ``base_ids`` is length ``N``.
    """
    feature_cols = feature_cols or FEATURE_COLS
    cols = [ID_COL] + [c for c in feature_cols if c != ID_COL]

    paths = sorted_frame_files(frames_dir, pattern)
    frames = [
        pd.read_parquet(f, columns=cols).sort_values(ID_COL)
        for f in track(paths, desc="Loading frames", unit="frame")
    ]
    base_ids = frames[0][ID_COL].to_numpy()

    pos = np.stack([df[TARGET_COLS].to_numpy(np.float32) for df in frames])  # (T, N, 3)
    rad = np.stack([df[["r"]].to_numpy(np.float32) for df in frames])  # (T, N, 1)
    return pos, rad, base_ids


def has_velocity_columns(path):
    """Return whether a frame parquet carries the DEM velocity columns.

    Args:
        path: Path to a single frame parquet file.

    Returns:
        bool: ``True`` if every column in ``VELOCITY_COLS`` is present.
    """
    names = set(pq.read_schema(path).names)
    return all(c in names for c in VELOCITY_COLS)


def load_velocities_stacked(frames_dir, pattern="frame_*.parquet"):
    """Load the DEM particle velocities of all frames (sorted by id), stacked over time.

    Args:
        frames_dir: Directory of parquet frames.
        pattern: Glob for frame files.

    Returns:
        numpy.ndarray: Velocity tensor of shape ``(T, N, 3)``, aligned with
        the ``pos`` returned by :func:`load_frames_stacked`.

    Raises:
        ValueError: If a frame lacks the ``VELOCITY_COLS`` columns.
    """
    paths = sorted_frame_files(frames_dir, pattern)
    missing = [p for p in paths if not has_velocity_columns(p)]
    if missing:
        raise ValueError(f"Frames lack velocity columns {VELOCITY_COLS}, e.g. {missing[0]}")
    return np.stack(
        [load_frame(p, [ID_COL] + VELOCITY_COLS)[VELOCITY_COLS].to_numpy(np.float32) for p in paths]
    )
