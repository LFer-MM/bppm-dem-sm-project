"""Pipeline entry point for every plot this project renders.

``generate_visualizations`` is the only place anything gets rendered:
training curves, both cell-grid frames (Lacey's and SR's -- different cell
sizes, see :mod:`bppm_dem_sm.config`), the five GT-vs-surrogate metrics
comparison plots, and the prediction animation. Every other stage
(``do_train``, ``do_process``, ``do_predict``, ``do_metrics``) only computes
and persists; nothing it produces is plotted until ``do_visualization`` runs
and reads it back from disk -- see project_structure_proposal.md section 6,
"Persist everywhere, render only in Visualization".
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import INTERIM_DIR, ExperimentConfig
from ..data_processing import frames as data_io
from ..metrics import run_metrics
from ..progress import bar
from . import metrics_plots
from .cell_grid import plot_particles_with_grid
from .training_curves import plot_training_history

_PLANE_AXES = {"xy": ("x", "y"), "xz": ("x", "z"), "yz": ("y", "z")}
VIZ_DIR = INTERIM_DIR / "figures"

SMALL_COLOR = "#d62728"
LARGE_COLOR = "#1f77b4"


def _radius_colors(r):
    """Map a bidisperse radius array to small/large category colors.

    Args:
        r: 1-D array of particle radii (two distinct values expected).

    Returns:
        numpy.ndarray: Per-particle color codes (small → red, large → blue).
    """
    small_r = np.unique(r).min()
    return np.where(r == small_r, SMALL_COLOR, LARGE_COLOR)


def animate_frames(frames_dir, config: ExperimentConfig, pattern="frame_*.parquet", save_path=None):
    """Build a 2D scatter animation colored by particle radius.

    Uses ``config.visualization`` for ``plane``, ``fps``, ``marker_size``, and
    ``every_nth_frame``.
    When saving MP4 without ffmpeg, falls back to GIF via Pillow.

    Args:
        frames_dir: Directory of parquet frames to animate.
        config: Visualization settings from ``ExperimentConfig``.
        pattern: Glob for frame files (e.g. ``pred_frame_*.parquet``).
        save_path: Optional output path (``.mp4`` or ``.gif``); ``None`` shows
            interactively when ``config.visualization.show_plots`` is true.

    Returns:
        tuple: ``(anim, resolved_save_path)`` where ``resolved_save_path`` may
        differ from ``save_path`` if MP4 was rewritten as GIF, or is ``None``
        when not saving.
    """
    from matplotlib.animation import FuncAnimation, writers
    import matplotlib.pyplot as plt

    viz = config.visualization
    ax_x, ax_y = _PLANE_AXES[viz.plane]
    files = data_io.sorted_frame_files(frames_dir, pattern)[:: viz.every_nth_frame]

    df0 = pd.read_parquet(files[0])
    fig, ax = plt.subplots()
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(ax_x)
    ax.set_ylabel(ax_y)
    ax.set_xlim(-6.2, 6.2)
    ax.set_ylim(-6.2, 6.2)

    sc = ax.scatter(
        df0[ax_x].to_numpy(), df0[ax_y].to_numpy(),
        c=_radius_colors(df0["r"].to_numpy()), s=viz.marker_size, alpha=0.75,
    )
    title = ax.set_title(os.path.basename(files[0]))

    def update(i):
        df = pd.read_parquet(files[i])
        sc.set_offsets(np.column_stack([df[ax_x].to_numpy(), df[ax_y].to_numpy()]))
        sc.set_color(_radius_colors(df["r"].to_numpy()))
        title.set_text(os.path.basename(files[i]))
        return sc, title

    anim = FuncAnimation(fig, update, frames=len(files), interval=int(1000 / viz.fps), blit=False)

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        # Pillow can write GIF/APNG, not MP4; use ffmpeg only when available.
        if save_path.suffix.lower() == ".mp4" and not writers.is_available("ffmpeg"):
            save_path = save_path.with_suffix(".gif")
            print("ffmpeg not available; saving animation as GIF instead.")
        writer = "ffmpeg" if save_path.suffix.lower() == ".mp4" else "pillow"
        pbar = bar(total=len(files), desc="Saving animation", unit="frame")

        def _on_progress(current_frame, total_frames):
            if total_frames:
                pbar.total = total_frames
            pbar.n = current_frame + 1
            pbar.refresh()

        try:
            anim.save(
                str(save_path),
                dpi=140,
                fps=viz.fps,
                writer=writer,
                progress_callback=_on_progress,
            )
        except TypeError:
            anim.save(str(save_path), dpi=140, fps=viz.fps, writer=writer)
        finally:
            pbar.close()
        print(f"Saved animation: {save_path}")
        if not viz.show_plots:
            plt.close(fig)
        return anim, save_path
    elif viz.show_plots:
        plt.show()
    return anim, None


def plot_frame_grid(frame_path, config: ExperimentConfig, save_path=None, show=True):
    """Render a single frame with the Lacey/granular-temperature cell grid overlaid.

    Args:
        frame_path: Parquet frame to scatter-plot.
        config: Supplies ``metrics.cell_size`` for the grid overlay.
        save_path: Optional path to save the figure.
        show: Whether to display the figure interactively.

    Returns:
        matplotlib.figure.Figure: Figure from :func:`plot_particles_with_grid`.
    """
    return plot_particles_with_grid(
        str(frame_path),
        config.metrics.cell_size,
        save_path=save_path,
        show=show,
    )


def plot_sr_grid(frame_path, config: ExperimentConfig, save_path=None, show=True):
    """Render a single frame with the SR (stochastic-random) cell grid overlaid.

    Deliberately a *different* cell size from :func:`plot_frame_grid` --
    ``config.stochastic.velocity_cell_size`` follows the paper's SR-specific
    formula (``4 x large-particle diameter``), not the Lacey/granular-
    temperature formula (``0.04 x drum diameter``); see
    :class:`bppm_dem_sm.config.StochasticOptions`.

    Args:
        frame_path: Parquet frame to scatter-plot.
        config: Supplies ``stochastic.velocity_cell_size`` for the grid overlay.
        save_path: Optional path to save the figure.
        show: Whether to display the figure interactively.

    Returns:
        matplotlib.figure.Figure: Figure from :func:`plot_particles_with_grid`.
    """
    return plot_particles_with_grid(
        str(frame_path),
        config.stochastic.velocity_cell_size,
        save_path=save_path,
        show=show,
    )


def generate_visualizations(config: ExperimentConfig, metrics: dict | None = None) -> dict:
    """Render every plot: training curves, both cell grids, metrics comparisons, animation.

    Each plot reads whatever its producing stage persisted to disk, so this
    runs standalone in a ``do_visualization``-only pass -- it does not
    require ``do_train``/``do_metrics``/``do_predict`` to have just run in
    the same process. Anything with no persisted input yet (e.g. no
    ``history.json`` because training hasn't run) is skipped rather than
    raising.

    Args:
        config: Pipeline settings controlling show/save and animation options.
        metrics: Optional metrics dict, e.g. already computed by
            ``run_metrics.compute_metrics(config)`` earlier in the same call.
            When omitted, loaded from disk via
            :func:`bppm_dem_sm.metrics.run_metrics.load_metrics`.

    Returns:
        dict: Paths and artists for whichever plots were actually rendered
        (a key is present only when its persisted input existed).
    """
    viz = config.visualization
    artifacts: dict = {}

    if viz.save_figures:
        VIZ_DIR.mkdir(parents=True, exist_ok=True)

    history_path = Path(config.model_path).with_suffix(".history.json")
    if history_path.exists() and (viz.show_plots or viz.save_figures):
        print("Rendering training curves...")
        history_save = VIZ_DIR / "training_curves.png" if viz.save_figures else None
        artifacts["training_curves_figure"] = plot_training_history(
            history_path, save_path=history_save, show=viz.show_plots
        )
        if viz.save_figures:
            artifacts["training_curves_save_path"] = history_save

    gt_files = data_io.sorted_frame_files(config.data_dir, config.frame_glob)
    if gt_files and (viz.show_plots or viz.save_figures):
        artifacts["grid_frame"] = gt_files[0]

        print("Rendering Lacey cell-grid frame...")
        lacey_save = VIZ_DIR / "cell_grid_frame_lacey.png" if viz.save_figures else None
        artifacts["grid_figure"] = plot_frame_grid(
            gt_files[0], config, save_path=lacey_save, show=viz.show_plots,
        )

        print("Rendering SR cell-grid frame...")
        sr_save = VIZ_DIR / "cell_grid_frame_sr.png" if viz.save_figures else None
        artifacts["sr_grid_figure"] = plot_sr_grid(
            gt_files[0], config, save_path=sr_save, show=viz.show_plots,
        )
        if viz.save_figures:
            artifacts["grid_save_path"] = lacey_save
            artifacts["sr_grid_save_path"] = sr_save

    resolved_metrics = metrics if metrics is not None else run_metrics.load_metrics(config)
    if resolved_metrics.get("gt") is not None:
        print("Rendering metrics comparison plots...")
        metrics_plots.plot_lacey_comparison(resolved_metrics, config, show=viz.show_plots)
        metrics_plots.plot_segregation_profile(resolved_metrics, config, show=viz.show_plots)
        metrics_plots.plot_velocity_distribution(resolved_metrics, config, show=viz.show_plots)
        metrics_plots.plot_granular_temperature(resolved_metrics, config, show=viz.show_plots)
        metrics_plots.plot_computing_speed(resolved_metrics, config, show=viz.show_plots)
        artifacts["metrics"] = resolved_metrics

    if data_io.sorted_frame_files(config.prediction.pred_frames_dir, "pred_frame_*.parquet"):
        print("Building prediction animation...")
        anim_save = VIZ_DIR / "pred_animation.mp4" if viz.save_figures else None
        anim, resolved_anim_path = animate_frames(
            config.prediction.pred_frames_dir, config, "pred_frame_*.parquet", anim_save
        )
        artifacts["animation"] = anim
        if viz.save_figures:
            artifacts["animation_save_path"] = resolved_anim_path

    return artifacts
