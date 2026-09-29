"""Mill geometry helpers (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.stl`'s public API.
"""

from __future__ import annotations

SAG_MILL_SLICE_BODY_GROUP = None


def initialize_sag_mill_slice(sagmill_stl_path):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.stl.initialize_sag_mill_slice`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def createBox(x, y, z):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.stl.createBox`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def createFunnel(x, y, z, fx, fy, dy):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.stl.createFunnel`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def chord_box_3d(diameter, y, box_height, depth):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.stl.chord_box_3d`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def get_surface_y(padding=0.1):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.stl.get_surface_y`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _obtain_sag_mill_slice_measurements(sag_mill_body_group):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.stl._obtain_sag_mill_slice_measurements`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _add_sag_mill_slice_caps(sag_mill_slice_body_group, sag_mill_slice_radius_m, z_min, z_max):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.stl._add_sag_mill_slice_caps`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")
