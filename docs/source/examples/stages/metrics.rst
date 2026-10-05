Metrics
=======

:mod:`bppm_dem_sm.metrics` scores ground-truth (DEM) and predicted frames
with the measures used in Kishida et al. (2025): Lacey's mixing index, the
radial/axial large-particle fraction profile, the velocity distribution per
species, granular temperature, and computing speed. Computation only -- the
plots are in :doc:`visualization`.

All of them at once
-------------------

:func:`~bppm_dem_sm.metrics.run_metrics.compute_metrics` is the
``do_metrics`` stage. It scores ``data_dir`` and, if predictions exist,
``prediction.pred_frames_dir``. It writes each result next to the frames it
came from, so :func:`~bppm_dem_sm.metrics.run_metrics.load_metrics` can read
them back later without recomputing:

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, MetricsOptions
   from bppm_dem_sm.metrics.run_metrics import compute_metrics, load_metrics

   cfg = ExperimentConfig(
       metrics=MetricsOptions(cell_size=0.44, min_particles_per_cell=15, metrics_dt=0.05),
   )
   m = compute_metrics(cfg)

   # In a later process, with the same cfg:
   m = load_metrics(cfg)

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Key (``_pred`` keys only with predictions)
     - Value
   * - ``gt`` / ``pred``
     - Lacey per frame: ``frame``, ``time``, ``lacey``, ``n_cells_used``,
       ``tracer_fraction_global``, ``mean_particles_per_cell``.
   * - ``radial_gt`` / ``radial_pred``, ``axial_gt`` / ``axial_pred``
     - Large-particle fraction per frame and bin: ``frame``, ``time``,
       ``bin``, ``bin_center``, ``fraction_large``, ``n_particles``.
   * - ``velocity_gt`` / ``velocity_pred``
     - Speeds per species and granular temperature per cell at the last frame
       pair: ``time``, ``frame_t``, ``frame_t1``, ``speed``
       (``{"small", "large"}``), ``granular_temperature``.
   * - ``computing_speed``
     - Only from ``load_metrics``, or added by the pipeline -- see below.

``time`` is ``frame * metrics_dt``. The tracer (large) species is detected
from the first ground-truth frame as the larger of the two radii.

Lacey mixing index
------------------

``M`` goes from 0 (fully segregated) to 1 (randomly mixed). Particles are
binned into cubic cells; cells with fewer than ``min_particles_per_cell``
particles are skipped:

.. code-block:: python

   import pandas as pd
   from bppm_dem_sm.metrics.lacey_mixing_index import detect_tracer_radius, lacey_index_for_frame

   df = pd.read_parquet("data/processed/sic_dataset_20s_dt0p0001_parquet/frame_00000.parquet")
   tracer_r = detect_tracer_radius(df["r"].to_numpy())
   M, n_cells, p_global, mean_n = lacey_index_for_frame(
       df, cell_size=0.44, tracer_radius=tracer_r, min_particles_per_cell=15
   )

``0.44`` m is ``0.04 x MILL_DIAMETER_M``, the paper's Lacey cell.

Segregation profile
-------------------

Fraction of large particles against distance from the mill axis (radial)
and position along it (axial). The cross section is assumed to lie in the
XY plane, with Z along the axis. Build the bin edges once and reuse them for
every frame you compare, so bins line up:

.. code-block:: python

   from bppm_dem_sm.metrics.segregation_profile import (
       axial_bin_edges,
       axial_fraction_profile,
       radial_bin_edges,
       radial_fraction_profile,
   )

   r_edges = radial_bin_edges(df, center_x=0.0, center_y=0.0, n_bins=12)
   z_edges = axial_bin_edges(df, center_z=0.0, n_bins=12)

   radial = radial_fraction_profile(df, tracer_r, r_edges)
   axial = axial_fraction_profile(df, tracer_r, z_edges)
   print(radial[["bin_center", "fraction_large", "n_particles"]])

Empty bins have ``fraction_large = NaN``.

Velocity distribution and granular temperature
----------------------------------------------

Both come from finite-difference velocities between two frames with the
same particle ids:

.. code-block:: python

   from bppm_dem_sm.metrics.velocity_metrics import (
       granular_temperature_by_cell,
       velocity_speed_by_species,
   )

   df_t = pd.read_parquet(".../frame_00100.parquet")
   df_t1 = pd.read_parquet(".../frame_00101.parquet")
   dt = 0.05  # seconds between the two frames

   speed = velocity_speed_by_species(df_t, df_t1, dt, tracer_r)
   print(speed["small"].mean(), speed["large"].mean())

   T_g = granular_temperature_by_cell(df_t, df_t1, dt, cell_size=0.44, min_particles_per_cell=15)
   # one value per cell: mean(||v_i - <v>_cell||^2) / 3

Rows are matched by ``id``, so the two frames may be stored in different
orders; differing particle sets raise ``ValueError``.

Computing speed
---------------

Compares this run's wall-clock training and prediction time with a DEM run
you timed yourself (the pipeline does not time DEM):

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig
   from bppm_dem_sm.config import ComputingSpeedOptions
   from bppm_dem_sm.metrics.computing_speed import compute_computing_speed, load_computing_speed

   cfg = ExperimentConfig(
       computing_speed=ComputingSpeedOptions(
           dem_reference_seconds=36 * 3600,      # full DEM run, same simulated duration
           dem_data_acquisition_seconds=2 * 3600,  # short DEM run that made the training data
       ),
   )
   cs = compute_computing_speed({"train_seconds": 1800.0, "predict_seconds": 540.0}, cfg)
   print(cs["prediction_only_speedup"], cs["all_steps_speedup"])  # 240.0 13.58...
   # also written to reports/computing_speed.json; read it back later with:
   cs = load_computing_speed()

In a pipeline run, ``timing`` comes from the stages that ran
(``results["timing"]``), and the result is stored as
``results["metrics"]["computing_speed"]``. A speedup is ``None`` when the
time it depends on was not recorded.
