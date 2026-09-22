"""Lacey mixing-index, segregation-profile, velocity, granular-temperature, and
computing-speed metrics over directories of ground-truth and predicted frames.

Computation only; the matching plots live in
:mod:`bppm_dem_sm.visualization.metrics_plots`.
"""

from __future__ import annotations

import os

import pandas as pd

from ..config import PipelineConfig
from ..data_processing import frames as data_io
from ..progress import track
from . import lacey_mixing_index as lacey
from . import segregation_profile as segprofile
from . import velocity_metrics as velmet
from .lacey_mixing_index import GT_FRAME_RE, PRED_FRAME_RE


def compute_lacey_over_dir(frames_dir, pattern, frame_re, tracer_r, config, out_name, label):
    """Compute the Lacey index per frame in a directory; save a summary parquet.

    Args:
        frames_dir: Directory of parquet frames.
        pattern: Glob for frame files.
        frame_re: Regex used by :func:`extract_frame_index`.
        tracer_r: Tracer (large) particle radius.
        config: Supplies ``metrics.cell_size``, ``metrics.min_particles_per_cell``,
            and ``metrics.metrics_dt``.
        out_name: Filename for the summary parquet written into ``frames_dir``.
        label: Short label for log messages (e.g. ``"GT"``, ``"PRED"``).

    Returns:
        pd.DataFrame: Per-frame Lacey summary sorted by ``frame``, with columns
        ``frame``, ``time``, ``lacey``, ``n_cells_used``,
        ``tracer_fraction_global``, ``mean_particles_per_cell``.
    """
    rows = []
    paths = data_io.sorted_frame_files(frames_dir, pattern)
    for pth in track(paths, desc=f"Lacey [{label}]", unit="frame"):
        frame_idx = lacey.extract_frame_index(pth, frame_re)
        df = pd.read_parquet(pth)
        M, n_cells, p_global, mean_n = lacey.lacey_index_for_frame(
            df, config.metrics.cell_size, tracer_r, config.metrics.min_particles_per_cell
        )
        rows.append(
            {
                "frame": frame_idx,
                "time": frame_idx * config.metrics.metrics_dt,
                "lacey": M,
                "n_cells_used": n_cells,
                "tracer_fraction_global": p_global,
                "mean_particles_per_cell": mean_n,
            }
        )

    out = pd.DataFrame(rows).sort_values("frame").reset_index(drop=True)
    out.to_parquet(os.path.join(str(frames_dir), out_name), index=False)
    print(f"[{label}] Saved Lacey summary ({len(out)} frames)")
    return out


def compute_profile_over_dir(
    frames_dir, pattern, frame_re, tracer_r, config, radial_edges, axial_edges, out_prefix, label
):
    """Compute radial/axial large-particle fraction profiles per frame; save parquets.

    Args:
        frames_dir: Directory of parquet frames.
        pattern: Glob for frame files.
        frame_re: Regex used by :func:`extract_frame_index`.
        tracer_r: Tracer (large) particle radius.
        config: Supplies ``metrics.center_x/center_y/center_z`` and ``metrics_dt``.
        radial_edges: Shared radial bin edges (same for every frame/directory
            being compared), from :func:`segregation_profile.radial_bin_edges`.
        axial_edges: Shared axial bin edges, from
            :func:`segregation_profile.axial_bin_edges`.
        out_prefix: Filename prefix for the two summary parquets written into
            ``frames_dir`` (``{prefix}_radial.parquet`` / ``{prefix}_axial.parquet``).
        label: Short label for log messages (e.g. ``"GT"``, ``"PRED"``).

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Long-format ``(radial, axial)``
        profiles with columns ``frame``, ``time``, ``bin``, ``bin_center``,
        ``fraction_large``, ``n_particles``.
    """
    m = config.metrics
    radial_rows, axial_rows = [], []
    paths = data_io.sorted_frame_files(frames_dir, pattern)
    for pth in track(paths, desc=f"Segregation profile [{label}]", unit="frame"):
        frame_idx = lacey.extract_frame_index(pth, frame_re)
        time = frame_idx * m.metrics_dt
        df = pd.read_parquet(pth)

        radial = segprofile.radial_fraction_profile(
            df, tracer_r, radial_edges, m.center_x, m.center_y
        )
        radial.insert(0, "time", time)
        radial.insert(0, "frame", frame_idx)
        radial_rows.append(radial)

        axial = segprofile.axial_fraction_profile(df, tracer_r, axial_edges, m.center_z)
        axial.insert(0, "time", time)
        axial.insert(0, "frame", frame_idx)
        axial_rows.append(axial)

    radial_out = pd.concat(radial_rows, ignore_index=True).sort_values(["frame", "bin"]).reset_index(drop=True)
    axial_out = pd.concat(axial_rows, ignore_index=True).sort_values(["frame", "bin"]).reset_index(drop=True)
    radial_out.to_parquet(os.path.join(str(frames_dir), f"{out_prefix}_radial.parquet"), index=False)
    axial_out.to_parquet(os.path.join(str(frames_dir), f"{out_prefix}_axial.parquet"), index=False)
    print(f"[{label}] Saved segregation profile ({len(paths)} frames)")
    return radial_out, axial_out


def compute_velocity_and_granular_temperature(frames_dir, pattern, frame_re, tracer_r, config, label):
    """Compute velocity distribution and granular temperature at the last available frame pair.

    Mirrors the paper's evaluation style (Fig. 9): a single, most-evolved-state
    snapshot rather than a time series, using the last two consecutive frames
    present in ``frames_dir``.

    Args:
        frames_dir: Directory of parquet frames.
        pattern: Glob for frame files.
        frame_re: Regex used by :func:`extract_frame_index`.
        tracer_r: Tracer (large) particle radius.
        config: Supplies ``metrics.cell_size``, ``metrics.min_particles_per_cell``,
            and ``metrics.metrics_dt``.
        label: Short label for log messages (e.g. ``"GT"``, ``"PRED"``).

    Returns:
        dict or None: ``{"time", "frame_t", "frame_t1", "speed", "granular_temperature"}``,
        or ``None`` if fewer than 2 frames are available.
    """
    m = config.metrics
    paths = data_io.sorted_frame_files(frames_dir, pattern)
    if len(paths) < 2:
        print(f"[{label}] Skipping velocity/granular-temperature: need >= 2 frames, found {len(paths)}")
        return None

    idx_t = lacey.extract_frame_index(paths[-2], frame_re)
    idx_t1 = lacey.extract_frame_index(paths[-1], frame_re)
    df_t = pd.read_parquet(paths[-2])
    df_t1 = pd.read_parquet(paths[-1])
    dt = m.metrics_dt * (idx_t1 - idx_t)

    speed = velmet.velocity_speed_by_species(df_t, df_t1, dt, tracer_r)
    granular_temperature = velmet.granular_temperature_by_cell(
        df_t, df_t1, dt, m.cell_size, m.min_particles_per_cell
    )
    print(
        f"[{label}] Velocity/granular temperature at t={idx_t1 * m.metrics_dt:.3f}s "
        f"(frames {idx_t}->{idx_t1}, {len(granular_temperature)} cells)"
    )
    return {
        "time": idx_t1 * m.metrics_dt,
        "frame_t": idx_t,
        "frame_t1": idx_t1,
        "speed": speed,
        "granular_temperature": granular_temperature,
    }


def compute_metrics(config: PipelineConfig) -> dict:
    """Compute Lacey index, segregation profile, velocity, and granular temperature.

    Detects the tracer radius from the first ground-truth frame, then runs
    each metric on DEM frames and, when present, on predicted frames under
    ``config.prediction.pred_frames_dir``. Radial/axial bin edges are derived
    once from the first ground-truth frame so GT and predicted profiles share
    the same bins.

    Args:
        config: Pipeline settings for data paths and metric parameters.

    Returns:
        dict: ``"gt"`` / optional ``"pred"`` Lacey summaries (``pd.DataFrame``);
        ``"radial_gt"`` / ``"axial_gt"`` / optional ``"radial_pred"`` /
        ``"axial_pred"`` profile summaries (``pd.DataFrame``); ``"velocity_gt"``
        / optional ``"velocity_pred"`` (``dict`` from
        :func:`compute_velocity_and_granular_temperature`, or absent if fewer
        than 2 frames were available).
    """
    m = config.metrics
    gt_paths = data_io.sorted_frame_files(config.data_dir, config.frame_glob)
    first_gt = pd.read_parquet(gt_paths[0])
    tracer_r = lacey.detect_tracer_radius(first_gt["r"].to_numpy())
    print(f"Detected tracer (large) radius r = {tracer_r}")

    results: dict = {
        "gt": compute_lacey_over_dir(
            config.data_dir, config.frame_glob, GT_FRAME_RE, tracer_r, config,
            "lacey_over_time.parquet", "GT",
        )
    }

    radial_edges = segprofile.radial_bin_edges(first_gt, m.center_x, m.center_y, m.n_radial_bins)
    axial_edges = segprofile.axial_bin_edges(first_gt, m.center_z, m.n_axial_bins)
    results["radial_gt"], results["axial_gt"] = compute_profile_over_dir(
        config.data_dir, config.frame_glob, GT_FRAME_RE, tracer_r, config,
        radial_edges, axial_edges, "segregation_profile", "GT",
    )

    velocity_gt = compute_velocity_and_granular_temperature(
        config.data_dir, config.frame_glob, GT_FRAME_RE, tracer_r, config, "GT"
    )
    if velocity_gt is not None:
        results["velocity_gt"] = velocity_gt

    if data_io.sorted_frame_files(config.prediction.pred_frames_dir, "pred_frame_*.parquet"):
        results["pred"] = compute_lacey_over_dir(
            config.prediction.pred_frames_dir, "pred_frame_*.parquet", PRED_FRAME_RE, tracer_r, config,
            "lacey_over_time_pred.parquet", "PRED",
        )
        results["radial_pred"], results["axial_pred"] = compute_profile_over_dir(
            config.prediction.pred_frames_dir, "pred_frame_*.parquet", PRED_FRAME_RE, tracer_r, config,
            radial_edges, axial_edges, "segregation_profile", "PRED",
        )
        velocity_pred = compute_velocity_and_granular_temperature(
            config.prediction.pred_frames_dir, "pred_frame_*.parquet", PRED_FRAME_RE, tracer_r, config, "PRED"
        )
        if velocity_pred is not None:
            results["velocity_pred"] = velocity_pred

    return results


def compute_computing_speed(timing: dict, config: PipelineConfig) -> dict:
    """Dimensionless computing speed vs. a user-supplied DEM reference (paper Fig. 15).

    Compares this run's own wall-clock training/prediction time (plus, if
    supplied, the short reference-DEM run used to build the GRU's training
    data) against ``config.computing_speed.dem_reference_seconds`` -- the
    wall-clock time of a full DEM run reproducing the same target simulated
    duration. Neither DEM time is measured by this pipeline; both are plain
    user-supplied values (there is no DEM stage in this pipeline to time
    automatically; see :class:`~bppm_dem_sm.config.ComputingSpeedOptions`).

    Mirrors the paper's two figures: prediction-only speedup (their ~240x) and
    all-RNNSR-steps speedup (their ~2.5x: reference-DEM data acquisition +
    training + prediction). The latter equals just train+predict when
    ``dem_data_acquisition_seconds`` is left at its 0.0 default.

    Args:
        timing: Wall-clock seconds recorded by
            :func:`bppm_dem_sm.pipeline.run_pipeline`, with optional
            ``train_seconds`` / ``predict_seconds`` keys (present only for
            stages that actually ran).
        config: Supplies ``computing_speed.dem_reference_seconds`` and
            ``computing_speed.dem_data_acquisition_seconds``.

    Returns:
        dict: ``dem_reference_seconds``, ``dem_data_acquisition_seconds``,
        ``train_seconds``, ``predict_seconds`` (as given, possibly ``None``),
        ``all_steps_seconds``, and the dimensionless
        ``prediction_only_speedup`` / ``all_steps_speedup`` (each ``None``
        where the underlying timing is unavailable).
    """
    dem_seconds = config.computing_speed.dem_reference_seconds
    dem_data_acquisition_s = config.computing_speed.dem_data_acquisition_seconds
    train_s = timing.get("train_seconds")
    predict_s = timing.get("predict_seconds")
    all_steps = (
        dem_data_acquisition_s + train_s + predict_s
        if train_s is not None and predict_s is not None
        else None
    )

    result = {
        "dem_reference_seconds": dem_seconds,
        "dem_data_acquisition_seconds": dem_data_acquisition_s,
        "train_seconds": train_s,
        "predict_seconds": predict_s,
        "all_steps_seconds": all_steps,
        "prediction_only_speedup": dem_seconds / predict_s if predict_s else None,
        "all_steps_speedup": dem_seconds / all_steps if all_steps else None,
    }
    print("[Computing speed] " + ", ".join(f"{k}={v}" for k, v in result.items()))
    return result
