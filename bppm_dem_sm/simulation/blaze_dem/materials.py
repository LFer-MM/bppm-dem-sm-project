"""Steel/rock material definitions and per-body material labeling (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.materials`'s public API.
"""

from __future__ import annotations

MATERIALS_MAP = {}


def initialize_simulation_materials(materials):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.materials.initialize_simulation_materials`.

    Raises:
        NotImplementedError: Always -- BlazeDEM backend not yet implemented.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _mat_label(b):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.materials._mat_label`.

    Raises:
        NotImplementedError: Always -- BlazeDEM backend not yet implemented.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")
