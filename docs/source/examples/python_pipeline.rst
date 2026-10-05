Python: the pipeline
====================

:func:`~bppm_dem_sm.experiment_pipeline.run_experiment_pipeline` is what
``bppm-dem-sm ml-pipeline`` calls. From Python you also get back what each
stage produced.

Three ways to configure a run
-----------------------------

From the same JSON file the CLI uses:

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, run_experiment_pipeline

   cfg = ExperimentConfig.from_json("configs/pipeline_example.json")
   results = run_experiment_pipeline(cfg)

From keyword overrides -- the same flat names as the CLI flags, applied on
top of ``config`` (or the defaults when it is omitted):

.. code-block:: python

   results = run_experiment_pipeline(do_train=True, epochs=10, batch_size=256)
   results = run_experiment_pipeline(cfg, autoregressive=True)

From nested option groups:

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig, PredictionOptions, TrainingOptions

   cfg = ExperimentConfig(
       do_train=True,
       training=TrainingOptions(epochs=10, batch_size=256),
       prediction=PredictionOptions(start_frame=66),
   )
   results = run_experiment_pipeline(cfg)

``StochasticOptions`` and ``ComputingSpeedOptions`` are imported from
:mod:`bppm_dem_sm.config`; the other option groups are also re-exported from
``bppm_dem_sm``.

The CLI recipes, in Python
--------------------------

One-to-one with :doc:`cli`. As there, ``do_predict``, ``do_metrics``, and
``do_visualization`` default to on.

.. code-block:: python

   from pathlib import Path
   from bppm_dem_sm import run_experiment_pipeline

   off = dict(do_predict=False, do_metrics=False, do_visualization=False)

   # Train only
   run_experiment_pipeline(do_train=True, epochs=20, **off)

   # Predict only, teacher-forced
   run_experiment_pipeline(do_metrics=False, do_visualization=False, start_frame=66)

   # Predict only, autoregressive + SR, into its own directory
   run_experiment_pipeline(
       do_metrics=False,
       do_visualization=False,
       autoregressive=True,
       predict_until_end=False,
       max_steps=50,
       enabled=True,  # stochastic.enabled
       pred_out_dir=Path("data/interim/rnn_predictions_ar_sr"),
   )

   # Metrics on existing predictions
   run_experiment_pipeline(
       do_predict=False,
       do_visualization=False,
       pred_out_dir=Path("data/interim/rnn_predictions_ar_sr"),
   )

   # Re-render figures only
   run_experiment_pipeline(
       do_predict=False, do_metrics=False, save_figures=True, show_plots=False
   )

Working with the results dict
-----------------------------

The return value has one key per stage that ran, plus ``config``:

.. list-table::
   :header-rows: 1
   :widths: 22 22 56

   * - Key
     - Present when
     - Value
   * - ``config``
     - always
     - The resolved :class:`~bppm_dem_sm.config.ExperimentConfig`
       (overrides applied).
   * - ``dem_simulation``
     - ``do_simulate``
     - ``subprocess.CompletedProcess`` of the YADE run.
   * - ``data_processing``
     - ``do_process``
     - ``{"data_dir": Path, "integrity_report": DataFrame}``.
   * - ``model`` / ``history``
     - ``do_train``
     - Trained Keras model and its ``History``.
   * - ``predictions``
     - ``do_predict``
     - ``DataFrame`` with ``frame_pred``, ``step``, ``id``, ``x``, ``y``,
       ``z``, ``dt``, ``r``.
   * - ``timing``
     - ``do_train`` or ``do_predict``
     - ``train_seconds`` / ``predict_seconds`` for the stages that ran.
   * - ``metrics``
     - ``do_metrics``
     - The :func:`~bppm_dem_sm.metrics.run_metrics.compute_metrics` dict plus
       ``computing_speed``.
   * - ``visualizations``
     - ``do_visualization``
     - Figures and saved paths from
       :func:`~bppm_dem_sm.visualization.run_visualization.generate_visualizations`.

.. code-block:: python

   results = run_experiment_pipeline(do_train=True, epochs=5)

   print(results["history"].history["val_loss"][-1])   # last validation loss
   preds = results["predictions"]
   print(preds.groupby("step").size().head())           # particles per predicted step

   m = results["metrics"]
   print(m["gt"][["time", "lacey"]].tail())             # DEM Lacey index over time
   if "pred" in m:
       print(m["pred"][["time", "lacey"]].tail())       # surrogate Lacey index
   print(m["computing_speed"]["prediction_only_speedup"])

When ``do_train`` is off, prediction loads ``model_path`` from disk, so
``model`` and ``history`` are absent.

Config management
-----------------

Save the resolved config of a run next to its outputs, then reload it:

.. code-block:: python

   import json
   from pathlib import Path
   from bppm_dem_sm import ExperimentConfig

   cfg = ExperimentConfig.from_json("configs/pipeline_example.json")
   Path("configs/my_run.json").write_text(json.dumps(cfg.to_dict(), indent=2))
   assert ExperimentConfig.from_json("configs/my_run.json") == cfg

:meth:`~bppm_dem_sm.config.ExperimentConfig.with_overrides` returns a
modified copy. It takes top-level fields, whole option groups, or flat leaf
names; leaf names apply after whole groups:

.. code-block:: python

   from bppm_dem_sm import VisualizationOptions

   cfg2 = cfg.with_overrides(
       do_train=True,
       epochs=5,
       visualization=VisualizationOptions(save_figures=True, show_plots=False),
   )
   print(cfg.training.epochs, cfg2.training.epochs)  # 20 5 -- cfg itself is unchanged

Unknown names fail early, in JSON and in Python alike:

.. code-block:: python

   cfg.with_overrides(epoch=5)
   # ValueError: Unknown ExperimentConfig override: 'epoch'
