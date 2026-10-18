"""bppm_dem_sm: bidisperse particle mixing DEM surrogate-model package.

Organized by pipeline stage:

- :mod:`bppm_dem_sm.simulation` -- DEM simulation, backend-selectable
  (``simulation.yade_dem``, implemented; ``simulation.blaze_dem``,
  placeholder). Never imported by the plain venv side, except
  ``simulation.launcher``, which shells out to the backend's executable
  instead of importing it.
- :mod:`bppm_dem_sm.data_processing` -- raw CSV -> training-ready parquet.
- :mod:`bppm_dem_sm.model` -- the surrogate: the GRU
  (:mod:`bppm_dem_sm.model.rnn`) and the stochastic-random (SR) model
  (:mod:`bppm_dem_sm.model.sr`), combined by ``model.training`` and
  ``model.prediction``.
- :mod:`bppm_dem_sm.metrics` -- post-hoc computation (Lacey index,
  segregation profile, velocity/granular temperature, computing speed).
- :mod:`bppm_dem_sm.visualization` -- all plotting/animation, including the
  plots for ``metrics`` and training curves.

Plus top-level plumbing: ``config``, ``experiment_pipeline``, ``cli``,
``progress``, ``tf_quiet``.

The ``bppm-dem-sm`` CLI (:mod:`bppm_dem_sm.cli`) exposes two subcommands:
``dem-sim`` (launches a DEM simulation as a subprocess) and ``ml-pipeline``
(runs :func:`~bppm_dem_sm.experiment_pipeline.run_experiment_pipeline`).

``run_experiment_pipeline`` is imported lazily on first access: importing it
pulls in pandas and TensorFlow, which YADE's own interpreter does not have.
Keeping it lazy lets ``yade_dem`` scripts import ``bppm_dem_sm.config`` and
``bppm_dem_sm.simulation`` under ``yade``.
"""

from .config import (
    ExperimentConfig,
    MetricsOptions,
    PredictionOptions,
    TrainingOptions,
    VisualizationOptions,
)

# --- Constants ---------------------------------------------------------------

__all__ = [
    "ExperimentConfig",
    "MetricsOptions",
    "PredictionOptions",
    "TrainingOptions",
    "VisualizationOptions",
    "run_experiment_pipeline",
]


# --- Private helper functions ------------------------------------------------


def __getattr__(name):
    """Import ``run_experiment_pipeline`` on first access (PEP 562)."""
    if name == "run_experiment_pipeline":
        from .experiment_pipeline import run_experiment_pipeline

        return run_experiment_pipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
