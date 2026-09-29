"""Periodic frame recording during a run, via CSV sphere dumps (YADE).

The ``PyRunner`` command string in :func:`start_frame_capture` is evaluated
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

_frameCaptureState = {}


def start_frame_capture(folder_name, interval, runner_label="frameCapture", iter_period=50):
    """Configure periodic CSV sphere dumps via PyRunner.

    Creates a folder named ``folder_name + str(O.dt) + "_"`` under the CWD and
    appends a runner that calls :func:`_save_sphere_frame`.

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


def _save_sphere_frame():
    """PyRunner: write sphere CSV when ``O.time`` reaches the next interval.

    Uses module-level ``_frameCaptureState`` configured by
    :func:`start_frame_capture`. Advances ``frame_id`` and ``next_save_time``.
    """
    print("Checking at time:", O.time)

    st = _frameCaptureState
    if not st:
        return

    t = O.time
    if t < st["next_save_time"]:
        return

    frame_id = st["frame_id"]
    folder = st["folder"]
    filename = os.path.join(folder, f"frame_{frame_id:05d}.csv")

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

    st["frame_id"] += 1
    st["next_save_time"] += st["interval"]
