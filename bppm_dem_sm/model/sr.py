"""Stochastic random (SR) velocity perturbation applied after the GRU prediction.

Implements the SR half of the extended-RNNSR method from Kishida, Nakamura,
Ohsaki & Watano (2025), "Surrogate model of DEM simulation for binary-sized
particle mixing and segregation", Powder Technology 455, 120811. The GRU
predicts the deterministic local mean component of a particle's trajectory
(Lagrangian behavior). This module supplies the local variability component:
a per-cell isotropic velocity standard deviation sigma_v(x), estimated once
from short-time reference DEM frames (Eulerian analysis, Eq. 2 of the paper),
which is then sampled as N(0, sigma_v(x)^2) per axis and added to the GRU's
predicted position at each autoregressive step (Eqs. 3-4).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..config import ID_COL, TARGET_COLS, ExperimentConfig
from ..data_processing import frames as data_io

# Spatial-hash coefficients for 3D cell indices (same as the Lacey grid).
_HASH_COEFFS = (73856093, 19349663, 83492791)


@dataclass
class VelocityStdField:
    """Lookup table for the local (Eulerian) velocity std sigma_v(x) on a cubic grid.

    Attributes:
        cell_size: Cubic cell edge length (m).
        origin: Grid origin ``(x, y, z)``; cell indices are
            ``floor((position - origin) / cell_size)``.
        sigma_by_cell: sigma_v per populated cell index ``(i, j, k)``.
    """

    cell_size: float
    origin: np.ndarray
    sigma_by_cell: dict[tuple[int, int, int], float]

    def sigma_at(self, positions: np.ndarray) -> np.ndarray:
        """Return sigma_v for each position; 0.0 where the cell has no field data.

        Args:
            positions: Array of shape ``(N, 3)`` of ``(x, y, z)`` positions.

        Returns:
            numpy.ndarray: Shape ``(N,)`` of isotropic velocity std per particle.
        """
        idx = np.floor((positions - self.origin) / self.cell_size).astype(np.int64)
        return np.fromiter(
            (self.sigma_by_cell.get(tuple(row), 0.0) for row in idx),
            dtype=np.float32,
            count=len(idx),
        )


def build_velocity_std_field(
    frames_dir,
    frame_glob,
    dt: float,
    cell_size: float,
    min_particles_per_cell: int = 15,
) -> VelocityStdField:
    """Estimate sigma_v(x) from consecutive reference DEM frames (paper Eq. 2).

    Particle velocities are finite-differenced between every consecutive pair
    of frames in ``frames_dir``, binned by their position (at the earlier
    frame) into fixed cubic cells, and pooled across all pairs to compute
    ``sigma_v(x) = sqrt(mean(||v_i - <v>_cell||^2))`` per cell. Pooling across
    frames is valid here because the Eulerian velocity field of a rotating-drum
    mixer stays quasi-steady even as the Lagrangian (segregating) behavior
    evolves -- see Section 2.2.3 of Kishida et al. (2025). Cells with fewer
    than ``min_particles_per_cell`` pooled observations are omitted (treated
    as zero-variance, i.e. no added noise, at lookup time).

    Args:
        frames_dir: Directory of reference DEM parquet frames, e.g. the same
            short-time window used to train the GRU (``config.train_data_dir``).
        frame_glob: Glob pattern for frame files.
        dt: Physical time spacing between consecutive frames (seconds).
        cell_size: Cubic cell edge length in meters.
        min_particles_per_cell: Minimum pooled particle-observations required
            for a cell to receive a non-zero sigma_v.

    Returns:
        VelocityStdField: Lookup table mapping position -> sigma_v(x).

    Raises:
        ValueError: If fewer than 2 frames are found, or frames do not share
            the same particle ids in the same order.
    """
    paths = data_io.sorted_frame_files(frames_dir, frame_glob)
    if len(paths) < 2:
        raise ValueError(
            f"Need >= 2 reference frames to estimate velocity, found {len(paths)} in {frames_dir}"
        )

    frames = [data_io.load_frame(p, [ID_COL] + TARGET_COLS) for p in paths]
    base_ids = frames[0][ID_COL].to_numpy()
    for f in frames[1:]:
        if not np.array_equal(f[ID_COL].to_numpy(), base_ids):
            raise ValueError("Reference frames must share the same particle ids in the same order")

    positions = [f[TARGET_COLS].to_numpy(np.float64) for f in frames]
    origin = np.min(np.stack(positions), axis=(0, 1))

    cell_idx_stack = np.concatenate(
        [np.floor((pos - origin) / cell_size).astype(np.int64) for pos in positions[:-1]],
        axis=0,
    )
    vel_stack = np.concatenate(
        [(positions[t + 1] - positions[t]) / dt for t in range(len(positions) - 1)],
        axis=0,
    )

    cx, cy, cz = _HASH_COEFFS
    h = cell_idx_stack[:, 0] * cx + cell_idx_stack[:, 1] * cy + cell_idx_stack[:, 2] * cz
    order = np.argsort(h, kind="stable")
    idx_sorted = cell_idx_stack[order]
    vel_sorted = vel_stack[order]
    h_sorted = h[order]

    splits = np.split(np.arange(len(h_sorted)), np.flatnonzero(np.diff(h_sorted)) + 1)

    sigma_by_cell: dict[tuple[int, int, int], float] = {}
    for group in splits:
        if len(group) < min_particles_per_cell:
            continue
        v = vel_sorted[group]
        mean_v = v.mean(axis=0)
        sq_dev = np.sum((v - mean_v) ** 2, axis=1)
        key = tuple(idx_sorted[group[0]].tolist())
        sigma_by_cell[key] = float(np.sqrt(sq_dev.mean()))

    return VelocityStdField(cell_size=cell_size, origin=origin, sigma_by_cell=sigma_by_cell)


def build_velocity_std_field_from_config(config: ExperimentConfig) -> VelocityStdField:
    """Build the sigma_v(x) field from ``config.train_data_dir``.

    Args:
        config: Pipeline settings; uses ``train_data_dir``, ``frame_glob``,
            ``prediction.dt_step`` (as Delta t_RNN), and ``stochastic.*``.

    Returns:
        VelocityStdField: Lookup table for :func:`sample_stochastic_displacement`.
    """
    sc = config.stochastic
    return build_velocity_std_field(
        config.train_data_dir,
        config.frame_glob,
        dt=config.prediction.dt_step,
        cell_size=sc.velocity_cell_size,
        min_particles_per_cell=sc.velocity_min_particles_per_cell,
    )


def sample_stochastic_displacement(
    positions: np.ndarray,
    field: VelocityStdField,
    dt_rnn: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Draw the SR displacement to add to the GRU's predicted position (paper Eqs. 3-4).

    Args:
        positions: Particle positions of shape ``(N, 3)`` used to look up
            sigma_v(x); evaluated at each particle's last known position (the
            fixed Eulerian cell it currently occupies), not its predicted one.
        field: Precomputed lookup from :func:`build_velocity_std_field`.
        dt_rnn: RNN prediction timestep (seconds), i.e. the paper's
            Delta t_RNN, converting the sampled stochastic velocity into a
            displacement.
        rng: ``numpy.random.Generator`` used for the draw.

    Returns:
        numpy.ndarray: Displacement of shape ``(N, 3)`` to add to the
        GRU-predicted ``(x, y, z)``.
    """
    sigma = field.sigma_at(positions)
    noise_velocity = rng.standard_normal(size=(positions.shape[0], 3)) * sigma[:, None]
    return (noise_velocity * dt_rnn).astype(np.float32)
