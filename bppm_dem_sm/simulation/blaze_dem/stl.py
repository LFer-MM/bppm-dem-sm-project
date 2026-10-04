"""Mill geometry helpers (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.stl`'s public API.
"""

from __future__ import annotations

#: Mirrors :data:`bppm_dem_sm.simulation.yade_dem.stl.SAG_MILL_SLICE_BODY_GROUP`.
SAG_MILL_SLICE_BODY_GROUP = None


def initialize_sag_mill_slice(sagmill_stl_path):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.stl.initialize_sag_mill_slice`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def createBox(x, y, z):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.stl.createBox`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def createFunnel(x, y, z, fx, fy, dy):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.stl.createFunnel`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def chord_box_3d(diameter, y, box_height, depth):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.stl.chord_box_3d`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def get_surface_y(padding=0.1):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.stl.get_surface_y`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _obtain_sag_mill_slice_measurements(sag_mill_body_group):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    ``bppm_dem_sm.simulation.yade_dem.stl._obtain_sag_mill_slice_measurements``.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _add_sag_mill_slice_caps(sag_mill_slice_body_group, sag_mill_slice_radius_m, z_min, z_max):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    ``bppm_dem_sm.simulation.yade_dem.stl._add_sag_mill_slice_caps``.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")
