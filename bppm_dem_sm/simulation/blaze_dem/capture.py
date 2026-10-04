"""Periodic frame recording during a run (BlazeDEM placeholder).

Mirrors :mod:`bppm_dem_sm.simulation.yade_dem.capture`'s public API.
"""

from __future__ import annotations

# Mirrors the YADE backend's runner state; unused until implemented.
_frameCaptureState = {}


def start_frame_capture(folder_name, interval, runner_label="frameCapture", iter_period=50):
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.capture.start_frame_capture`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


def _save_sphere_frame():
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    ``bppm_dem_sm.simulation.yade_dem.capture._save_sphere_frame``.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")
