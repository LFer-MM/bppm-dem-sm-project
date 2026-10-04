"""Overlap checks and particle inventory counting (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.diagnostics`'s public API.
"""

from __future__ import annotations


def check_overlaps():
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.diagnostics.check_overlaps`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def get_particle_inventory(r_small, r_large, tol=1e-6, verbose=True):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.diagnostics.get_particle_inventory`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")
