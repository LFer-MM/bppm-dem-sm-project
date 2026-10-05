End-to-end walkthroughs
=======================

Full studies, each shown from the CLI and from Python. Pick one; both do the
same thing.

From raw DEM CSVs to a Lacey comparison plot
--------------------------------------------

The whole study in one run: convert the DEM dump, train the GRU, predict
the rest of the run, score it against DEM, and save every figure.

Inputs:

- ``data/raw/sic_csv_frames/`` -- the DEM CSV dump of the full run (from
  ``bppm-dem-sm dem-sim``, or add ``--do-simulate`` / ``do_simulate=True``
  to produce it in the same run).
- ``data/processed/sic_training_dataset_3s_4s_parquet/`` -- the short
  reference window the GRU is trained on (``train_data_dir``). The pipeline
  does not cut this window from the full run; prepare it beforehand.

CLI -- save the settings as ``configs/full_study.json``, so the run can be repeated:

.. code-block:: json

   {
     "raw_data_dir": "data/raw/sic_csv_frames",
     "data_dir": "data/processed/sic_dataset_20s_dt0p0001_parquet",
     "train_data_dir": "data/processed/sic_training_dataset_3s_4s_parquet",
     "model_path": "models/rnn_gru_sic_model.keras",
     "do_process": true,
     "do_train": true,
     "do_predict": true,
     "do_metrics": true,
     "do_visualization": true,
     "training": {"epochs": 20},
     "prediction": {"start_frame": 66, "autoregressive": true},
     "stochastic": {"enabled": true},
     "computing_speed": {"dem_reference_seconds": 86400.0},
     "visualization": {"save_figures": true, "show_plots": false}
   }

.. code-block:: bash

   bppm-dem-sm ml-pipeline --config configs/full_study.json

Python -- the same settings:

.. code-block:: python

   from pathlib import Path
   from bppm_dem_sm import (
       ExperimentConfig,
       PredictionOptions,
       TrainingOptions,
       VisualizationOptions,
       run_experiment_pipeline,
   )
   from bppm_dem_sm.config import ComputingSpeedOptions, StochasticOptions

   cfg = ExperimentConfig(
       raw_data_dir=Path("data/raw/sic_csv_frames"),
       data_dir=Path("data/processed/sic_dataset_20s_dt0p0001_parquet"),
       train_data_dir=Path("data/processed/sic_training_dataset_3s_4s_parquet"),
       model_path=Path("models/rnn_gru_sic_model.keras"),
       do_process=True,
       do_train=True,
       training=TrainingOptions(epochs=20),
       prediction=PredictionOptions(start_frame=66, autoregressive=True),
       stochastic=StochasticOptions(enabled=True),
       computing_speed=ComputingSpeedOptions(dem_reference_seconds=86400.0),
       visualization=VisualizationOptions(save_figures=True, show_plots=False),
   )
   results = run_experiment_pipeline(cfg)

   m = results["metrics"]
   print("final Lacey index, DEM:", m["gt"]["lacey"].iloc[-1])
   print("final Lacey index, surrogate:", m["pred"]["lacey"].iloc[-1])

.. figure:: _images/lacey_comparison.png
   :alt: Lacey mixing index over 20 s for DEM and the surrogate; the surrogate starts at 4 s and ends above DEM.
   :width: 80%

   Result of this walkthrough on the SiC dataset, trained on 3.0-4.0 s, autoregressive with SR from 4.05 s (the walkthrough settings). The surrogate ends at a Lacey index of 0.75 against DEM's 0.60: it mixes too much over the rollout.

What you get:

- ``models/rnn_gru_sic_model.keras`` and ``.history.json``
- ``data/interim/rnn_predictions/pred_frames/pred_frame_*.parquet`` and
  ``predictions_all.parquet``
- metric tables next to each frame set (``lacey_over_time*.parquet``,
  ``segregation_profile_*.parquet``, ``velocity_speed.json``,
  ``granular_temperature.parquet``) and ``reports/computing_speed.json``
- ``reports/figures/lacey_comparison.png`` and the other comparison
  figures; training curves, cell grids, and the animation under
  ``data/interim/figures/``

Re-scoring an existing model without retraining
-----------------------------------------------

The model is trained; now compare prediction settings -- here
teacher-forced vs. autoregressive with SR -- each in its own output
directory, then plot each against DEM.

CLI:

.. code-block:: bash

   bppm-dem-sm ml-pipeline --no-do-visualization \
       --pred-out-dir data/interim/pred_teacher_forced

   bppm-dem-sm ml-pipeline --no-do-visualization \
       --autoregressive --enabled --pred-out-dir data/interim/pred_ar_sr

   bppm-dem-sm ml-pipeline --no-do-predict --no-do-metrics --do-visualization \
       --save-figures --no-show-plots --pred-out-dir data/interim/pred_ar_sr

Python -- keep both metric dicts in memory and compare directly:

.. code-block:: python

   from pathlib import Path
   from bppm_dem_sm import ExperimentConfig, run_experiment_pipeline

   base = ExperimentConfig(do_visualization=False)  # do_train defaults to off

   runs = {
       "teacher_forced": base.with_overrides(pred_out_dir=Path("data/interim/pred_teacher_forced")),
       "ar_sr": base.with_overrides(
           autoregressive=True, enabled=True, pred_out_dir=Path("data/interim/pred_ar_sr")
       ),
   }
   scores = {name: run_experiment_pipeline(cfg)["metrics"] for name, cfg in runs.items()}

   for name, m in scores.items():
       print(name, "final Lacey:", m["pred"]["lacey"].iloc[-1], "DEM:", m["gt"]["lacey"].iloc[-1])

   run_experiment_pipeline(
       runs["ar_sr"], do_predict=False, do_metrics=False, do_visualization=True,
       save_figures=True, show_plots=False,
   )

.. note::

   Figure file names do not include the prediction directory, so the last
   visualization run overwrites the previous one's figures. Move or rename
   them between runs to keep both. Ground-truth metric tables are rewritten
   on every metrics run too; they do not change, as ``data_dir`` is the same.

On the dataset used for these docs (same trained model, predicting from
4.05 s to 19.85 s), the final values were:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Prediction mode
     - Final Lacey index
     - Mean large-particle speed (m/s)
   * - DEM (ground truth)
     - 0.599
     - 0.53
   * - Teacher-forced
     - 0.604
     - 0.58
   * - Autoregressive, no SR
     - 0.441
     - 1.32
   * - Autoregressive + SR
     - 0.753
     - 1.31

Teacher-forced prediction tracks DEM because every step starts from
ground truth; in the autoregressive rollouts, errors accumulate.
