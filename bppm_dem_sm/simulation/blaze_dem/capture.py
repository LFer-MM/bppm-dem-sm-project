"""Periodic frame recording during a run (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.capture`'s public API.
"""

from __future__ import annotations

_frameCaptureState = {}


def start_frame_capture(folder_name, interval, runner_label="frameCapture", iter_period=50):
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.capture.start_frame_capture`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _save_sphere_frame():
    """Placeholder -- see :func:`bppm_dem_sm.simulation.yade_dem.capture._save_sphere_frame`."""
    raise NotImplementedError("BlazeDEM backend not yet implemented")
