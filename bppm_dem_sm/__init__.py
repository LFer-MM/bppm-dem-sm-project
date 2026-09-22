"""bppm_dem_sm: bidisperse particle mixing DEM surrogate-model package.

Organized by pipeline stage:

- :mod:`bppm_dem_sm.simulation` -- YADE-only DEM simulation (never imported
  by the plain venv side, except ``simulation.launcher``, which shells out
  to ``yade`` instead of importing it).
- :mod:`bppm_dem_sm.data_processing` -- raw CSV -> training-ready parquet.
- :mod:`bppm_dem_sm.model` -- the GRU surrogate: build/train/predict, plus
  the stochastic-random (SR) term.
- :mod:`bppm_dem_sm.metrics` -- post-hoc computation (Lacey index,
  segregation profile, velocity/granular temperature, computing speed).
- :mod:`bppm_dem_sm.visualization` -- all plotting/animation, including the
  plots for ``metrics`` and training curves.

Plus top-level plumbing: ``config``, ``pipeline``, ``cli``, ``progress``,
``tf_quiet``.

The ``bppm-dem-sm`` CLI (:mod:`bppm_dem_sm.cli`) exposes two subcommands:
``dem-sim`` (launches a YADE DEM simulation as a subprocess) and
``ml-pipeline`` (runs :func:`run_pipeline`).
"""

from .config import (
    MetricsOptions,
    PipelineConfig,
    PredictionOptions,
    TrainingOptions,
    VisualizationOptions,
)
from .pipeline import run_pipeline

__all__ = [
    "MetricsOptions",
    "PipelineConfig",
    "PredictionOptions",
    "TrainingOptions",
    "VisualizationOptions",
    "run_pipeline",
]
