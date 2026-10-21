"""Fitting the SR model: a closed-form estimate of sigma_v(x) (Step 3, Eq. 2).

"Fitting" rather than "training": sigma_v(x) is computed in one pass as a
per-cell standard deviation, with no loss, optimizer, or epochs.
"""

from __future__ import annotations

import numpy as np

from ...config import ExperimentConfig
from ...data_processing import binning
from .loading import sr_path_for
from .model import SRModel


def fit_sr(
    positions: np.ndarray,
    velocities: np.ndarray,
    cell_size: float,
    min_particles_per_cell: int = 15,
) -> SRModel:
    """Fit the SR model: sigma_v(x) from reference DEM frames (Step 3, Eq. 2).

    Each particle's instantaneous DEM velocity ``v_i`` is binned by its
    position in the same frame into fixed cubic cells and pooled across
    frames (spatiotemporal averaging of ``<v_i>``) to compute, per axis,
    ``sigma_v(x) = sqrt(mean((v_i - <v_i>)^2))`` -- a vector, one component
    per velocity component. Pooling across frames is valid because the
    Eulerian velocity field of a rotating-drum mixer stays quasi-steady even
    as the Lagrangian (segregating) behavior evolves -- see Section 2.2.3 of
    Kishida et al. (2025). Large and small particles are pooled together
    (Section 2.3, item 2). Cells with fewer than ``min_particles_per_cell``
    pooled observations are omitted (zero sigma, i.e. no added noise, at
    sampling time).

    Args:
        positions: Position tensor of shape ``(T, N, 3)``.
        velocities: DEM velocity tensor of shape ``(T, N, 3)``, aligned with
            ``positions``.
        cell_size: Cubic cell edge length in meters.
        min_particles_per_cell: Minimum pooled particle-observations required
            for a cell to receive a non-zero sigma_v.

    Returns:
        SRModel: The fitted model.

    Raises:
        ValueError: If ``positions`` holds no frames.
    """
    if len(positions) == 0:
        raise ValueError("Need at least one reference frame to fit the SR model")

    pos = np.asarray(positions, dtype=np.float64).reshape(-1, 3)
    vel = np.asarray(velocities, dtype=np.float64).reshape(-1, 3)
    origin = pos.min(axis=0)
    cell_idx = binning.cell_indices(pos, cell_size, origin)

    sigma_by_cell: dict[tuple[int, int, int], np.ndarray] = {}
    for group in binning.group_by_cell(cell_idx):
        if len(group) < min_particles_per_cell:
            continue
        key = tuple(cell_idx[group[0]].tolist())
        sigma_by_cell[key] = vel[group].std(axis=0).astype(np.float32)

    return SRModel(cell_size=cell_size, origin=origin, sigma_by_cell=sigma_by_cell)


def fit_and_save_sr(positions: np.ndarray, velocities: np.ndarray, config: ExperimentConfig) -> SRModel:
    """Fit the SR model with ``config.stochastic`` settings and save it next to the GRU.

    Args:
        positions: Raw (not local-mean) position tensor of shape ``(T, N, 3)``.
        velocities: DEM velocity tensor of shape ``(T, N, 3)``.
        config: Pipeline settings; uses ``model_path`` and ``stochastic.*``.

    Returns:
        SRModel: The fitted model, saved to ``sr_path_for(config.model_path)``.
    """
    sc = config.stochastic
    sr_model = fit_sr(
        positions,
        velocities,
        cell_size=sc.velocity_cell_size,
        min_particles_per_cell=sc.velocity_min_particles_per_cell,
    )
    sr_path = sr_path_for(config.model_path)
    sr_model.save(sr_path)
    print(f"Saved SR model to: {sr_path}")
    return sr_model
