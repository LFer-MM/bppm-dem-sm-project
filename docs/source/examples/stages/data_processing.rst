Data processing
===============

:mod:`bppm_dem_sm.data_processing` turns raw DEM CSV dumps into parquet
frames and parquet frames into a supervised dataset for the GRU.

CSV to parquet, with an integrity check
---------------------------------------

The pipeline's ``do_process`` stage, on its own. Converts every CSV in
``raw_data_dir`` into ``data_dir``, then checks the particle inventory:

.. code-block:: python

   from pathlib import Path
   from bppm_dem_sm import ExperimentConfig
   from bppm_dem_sm.data_processing.run_data_processing import process_frames

   cfg = ExperimentConfig(
       raw_data_dir=Path("data/raw/sic_csv_frames"),
       data_dir=Path("data/processed/sic_dataset_20s_dt0p0001_parquet"),
   )
   result = process_frames(cfg)
   report = result["integrity_report"]

Or call the two steps directly:

.. code-block:: python

   from bppm_dem_sm.data_processing.convert import convert_folder_csv_to_parquet
   from bppm_dem_sm.data_processing.integrity import report_particle_integrity

   convert_folder_csv_to_parquet(
       "data/raw/sic_csv_frames",
       "data/processed/sic_dataset_20s_dt0p0001_parquet",
   )
   report = report_particle_integrity("data/processed/sic_dataset_20s_dt0p0001_parquet")

``report`` has one row per file and one column per distinct radius, holding
particle counts. A healthy bidisperse export has the same inventory in every
frame:

.. code-block:: python

   print(report.std())  # ~0 for every radius

Loading frames
--------------

.. code-block:: python

   from bppm_dem_sm.data_processing import frames as data_io

   paths = data_io.sorted_frame_files(
       "data/processed/sic_dataset_20s_dt0p0001_parquet", "frame_*.parquet"
   )
   df = data_io.load_frame(paths[0], ["id", "x", "y", "z", "r"])

``sorted_frame_files`` sorts by file name, so zero-padded frame indices keep
time order. ``load_frame`` sorts rows by ``id``, so ``id`` must be among the
requested columns.

Building the supervised dataset
-------------------------------

What ``train_and_save`` does before fitting: stack every frame, cut sliding
windows of ``frames_in`` steps, and split off a validation set.

.. code-block:: python

   from bppm_dem_sm.config import FEATURE_COLS
   from bppm_dem_sm.data_processing import dataset as data_ds
   from bppm_dem_sm.data_processing import frames as data_io

   pos, rad, ids = data_io.load_frames_stacked(
       "data/processed/sic_training_dataset_3s_4s_parquet",
       pattern="frame_*.parquet",
       feature_cols=FEATURE_COLS,
   )
   # pos: (T, N, 3)   rad: (T, N, 1)   ids: (N,)

   X, y = data_ds.build_supervised_dataset(pos, rad, frames_in=15)
   # X: ((T - 15) * N, 15, 4) windows of x, y, z, r
   # y: ((T - 15) * N, 3)     the next x, y, z

   X_train, y_train, X_val, y_val = data_ds.train_test_split(X, y, val_fraction=0.1, seed=0)
