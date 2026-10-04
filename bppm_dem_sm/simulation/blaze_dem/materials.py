"""Steel/rock material definitions and per-body material labeling (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.materials`'s public API.
"""

from __future__ import annotations

#: Mirrors :data:`bppm_dem_sm.simulation.yade_dem.materials.MATERIALS_MAP`.
MATERIALS_MAP = {}


def initialize_simulation_materials(materials):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.materials.initialize_simulation_materials`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _mat_label(b):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    ``bppm_dem_sm.simulation.yade_dem.materials._mat_label``.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")
