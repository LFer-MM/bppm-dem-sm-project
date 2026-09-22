"""bppm_dem_sm: bidisperse particle mixing DEM surrogate-model package.

All code lives in flat modules at the package root (config, data_io, training,
prediction, run_metrics, lacey_mixing_index, segregation_profile,
velocity_metrics, stochastic_motion, run_visualization, cell_grid,
animate_particles, csv_to_parquet, verify_particle_integrity, sim_functions,
simulation, dem_launcher, pipeline, cli, progress).

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
