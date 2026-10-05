Python: stage by stage
======================

Each pipeline stage is a plain function you can call on its own. Most take
an :class:`~bppm_dem_sm.config.ExperimentConfig` for their paths and
settings; the lower-level helpers on these pages take arrays, DataFrames, or
paths directly, so they also work on frames this pipeline did not produce.

Frames are parquet tables with one row per particle and at least ``id``,
``x``, ``y``, ``z``, ``r`` columns, one file per time step
(``frame_00000.parquet``, ...).

One page per subpackage, matching :doc:`../../api`:

.. toctree::
   :maxdepth: 1

   data_processing
   model
   sr
   metrics
   visualization
   simulation
