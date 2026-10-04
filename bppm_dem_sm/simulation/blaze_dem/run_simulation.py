"""BlazeDEM scenario orchestrator (placeholder).

Mirrors :func:`bppm_dem_sm.simulation.yade_dem.run_simulation.run`'s shape.
"""

from __future__ import annotations

# --- Public functions --------------------------------------------------------


def run():
    """Raise ``NotImplementedError`` (BlazeDEM placeholder).

    Reserves the signature of
    :func:`bppm_dem_sm.simulation.yade_dem.run_simulation.run`.

    Raises:
        NotImplementedError: Always; the BlazeDEM backend is not implemented yet.
    """
    raise NotImplementedError("BlazeDEM backend not yet implemented")


# --- Script entry point ------------------------------------------------------

if __name__ == "__main__":
    run()
