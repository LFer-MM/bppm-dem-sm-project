Visualization
=============

:mod:`bppm_dem_sm.visualization` holds every plot and animation in the
project. Other stages only compute and save, so each plot here reads its
input from disk (or from a dict you pass) and works in a separate process
from the stage that produced it.

Every figure from one call
--------------------------

:func:`~bppm_dem_sm.visualization.run_visualization.generate_visualizations`
is the ``do_visualization`` stage. It renders whatever has inputs on disk
and skips the rest:

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, VisualizationOptions
   from bppm_dem_sm.visualization.run_visualization import generate_visualizations

   cfg = ExperimentConfig(
       visualization=VisualizationOptions(plane="xy", fps=30, save_figures=True, show_plots=False),
   )
   artifacts = generate_visualizations(cfg)  # metrics loaded from disk
   # or, with metrics already in memory:
   # artifacts = generate_visualizations(cfg, metrics=m)

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Figure
     - Needs
     - Saved to (``save_figures=True``)
   * - Training curves
     - ``<model_path>.history.json``
     - ``data/interim/figures/training_curves.png``
   * - Lacey and SR cell grids
     - a frame in ``data_dir``
     - ``data/interim/figures/cell_grid_frame_{lacey,sr}.png``
   * - Five metrics comparisons
     - ``gt`` Lacey results
     - ``reports/figures/*_comparison.png``
   * - Prediction animation
     - frames in ``pred_frames_dir``
     - ``data/interim/figures/pred_animation.mp4`` (``.gif`` without ffmpeg)

With ``show_plots=False`` and ``save_figures=False``, the training curves
and grids are skipped.

Training curves
---------------

Takes the history file ``train_and_save`` wrote, a loaded dict, or a Keras
``History``:

.. code-block:: python

   from bppm_dem_sm.visualization.training_curves import plot_training_history

   fig = plot_training_history(
       "models/rnn_gru_sic_model.history.json",
       save_path="reports/figures/training_curves.png",
       show=False,
   )
   # or: plot_training_history(history) right after train_and_save

Metrics comparison plots
------------------------

Each takes the metrics dict from ``compute_metrics`` or ``load_metrics``
and draws DEM against surrogate (DEM only when no ``*_pred`` keys exist). A
plot whose input is missing prints a message and returns ``None``:

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, VisualizationOptions
   from bppm_dem_sm.metrics.run_metrics import load_metrics
   from bppm_dem_sm.visualization import metrics_plots

   cfg = ExperimentConfig(visualization=VisualizationOptions(save_figures=True))
   m = load_metrics(cfg)

   metrics_plots.plot_lacey_comparison(m, cfg, show=False)       # Lacey index vs. time
   metrics_plots.plot_segregation_profile(m, cfg, show=False)    # radial + axial, last frame
   metrics_plots.plot_velocity_distribution(m, cfg, show=False)  # speed histograms per species
   metrics_plots.plot_granular_temperature(m, cfg, show=False)   # per-cell boxplots
   metrics_plots.plot_computing_speed(m, cfg, show=False)        # speedup bars

These save under ``reports/figures/`` when
``visualization.save_figures`` is set.

Cell-grid overlay on one frame
------------------------------

A frame's XY scatter (rocks red, balls blue) with a square grid of
``cell_size``. Use it to check a cell size against the particle sizes:

.. code-block:: python

   from bppm_dem_sm.visualization.cell_grid import plot_particles_with_grid

   frame = "data/processed/sic_dataset_20s_dt0p0001_parquet/frame_00000.parquet"
   plot_particles_with_grid(frame, cell_size=0.44, save_path="reports/figures/grid_lacey.png", show=False)
   plot_particles_with_grid(frame, cell_size=0.5588, save_path="reports/figures/grid_sr.png", show=False)

``0.44`` is the Lacey / granular-temperature cell
(``metrics.cell_size``); ``0.5588`` is the SR cell
(``stochastic.velocity_cell_size``).
:func:`~bppm_dem_sm.visualization.run_visualization.plot_frame_grid` and
:func:`~bppm_dem_sm.visualization.run_visualization.plot_sr_grid` read
those values from a config.

Animating frames
----------------

From a config (plane, fps, marker size, and stride come from
``visualization``); MP4 falls back to GIF when ffmpeg is missing:

.. code-block:: python

   from bppm_dem_sm.visualization.run_visualization import animate_frames

   anim, path = animate_frames(
       cfg.prediction.pred_frames_dir, cfg, pattern="pred_frame_*.parquet",
       save_path="reports/figures/pred_animation.mp4",
   )

Without a config, for any frame directory:

.. code-block:: python

   from bppm_dem_sm.visualization.animate_particles import animate_particles

   animate_particles(
       "data/processed/sic_dataset_20s_dt0p0001_parquet",
       glob_pattern="frame_*.parquet",
       plane="xz",
       every_nth_frame=5,
       fps=30,
       save_path="reports/figures/gt_animation.mp4",
   )

``animate_particles`` has no GIF fallback: saving ``.mp4`` needs ffmpeg.
