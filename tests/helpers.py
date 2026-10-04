"""Shared test helpers: synthetic parquet frames and a small metrics config.

Importable from any test module as ``helpers`` (``tests/`` is on pytest's
``pythonpath``; see ``pyproject.toml``).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from bppm_dem_sm.config import ExperimentConfig, MetricsOptions, PredictionOptions

# --- Public functions --------------------------------------------------------


def write_frame(path, ids, xyz, r=None):
    """Write one parquet frame with ``id``, ``x``, ``y``, ``z`` (and ``r``) columns.

    Args:
        path: Destination parquet path.
        ids: Particle ids, length ``N``.
        xyz: Positions of shape ``(N, 3)``.
        r: Optional radii, length ``N``; the ``r`` column is omitted if ``None``.
    """
    columns = {"id": ids, "x": xyz[:, 0], "y": xyz[:, 1], "z": xyz[:, 2]}
    if r is not None:
        columns["r"] = r
    pd.DataFrame(columns).to_parquet(path, index=False)


def write_frames(frames_dir, n_frames, *, seed=0, start_idx=0, prefix="frame"):
    """Write ``n_frames`` frames of 8 bidisperse particles in linear motion.

    Four particles have radius 0.1 and four 0.2; positions start uniform in
    ``[-1, 1)`` and advance by a random velocity times 0.05 s per frame.

    Args:
        frames_dir: Destination directory (created if missing).
        n_frames: Number of frames to write.
        seed: RNG seed for initial positions and velocities.
        start_idx: Index of the first frame in the file names.
        prefix: File-name prefix, e.g. ``"frame"`` or ``"pred_frame"``.

    Returns:
        tuple: ``(ids, r)`` shared by every frame written.
    """
    frames_dir.mkdir(parents=True, exist_ok=True)
    ids = np.arange(8)
    r = np.array([0.1] * 4 + [0.2] * 4)
    rng = np.random.default_rng(seed)
    pos0 = rng.uniform(-1, 1, size=(8, 3))
    v = rng.normal(0, 0.1, size=(8, 3))
    dt = 0.05
    for step in range(n_frames):
        idx = start_idx + step
        write_frame(frames_dir / f"{prefix}_{idx:05d}.parquet", ids, pos0 + step * v * dt, r)
    return ids, r


def metrics_config(tmp_path, with_pred):
    """Build a config over 3 fresh GT frames, plus 2 predicted frames if ``with_pred``.

    Args:
        tmp_path: Scratch directory (pytest's ``tmp_path``).
        with_pred: If ``True``, also write predicted frames numbered from 10.

    Returns:
        ExperimentConfig: Config whose metrics grid puts every particle in one cell.
    """
    data_dir = tmp_path / "data"
    write_frames(data_dir, n_frames=3, seed=0)

    out_dir = tmp_path / "out"
    if with_pred:
        write_frames(out_dir / "pred_frames", n_frames=2, seed=1, start_idx=10, prefix="pred_frame")

    return ExperimentConfig(
        data_dir=data_dir,
        prediction=PredictionOptions(pred_out_dir=out_dir),
        metrics=MetricsOptions(
            cell_size=100.0,
            min_particles_per_cell=2,
            metrics_dt=0.05,
            n_radial_bins=2,
            n_axial_bins=2,
        ),
    )
