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
:class:`~bppm_dem_sm.config.PipelineConfig` (nested ``training`` /
``prediction`` / ``metrics`` / ``visualization`` objects). When ``--config``
is set, other pipeline flags are ignored.

.. code-block:: bash

   bppm-pipeline --config configs/pipeline_example.json

The checked-in example:

.. literalinclude:: ../../configs/pipeline_example.json
   :language: json

CLI flags without JSON
~~~~~~~~~~~~~~~~~~~~~~

Boolean flags use ``--flag`` / ``--no-flag``. Nested option-group fields stay
flat (``--epochs``, not ``--training-epochs``):

.. code-block:: bash

   bppm-pipeline --do-train --no-do-predict --epochs 10
   bppm-pipeline --do-predict --start-frame 66 --no-autoregressive
   bppm-pipeline --no-do-train --do-metrics --cell-size 0.4732
   bppm-pipeline --do-visualization --save-figures --no-show-plots --plane xy

See ``bppm-pipeline --help`` for the full flag list.

From Python
~~~~~~~~~~~

Load the same JSON, or build a :class:`~bppm_dem_sm.config.PipelineConfig`
in code. :func:`~bppm_dem_sm.pipeline.run_pipeline` returns a dict of
artifacts keyed by stage (``config``, and optionally ``model``, ``history``,
``predictions``, ``metrics``, ``visualizations``).

.. code-block:: python

   from bppm_dem_sm import PipelineConfig, TrainingOptions, run_pipeline

   cfg = PipelineConfig.from_json("configs/pipeline_example.json")
   results = run_pipeline(cfg)

   # Keyword overrides (core fields or nested leaf names):
   results = run_pipeline(do_train=True, do_predict=False, epochs=10)

   # Nested option groups:
   cfg = PipelineConfig(
       do_train=True,
       do_predict=False,
       training=TrainingOptions(epochs=10, batch_size=256),
   )
   results = run_pipeline(cfg)

Configuration
-------------

JSON round-trip
~~~~~~~~~~~~~~~

.. code-block:: python

   from pathlib import Path
   import json
   from bppm_dem_sm import PipelineConfig

   cfg = PipelineConfig.from_json("configs/pipeline_example.json")
   Path("configs/my_run.json").write_text(json.dumps(cfg.to_dict(), indent=2))

Overrides on an existing config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:meth:`~bppm_dem_sm.config.PipelineConfig.with_overrides` accepts top-level
fields, whole option groups, or nested leaf names:

.. code-block:: python

   from bppm_dem_sm import PipelineConfig, VisualizationOptions

   cfg = PipelineConfig.from_json("configs/pipeline_example.json")
   cfg = cfg.with_overrides(
       do_train=True,
       epochs=5,
       visualization=VisualizationOptions(save_figures=True, show_plots=False),
   )

Data preparation
----------------

Convert DEM CSV dumps to Parquet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from bppm_dem_sm.data_processing.csv_to_parquet import convert_folder_csv_to_parquet

   convert_folder_csv_to_parquet(
       "data/raw/sic_csv_frames",
       "data/processed/sic_dataset_20s_dt0p0001_parquet",
   )

Check particle inventory across frames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A healthy bidisperse export should have near-zero standard deviation of
counts per radius class (same inventory every frame):

.. code-block:: python

   from bppm_dem_sm.data_processing.integrity import report_particle_integrity

   report_particle_integrity("data/processed/sic_dataset_20s_dt0p0001_parquet")

Load frames for the surrogate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from bppm_dem_sm.data_processing import frames as data_io
   from bppm_dem_sm.config import FEATURE_COLS

   pos, rad, ids = data_io.load_frames_stacked(
       "data/processed/sic_training_dataset_3s_4s_parquet",
       pattern="frame_*.parquet",
       feature_cols=FEATURE_COLS,
   )
   X, y = data_io.build_supervised_dataset(pos, rad, frames_in=15)
   # X: [(T - frames_in) * N, frames_in, 4]  y: [(T - frames_in) * N, 3]

Training and prediction
-----------------------

Train only
~~~~~~~~~~

Writes a ``.keras`` artifact to ``config.model_path``:

.. code-block:: python

   from bppm_dem_sm import PipelineConfig, TrainingOptions, run_pipeline
   from bppm_dem_sm.model.training import train_and_save

   cfg = PipelineConfig(
       do_train=True,
       do_predict=False,
       do_metrics=False,
       do_visualization=False,
       training=TrainingOptions(epochs=20, batch_size=500),
   )
   model, history = train_and_save(cfg)
   # or: run_pipeline(cfg)

Predict only
~~~~~~~~~~~~

Loads ``config.model_path`` unless you pass a model. Writes
``pred_frame_XXXXX.parquet`` under ``prediction.pred_frames_dir`` and a
combined table at ``prediction.pred_combined_parquet``.

.. code-block:: python

   from bppm_dem_sm import PipelineConfig, PredictionOptions
   from bppm_dem_sm.model.prediction import predict_frames

   cfg = PipelineConfig(
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
predictions exist, next to the predicted frames.

.. code-block:: python

   from bppm_dem_sm import PipelineConfig, MetricsOptions
   from bppm_dem_sm.metrics.run_metrics import compute_metrics
   from bppm_dem_sm.visualization.metrics_plots import plot_lacey_comparison

   cfg = PipelineConfig(
       do_metrics=True,
       metrics=MetricsOptions(cell_size=0.4732, min_particles_per_cell=15, metrics_dt=0.05),
   )
   summaries = compute_metrics(cfg)  # {"gt": DataFrame, optionally "pred": DataFrame}
   plot_lacey_comparison(summaries, cfg, show=False)

Single-frame Lacey index
~~~~~~~~~~~~~~~~~~~~~~~~

The index ``M`` is 0 (fully segregated) to 1 (randomly mixed):

.. code-block:: python

   import pandas as pd
   from bppm_dem_sm.metrics.lacey_mixing_index import detect_tracer_radius, lacey_index_for_frame

   df = pd.read_parquet("data/processed/sic_dataset_20s_dt0p0001_parquet/frame_00000.parquet")
   tracer_r = detect_tracer_radius(df["r"].to_numpy())
   M, n_cells, p_global, mean_n = lacey_index_for_frame(
       df, cell_size=0.4732, tracer_radius=tracer_r, min_particles_per_cell=15
   )
   print(M, n_cells, p_global, mean_n)

Visualization
-------------

Pipeline cell-grid and prediction animation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from bppm_dem_sm import PipelineConfig, VisualizationOptions
   from bppm_dem_sm.visualization.run_visualization import generate_visualizations

   cfg = PipelineConfig(
       visualization=VisualizationOptions(
           plane="xy",
           fps=30,
           save_figures=True,
           show_plots=False,
       ),
   )
   artifacts = generate_visualizations(cfg)
   # artifacts may include grid_save_path / animation_save_path under data/interim/figures

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

.. code-block:: python

   from bppm_dem_sm.visualization.cell_grid import plot_particles_with_grid

   plot_particles_with_grid(
       "data/processed/sic_dataset_20s_dt0p0001_parquet/frame_00000.parquet",
       cell_size=0.4732,
       save_path="reports/figures/cell_grid_frame.png",
       show=False,
   )

DEM simulation (YADE)
---------------------

The mill-slice ingress lives in :func:`bppm_dem_sm.simulation.simulation.run`
and requires a YADE interpreter (not the usual ``python`` / ``bppm-pipeline``
entry point). From a YADE session at the repo root:

.. code-block:: python

   from bppm_dem_sm.simulation.simulation import run

   run()

That call sets Hertz–Mindlin contacts from
:func:`~bppm_dem_sm.config.build_material_interactions`, opens a Qt viewer,
and ingresses a random bidisperse rock/steel charge. Particle counts,
diameters, and the mill STL path are package defaults on
``bppm_dem_sm.config`` (``ROCK_COUNT``, ``BALL_COUNT``,
``SAGMILL_STL_PATH``, …).
