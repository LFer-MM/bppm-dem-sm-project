"""Frame loading for the RNN surrogate."""

from __future__ import annotations

import glob
import os

import numpy as np
import pandas as pd

from ..config import FEATURE_COLS, ID_COL, TARGET_COLS
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
