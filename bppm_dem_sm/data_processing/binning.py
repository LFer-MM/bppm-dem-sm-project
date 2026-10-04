"""Cubic-cell spatial binning shared by the Lacey index, granular temperature, and SR.

Particles are assigned integer cell indices ``floor((position - origin) /
cell_size)`` and grouped per occupied cell via a spatial hash of those
indices. :mod:`bppm_dem_sm.metrics.lacey_mixing_index`,
:mod:`bppm_dem_sm.metrics.velocity_metrics`, and :mod:`bppm_dem_sm.model.sr`
all bin on this one grid convention.
"""

from __future__ import annotations

import numpy as np

# --- Constants ---------------------------------------------------------------

#: Spatial-hash coefficients for 3D integer cell indices.
HASH_COEFFS = (73856093, 19349663, 83492791)


# --- Public functions --------------------------------------------------------


def cell_indices(positions, cell_size, origin):
    """Return the integer cubic-cell index of each position.

    Args:
        positions: Array of shape ``(N, 3)`` of ``(x, y, z)`` positions.
        cell_size: Cubic cell edge length in meters.
        origin: Grid origin ``(x, y, z)``, broadcastable against ``positions``.

    Returns:
        numpy.ndarray: Shape ``(N, 3)`` int64 indices
        ``floor((positions - origin) / cell_size)``.
    """
    return np.floor((positions - origin) / cell_size).astype(np.int64)


def group_by_cell(cell_idx):
    """Group rows of ``cell_idx`` that share a cell.

    Args:
        cell_idx: Array of shape ``(N, 3)`` of integer cell indices, e.g. from
            :func:`cell_indices`.

    Returns:
        list[numpy.ndarray]: One array of row indices into ``cell_idx`` per
        occupied cell, ordered by spatial hash; rows keep their original
        relative order within each group.
    """
    cx, cy, cz = HASH_COEFFS
    h = cell_idx[:, 0] * cx + cell_idx[:, 1] * cy + cell_idx[:, 2] * cz
    order = np.argsort(h, kind="stable")
    return np.split(order, np.flatnonzero(np.diff(h[order])) + 1)
