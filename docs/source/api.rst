Python API reference
====================

Autodoc for the ``bppm_dem_sm`` package. This is the **callable Python
interface** (importable modules, classes, and functions). The CLI
``bppm-pipeline`` is a thin wrapper around the same code—especially
:class:`~bppm_dem_sm.config.PipelineConfig` and
:func:`~bppm_dem_sm.pipeline.run_pipeline`.

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

.. automodule:: bppm_dem_sm.pipeline
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.tf_quiet
   :members:
   :show-inheritance:

Data processing
---------------

.. automodule:: bppm_dem_sm.data_processing.frames
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.data_processing.csv_to_parquet
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.data_processing.integrity
   :members:
   :show-inheritance:

Model training and prediction
-----------------------------

.. automodule:: bppm_dem_sm.model.training
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.model.prediction
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.model.stochastic_motion
   :members:
   :show-inheritance:

Metrics
-------

.. automodule:: bppm_dem_sm.metrics.lacey_mixing_index
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.metrics.segregation_profile
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.metrics.velocity_metrics
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.metrics.run_metrics
   :members:
   :show-inheritance:

Visualization
-------------

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

DEM simulation (YADE)
---------------------

.. automodule:: bppm_dem_sm.simulation.simulation
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.simulation.sim_functions
   :members:
   :show-inheritance:

.. automodule:: bppm_dem_sm.simulation.launcher
   :members:
   :show-inheritance:
