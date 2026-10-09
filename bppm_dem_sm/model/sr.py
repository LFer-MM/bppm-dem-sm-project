"""Stochastic random (SR) velocity perturbation applied after the GRU prediction.

Implements the SR half of the extended-RNNSR method from Kishida, Nakamura,
Ohsaki & Watano (2025), "Surrogate model of DEM simulation for binary-sized
particle mixing and segregation", Powder Technology 455, 120811. The GRU
predicts the deterministic local mean component of a particle's trajectory
(Lagrangian behavior). This module supplies the local variability component:
a per-cell velocity standard deviation vector sigma_v(x), one component per
axis, estimated once from short-time reference DEM frames (Eulerian
analysis, Eq. 2 of the paper), which is then sampled as N(0, sigma_v(x)^2)
per axis and added to the GRU's predicted position at each autoregressive
step (Eqs. 3-4).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..config import ID_COL, TARGET_COLS, VELOCITY_COLS, ExperimentConfig
from ..data_processing import binning
from ..data_processing import frames as data_io

# --- Public classes ----------------------------------------------------------


@dataclass
class VelocityStdField:
    """Lookup table for the local (Eulerian) velocity std sigma_v(x) on a cubic grid.

    Attributes:
        cell_size: Cubic cell edge length (m).
        origin: Grid origin ``(x, y, z)``; cell indices are
            ``floor((position - origin) / cell_size)``.
        sigma_by_cell: sigma_v vector ``(sx, sy, sz)`` per populated cell
            index ``(i, j, k)``.
    """

    cell_size: float
    origin: np.ndarray
    sigma_by_cell: dict[tuple[int, int, int], np.ndarray]

    def sigma_at(self, positions: np.ndarray) -> np.ndarray:
        """Return the sigma_v vector for each position; zeros where the cell has no field data.

        Args:
            positions: Array of shape ``(N, 3)`` of ``(x, y, z)`` positions.

        Returns:
            numpy.ndarray: Shape ``(N, 3)`` of per-axis velocity std per particle.
        """
        idx = binning.cell_indices(positions, self.cell_size, self.origin)
        zero = np.zeros(3, dtype=np.float32)
        out = np.empty((len(idx), 3), dtype=np.float32)
        for n, row in enumerate(idx):
            out[n] = self.sigma_by_cell.get(tuple(row), zero)
        return out


# --- Public functions --------------------------------------------------------


def build_velocity_std_field(
    frames_dir,
    frame_glob,
    dt: float,
    cell_size: float,
    min_particles_per_cell: int = 15,
) -> VelocityStdField:
    """Estimate sigma_v(x) from consecutive reference DEM frames (paper Eq. 2).

    Uses each particle's instantaneous DEM velocity ``v_i`` (the
    ``VELOCITY_COLS`` columns) when every frame carries them, as the paper
    does; otherwise velocities are finite-differenced between consecutive
    frames over ``dt``, which only approximates ``v_i``. Velocities are binned
    by position into fixed cubic cells and pooled across frames
    (spatiotemporal averaging of ``<v_i>``) to compute, per axis,
    ``sigma_v(x) = sqrt(mean((v_i - <v_i>)^2))`` -- a vector, one component
    per velocity component. Pooling across frames is valid because the
    Eulerian velocity field of a rotating-drum mixer stays quasi-steady even
    as the Lagrangian (segregating) behavior evolves -- see Section 2.2.3 of
    Kishida et al. (2025). Large and small particles are pooled together
    (Section 2.3, item 2). Cells with fewer than ``min_particles_per_cell``
    pooled observations are omitted (zero sigma, i.e. no added noise, at
    lookup time).

    Args:
        frames_dir: Directory of reference DEM parquet frames, e.g. the same
            short-time window used to train the GRU (``config.train_data_dir``).
        frame_glob: Glob pattern for frame files.
        dt: Physical time spacing between consecutive frames (seconds);
            only used by the finite-difference fallback.
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

    use_dem_velocity = all(data_io.has_velocity_columns(p) for p in paths)
    cols = [ID_COL] + TARGET_COLS + (VELOCITY_COLS if use_dem_velocity else [])
    frames = [data_io.load_frame(p, cols) for p in paths]
    base_ids = frames[0][ID_COL].to_numpy()
    for f in frames[1:]:
        if not np.array_equal(f[ID_COL].to_numpy(), base_ids):
            raise ValueError("Reference frames must share the same particle ids in the same order")

    positions = [f[TARGET_COLS].to_numpy(np.float64) for f in frames]
    origin = np.min(np.stack(positions), axis=(0, 1))

    if use_dem_velocity:
        binned_positions = positions
        velocities = [f[VELOCITY_COLS].to_numpy(np.float64) for f in frames]
    else:
        binned_positions = positions[:-1]
        velocities = [(positions[t + 1] - positions[t]) / dt for t in range(len(positions) - 1)]

    cell_idx_stack = np.concatenate(
        [binning.cell_indices(pos, cell_size, origin) for pos in binned_positions],
        axis=0,
    )
    vel_stack = np.concatenate(velocities, axis=0)

    sigma_by_cell: dict[tuple[int, int, int], np.ndarray] = {}
    for group in binning.group_by_cell(cell_idx_stack):
        if len(group) < min_particles_per_cell:
            continue
        v = vel_stack[group]
        key = tuple(cell_idx_stack[group[0]].tolist())
        sigma_by_cell[key] = v.std(axis=0).astype(np.float32)

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
    noise_velocity = rng.standard_normal(size=(positions.shape[0], 3)) * sigma
    return (noise_velocity * dt_rnn).astype(np.float32)
