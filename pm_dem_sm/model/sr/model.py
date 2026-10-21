"""The SR model itself: sigma_v(x) on a cubic grid, sampled as a Gaussian (Eqs. 2-3).

Unlike the GRU, the SR model has no layers or learned weights: it is a
statistical lookup table, one velocity standard deviation vector sigma_v per
grid cell, from which a local variability velocity
``v_tilde ~ N(0, sigma_v(x)^2)`` is drawn per axis. :class:`SRModel` holds
that table, samples from it, and defines its ``.npz`` file format.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ...data_processing import binning


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
            path: Destination path, e.g. from
                :func:`pm_dem_sm.model.sr.loading.sr_path_for`.
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
