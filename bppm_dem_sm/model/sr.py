"""Stochastic random (SR) model: the local variability half of the extended-RNNSR.

Implements the SR model of Kishida, Nakamura, Ohsaki & Watano (2025),
"Surrogate model of DEM simulation for binary-sized particle mixing and
segregation", Powder Technology 455, 120811. The GRU predicts the
deterministic local mean component of a particle's trajectory (Lagrangian
behavior); the SR model supplies the local variability component (Eulerian
behavior):

- :func:`fit_sr` estimates a per-cell velocity standard deviation vector
  sigma_v(x), one component per axis, from short-time reference DEM frames
  (Step 3, Eq. 2).
- :meth:`SRModel.sample` draws a local variability velocity
  ``v_tilde ~ N(0, sigma_v(x)^2)`` per axis at each particle's cell (Step 4,
  Eq. 3).

Combining the two halves, ``x = x_bar_RNN + v_tilde * Delta t_RNN`` (Eq. 4),
is the RNNSR's job and lives in
:func:`bppm_dem_sm.model.rnn.prediction.predict_frames`. The fitted model is
saved next to the GRU as ``<model stem>.sr.npz`` (see :func:`sr_path_for`).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ..config import ExperimentConfig
from ..data_processing import binning
from ..data_processing import frames as data_io

# --- Public classes ----------------------------------------------------------


@dataclass
class SRModel:
    """Fitted SR model: sigma_v(x) on a cubic grid, sampled as a Gaussian (Eqs. 2-3).

    Attributes:
        cell_size: Cubic cell edge length (m).
        origin: Grid origin ``(x, y, z)``; cell indices are
            ``floor((position - origin) / cell_size)``.
        sigma_by_cell: sigma_v vector ``(sx, sy, sz)`` per populated cell
            index ``(i, j, k)``. Cells not listed have sigma_v = 0.
    """

    cell_size: float
    origin: np.ndarray
    sigma_by_cell: dict[tuple[int, int, int], np.ndarray]

    def sigma_at(self, positions: np.ndarray) -> np.ndarray:
        """Return the sigma_v vector for each position; zeros where the cell has no data.

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

    def sample(self, positions: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        """Draw the local variability velocity ``v_tilde ~ N(0, sigma_v(x)^2)`` per axis (Eq. 3).

        Args:
            positions: Particle positions of shape ``(N, 3)`` used to look up
                sigma_v(x): the fixed Eulerian cell each particle occupies.
            rng: ``numpy.random.Generator`` used for the draw.

        Returns:
            numpy.ndarray: Velocities of shape ``(N, 3)``; multiply by
            Delta t_RNN for the displacement of Eq. 4.
        """
        sigma = self.sigma_at(positions)
        return (rng.standard_normal(size=(positions.shape[0], 3)) * sigma).astype(np.float32)

    def save(self, path) -> None:
        """Write the fitted model to an ``.npz`` file.

        Args:
            path: Destination path, e.g. from :func:`sr_path_for`.
        """
        keys = np.array(list(self.sigma_by_cell), dtype=np.int64).reshape(-1, 3)
        sigmas = np.array(list(self.sigma_by_cell.values()), dtype=np.float32).reshape(-1, 3)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            np.savez(f, cell_size=self.cell_size, origin=self.origin, keys=keys, sigmas=sigmas)

    @classmethod
    def load(cls, path) -> SRModel:
        """Read a model written by :meth:`save`.

        Args:
            path: Path to the ``.npz`` file.

        Returns:
            SRModel: The fitted model.
        """
        with np.load(path) as data:
            sigma_by_cell = {
                tuple(int(i) for i in key): sigma for key, sigma in zip(data["keys"], data["sigmas"])
            }
            return cls(
                cell_size=float(data["cell_size"]),
                origin=data["origin"],
                sigma_by_cell=sigma_by_cell,
            )


# --- Public functions --------------------------------------------------------


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


def fit_sr_from_config(config: ExperimentConfig) -> SRModel:
    """Fit the SR model on ``config.train_data_dir``.

    Args:
        config: Pipeline settings; uses ``train_data_dir``, ``frame_glob``,
            and ``stochastic.*``.

    Returns:
        SRModel: The fitted model.
    """
    pos, _, _ = data_io.load_frames_stacked(config.train_data_dir, config.frame_glob)
    vel = data_io.load_velocities_stacked(config.train_data_dir, config.frame_glob)
    sc = config.stochastic
    return fit_sr(
        pos,
        vel,
        cell_size=sc.velocity_cell_size,
        min_particles_per_cell=sc.velocity_min_particles_per_cell,
    )


def sr_path_for(model_path) -> Path:
    """Return where the SR model paired with a saved GRU lives.

    Args:
        model_path: The GRU's path (``.keras``, ``.h5``, or SavedModel dir).

    Returns:
        pathlib.Path: ``<model_path stem>.sr.npz`` in the same directory.
    """
    return Path(model_path).with_suffix(".sr.npz")
