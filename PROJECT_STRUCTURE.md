# Project structure — `bppm-dem-sm-project`

Function-level map of the codebase as of this session. One overriding fact to keep in mind while reading this: **`bppm_dem_sm` is two codebases sharing a directory.** `simulation.py` / `sim_functions.py` (and the YADE-only bits of `config.py`) run inside YADE's embedded Python interpreter and only ever produce CSV frames on disk. Everything else — `pipeline.py` onward — runs in a normal TensorFlow/pandas venv and only ever *consumes* those frames as files. The two sides never call each other in-process.

Legend: `fn(...)` = function, `class Foo` = class/dataclass, `_private` = module-private helper (leading underscore).

---

## 1. DEM simulation (YADE runtime only)

### `bppm_dem_sm/simulation.py`
Entry point run as `yade bppm_dem_sm/simulation.py`.
- `run()` — initializes materials/engines, loads the SAG mill STL slice, and ingresses a randomly-mixed bidisperse rock/steel charge via `sim_functions.ingress_random`.

### `bppm_dem_sm/sim_functions.py`
YADE helpers for the bidisperse SAG-mill-slice simulation (materials, engines, particle I/O, settling, rotation, frame capture, chord-box ingress).
- `initialize_simulation_materials(materials)` — registers `FrictMat` entries into `O.materials`/`MATERIALS_MAP`.
- `initialize_sag_mill_slice(sagmill_stl_path)` — loads the STL slice, adds end caps, sets `SAG_MILL_SLICE_BODY_GROUP`.
- `initialize_engines(contact_model, contact_model_params, rotation_engine=False)` — builds `O.engines` for Cundall–Strack or Hertz–Mindlin contact, optionally with a `RotationEngine`.
- `load_rock_particles(rock_diam_m, rock_count)` — spawns rock spheres across four vertical regions.
- `load_ball_particles(ball_diam_m, ball_count)` — spawns steel-ball spheres across four vertical regions.
- `load_all_particles(particle_diam_m, particle_count)` — spawns undifferentiated white spheres across a 9-region vertical stack.
- `set_dt(new_dt=None, factor=0.3)` — sets `O.dt` explicitly or from the P-wave critical timestep.
- `set_gravity_damping(new_gravity_damping)` — sets numerical damping on the labeled `NewtonIntegrator`.
- `save_particle_positions(csv_path, include_velocity=True, include_ang_vel=True)` — dumps all spheres to CSV.
- `load_particle_positions(csv_path, *, set_vel_zero=True, set_ang_vel_zero=True)` — recreates spheres from a CSV written by the function above.
- `run_until_forces_balanced(threshold=0.001, interval=1000, motion_start_steps=20, wait_chunk=1000, max_chunks=5000)` — runs until `unbalancedForce()` drops below `threshold`.
- `settle_balance_save(gravity_damping, csv_path)` — sets damping, waits for balance, saves positions.
- `rotate_mill_indefinitely(speed_rpm=9)` — sets rotation speed and runs the mill open-ended.
- `rotate_mill_by_degrees(degrees, speed_rpm=9)` — rotates for the time needed to cover `degrees` at `speed_rpm`.
- `rotate_mill_by_time(virtual_time_seconds, speed_rpm=9)` — rotates for a fixed simulated duration.
- `start_frame_capture(folder_name, interval, runner_label="frameCapture", iter_period=50)` — installs a `PyRunner` that periodically dumps sphere-state CSVs.
- `createBox(x, y, z)` — appends box-wall facets (fixed 0.375 m height).
- `createFunnel(x, y, z, fx, fy, dy)` — appends funnel + deposit-box facets for ingress geometry.
- `check_overlaps()` — returns the worst sphere–sphere relative penetration depth.
- `chord_box_3d(diameter, y, box_height, depth)` — geometry dict for a chord-shaped ingress box at height `y`.
- `get_surface_y(padding=0.1)` — Y coordinate just above the current tallest sphere (next ingress height).
- `ingress_random(diameter, depth, r_small, r_large, n_small, n_large, box_height, material_small, material_large, color_small, color_large, settle_steps=10000, padding=0.1, verbose=True)` — pours randomly-mixed small/large batches via chord boxes, settling after each.
- `ingress_segregated(diameter, depth, r_small, r_large, n_small, n_large, box_height, material_small, material_large, color_small, color_large, settle_steps=10000, padding=0.1, verbose=True)` — same batching, but pours all small particles first, then all large (fully segregated charge).
- `get_particle_inventory(r_small, r_large, tol=1e-6, verbose=True)` — counts spheres per size class.
- `_obtain_sag_mill_slice_measurements(sag_mill_body_group)` — bounding radius/Z-extent of the mill slice.
- `_add_sag_mill_slice_caps(sag_mill_slice_body_group, sag_mill_slice_radius_m, z_min, z_max)` — appends triangular end-cap facets.
- `_balance_check()` — `PyRunner` hook: stops the sim once `unbalancedForce()` is below threshold.
- `_get_rotation_engine(label="rotation_engine")` — looks up a `RotationEngine` by label.
- `_mat_label(b)` — material label string for a body.
- `_save_sphere_frame()` — `PyRunner` hook: writes one sphere-state CSV frame when the next capture time is reached.

---

## 2. ML surrogate pipeline core (TensorFlow/pandas venv)

### `bppm_dem_sm/config.py`
Configuration and path resolution for the whole pipeline; also (separately) holds the YADE/SAG-mill constants used by section 1.

Module constants: `REPO_ROOT`, `DATA_DIR`, `RAW_DIR`, `INTERIM_DIR`, `PROCESSED_DIR`, `MODELS_DIR`, `REPORTS_DIR`, `FIGURES_DIR`, `DEFAULT_DATASET`, `DEFAULT_TRAIN_DATASET`, `DEFAULT_MODEL_NAME`, `ID_COL`, `FEATURE_COLS`, `TARGET_COLS`, `ROCK_COUNT`, `ROCK_DIAM_M`, `BALL_COUNT`, `BALL_DIAM_M`, `SAGMILL_STL_PATH`, `MATERIALS`.

- `build_material_interactions()` — YADE `MatchMaker` of steel/rock restitution coefficients (needs YADE).
- `class TrainingOptions` — GRU hyperparameters: `epochs`, `batch_size`, `learning_rate`, `val_fraction`, `seed`, `gru_units`, `dense_units`.
- `class PredictionOptions` — sliding-window prediction settings: `start_frame`, `autoregressive`, `predict_until_end`, `max_steps`, `predict_batch_size`, `dt0`, `dt_step`, `pred_out_dir`; properties `pred_frames_dir`, `pred_combined_parquet`.
- `class MetricsOptions` — `cell_size`, `min_particles_per_cell`, `metrics_dt` (shared by Lacey + granular temperature), plus `center_x/y/z`, `n_radial_bins`, `n_axial_bins` (segregation profile).
- `class ComputingSpeedOptions` — `dem_reference_seconds` (default 24 h placeholder), `dem_data_acquisition_seconds` (default 0.0) — both user-supplied DEM wall-clock measurements.
- `class StochasticOptions` — SR velocity-perturbation settings: `enabled`, `velocity_cell_size`, `velocity_min_particles_per_cell`, `stochastic_seed`.
- `class VisualizationOptions` — `plane`, `fps`, `marker_size`, `every_nth_frame`, `save_figures`, `show_plots`.
- `class PipelineConfig` — top-level config: data/model paths, stage toggles (`do_train`/`do_predict`/`do_metrics`/`do_visualization`), and all option groups above.
  - `.to_dict()` — recursive serialization (Paths → strings).
  - `.with_overrides(**overrides)` — copy with top-level, group, or flat leaf-name overrides applied.
  - `.from_dict(data)` / `.from_json(path)` — classmethods to build a config from a mapping / JSON file.
- `_option_group_types()` — maps group field name → option dataclass.
- `_leaf_to_group()` — maps a nested leaf field name → its owning group name.
- `_to_plain_dict(obj)` / `_from_plain_dict(cls, data)` — recursive dataclass ⇄ dict conversion.
- `_coerce_bool(value, key)` — coerces common string forms (`"true"`, `"0"`, ...) to `bool`.

### `bppm_dem_sm/pipeline.py`
- `run_pipeline(config=None, **overrides)` — orchestrates Training → Prediction → Metrics → Visualization (each gated by its `do_*` flag); times training/prediction wall-clock seconds into `results["timing"]`; injects `compute_computing_speed()` into the metrics dict; returns a dict of artifacts.

### `bppm_dem_sm/training.py`
- `build_model(frames_in, n_features=4, gru_units=20, dense_units=15, learning_rate=0.01)` — builds/compiles the `Input → GRU → Dense(tanh) → Dense(3, linear)` Keras model.
- `train_and_save(config, plot_history=True)` — builds the supervised dataset, fits the model, saves a `.keras` artifact, optionally plots loss; returns `(model, history)`.
- `plot_training_history(history, show=True)` — train/val MSE curve figure.

### `bppm_dem_sm/prediction.py`
- `class _SavedModelWrapper` — Keras-`predict`-like adapter over a legacy TensorFlow SavedModel export (Keras 3 can't load these directly).
- `_resolve_model_path(path)` — finds an existing `.keras`/`.h5`/SavedModel artifact for a requested path.
- `load_model(path)` — loads a Keras model or `_SavedModelWrapper`.
- `predict_frames(config, model=None)` — slides a window over frames, predicts next positions (GRU), adds the SR stochastic displacement when `config.stochastic.enabled`, writes per-step and combined parquet outputs.

### `bppm_dem_sm/stochastic_motion.py`
SR (stochastically-calculated random motion) half of the extended-RNNSR method (Kishida et al. 2025).
- `class VelocityStdField` — per-cell isotropic velocity-std lookup; `.sigma_at(positions)` returns σ_v per particle.
- `build_velocity_std_field(frames_dir, frame_glob, dt, cell_size, min_particles_per_cell=15)` — estimates σ_v(x) from consecutive reference DEM frames (paper Eq. 2).
- `build_velocity_std_field_from_config(config)` — builds the field from `config.train_data_dir`.
- `sample_stochastic_displacement(positions, field, dt_rnn, rng)` — draws the SR displacement to add to the GRU's predicted position (paper Eqs. 3–4).

### `bppm_dem_sm/data_io.py`
- `sorted_frame_files(frames_dir, pattern="frame_*.parquet")` — sorted matching parquet paths.
- `load_frame(path, cols=None)` — reads one frame, sorted by `id`.
- `load_frames_stacked(frames_dir, pattern="frame_*.parquet", feature_cols=None)` — stacks all frames into `(pos [T,N,3], rad [T,N,1], base_ids)`.
- `build_supervised_dataset(pos, rad, frames_in)` — builds sliding-window `(X, y)` training pairs.
- `train_test_split(X, y, val_fraction=0.1, seed=0)` — shuffles and splits into train/validation.

### `bppm_dem_sm/csv_to_parquet.py`
- `convert_csv_file_to_parquet(csv_path, parquet_path)` — one file.
- `convert_folder_csv_to_parquet(input_folder, output_folder)` — every `*.csv` in a folder.

### `bppm_dem_sm/verify_particle_integrity.py`
- `particle_radius_counts_per_file(folder_path, size_column="r")` — per-file radius value-counts table.
- `report_particle_integrity(folder_path, size_column="r")` — prints counts/mean/std as a sanity check (std should be ~0 for a healthy export).

---

## 3. Metrics (post-hoc analysis of parquet frames)

### `bppm_dem_sm/lacey_mixing_index.py`
Constants: `GT_FRAME_RE`, `PRED_FRAME_RE`.
- `extract_frame_index(path, frame_re=GT_FRAME_RE)` — parses the frame index from a filename.
- `detect_tracer_radius(r_values)` — picks the larger of two radii as the tracer species.
- `lacey_index_for_frame(df, cell_size, tracer_radius, min_particles_per_cell=5)` — Lacey's mixing index `M` on a 3D cubic-cell grid; returns `(M, n_cells_used, p_global, mean_particles_per_cell)`.

### `bppm_dem_sm/segregation_profile.py`
Radial/axial large-particle fraction profile (paper Figs. 8b/c, 11b/c, 12b, 14b).
- `radial_bin_edges(df, center_x=0.0, center_y=0.0, n_bins=12)` — equal-width radial bin edges spanning the frame's extent.
- `axial_bin_edges(df, center_z=0.0, n_bins=12)` — equal-width axial (signed) bin edges.
- `_fraction_by_bin(distance, is_tracer, bin_edges)` — bins a distance array and reports the tracer fraction per bin.
- `radial_fraction_profile(df, tracer_radius, bin_edges, center_x=0.0, center_y=0.0)` — fraction of large particles vs. radial distance.
- `axial_fraction_profile(df, tracer_radius, bin_edges, center_z=0.0)` — fraction of large particles vs. axial distance.

### `bppm_dem_sm/velocity_metrics.py`
Velocity-distribution and granular-temperature metrics (paper Fig. 9).
- `_matched_velocity(df_t, df_t1, dt)` — finite-differences velocity between two id-aligned frames.
- `velocity_speed_by_species(df_t, df_t1, dt, tracer_radius)` — `{"small": speeds, "large": speeds}`.
- `granular_temperature_by_cell(df_t, df_t1, dt, cell_size, min_particles_per_cell=15)` — per-cell granular temperature `mean(‖v_i − ⟨v⟩‖²)/3`.

### `bppm_dem_sm/run_metrics.py`
Ties the above together over directories of GT/predicted frames, plus the computing-speed metric.
- `compute_lacey_over_dir(frames_dir, pattern, frame_re, tracer_r, config, out_name, label)` — per-frame Lacey summary, saved to parquet.
- `compute_profile_over_dir(frames_dir, pattern, frame_re, tracer_r, config, radial_edges, axial_edges, out_prefix, label)` — per-frame radial/axial profile summaries, saved to parquet.
- `compute_velocity_and_granular_temperature(frames_dir, pattern, frame_re, tracer_r, config, label)` — velocity distribution + granular temperature at the *last available frame pair* (mirrors the paper's single end-state snapshot).
- `compute_metrics(config)` — orchestrates all of the above for ground truth (and predictions, if present); shared radial/axial bins derived from the first GT frame.
- `compute_computing_speed(timing, config)` — dimensionless speedup vs. `config.computing_speed.dem_reference_seconds`; folds in `dem_data_acquisition_seconds` when set.
- `plot_lacey_comparison(metrics, config, show=True)` — Lacey index vs. time, GT vs. surrogate.
- `_latest_time_slice(profile_df)` — rows for the last (largest) `frame` in a profile summary.
- `plot_segregation_profile(metrics, config, show=True)` — radial + axial fraction profile at the final frame.
- `plot_velocity_distribution(metrics, config, show=True)` — small/large particle speed histograms, GT vs. surrogate.
- `plot_granular_temperature(metrics, config, show=True)` — per-cell granular temperature boxplots, GT vs. surrogate.
- `plot_computing_speed(metrics, config, show=True)` — bar chart of dimensionless speedup(s) vs. the DEM reference.

---

## 4. Visualization

### `bppm_dem_sm/cell_grid.py`
- `plot_particles_with_grid(frame_path, cell_size, use_equal_aspect=True, save_path=None, show=True)` — scatters both species on XY with the Lacey cell grid overlaid.

### `bppm_dem_sm/animate_particles.py`
Standalone 2D animation (not pipeline-wired; see `run_visualization.animate_frames` for that).
- `radius_colors(r)` — maps a bidisperse radius array to small/large colors.
- `animate_particles(frames_dir, glob_pattern="frame_*.parquet", plane="xy", every_nth_frame=1, fps=30, marker_size=4.0, save_path=None)` — builds/shows/saves a 2D scatter animation.

### `bppm_dem_sm/run_visualization.py`
Pipeline-integrated plots (the Visualization stage).
- `_radius_colors(r)` — same mapping as above (private copy).
- `animate_frames(frames_dir, config, pattern="frame_*.parquet", save_path=None)` — 2D scatter animation using `config.visualization`; falls back MP4→GIF via Pillow when ffmpeg is unavailable.
- `plot_frame_grid(frame_path, config, save_path=None, show=True)` — one frame with the cell grid overlaid (delegates to `cell_grid.plot_particles_with_grid`).
- `generate_visualizations(config)` — renders the cell-grid frame and the prediction animation; returns a dict of artifacts/paths.

---

## 5. CLI & plumbing

### `bppm_dem_sm/cli.py`
- `_bool_fields(cls)` / `_path_fields(cls)` — field names typed `bool`/`Path` on a dataclass.
- `_add_config_flag(container, f, owning_cls)` — adds one typed argparse flag for a dataclass field.
- `build_parser()` — builds the full `bppm-pipeline` argparse parser (one flag per `PipelineConfig` field and per option-group leaf, plus `--config`).
- `_leaf_override_names()` — CLI dest names mapping onto `PipelineConfig.with_overrides`.
- `config_from_args(args)` — resolves a `PipelineConfig` from parsed CLI args (JSON file takes precedence over flags).
- `main(argv=None)` — CLI entry point (the `bppm-pipeline` console script); parses args and calls `run_pipeline`.

### `bppm_dem_sm/progress.py`
- `plan(titles)` — prints which stages will run.
- `stage(index, total, title)` — high-visibility banner for one stage.
- `complete(message="Pipeline complete.")` — closing banner.
- `track(iterable, desc, unit="it", **kwargs)` — wraps an iterable in a tqdm bar.
- `bar(total=None, desc="", unit="it", **kwargs)` — manual tqdm bar for non-iterable progress.

### `bppm_dem_sm/tf_quiet.py`
- `silence_tensorflow()` — sets `TF_CPP_MIN_LOG_LEVEL`/`TF_ENABLE_ONEDNN_OPTS` before TF/Keras import.

### `bppm_dem_sm/__init__.py`
Re-exports `MetricsOptions`, `PipelineConfig`, `PredictionOptions`, `TrainingOptions`, `VisualizationOptions`, `run_pipeline`.

### `bppm_dem_sm/__main__.py`
Enables `python -m bppm_dem_sm`: silences TensorFlow, then calls `cli.main()`.

---

## 6. Tests (`tests/`)

Two eras coexist:

**Current style** (`from bppm_dem_sm.x import y`, matches the flat package layout):
- `test_cli_pipeline_config.py` — `PipelineConfig` JSON/dict coercion, `with_overrides`, CLI flag parsing, `run_pipeline` stage banners (training/prediction monkeypatched).
- `test_stochastic_motion.py` — `VelocityStdField` construction/lookup, known-variance checks, `sample_stochastic_displacement` reproducibility, and an end-to-end `predict_frames` run with a stub GRU model proving the SR term applies post-GRU.
- `test_segregation_profile.py` — bin-edge construction, fraction-by-bin correctness, custom-center handling.
- `test_velocity_metrics.py` — species-split speed correctness, id-mismatch errors, granular-temperature known-variance and sparse-cell exclusion.
- `test_run_metrics.py` — `compute_metrics` with/without predictions, single-frame velocity skip, all four metric plots render without error.
- `test_computing_speed.py` — `ComputingSpeedOptions` defaults/roundtrip, `compute_computing_speed` math (both timings, predict-only, no timing, with/without `dem_data_acquisition_seconds`), `plot_computing_speed` no-op cases, `run_pipeline` timing wiring end-to-end.

**Pre-refactor style** (import old flat module names like `s0_csv_to_parquet`, `s1_rnn_predictions` via a `conftest.py` sys.path shim pointing at directories — `data_gen_sim/`, `model/RNNSR/`, etc. — that no longer exist under `bppm_dem_sm/`). **Currently broken**, predates this session, not touched here:
- `conftest.py` — the stale sys.path shim itself.
- `test_s0_calc_lmi_across_frames.py`, `test_s0_csv_to_parquet.py`, `test_s1_rnn_predictions.py`, `test_s1_verify_particle_integrity.py`, `test_u0_animate_particles.py`, `test_u1_visualize_cell_grid.py` — fail to collect (`ModuleNotFoundError`/`FileNotFoundError`).
- `test_ingress_func_v1.py`, `test_s1_sim_functions.py` — currently skipped/passing depending on environment (YADE-dependent).

---

## 7. Everything else (not function-level code)

- `configs/pipeline_example.json` — a full `PipelineConfig` example covering every option group.
- `notebooks/global_pipeline.ipynb` — notebook-driven pipeline run.
- `models/rnn_gru_sic_model/` — a saved Keras/TF model artifact (SavedModel format).
- `reports/figures/` — saved plot output (currently `lacey_comparison.png`).
- `docs/` — Sphinx documentation (`source/`, autogenerated API stub, `Makefile`).
- `data/` — **not present locally**; expected layout per `config.py`: `data/raw/`, `data/interim/`, `data/processed/`.
- `requirements.txt`, `pyproject.toml`, `Makefile`, `README.md` — standard project plumbing.
