"""Contact model, dt/damping, rotation, and force-balance settling (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.engines`'s public API.
"""

from __future__ import annotations

#: Mirrors :data:`bppm_dem_sm.simulation.yade_dem.engines.BALANCE_STATE`.
BALANCE_STATE = {
    "done": False,
    "threshold": 1e-3,
    "label": "balance_monitor",
    "last_unb": None,
}


def initialize_engines(contact_model, contact_model_params, rotation_engine=False):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.engines.initialize_engines`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def set_dt(new_dt=None, factor=0.3):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.engines.set_dt`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def set_gravity_damping(new_gravity_damping):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.engines.set_gravity_damping`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def run_until_forces_balanced(threshold=0.001, interval=1000, motion_start_steps=20, wait_chunk=1000, max_chunks=5000):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.engines.run_until_forces_balanced`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def rotate_mill_indefinitely(speed_rpm=9):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.engines.rotate_mill_indefinitely`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def rotate_mill_by_degrees(degrees, speed_rpm=9):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.engines.rotate_mill_by_degrees`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def rotate_mill_by_time(virtual_time_seconds, speed_rpm=9):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.engines.rotate_mill_by_time`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _get_rotation_engine(label="rotation_engine"):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    ``bppm_dem_sm.simulation.yade_dem.engines._get_rotation_engine``.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _balance_check():
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    ``bppm_dem_sm.simulation.yade_dem.engines._balance_check``.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")
