"""DEM simulation: mill setup, materials, ingress, and rotation -- backend-selectable.

Two backends, same shape: :mod:`bppm_dem_sm.simulation.yade_dem` (YADE,
implemented) and :mod:`bppm_dem_sm.simulation.blaze_dem` (BlazeDEM,
placeholder -- every function raises ``NotImplementedError``). Which one runs
is :class:`bppm_dem_sm.config.ExperimentConfig`'s ``dem_backend`` field.

Everything inside a backend subpackage runs inside that engine's own
(possibly embedded/patched) Python interpreter, or shells out to it
(``launcher``); nothing in this ``simulation`` package is importable from the
plain TensorFlow/pandas venv side except ``launcher``, which never imports a
DEM engine's own Python API itself.
"""
