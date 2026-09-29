"""Post-hoc analysis of parquet frames: Lacey index, segregation, velocity, computing speed.

Only computation lives here; the matching plots are in
:mod:`bppm_dem_sm.visualization.metrics_plots`. Every result
``run_metrics.compute_metrics``/``computing_speed.compute_computing_speed``
return is also persisted to disk, and ``run_metrics.load_metrics`` /
``computing_speed.load_computing_speed`` read it back -- so
``do_visualization`` can render these plots without ``do_metrics`` having
just run in the same process.
"""
