"""Save/load particle positions, and settle-then-save (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.state`'s public API.
"""

from __future__ import annotations


def save_particle_positions(csv_path, include_velocity=True, include_ang_vel=True):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.state.save_particle_positions`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def load_particle_positions(csv_path, *, set_vel_zero=True, set_ang_vel_zero=True):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.state.load_particle_positions`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def settle_balance_save(gravity_damping, csv_path):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.state.settle_balance_save`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")
