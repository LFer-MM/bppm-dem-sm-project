Bidisperse Polyhedrical Particle Mixing DEM Surrogate Model
===========================================================

Surrogate modeling for **bidisperse particle mixing** in a DEM SAG-mill
slice (YADE implemented; BlazeDEM a placeholder backend): train a GRU on
particle frame sequences, roll out predictions, score mixing with the Lacey
index, and render animations / cell-grid views.

You typically drive the stack with the ``bppm-dem-sm`` CLI (or by importing
``run_experiment_pipeline`` / ``ExperimentConfig`` in Python). The pages
below document that **Python library surface**—not an HTTP/REST service.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   examples
   api
   docstring_style
