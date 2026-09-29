"""Dimensionless computing-speed metric: this run's cost vs. a DEM reference (paper Fig. 15).

Was ``compute_computing_speed`` inside ``run_metrics.py`` -- pulled into its
own module because it's an unrelated concern (wall-clock comparison, not a
particle-frame metric computed from parquet frames).
"""

from __future__ import annotations

import json
from pathlib import Path

from ..config import REPORTS_DIR, ExperimentConfig

_COMPUTING_SPEED_FILENAME = "computing_speed.json"


def compute_computing_speed(timing: dict, config: ExperimentConfig) -> dict:
    """Dimensionless computing speed vs. a user-supplied DEM reference (paper Fig. 15).

    Compares this run's own wall-clock training/prediction time (plus, if
    supplied, the short reference-DEM run used to build the GRU's training
    data) against ``config.computing_speed.dem_reference_seconds`` -- the
    wall-clock time of a full DEM run reproducing the same target simulated
    duration. Neither DEM time is measured by this pipeline; both are plain
    user-supplied values (there is no DEM stage in this pipeline to time
    automatically; see :class:`~bppm_dem_sm.config.ComputingSpeedOptions`).

    Mirrors the paper's two figures: prediction-only speedup (their ~240x) and
    all-RNNSR-steps speedup (their ~2.5x: reference-DEM data acquisition +
    training + prediction). The latter equals just train+predict when
    ``dem_data_acquisition_seconds`` is left at its 0.0 default.

    Persists the result to ``reports/computing_speed.json`` so
    :func:`bppm_dem_sm.visualization.metrics_plots.plot_computing_speed` can
    render it later, gated by ``do_visualization``, without needing
    ``timing`` from the same process -- see :func:`load_computing_speed`.

    Args:
        timing: Wall-clock seconds recorded by
            :func:`bppm_dem_sm.experiment_pipeline.run_experiment_pipeline`, with
            optional ``train_seconds`` / ``predict_seconds`` keys (present
            only for stages that actually ran).
        config: Supplies ``computing_speed.dem_reference_seconds`` and
            ``computing_speed.dem_data_acquisition_seconds``.

    Returns:
        dict: ``dem_reference_seconds``, ``dem_data_acquisition_seconds``,
        ``train_seconds``, ``predict_seconds`` (as given, possibly ``None``),
        ``all_steps_seconds``, and the dimensionless
        ``prediction_only_speedup`` / ``all_steps_speedup`` (each ``None``
        where the underlying timing is unavailable).
    """
    dem_seconds = config.computing_speed.dem_reference_seconds
    dem_data_acquisition_s = config.computing_speed.dem_data_acquisition_seconds
    train_s = timing.get("train_seconds")
    predict_s = timing.get("predict_seconds")
    all_steps = (
        dem_data_acquisition_s + train_s + predict_s
        if train_s is not None and predict_s is not None
        else None
    )

    result = {
        "dem_reference_seconds": dem_seconds,
        "dem_data_acquisition_seconds": dem_data_acquisition_s,
        "train_seconds": train_s,
        "predict_seconds": predict_s,
        "all_steps_seconds": all_steps,
        "prediction_only_speedup": dem_seconds / predict_s if predict_s else None,
        "all_steps_speedup": dem_seconds / all_steps if all_steps else None,
    }
    print("[Computing speed] " + ", ".join(f"{k}={v}" for k, v in result.items()))

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / _COMPUTING_SPEED_FILENAME).write_text(json.dumps(result), encoding="utf-8")

    return result


def load_computing_speed(path: Path | str | None = None) -> dict | None:
    """Read a previously persisted computing-speed result, if present.

    Lets :func:`bppm_dem_sm.visualization.run_visualization.generate_visualizations`
    render the computing-speed bar chart in a ``do_visualization``-only run,
    without re-running ``do_metrics`` in the same process.

    Args:
        path: Override for the persisted file; defaults to
            ``REPORTS_DIR / "computing_speed.json"``.

    Returns:
        dict or None: The persisted result (same shape as
        :func:`compute_computing_speed`'s return), or ``None`` if the file
        doesn't exist yet.
    """
    resolved = Path(path) if path is not None else REPORTS_DIR / _COMPUTING_SPEED_FILENAME
    if not resolved.exists():
        return None
    return json.loads(resolved.read_text(encoding="utf-8"))
