DEM simulation
==============

The DEM scenario runs under YADE's own Python interpreter, which cannot be
imported into this package's environment.
:func:`~bppm_dem_sm.simulation.launcher.launch_simulation` therefore starts
it as a subprocess; this is what ``bppm-dem-sm dem-sim`` and
``do_simulate`` call.

Launching the packaged scenario
-------------------------------

.. code-block:: python

   from bppm_dem_sm.simulation.launcher import find_yade_executable, launch_simulation

   if find_yade_executable() is None:
       raise SystemExit("Install YADE and put it on PATH first.")

   result = launch_simulation(backend="yade")
   print(result.returncode)  # nonzero exit codes are returned, not raised

Other scripts, executables, and arguments
-----------------------------------------

.. code-block:: python

   launch_simulation(
       script="path/to/my_scenario.py",  # default: simulation/yade_dem/run_simulation.py
       yade_executable="yade-2024.02a",  # name on PATH or a full path
       extra_args=["-j", "4"],           # passed to the executable after the script path
   )

``FileNotFoundError`` is raised when the executable is not on ``PATH``.

As a pipeline stage
-------------------

.. code-block:: python

   from bppm_dem_sm import run_experiment_pipeline

   results = run_experiment_pipeline(
       do_simulate=True, do_predict=False, do_metrics=False, do_visualization=False
   )
   print(results["dem_simulation"].returncode)

Particle counts, diameters, materials, and mill geometry are module
constants in :mod:`bppm_dem_sm.config` (``ROCK_COUNT``, ``BALL_COUNT``,
``MILL_DIAMETER_M``, ``SAGMILL_STL_PATH``, ...), not ``ExperimentConfig``
fields: edit them there.

Backends
--------

``backend="yade"`` is the only implemented backend. ``backend="blaze"``
(:mod:`bppm_dem_sm.simulation.blaze_dem`) is a placeholder and raises
``NotImplementedError``.
