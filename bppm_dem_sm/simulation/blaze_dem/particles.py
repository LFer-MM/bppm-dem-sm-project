"""Particle loading and ingress (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.particles`'s public API.
"""

from __future__ import annotations


def load_rock_particles(rock_diam_m, rock_count):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.particles.load_rock_particles`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def load_ball_particles(ball_diam_m, ball_count):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.particles.load_ball_particles`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def load_all_particles(particle_diam_m, particle_count):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.particles.load_all_particles`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def ingress_random(diameter, depth, r_small, r_large, n_small, n_large, box_height,
                   material_small, material_large, color_small, color_large,
                   settle_steps=10000, padding=0.1, verbose=True):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.particles.ingress_random`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def ingress_segregated(diameter, depth, r_small, r_large, n_small, n_large, box_height,
                       material_small, material_large, color_small, color_large,
                       settle_steps=10000, padding=0.1, verbose=True):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.particles.ingress_segregated`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")
