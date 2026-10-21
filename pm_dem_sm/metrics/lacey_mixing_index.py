"""Lacey mixing-index computation for bidisperse particle frames.

The Lacey index ``M`` ranges from 0 (fully segregated) to 1 (fully mixed).
"""

from __future__ import annotations

import os
import re

import numpy as np

from ..data_processing import binning

# --- Constants ---------------------------------------------------------------

#: Ground-truth frame filename (``frame_XXXXX.parquet``); group 1 is the index.
GT_FRAME_RE = re.compile(r"frame_(\d+)\.parquet$", re.IGNORECASE)
#: Predicted frame filename (``pred_frame_XXXXX.parquet``); group 1 is the index.
PRED_FRAME_RE = re.compile(r"pred_frame_(\d+)\.parquet$", re.IGNORECASE)


# --- Public functions --------------------------------------------------------


def extract_frame_index(path, frame_re=GT_FRAME_RE):
    """Parse the frame index from a filename.

    Args:
        path: File path whose basename matches ``frame_re``.
        frame_re: Compiled regex with one capture group for the frame index
            (default ``GT_FRAME_RE`` for ``frame_XXXXX.parquet``).

    Returns:
        int: Frame index extracted from the filename.
    """
    return int(frame_re.search(os.path.basename(path)).group(1))


def detect_tracer_radius(r_values):
    """Pick the larger of the two radii as the tracer species.

    Args:
        r_values: Array of particle radii from a bidisperse frame.

    Returns:
        float: Larger distinct radius (tracer / large balls).
    """
    return float(np.unique(np.round(r_values.astype(float), 12)).max())


def lacey_index_for_frame(df, cell_size, tracer_radius, min_particles_per_cell=5):
    """Compute Lacey M on a 3D cell grid for one frame.

    Particles are binned into cubic cells of edge ``cell_size``. Cells with
    fewer than ``min_particles_per_cell`` are ignored. ``M`` is clipped to
    ``[0, 1]`` (0 = segregated, 1 = randomly mixed).

    Args:
        df: Frame table with columns ``x``, ``y``, ``z``, ``r``.
        cell_size: Cubic cell edge length in meters.
        tracer_radius: Radius identifying the tracer (large) species.
        min_particles_per_cell: Minimum count for a cell to contribute to ``M``.

    Returns:
        tuple: ``(M, n_cells_used, p_global, mean_particles_per_cell)`` where
        ``M`` is the Lacey index, ``p_global`` is the global tracer fraction,
        and ``mean_particles_per_cell`` is over cells that passed the filter.
    """
    positions = df[["x", "y", "z"]].to_numpy(float)

    r = np.round(df["r"].to_numpy(float), 12)
    tracer = (r == np.round(tracer_radius, 12)).astype(np.int32)
    p = float(tracer.mean())

    cell_idx = binning.cell_indices(positions, cell_size, positions.min(axis=0))

    n_list, p_list = [], []
    for idxs in binning.group_by_cell(cell_idx):
        if len(idxs) < min_particles_per_cell:
            continue
        n_list.append(len(idxs))
        p_list.append(int(tracer[idxs].sum()) / len(idxs))

    n_i = np.asarray(n_list, dtype=float)
    p_i = np.asarray(p_list, dtype=float)

    S2 = float(np.sum(n_i * (p_i - p) ** 2) / np.sum(n_i))
    S0_2 = float(p * (1.0 - p))
    Sr2 = float(np.mean(p * (1.0 - p) / n_i))

    M = float(np.clip((S0_2 - S2) / (S0_2 - Sr2), 0.0, 1.0))
    return M, len(n_list), p, float(n_i.mean())
