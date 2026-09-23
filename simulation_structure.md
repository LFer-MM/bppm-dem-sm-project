# Simulation Section — Structure

Overview of the `simulation` subpackage (`bppm_dem_sm/simulation/`) and its
tests (`tests/simulation/`). This is the DEM (YADE) side of the project: the
part of the codebase that sets up, runs, and drives the discrete-element
mill simulation, as opposed to the data-processing/model/metrics packages
that run under the plain TensorFlow/pandas environment.

## Package boundary: two Python interpreters

The subpackage docstring (`bppm_dem_sm/simulation/__init__.py`) spells out
the key constraint that shapes this whole section:

> Everything here runs inside YADE's embedded Python interpreter
> (`simulation`, `sim_functions`) or shells out to it (`launcher`); nothing
> in this subpackage is importable from the plain TensorFlow/pandas venv
> side except `launcher`, which never imports yade itself.

So the three modules split cleanly along that boundary:

| Module | Runs under | Role |
|---|---|---|
| `launcher.py` | normal project venv | Shells out to the `yade` executable as a subprocess |
| `simulation.py` | YADE's embedded interpreter | Entry-point script: builds the mill scene and starts ingress |
| `sim_functions.py` | YADE's embedded interpreter | Library of simulation primitives used by `simulation.py` |

## Module breakdown

### `launcher.py` (65 lines)
Bridges the normal Python venv to the YADE executable. Never imports `yade`.

- `DEFAULT_SIMULATION_SCRIPT` — path constant pointing at the packaged `simulation.py`
- `find_yade_executable(name="yade")` — locates the YADE executable on `PATH`
- `launch_simulation(script, yade_executable, extra_args)` — runs a YADE script as a subprocess, raising `FileNotFoundError` if `yade` isn't installed

### `simulation.py` (65 lines)
The YADE entry-point script for the "random-mix ingress" scenario on the
bidisperse SAG mill slice.

- `run()` — orchestrates a full scenario:
  1. `initialize_simulation_materials` / `initialize_sag_mill_slice` / `initialize_engines` (Hertz–Mindlin contacts)
  2. `set_dt`, `set_gravity_damping`
  3. Opens the YADE Qt viewer (`qt.Controller()`, `qt.View()`)
  4. Calls `sim_functions.ingress_random(...)` to drop a rock/steel bidisperse charge into the mill
- Several commented-out alternative steps (manual balancing, saving/loading particle positions, overlap checks) documenting other workflows this script can be adapted to run manually from the YADE terminal.

### `sim_functions.py` (995 lines)
The core simulation library — everything `simulation.py` (and potentially
other future entry-point scripts) calls into. Grouped by concern:

**Setup / initialization**
- `initialize_simulation_materials(materials)`
- `initialize_sag_mill_slice(sagmill_stl_path)`
- `initialize_engines(contact_model, contact_model_params, rotation_engine=False)`

**Particle loading**
- `load_rock_particles(rock_diam_m, rock_count)`
- `load_ball_particles(ball_diam_m, ball_count)`
- `load_all_particles(particle_diam_m, particle_count)`

**Time step / physics tuning**
- `set_dt(new_dt=None, factor=0.3)`
- `set_gravity_damping(new_gravity_damping)`

**State persistence**
- `save_particle_positions(csv_path, include_velocity=True, include_ang_vel=True)`
- `load_particle_positions(csv_path, *, set_vel_zero=True, set_ang_vel_zero=True)`

**Settling / equilibration**
- `run_until_forces_balanced(threshold=0.001, interval=1000, motion_start_steps=20, wait_chunk=1000, max_chunks=5000)`
- `settle_balance_save(gravity_damping, csv_path)`
- `_balance_check()` *(internal)*

**Mill rotation**
- `rotate_mill_indefinitely(speed_rpm=9)`
- `rotate_mill_by_degrees(degrees, speed_rpm=9)`
- `rotate_mill_by_time(virtual_time_seconds, speed_rpm=9)`
- `_get_rotation_engine(label="rotation_engine")` *(internal)*

**Frame capture / recording**
- `start_frame_capture(folder_name, interval, runner_label="frameCapture", iter_period=50)`
- `_save_sphere_frame()` *(internal)*
- `_mat_label(b)` *(internal helper for labeling by material)*

**Geometry helpers**
- `createBox(x, y, z)`
- `createFunnel(x, y, z, fx, fy, dy)`
- `chord_box_3d(diameter, y, box_height, depth)`
- `get_surface_y(padding=0.1)`
- `_obtain_sag_mill_slice_measurements(sag_mill_body_group)` *(internal)*
- `_add_sag_mill_slice_caps(sag_mill_slice_body_group, sag_mill_slice_radius_m, z_min, z_max)` *(internal)*

**Diagnostics**
- `check_overlaps()`
- `get_particle_inventory(r_small, r_large, tol=1e-6, verbose=True)`

**Particle ingress (charge generation)**
- `ingress_random(diameter, depth, r_small, r_large, n_small, n_large, box_height, ...)` — random bidisperse rock/steel charge (used by `simulation.run()`)
- `ingress_segregated(diameter, depth, r_small, r_large, n_small, n_large, box_height, ...)` — segregated variant of the same charge-loading scheme

## Tests (`tests/simulation/`)

Mirrors the package, testing only what can run without YADE installed
(pure-Python geometry/label helpers and the subprocess launcher, with the
`yade`-dependent internals mocked out or untested at this layer).

### `test_launcher.py` (74 lines)
- `test_default_simulation_script_points_at_packaged_file()`
- `test_find_yade_executable_returns_none_when_missing()`
- `test_launch_simulation_raises_when_yade_missing(monkeypatch)`
- `test_launch_simulation_uses_default_script_and_resolved_executable(monkeypatch)`
- `test_launch_simulation_custom_script_and_extra_args(monkeypatch, tmp_path)`
- `test_launch_simulation_propagates_nonzero_returncode(monkeypatch)`

### `test_sim_functions.py` (44 lines)
- `test_mat_label_empty_material()`
- `test_mat_label_with_label()`
- `test_chord_box_3d_geometry_and_corners()`
- `test_chord_box_3d_clamps_y_to_radius()`

---

## Directory tree

```
bppm_dem_sm/simulation/
├── __init__.py          # subpackage docstring: YADE-only boundary note
├── launcher.py           # subprocess bridge (venv side, no `yade` import)
├── sim_functions.py      # simulation primitives library (YADE side, 995 lines)
└── simulation.py          # scenario entry-point script (YADE side)

tests/simulation/
├── test_launcher.py       # launcher subprocess tests
└── test_sim_functions.py  # pure-Python helper tests (_mat_label, chord_box_3d)
```
