"""Velocity-distribution and granular-temperature metrics (paper Fig. 9).

Both are derived from particle velocities finite-differenced between two
consecutive frames sharing the same particle ids, following Kishida et al.
(2025), "Surrogate model of DEM simulation for binary-sized particle mixing
and segregation", Powder Technology 455, 120811, Section 4.1. Granular
temperature reuses the same cubic-cell grid convention as Lacey's mixing
index (:mod:`bppm_dem_sm.metrics.lacey_mixing_index`); the paper uses the same cell
size for both.
"""

from __future__ import annotations

import numpy as np

from ..config import ID_COL, TARGET_COLS
from ..data_processing import binning

# --- Public functions --------------------------------------------------------


def velocity_speed_by_species(df_t, df_t1, dt, tracer_radius):
    """Compute absolute velocity per species between two consecutive frames (Fig. 9a data).

    Args:
        df_t: Earlier frame (``id``, ``x``, ``y``, ``z``, ``r`` columns).
        df_t1: Later frame, same particle ids as ``df_t``.
        dt: Time spacing between the two frames (seconds).
        tracer_radius: Radius identifying the large/tracer species.

    Returns:
        dict[str, numpy.ndarray]: ``{"small": speeds, "large": speeds}``.
    """
    _, velocity, r = _matched_velocity(df_t, df_t1, dt)
    speed = np.linalg.norm(velocity, axis=1)
    is_large = np.round(r, 12) == np.round(tracer_radius, 12)
    return {"large": speed[is_large], "small": speed[~is_large]}


def granular_temperature_by_cell(df_t, df_t1, dt, cell_size, min_particles_per_cell=15):
    """Compute per-cell granular temperature ``mean(||v_i - <v>_cell||^2) / 3`` (Fig. 9b).

    Particles are binned by their position in ``df_t`` into cubic cells of
    edge ``cell_size`` (same grid convention as
    :func:`bppm_dem_sm.metrics.lacey_mixing_index.lacey_index_for_frame`). Cells with
    fewer than ``min_particles_per_cell`` particles are excluded, matching
    the paper's treatment of sparsely populated cells.

    Args:
        df_t: Earlier frame (``id``, ``x``, ``y``, ``z`` columns).
        df_t1: Later frame, same particle ids as ``df_t``.
        dt: Time spacing between the two frames (seconds).
        cell_size: Cubic cell edge length in meters.
        min_particles_per_cell: Minimum particle count for a cell to contribute.

    Returns:
        numpy.ndarray: One granular-temperature value per qualifying cell.
    """
    pos_t, velocity, _ = _matched_velocity(df_t, df_t1, dt)
    cell_idx = binning.cell_indices(pos_t, cell_size, pos_t.min(axis=0))

    temperatures = []
    for group in binning.group_by_cell(cell_idx):
        if len(group) < min_particles_per_cell:
            continue
        v = velocity[group]
        mean_v = v.mean(axis=0)
        sq_dev = np.sum((v - mean_v) ** 2, axis=1)
        temperatures.append(sq_dev.mean() / 3.0)
    return np.asarray(temperatures, dtype=np.float64)


# --- Private helper functions ------------------------------------------------


def _matched_velocity(df_t, df_t1, dt):
    """Compute finite-difference velocities between two id-aligned frames.

    Args:
        df_t: Earlier frame (``id``, ``x``, ``y``, ``z``, ``r`` columns).
        df_t1: Later frame, same particle ids as ``df_t``.
        dt: Time spacing between the two frames (seconds).

    Returns:
        tuple: ``(positions_t, velocity, r)`` for particles present in both
        frames, aligned by ``id``; ``positions_t`` and ``r`` are taken from
        ``df_t``.

    Raises:
        ValueError: If the two frames do not share the same particle ids in
            the same order once sorted by id.
    """
    a = df_t.sort_values(ID_COL).reset_index(drop=True)
    b = df_t1.sort_values(ID_COL).reset_index(drop=True)
    if not np.array_equal(a[ID_COL].to_numpy(), b[ID_COL].to_numpy()):
        raise ValueError("Frame pair must share the same particle ids in the same order")
    pos_t = a[TARGET_COLS].to_numpy(np.float64)
    pos_t1 = b[TARGET_COLS].to_numpy(np.float64)
    velocity = (pos_t1 - pos_t) / dt
    return pos_t, velocity, a["r"].to_numpy(float)
