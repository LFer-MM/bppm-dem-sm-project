"""Plots comparing ground-truth vs. surrogate metrics.

Each plot renders results produced by :mod:`bppm_dem_sm.metrics.run_metrics`
or :mod:`bppm_dem_sm.metrics.computing_speed`.
"""

from __future__ import annotations

import pandas as pd

from ..config import FIGURES_DIR, ExperimentConfig

# --- Public functions --------------------------------------------------------


def plot_lacey_comparison(metrics: dict, config: ExperimentConfig, show=True):
    """Plot ground-truth vs. surrogate Lacey index over time.

    Args:
        metrics: Mapping from :func:`bppm_dem_sm.metrics.run_metrics.compute_metrics`
            (``gt`` / optional ``pred``).
        config: If ``visualization.save_figures``, writes ``lacey_comparison.png``
            under ``FIGURES_DIR``.
        show: If ``True``, display the figure interactively.

    Returns:
        matplotlib.figure.Figure: Lacey-vs-time comparison figure.
    """
    import matplotlib.pyplot as plt

    fig = plt.figure()
    plt.plot(metrics["gt"]["time"], metrics["gt"]["lacey"], label="Ground Truth (DEM)", c="red")
    if "pred" in metrics:
        plt.plot(metrics["pred"]["time"], metrics["pred"]["lacey"], label="Surrogate Model (RNN)", c="blue")

    plt.xlabel("Time (s)")
    plt.ylabel("Lacey's Mixing Index")
    plt.title("LMI vs. Time")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    if config.visualization.save_figures:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIGURES_DIR / "lacey_comparison.png", dpi=140)
    if show:
        plt.show()
    return fig


def plot_segregation_profile(metrics: dict, config: ExperimentConfig, show=True):
    """Plot radial and axial large-particle fraction profiles at the final frame.

    Args:
        metrics: Mapping from :func:`bppm_dem_sm.metrics.run_metrics.compute_metrics`;
            requires ``radial_gt`` and ``axial_gt``, with optional
            ``radial_pred`` / ``axial_pred``.
        config: If ``visualization.save_figures``, writes
            ``segregation_profile_comparison.png`` under ``FIGURES_DIR``.
        show: If ``True``, display the figure interactively.

    Returns:
        matplotlib.figure.Figure: Side-by-side radial/axial profile figure.
    """
    import matplotlib.pyplot as plt

    fig, (ax_radial, ax_axial) = plt.subplots(1, 2, figsize=(10, 4))

    gt_radial = _latest_time_slice(metrics["radial_gt"])
    ax_radial.plot(gt_radial["bin_center"], gt_radial["fraction_large"], "ks", label="DEM (ground truth)")
    if "radial_pred" in metrics:
        pred_radial = _latest_time_slice(metrics["radial_pred"])
        ax_radial.plot(
            pred_radial["bin_center"], pred_radial["fraction_large"],
            "rs", markerfacecolor="none", label="Surrogate model (RNN)",
        )
    ax_radial.set_xlabel("Radial distance from center [m]")
    ax_radial.set_ylabel("Fraction of large particle [-]")
    ax_radial.set_ylim(0.0, 1.0)
    ax_radial.grid(True, alpha=0.3)
    ax_radial.legend()

    gt_axial = _latest_time_slice(metrics["axial_gt"])
    ax_axial.plot(gt_axial["bin_center"], gt_axial["fraction_large"], "ks", label="DEM (ground truth)")
    if "axial_pred" in metrics:
        pred_axial = _latest_time_slice(metrics["axial_pred"])
        ax_axial.plot(
            pred_axial["bin_center"], pred_axial["fraction_large"],
            "rs", markerfacecolor="none", label="Surrogate model (RNN)",
        )
    ax_axial.set_xlabel("Axial distance from center [m]")
    ax_axial.set_ylabel("Fraction of large particle [-]")
    ax_axial.set_ylim(0.0, 1.0)
    ax_axial.grid(True, alpha=0.3)
    ax_axial.legend()

    fig.suptitle("Large-particle fraction profile (final frame)")
    plt.tight_layout()

    if config.visualization.save_figures:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIGURES_DIR / "segregation_profile_comparison.png", dpi=140)
    if show:
        plt.show()
    return fig


def plot_velocity_distribution(metrics: dict, config: ExperimentConfig, show=True):
    """Plot small/large particle absolute-velocity distributions, DEM vs. surrogate.

    Args:
        metrics: Mapping from :func:`bppm_dem_sm.metrics.run_metrics.compute_metrics`;
            requires ``velocity_gt``, with optional ``velocity_pred``.
        config: If ``visualization.save_figures``, writes
            ``velocity_distribution_comparison.png`` under ``FIGURES_DIR``.
        show: If ``True``, display the figure interactively.

    Returns:
        matplotlib.figure.Figure | None: Side-by-side histogram figure, or
        ``None`` if ``velocity_gt`` is unavailable.
    """
    if "velocity_gt" not in metrics:
        print("Skipping velocity distribution plot: no velocity_gt in metrics.")
        return None

    import matplotlib.pyplot as plt

    gt_speed = metrics["velocity_gt"]["speed"]
    pred_speed = metrics.get("velocity_pred", {}).get("speed") if "velocity_pred" in metrics else None

    fig, (ax_small, ax_large) = plt.subplots(1, 2, figsize=(10, 4))
    for ax, species, title in ((ax_small, "small", "Small particles"), (ax_large, "large", "Large particles")):
        ax.hist(gt_speed[species], bins=30, density=True, histtype="step", color="black", label="DEM (ground truth)")
        if pred_speed is not None:
            ax.hist(
                pred_speed[species], bins=30, density=True, histtype="step", color="blue",
                label="Surrogate model (RNN)",
            )
        ax.set_title(title)
        ax.set_xlabel("Absolute velocity [m/s]")
        ax.set_ylabel("Density")
        ax.grid(True, alpha=0.3)
        ax.legend()

    fig.suptitle("Particle velocity distribution (final frame pair)")
    plt.tight_layout()

    if config.visualization.save_figures:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIGURES_DIR / "velocity_distribution_comparison.png", dpi=140)
    if show:
        plt.show()
    return fig


def plot_granular_temperature(metrics: dict, config: ExperimentConfig, show=True):
    """Plot boxplots of per-cell granular temperature, DEM vs. surrogate.

    Args:
        metrics: Mapping from :func:`bppm_dem_sm.metrics.run_metrics.compute_metrics`;
            requires ``velocity_gt``, with optional ``velocity_pred``.
        config: If ``visualization.save_figures``, writes
            ``granular_temperature_comparison.png`` under ``FIGURES_DIR``.
        show: If ``True``, display the figure interactively.

    Returns:
        matplotlib.figure.Figure | None: Boxplot figure, or ``None`` if
        ``velocity_gt`` is unavailable.
    """
    if "velocity_gt" not in metrics:
        print("Skipping granular temperature plot: no velocity_gt in metrics.")
        return None

    import matplotlib.pyplot as plt

    data = [metrics["velocity_gt"]["granular_temperature"]]
    labels = ["DEM\n(ground truth)"]
    if "velocity_pred" in metrics:
        data.append(metrics["velocity_pred"]["granular_temperature"])
        labels.append("Surrogate model\n(RNN)")

    fig = plt.figure()
    plt.boxplot(data, showmeans=True)
    plt.xticks(range(1, len(labels) + 1), labels)
    plt.yscale("log")
    plt.ylabel("Granular temperature [m^2/s^2]")
    plt.title("Granular temperature (final frame pair)")
    plt.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()

    if config.visualization.save_figures:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIGURES_DIR / "granular_temperature_comparison.png", dpi=140)
    if show:
        plt.show()
    return fig


def plot_computing_speed(metrics: dict, config: ExperimentConfig, show=True):
    """Plot dimensionless computing speed vs. the DEM reference (paper Fig. 15).

    Args:
        metrics: Mapping with an optional ``"computing_speed"`` entry from
            :func:`bppm_dem_sm.metrics.computing_speed.compute_computing_speed`
            (set by :func:`bppm_dem_sm.experiment_pipeline.run_experiment_pipeline`,
            or loaded from disk by
            :func:`~bppm_dem_sm.metrics.run_metrics.load_metrics`; absent if
            neither ever ran).
        config: If ``visualization.save_figures``, writes
            ``computing_speed_comparison.png`` under ``FIGURES_DIR``.
        show: If ``True``, display the figure interactively.

    Returns:
        matplotlib.figure.Figure | None: Bar-chart figure, or ``None`` if no
        speedup could be computed (no timing recorded this run).
    """
    cs = metrics.get("computing_speed")
    if not cs:
        print("Skipping computing speed plot: no computing_speed in metrics.")
        return None

    bars = []
    if cs.get("all_steps_speedup") is not None:
        bars.append(("All RNNSR\nsteps", cs["all_steps_speedup"]))
    if cs.get("prediction_only_speedup") is not None:
        bars.append(("Prediction\nonly", cs["prediction_only_speedup"]))
    if not bars:
        print("Skipping computing speed plot: no timed stage available.")
        return None

    import matplotlib.pyplot as plt

    labels, values = zip(*bars)
    fig = plt.figure()
    plt.bar(labels, values, color=["orange", "royalblue"][: len(bars)])
    plt.axhline(1.0, color="black", linewidth=0.8, linestyle="--", label="DEM (reference)")
    plt.yscale("log")
    plt.ylabel("Dimensionless computing speed [-]")
    plt.title(f"Computing speed vs. DEM reference ({cs['dem_reference_seconds'] / 3600:.2f} h)")
    plt.grid(True, alpha=0.3, axis="y")
    plt.legend()
    plt.tight_layout()

    if config.visualization.save_figures:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(FIGURES_DIR / "computing_speed_comparison.png", dpi=140)
    if show:
        plt.show()
    return fig


# --- Private helper functions ------------------------------------------------


def _latest_time_slice(profile_df: pd.DataFrame) -> pd.DataFrame:
    """Return the rows for the last (largest) ``frame`` in a profile summary."""
    return profile_df[profile_df["frame"] == profile_df["frame"].max()].sort_values("bin")
