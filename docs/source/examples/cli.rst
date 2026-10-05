Command line
============

The ``bppm-dem-sm`` console script has two subcommands: ``ml-pipeline``
(run the experiment pipeline) and ``dem-sim`` (launch a DEM simulation).
``python -m bppm_dem_sm`` is the same program.

Full pipeline from a JSON config
--------------------------------

Pass a JSON file whose keys match
:class:`~bppm_dem_sm.config.ExperimentConfig`, with nested ``training`` /
``prediction`` / ``metrics`` / ``stochastic`` / ``computing_speed`` /
``visualization`` objects. Omitted keys keep their defaults.

.. code-block:: bash

   bppm-dem-sm ml-pipeline --config configs/pipeline_example.json

The checked-in example:

.. literalinclude:: ../../../configs/pipeline_example.json
   :language: json

.. note::

   When ``--config`` is set, every other ``ml-pipeline`` flag is ignored. To
   change one value of a JSON run, copy the file and edit the copy.

Overriding with flags
---------------------

Without ``--config``, each flag overrides one default. Boolean fields use
``--flag`` / ``--no-flag``. Fields inside option groups keep their own name
-- ``--epochs``, not ``--training-epochs``; ``--enabled`` toggles the SR
term (``stochastic.enabled``):

.. code-block:: bash

   bppm-dem-sm ml-pipeline --epochs 10 --batch-size 256
   bppm-dem-sm ml-pipeline --start-frame 66 --autoregressive --max-steps 50 --no-predict-until-end
   bppm-dem-sm ml-pipeline --cell-size 0.44 --min-particles-per-cell 15
   bppm-dem-sm ml-pipeline --enabled --stochastic-seed 1
   bppm-dem-sm ml-pipeline --plane xz --fps 15 --save-figures --no-show-plots

``bppm-dem-sm ml-pipeline --help`` lists every flag, grouped as in the JSON.

Common recipes
--------------

``do_predict``, ``do_metrics``, and ``do_visualization`` default to on, so a
partial run switches off the stages it does not want.

Train only
~~~~~~~~~~

Writes ``model_path`` and its ``<name>.history.json``:

.. code-block:: bash

   bppm-dem-sm ml-pipeline --do-train --no-do-predict --no-do-metrics --no-do-visualization \
       --epochs 20 --model-path models/rnn_gru_sic_model.keras

Predict only
~~~~~~~~~~~~

Teacher-forced (default): every step feeds the next **ground-truth** frame
into the window:

.. code-block:: bash

   bppm-dem-sm ml-pipeline --no-do-metrics --no-do-visualization --start-frame 66

Autoregressive: every step feeds the model's own prediction back in, here
for 50 steps, with the SR term added and a separate output directory so the
teacher-forced run is kept:

.. code-block:: bash

   bppm-dem-sm ml-pipeline --no-do-metrics --no-do-visualization \
       --autoregressive --no-predict-until-end --max-steps 50 \
       --enabled --pred-out-dir data/interim/rnn_predictions_ar_sr

Metrics on existing predictions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Scores ``data_dir`` and, when present, ``pred_out_dir/pred_frames``:

.. code-block:: bash

   bppm-dem-sm ml-pipeline --no-do-predict --do-metrics --no-do-visualization \
       --pred-out-dir data/interim/rnn_predictions_ar_sr

Re-render figures only
~~~~~~~~~~~~~~~~~~~~~~

Reads whatever the earlier stages persisted; nothing is recomputed:

.. code-block:: bash

   bppm-dem-sm ml-pipeline --no-do-predict --no-do-metrics --do-visualization \
       --save-figures --no-show-plots

Launching a DEM simulation
--------------------------

``dem-sim`` runs the packaged YADE scenario as a subprocess and exits with
its return code. YADE must be installed and on ``PATH``:

.. code-block:: bash

   bppm-dem-sm dem-sim
   bppm-dem-sm dem-sim --yade-executable yade-2024.02a
   bppm-dem-sm dem-sim --script path/to/my_scenario.py

``--dem-backend blaze`` is accepted but exits with an error until the
BlazeDEM backend is implemented. The same launch is available as a pipeline
stage (``ml-pipeline --do-simulate``) and from Python -- see
:doc:`stages/simulation`.
