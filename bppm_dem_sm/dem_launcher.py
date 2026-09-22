"""Launches YADE DEM simulations as a subprocess from the normal Python environment.

YADE ships as its own patched Python interpreter (Boost.Python bindings baked
in) and cannot be imported into this package's TensorFlow/pandas venv --
that's why :mod:`bppm_dem_sm.simulation` and :mod:`bppm_dem_sm.sim_functions`
only run under ``yade``, never under this package's own interpreter. This
module never imports yade; it only shells out to the ``yade`` executable,
gated on it actually being installed on the workstation.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

DEFAULT_SIMULATION_SCRIPT = Path(__file__).resolve().parent / "simulation.py"


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
) -> subprocess.CompletedProcess:
    """Run a YADE simulation script as a subprocess.

    Args:
        script: Path to the YADE script to run; defaults to the packaged
            ``simulation.py`` (:data:`DEFAULT_SIMULATION_SCRIPT`).
        yade_executable: YADE executable name or path (default ``"yade"``).
        extra_args: Additional command-line arguments forwarded to ``yade``
            after the script path.

    Returns:
        subprocess.CompletedProcess: Result of the completed YADE run (check
        ``.returncode``; this function does not raise on a nonzero exit).

    Raises:
        FileNotFoundError: If ``yade_executable`` is not found on PATH.
    """
    resolved = find_yade_executable(yade_executable)
    if resolved is None:
        raise FileNotFoundError(
            f"YADE executable {yade_executable!r} not found on PATH. "
            "Install YADE and ensure it is on PATH to run DEM simulations."
        )

    script_path = Path(script) if script is not None else DEFAULT_SIMULATION_SCRIPT
    cmd = [resolved, str(script_path), *(extra_args or [])]
    print(f"Launching DEM simulation: {' '.join(cmd)}")
    return subprocess.run(cmd, check=False)
