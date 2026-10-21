"""Periodic frame recording during a run, via CSV sphere dumps (YADE).

Every frame is one CSV with columns ``id, x, y, z, r, m, vx, vy, vz`` -- the
schema :mod:`pm_dem_sm.data_processing` converts to parquet.

The ``PyRunner`` command strings in :func:`start_frame_capture` and
:func:`start_recording` are evaluated
by YADE in the top-level running script's global namespace, so
``yade_dem/run_simulation.py`` must import this module unaliased
(``from . import capture``) for the name ``capture`` to resolve there.
"""

from __future__ import annotations

import csv
import os

from yade import Sphere
from yade.wrapper import O, PyRunner

from . import materials

# --- Module state ------------------------------------------------------------

# Runner state shared between start_frame_capture and the PyRunner hook.
_frameCaptureState = {}
# Runner state shared between start_recording and the PyRunner hook.
_recordingState = {}


# --- Public functions --------------------------------------------------------


def start_frame_capture(folder_name, interval, runner_label="frameCapture", iter_period=50):
    """Configure periodic CSV sphere dumps via PyRunner.

    Creates a folder named ``folder_name + str(O.dt) + "_"`` under the CWD and
    appends a runner that calls ``_save_sphere_frame``.

    Args:
        folder_name: Base name for the output folder (``O.dt`` is appended).
        interval: Simulation-time interval between CSV dumps (seconds).
        runner_label: Label for the ``PyRunner`` engine.
        iter_period: How often (in DEM iterations) the runner fires.

    Returns:
        list: The appended ``PyRunner`` engine(s).
    """
    folder_name = folder_name + str(O.dt) + "_"
    folder = os.path.join(os.getcwd(), folder_name)
    os.makedirs(folder, exist_ok=True)

    _frameCaptureState.clear()
    _frameCaptureState.update({
        "interval": float(interval),
        "next_save_time": float(O.time),
        "frame_id": 0,
        "folder": folder,
    })

    r = [PyRunner(command="capture._save_sphere_frame()", iterPeriod=int(iter_period), label=runner_label)]
    O.engines += r

    print(f"[FrameCapture] Saving spheres every {interval}s into: {folder}")
    return r


def start_recording(frames_dir, interval, index_path, runner_label="recorder"):
    """Write a frame CSV every ``interval`` seconds of simulated time, from now on.

    Frames go to ``frames_dir/frame_00000.csv``, ``frame_00001.csv``, ...;
    the first one is written on the next step. ``index_path`` gets one row
    per frame (``frame, time, iter``) so frame times are exact even though
    the runner fires on the first step past each period.

    Args:
        frames_dir: Output directory for frame CSVs (created if needed).
        interval: Simulated time between frames (s).
        index_path: CSV path for the frame-time index.
        runner_label: Label for the ``PyRunner`` engine.

    Returns:
        PyRunner: The appended runner.
    """
    os.makedirs(frames_dir, exist_ok=True)
    _recordingState.clear()
    _recordingState.update({"folder": str(frames_dir), "index": str(index_path), "frame_id": 0})
    with open(index_path, "w", newline="") as f:
        csv.writer(f).writerow(["frame", "time", "iter"])

    runner = PyRunner(command="capture._record_frame()", virtPeriod=float(interval),
                      initRun=True, label=runner_label)
    O.engines += [runner]
    print(f"[Recorder] Saving spheres every {interval}s into: {frames_dir}")
    return runner


def stop_recording(runner_label="recorder"):
    """Remove the recording ``PyRunner`` and return the number of frames written.

    Args:
        runner_label: Label used in :func:`start_recording`.

    Returns:
        int: Frames written since :func:`start_recording`.
    """
    O.engines = [e for e in O.engines if getattr(e, "label", None) != runner_label]
    return _recordingState.get("frame_id", 0)


# --- Private helper functions ------------------------------------------------


def _save_sphere_frame():
    """Write a sphere CSV once ``O.time`` reaches the next interval (``PyRunner`` hook).

    Uses module-level ``_frameCaptureState`` configured by
    :func:`start_frame_capture`. Advances ``frame_id`` and ``next_save_time``.
    """
    st = _frameCaptureState
    if not st:
        return

    t = O.time
    if t < st["next_save_time"]:
        return

    frame_id = st["frame_id"]
    _write_frame(os.path.join(st["folder"], f"frame_{frame_id:05d}.csv"))

    st["frame_id"] += 1
    st["next_save_time"] += st["interval"]


def _record_frame():
    """Write the next frame and its index row (``PyRunner`` hook for :func:`start_recording`)."""
    st = _recordingState
    if not st:
        return
    frame_id = st["frame_id"]
    _write_frame(os.path.join(st["folder"], f"frame_{frame_id:05d}.csv"))
    with open(st["index"], "a", newline="") as f:
        csv.writer(f).writerow([frame_id, repr(float(O.time)), int(O.iter)])
    st["frame_id"] += 1


def _write_frame(filename):
    """Write every sphere's id, position, radius, material label, and velocity to ``filename``.

    Args:
        filename: Output CSV path.
    """
    with open(filename, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id","x","y","z","r","m","vx","vy","vz"])

        for b in O.bodies:
            if not b:
                continue
            if not isinstance(getattr(b, "shape", None), Sphere):
                continue

            p = b.state.pos
            v = b.state.vel

            w.writerow([
                int(b.id),
                float(p[0]), float(p[1]), float(p[2]),
                float(b.shape.radius),
                materials._mat_label(b),
                float(v[0]), float(v[1]), float(v[2]),
            ])
