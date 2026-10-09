Stochastic random (SR) term
===========================

:mod:`bppm_dem_sm.model.sr` implements the SR half of the extended-RNNSR
method (Kishida et al., 2025). The GRU predicts each particle's local mean
motion; the SR term adds the local velocity fluctuation around it. A
per-cell velocity standard deviation sigma_v(x) is estimated once from
reference DEM frames, then sampled as N(0, sigma_v(x)^2) per axis at every
prediction step.

Enabling it in prediction
-------------------------

Usually all you need -- ``predict_frames`` builds the field from
``train_data_dir`` and adds a draw to every predicted position:

.. code-block:: python

   from bppm_dem_sm import ExperimentConfig
   from bppm_dem_sm.config import StochasticOptions
   from bppm_dem_sm.model.rnn.prediction import predict_frames

   cfg = ExperimentConfig(
       stochastic=StochasticOptions(enabled=True, stochastic_seed=0),
   ).with_overrides(autoregressive=True)
   preds = predict_frames(cfg)

From the CLI: ``bppm-dem-sm ml-pipeline --enabled --autoregressive``. The
same ``stochastic_seed`` gives the same draws.

Building the sigma_v(x) field
-----------------------------

From the config -- ``train_data_dir`` and the ``stochastic`` cell settings:

.. code-block:: python

   from bppm_dem_sm.model.sr import build_velocity_std_field_from_config

   field = build_velocity_std_field_from_config(cfg)
   print(len(field.sigma_by_cell), "cells with a sigma_v")

Or from any directory of frames that share particle ids:

.. code-block:: python

   from bppm_dem_sm.model.sr import build_velocity_std_field

   field = build_velocity_std_field(
       "data/processed/sic_training_dataset_3s_4s_parquet",
       "frame_*.parquet",
       cell_size=0.5588,        # 4 x large-particle diameter
       min_particles_per_cell=15,
   )

Each particle's DEM velocity (the ``vx``, ``vy``, ``vz`` columns) is binned
by position and pooled over all frames per cell, and sigma_v is the
standard deviation of each velocity component (paper Eq. 2), so it is a
3-vector per cell. Large and small particles share one field. Cells with fewer than ``min_particles_per_cell`` observations get
sigma_v = 0, i.e. no added noise.

.. note::

   ``velocity_cell_size`` (0.5588 m, ``4 x BALL_DIAM_M``) is deliberately
   not the Lacey cell size (0.44 m, ``0.04 x MILL_DIAMETER_M``); see
   :class:`~bppm_dem_sm.config.StochasticOptions`. Both grids can be drawn
   with :func:`~bppm_dem_sm.visualization.cell_grid.plot_particles_with_grid`
   -- see :doc:`visualization`.

Sampling a displacement
-----------------------

What ``predict_frames`` adds at each step, for any ``(N, 3)`` positions:

.. code-block:: python

   import numpy as np
   from bppm_dem_sm.data_processing import frames as data_io
   from bppm_dem_sm.model.sr import sample_stochastic_displacement

   paths = data_io.sorted_frame_files("data/processed/sic_dataset_20s_dt0p0001_parquet")
   df = data_io.load_frame(paths[0], ["id", "x", "y", "z"])  # rows sorted by id
   pos = df[["x", "y", "z"]].to_numpy(np.float32)

   rng = np.random.default_rng(0)
   sigma = field.sigma_at(pos)  # (N, 3) per-axis sigma_v at each particle's cell
   disp = sample_stochastic_displacement(pos, field, dt_rnn=0.05, rng=rng)  # (N, 3)
   new_pos = pos + disp  # in the pipeline: GRU prediction + disp
