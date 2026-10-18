"""DEM simulation: mill setup, materials, ingress, and rotation -- backend-selectable.

Two backends, same shape: :mod:`bppm_dem_sm.simulation.yade_dem` (YADE,
implemented) and :mod:`bppm_dem_sm.simulation.blaze_dem` (BlazeDEM,
placeholder -- every function raises ``NotImplementedError``). Which one runs
is :class:`bppm_dem_sm.config.ExperimentConfig`'s ``dem_backend`` field.

Everything inside a backend subpackage runs inside that engine's own
(possibly embedded/patched) Python interpreter. The top-level modules are
stdlib-only and import on both sides: ``scenario`` (the JSON-backed run
definition and its sanity checks), ``mill_geometry`` (parametric shell and
lifter triangles), and ``launcher``, which shells out to the engine's
executable and never imports its Python API.
"""
