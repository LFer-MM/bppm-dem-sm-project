Python API reference
====================

Autodoc for the ``bppm_dem_sm`` package. This is the **callable Python
interface** (importable modules, classes, and functions). The CLI
``bppm-dem-sm ml-pipeline`` is a thin wrapper around the same code—especially
:class:`~bppm_dem_sm.config.ExperimentConfig` and
:func:`~bppm_dem_sm.experiment_pipeline.run_experiment_pipeline`.

Package overview
----------------

.. automodule:: bppm_dem_sm
   :no-members:

Configuration and CLI
---------------------

.. automodule:: bppm_dem_sm.config
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.cli
   :members:
   :show-inheritance:

Pipeline orchestration
----------------------

.. automodule:: bppm_dem_sm.experiment_pipeline
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.progress
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.tf_quiet
   :members:
   :show-inheritance:

Data processing
---------------

.. automodule:: bppm_dem_sm.data_processing
   :no-members:

.. automodule:: bppm_dem_sm.data_processing.frames
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.data_processing.dataset
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.data_processing.binning
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.data_processing.convert
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.data_processing.integrity
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.data_processing.run_data_processing
   :members:
   :show-inheritance:

Model training and prediction
-----------------------------

.. automodule:: bppm_dem_sm.model
   :no-members:

.. automodule:: bppm_dem_sm.model.rnn
   :no-members:

.. automodule:: bppm_dem_sm.model.rnn.architecture
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.model.rnn.training
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.model.rnn.loading
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.model.rnn.prediction
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.model.sr
   :members:
   :show-inheritance:

Metrics
-------

.. automodule:: bppm_dem_sm.metrics
   :no-members:

.. automodule:: bppm_dem_sm.metrics.lacey_mixing_index
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.metrics.segregation_profile
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.metrics.velocity_metrics
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.metrics.computing_speed
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.metrics.run_metrics
   :members:
   :show-inheritance:

Visualization
-------------

.. automodule:: bppm_dem_sm.visualization
   :no-members:

.. automodule:: bppm_dem_sm.visualization.animate_particles
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.visualization.cell_grid
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.visualization.run_visualization
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.visualization.training_curves
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.visualization.metrics_plots
   :members:
   :show-inheritance:

DEM simulation
--------------

.. automodule:: bppm_dem_sm.simulation
   :no-members:

.. automodule:: bppm_dem_sm.simulation.launcher
   :members:
   :show-inheritance:

YADE backend
~~~~~~~~~~~~

.. automodule:: bppm_dem_sm.simulation.yade_dem
   :no-members:

.. automodule:: bppm_dem_sm.simulation.yade_dem.run_simulation
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.simulation.yade_dem.materials
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.simulation.yade_dem.stl
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.simulation.yade_dem.engines
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.simulation.yade_dem.particles
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.simulation.yade_dem.state
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.simulation.yade_dem.capture
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.simulation.yade_dem.diagnostics
   :members:
   :show-inheritance:

BlazeDEM backend (placeholder)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not implemented yet -- every function raises ``NotImplementedError``. See
:mod:`bppm_dem_sm.simulation.blaze_dem`.

.. automodule:: bppm_dem_sm.simulation.blaze_dem
   :no-members:
