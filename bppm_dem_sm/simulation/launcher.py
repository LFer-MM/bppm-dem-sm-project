"""Launches a DEM simulation as a subprocess from the normal Python environment.

Shared across DEM backends -- it dispatches on ``backend`` but never imports
either backend's own Python API itself. YADE ships as its own patched Python
interpreter (Boost.Python bindings baked in) and cannot be imported into this
package's TensorFlow/pandas venv -- that's why
:mod:`bppm_dem_sm.simulation.yade_dem` only runs under ``yade``, never under
this package's own interpreter. This module never imports yade (or a future
BlazeDEM binding); it only shells out to the backend's executable, gated on
it actually being installed on the workstation.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

DEFAULT_SIMULATION_SCRIPTS = {
    "yade": Path(__file__).resolve().parent / "yade_dem" / "run_simulation.py",
    "blaze": Path(__file__).resolve().parent / "blaze_dem" / "run_simulation.py",
}
DEFAULT_SIMULATION_SCRIPT = DEFAULT_SIMULATION_SCRIPTS["yade"]


def find_yade_executable(name: str = "yade") -> str | None:
    """Locate the YADE executable on PATH.

    Args:
        name: Executable name to search for (e.g. a version-suffixed build
            like ``"yade-2024.02a"``).

    Returns:
        str or None: Absolute path to the executable, or ``None`` if not found.
    """
    return shutil.which(name)


def launch_simulation(
    script: Path | str | None = None,
    yade_executable: str = "yade",
    extra_args: list[str] | None = None,
    backend: str = "yade",
) -> subprocess.CompletedProcess:
    """Run a DEM simulation script as a subprocess.

    Args:
        script: Path to the script to run; defaults to the packaged
            ``run_simulation.py`` for ``backend``
            (:data:`DEFAULT_SIMULATION_SCRIPTS`).
        yade_executable: YADE executable name or path (default ``"yade"``);
            only used when ``backend == "yade"``.
        extra_args: Additional command-line arguments forwarded to the
            executable after the script path.
        backend: Which DEM backend to launch -- ``"yade"`` (implemented) or
            ``"blaze"`` (not yet implemented; raises ``NotImplementedError``).

    Returns:
        subprocess.CompletedProcess: Result of the completed DEM run (check
        ``.returncode``; this function does not raise on a nonzero exit).

    Raises:
        FileNotFoundError: If ``yade_executable`` is not found on PATH.
        NotImplementedError: If ``backend`` is not ``"yade"`` -- BlazeDEM's
            launch mechanism (executable name, invocation style) isn't
            decided yet; see :mod:`bppm_dem_sm.simulation.blaze_dem`.
    """
    if backend != "yade":
        raise NotImplementedError(
            f"DEM backend {backend!r} not yet implemented in launch_simulation() "
            "-- only 'yade' can be launched today."
        )

    resolved = find_yade_executable(yade_executable)
    if resolved is None:
        raise FileNotFoundError(
            f"YADE executable {yade_executable!r} not found on PATH. "
            "Install YADE and ensure it is on PATH to run DEM simulations."
        )

    script_path = Path(script) if script is not None else DEFAULT_SIMULATION_SCRIPTS[backend]
    cmd = [resolved, str(script_path), *(extra_args or [])]
    print(f"Launching DEM simulation: {' '.join(cmd)}")
    return subprocess.run(cmd, check=False)
