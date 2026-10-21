"""Mill-state log and steady-state detection during a run (YADE).

A ``PyRunner`` appends one row to ``mill_log.csv`` every monitor interval
(``revolutions`` counts from the start of the current stage):
the charge centre-of-mass angle (all particles and per species), kinetic
energy, the torque the charge exerts on the mill and the matching drive
power, and the largest sphere-sphere overlap. Spin-up uses the in-memory
copy of that log to decide when the charge has reached steady state.

Angles are measured from straight down (``-Y``), positive toward ``+X``: a
mill turning counter-clockwise seen from ``+Z`` lifts its charge to positive
angles.

The ``PyRunner`` command string below is evaluated by YADE in the top-level
running script's global namespace, so ``yade_dem/run_simulation.py`` must
import this module unaliased (``from ... import monitor``).
"""

from __future__ import annotations

import csv
import math

from yade import Sphere
from yade.utils import kineticEnergy, unbalancedForce
from yade.wrapper import O, PyRunner

# --- Constants ---------------------------------------------------------------

#: Columns of ``mill_log.csv``, in order.
LOG_COLUMNS = [
    "time", "iter", "stage", "revolutions", "angle_all_deg", "angle_small_deg",
    "angle_large_deg", "kinetic_J", "torque_Nm", "power_kW", "max_overlap_rel",
    "unbalanced",
]


# --- Module state ------------------------------------------------------------

#: Monitor configuration and the in-memory log rows.
MONITOR_STATE = {"rows": []}


# --- Public functions --------------------------------------------------------


def start_monitor(log_path, interval, mill_ids, r_split, omega, stage, runner_label="monitor"):
    """Append a ``PyRunner`` that logs the mill state every ``interval`` seconds.

    Appends to ``log_path`` if it exists (resumed runs keep one log).

    Args:
        log_path: CSV path of the mill log.
        interval: Simulated time between rows (s).
        mill_ids: Body ids of the mill liner and end walls.
        r_split: Radius threshold separating small from large spheres (m).
        omega: Mill angular velocity (rad/s); converts torque to power.
        stage: Stage name written in the ``stage`` column.
        runner_label: Label for the ``PyRunner`` engine.

    Returns:
        PyRunner: The appended runner.
    """
    stop_monitor(runner_label)
    MONITOR_STATE.update({
        "path": str(log_path), "mill_ids": list(mill_ids), "r_split": float(r_split),
        "omega": float(omega), "stage": stage, "rows": [], "t0": float(O.time),
    })
    try:
        with open(log_path, newline="") as f:
            has_header = bool(f.readline())
    except FileNotFoundError:
        has_header = False
    if not has_header:
        with open(log_path, "w", newline="") as f:
            csv.writer(f).writerow(LOG_COLUMNS)

    runner = PyRunner(command="monitor._log_row()", virtPeriod=float(interval),
                      initRun=True, label=runner_label)
    O.engines += [runner]
    return runner


def set_stage(stage, omega=None):
    """Change the stage name (and optionally the mill speed) written to the log.

    Args:
        stage: Stage name for subsequent rows.
        omega: New mill angular velocity (rad/s), or ``None`` to keep it.
    """
    MONITOR_STATE["stage"] = stage
    if omega is not None:
        MONITOR_STATE["omega"] = float(omega)
    MONITOR_STATE["rows"] = []
    MONITOR_STATE["t0"] = float(O.time)


def stop_monitor(runner_label="monitor"):
    """Remove the monitor ``PyRunner`` if present.

    Args:
        runner_label: Label used in :func:`start_monitor`.
    """
    O.engines = [e for e in O.engines if getattr(e, "label", None) != runner_label]


def steady_state(window_s, angle_tol_deg, power_rel_tol):
    """Compare the last two ``window_s`` windows of the current stage's log.

    Args:
        window_s: Length of each window (s).
        angle_tol_deg: Allowed change of mean charge angle (deg).
        power_rel_tol: Allowed relative change of mean power.

    Returns:
        dict | None: ``None`` until two full windows exist; otherwise the
        window means and ``steady`` (bool).
    """
    rows = MONITOR_STATE["rows"]
    if not rows or rows[-1]["time"] - rows[0]["time"] < 2 * window_s:
        return None
    t_end = rows[-1]["time"]
    last = [r for r in rows if r["time"] > t_end - window_s]
    prev = [r for r in rows if t_end - 2 * window_s < r["time"] <= t_end - window_s]
    if not last or not prev:
        return None
    a1, a0 = _mean(last, "angle_all_deg"), _mean(prev, "angle_all_deg")
    p1, p0 = _mean(last, "power_kW"), _mean(prev, "power_kW")
    d_power = abs(p1 - p0) / max(abs(p0), 1e-9)
    return {
        "time": t_end, "angle_deg": a1, "angle_change_deg": a1 - a0, "power_kW": p1,
        "power_rel_change": d_power,
        "steady": abs(a1 - a0) < angle_tol_deg and d_power < power_rel_tol,
    }


def charge_angles(r_split):
    """Return the charge centre-of-mass angle of all, small, and large spheres (deg).

    Args:
        r_split: Radius threshold separating small from large spheres (m).

    Returns:
        tuple[float, float, float]: ``(all, small, large)``; ``nan`` for an
        empty group.
    """
    sums = {"all": [0.0, 0.0, 0.0], "small": [0.0, 0.0, 0.0], "large": [0.0, 0.0, 0.0]}
    for b in O.bodies:
        if not b or not isinstance(b.shape, Sphere):
            continue
        m, p = b.state.mass, b.state.pos
        group = "small" if b.shape.radius < r_split else "large"
        for key in ("all", group):
            s = sums[key]
            s[0] += m * p[0]
            s[1] += m * p[1]
            s[2] += m
    return tuple(
        math.degrees(math.atan2(s[0], -s[1])) if s[2] else float("nan")
        for s in (sums["all"], sums["small"], sums["large"])
    )


def mill_torque(mill_ids):
    """Return the Z torque the particles exert on the mill about its axis (N m).

    Args:
        mill_ids: Body ids of the mill liner and end walls.

    Returns:
        float: Torque about ``+Z`` through the origin.
    """
    tz = 0.0
    for i in mill_ids:
        f = O.forces.f(i)
        p = O.bodies[i].state.pos
        tz += p[0] * f[1] - p[1] * f[0] + O.forces.t(i)[2]
    return tz


def max_overlap():
    """Return the largest sphere-sphere penetration depth relative to the smaller radius."""
    worst = 0.0
    for i in O.interactions:
        if not i.isReal:
            continue
        s1, s2 = O.bodies[i.id1].shape, O.bodies[i.id2].shape
        if not isinstance(s1, Sphere) or not isinstance(s2, Sphere):
            continue
        worst = max(worst, i.geom.penetrationDepth / min(s1.radius, s2.radius))
    return worst


# --- Private helper functions ------------------------------------------------


def _log_row():
    """Append one mill-state row to the log (``PyRunner`` hook)."""
    st = MONITOR_STATE
    if "path" not in st:
        return
    a_all, a_small, a_large = charge_angles(st["r_split"])
    torque = mill_torque(st["mill_ids"])
    omega = st["omega"]
    row = {
        "time": float(O.time),
        "iter": int(O.iter),
        "stage": st["stage"],
        "revolutions": (float(O.time) - st["t0"]) * abs(omega) / (2 * math.pi),
        "angle_all_deg": a_all,
        "angle_small_deg": a_small,
        "angle_large_deg": a_large,
        "kinetic_J": kineticEnergy(),
        "torque_Nm": torque,
        # The drive supplies the opposite of the charge's torque on the mill.
        "power_kW": -torque * omega / 1000.0,
        "max_overlap_rel": max_overlap(),
        "unbalanced": unbalancedForce(),
    }
    st["rows"].append(row)
    with open(st["path"], "a", newline="") as f:
        csv.writer(f).writerow([row[c] for c in LOG_COLUMNS])


def _mean(rows, key):
    """Return the mean of ``key`` over ``rows``."""
    return sum(r[key] for r in rows) / len(rows)
