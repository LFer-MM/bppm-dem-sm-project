Examples
========

Snippets below assume the package is installed from the repository root
(``pip install -e .``). Paths are relative to that root. For install and the
shortest CLI walkthrough, see :doc:`getting_started`.

End-to-end pipeline
-------------------

CLI with a JSON config
~~~~~~~~~~~~~~~~~~~~~~

Preferred: pass a JSON file whose keys match
:class:`~bppm_dem_sm.config.ExperimentConfig` (nested ``training`` /
``prediction`` / ``metrics`` / ``visualization`` objects). When ``--config``
is set, other pipeline flags are ignored.

.. code-block:: bash

   bppm-dem-sm ml-pipeline --config configs/pipeline_example.json

The checked-in example:

.. literalinclude:: ../../configs/pipeline_example.json
   :language: json

CLI flags without JSON
~~~~~~~~~~~~~~~~~~~~~~

Boolean flags use ``--flag`` / ``--no-flag``. Nested option-group fields stay
flat (``--epochs``, not ``--training-epochs``):

.. code-block:: bash

   bppm-dem-sm ml-pipeline --do-train --no-do-predict --epochs 10
   bppm-dem-sm ml-pipeline --do-predict --start-frame 66 --no-autoregressive
   bppm-dem-sm ml-pipeline --no-do-train --do-metrics --cell-size 0.44
   bppm-dem-sm ml-pipeline --do-visualization --save-figures --no-show-plots --plane xy

See ``bppm-dem-sm ml-pipeline --help`` for the full flag list.

From Python
~~~~~~~~~~~

Load the same JSON, or build an :class:`~bppm_dem_sm.config.ExperimentConfig`
in code. :func:`~bppm_dem_sm.experiment_pipeline.run_experiment_pipeline`
returns a dict of artifacts keyed by stage (``config``, and optionally
``dem_simulation``, ``data_processing``, ``model``, ``history``,
``predictions``, ``metrics``, ``visualizations``).

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, TrainingOptions, run_experiment_pipeline

   cfg = ExperimentConfig.from_json("configs/pipeline_example.json")
   results = run_experiment_pipeline(cfg)

   # Keyword overrides (core fields or nested leaf names):
   results = run_experiment_pipeline(do_train=True, do_predict=False, epochs=10)

   # Nested option groups:
   cfg = ExperimentConfig(
       do_train=True,
       do_predict=False,
       training=TrainingOptions(epochs=10, batch_size=256),
   )
   results = run_experiment_pipeline(cfg)

Configuration
-------------

JSON round-trip
~~~~~~~~~~~~~~~

.. code-block:: python

   from pathlib import Path
   import json
   from bppm_dem_sm import ExperimentConfig

   cfg = ExperimentConfig.from_json("configs/pipeline_example.json")
   Path("configs/my_run.json").write_text(json.dumps(cfg.to_dict(), indent=2))

Overrides on an existing config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:meth:`~bppm_dem_sm.config.ExperimentConfig.with_overrides` accepts top-level
fields, whole option groups, or nested leaf names:

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, VisualizationOptions

   cfg = ExperimentConfig.from_json("configs/pipeline_example.json")
   cfg = cfg.with_overrides(
       do_train=True,
       epochs=5,
       visualization=VisualizationOptions(save_figures=True, show_plots=False),
   )

Data preparation
----------------

Convert DEM CSV dumps to Parquet, and check integrity, in one gated stage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig
   from bppm_dem_sm.data_processing.run_data_processing import process_frames

   cfg = ExperimentConfig(
       raw_data_dir="data/raw/sic_csv_frames",
       data_dir="data/processed/sic_dataset_20s_dt0p0001_parquet",
   )
   result = process_frames(cfg)
   # result = {"data_dir": ..., "integrity_report": DataFrame}

Or call the two steps directly:

.. code-block:: python

   from bppm_dem_sm.data_processing.convert import convert_folder_csv_to_parquet
   from bppm_dem_sm.data_processing.integrity import report_particle_integrity

   convert_folder_csv_to_parquet(
       "data/raw/sic_csv_frames",
       "data/processed/sic_dataset_20s_dt0p0001_parquet",
   )
   report_particle_integrity("data/processed/sic_dataset_20s_dt0p0001_parquet")

Load frames and build the supervised dataset for the surrogate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from bppm_dem_sm.data_processing import frames as data_io
   from bppm_dem_sm.data_processing import dataset as data_ds
   from bppm_dem_sm.config import FEATURE_COLS

   pos, rad, ids = data_io.load_frames_stacked(
       "data/processed/sic_training_dataset_3s_4s_parquet",
       pattern="frame_*.parquet",
       feature_cols=FEATURE_COLS,
   )
   X, y = data_ds.build_supervised_dataset(pos, rad, frames_in=15)
   # X: [(T - frames_in) * N, frames_in, 4]  y: [(T - frames_in) * N, 3]

Training and prediction
-----------------------

Train only
~~~~~~~~~~

Writes a ``.keras`` artifact to ``config.model_path`` and a
``<name>.history.json`` sibling with the per-epoch loss (no plot is
rendered here -- see :doc:`Visualization <examples>` below):

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, TrainingOptions, run_experiment_pipeline
   from bppm_dem_sm.model.rnn.training import train_and_save

   cfg = ExperimentConfig(
       do_train=True,
       do_predict=False,
       do_metrics=False,
       do_visualization=False,
       training=TrainingOptions(epochs=20, batch_size=500),
   )
   model, history = train_and_save(cfg)
   # or: run_experiment_pipeline(cfg)

Predict only
~~~~~~~~~~~~

Loads ``config.model_path`` unless you pass a model. Writes
``pred_frame_XXXXX.parquet`` under ``prediction.pred_frames_dir`` and a
combined table at ``prediction.pred_combined_parquet``.

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, PredictionOptions
   from bppm_dem_sm.model.rnn.prediction import predict_frames

   cfg = ExperimentConfig(
       do_train=False,
       do_predict=True,
       do_metrics=False,
       do_visualization=False,
       prediction=PredictionOptions(
           start_frame=66,
           autoregressive=False,
           predict_until_end=True,
           pred_out_dir="data/interim/rnn_predictions",
       ),
   )
   preds = predict_frames(cfg)

Teacher-forced vs autoregressive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With ``autoregressive=False`` (default), each step feeds the next
**ground-truth** frame into the sliding window. Set
``autoregressive=True`` to feed the model's own predicted ``(x, y, z)``
back in:

.. code-block:: python

   cfg = cfg.with_overrides(autoregressive=True, max_steps=50, predict_until_end=False)

Metrics (Lacey mixing index)
----------------------------

Pipeline comparison of DEM vs predicted frames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:func:`~bppm_dem_sm.metrics.run_metrics.compute_metrics` writes a
``lacey_over_time.parquet`` next to the ground-truth frames and, when
predictions exist, next to the predicted frames -- along with
``segregation_profile_{radial,axial}.parquet``, ``velocity_speed.json``,
and ``granular_temperature.parquet``. A later call to
:func:`~bppm_dem_sm.metrics.run_metrics.load_metrics` reads all of it back,
without needing to recompute:

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, MetricsOptions
   from bppm_dem_sm.metrics.run_metrics import compute_metrics, load_metrics
   from bppm_dem_sm.visualization.metrics_plots import plot_lacey_comparison

   cfg = ExperimentConfig(
       do_metrics=True,
       metrics=MetricsOptions(cell_size=0.44, min_particles_per_cell=15, metrics_dt=0.05),
   )
   summaries = compute_metrics(cfg)  # {"gt": DataFrame, optionally "pred": DataFrame, ...}
   plot_lacey_comparison(summaries, cfg, show=False)

   # In a later process, with the same cfg:
   summaries = load_metrics(cfg)

Single-frame Lacey index
~~~~~~~~~~~~~~~~~~~~~~~~

The index ``M`` is 0 (fully segregated) to 1 (randomly mixed). ``0.44`` here
is ``0.04 x MILL_DIAMETER_M`` -- see :class:`~bppm_dem_sm.config.MetricsOptions`
for why this is a *different* cell size from the SR field's below:

.. code-block:: python

   import pandas as pd
   from bppm_dem_sm.metrics.lacey_mixing_index import detect_tracer_radius, lacey_index_for_frame

   df = pd.read_parquet("data/processed/sic_dataset_20s_dt0p0001_parquet/frame_00000.parquet")
   tracer_r = detect_tracer_radius(df["r"].to_numpy())
   M, n_cells, p_global, mean_n = lacey_index_for_frame(
       df, cell_size=0.44, tracer_radius=tracer_r, min_particles_per_cell=15
   )
   print(M, n_cells, p_global, mean_n)

Visualization
-------------

Everything renders from one call
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``generate_visualizations`` is the only place anything gets plotted in this
project -- training curves, both cell-grid frames (Lacey's and SR's, at
their two different cell sizes), the metrics comparison plots, and the
prediction animation. Each reads whatever its stage already persisted to
disk, so this works even when called on its own, in a separate process from
``do_train``/``do_metrics``:

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, VisualizationOptions
   from bppm_dem_sm.visualization.run_visualization import generate_visualizations

   cfg = ExperimentConfig(
       visualization=VisualizationOptions(
           plane="xy",
           fps=30,
           save_figures=True,
           show_plots=False,
       ),
   )
   artifacts = generate_visualizations(cfg)
   # artifacts may include grid_save_path / sr_grid_save_path / animation_save_path
   # under data/interim/figures, and training_curves_save_path once do_train has run

Standalone animation of any frame directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from bppm_dem_sm.visualization.animate_particles import animate_particles

   animate_particles(
       "data/processed/sic_dataset_20s_dt0p0001_parquet",
       glob_pattern="frame_*.parquet",
       plane="xy",
       every_nth_frame=5,
       fps=30,
       save_path="reports/figures/gt_animation.gif",
   )

Cell-grid overlay on one frame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same overlay function is used for both grids -- only ``cell_size``
differs (Lacey's ``0.04 x MILL_DIAMETER_M`` vs. SR's
``4 x BALL_DIAM_M``; see :mod:`bppm_dem_sm.config`):

.. code-block:: python

   from bppm_dem_sm.visualization.cell_grid import plot_particles_with_grid

   plot_particles_with_grid(
       "data/processed/sic_dataset_20s_dt0p0001_parquet/frame_00000.parquet",
       cell_size=0.44,  # or 0.5588 for the SR grid
       save_path="reports/figures/cell_grid_frame.png",
       show=False,
   )

DEM simulation
--------------

The mill-slice ingress lives in
:func:`bppm_dem_sm.simulation.yade_dem.run_simulation.run` and requires a
YADE interpreter (not the usual ``python`` / ``bppm-dem-sm`` entry point).
From a YADE session at the repo root:

.. code-block:: python

   from bppm_dem_sm.simulation.yade_dem.run_simulation import run

   run()

That call sets Hertz–Mindlin contacts from
:func:`~bppm_dem_sm.config.build_yade_material_interactions`, opens a Qt
viewer, and ingresses a random bidisperse rock/steel charge. Particle
counts, diameters, mill diameter, and the mill STL path are package
defaults on ``bppm_dem_sm.config`` (``ROCK_COUNT``, ``BALL_COUNT``,
``MILL_DIAMETER_M``, ``SAGMILL_STL_PATH``, …).

From the normal venv (not a YADE session), launch it as a subprocess
instead -- this is what ``bppm-dem-sm dem-sim`` and
``ExperimentConfig.do_simulate`` do:

.. code-block:: python

   from bppm_dem_sm.simulation.launcher import launch_simulation

   launch_simulation(backend="yade")  # requires yade on PATH

``backend="blaze"`` is reserved for the placeholder BlazeDEM backend
(:mod:`bppm_dem_sm.simulation.blaze_dem`) and raises ``NotImplementedError``
until that's implemented.
