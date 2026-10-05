"""Draw the explanatory diagrams embedded in the examples docs.

Writes PNGs into ``docs/source/examples/_images/``. These are schematics, not
results, so they need no data; rerun this script after editing one:

    python docs/scripts/make_diagrams.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

# --- Constants ---------------------------------------------------------------

OUT_DIR = Path(__file__).resolve().parents[1] / "source" / "examples" / "_images"
DPI = 150

# Okabe-Ito colorblind-safe palette.
STAGE = "#0072B2"  # pipeline stages
DATA = "#E8EEF4"  # files on disk
GT = "#999999"  # ground-truth frames
PRED = "#E69F00"  # predicted frames / targets
INPUT = "#56B4E9"  # model input window
INK = "#222222"
_NODE_W = 1.7  # box width (in) for stages and file sets


# --- Public functions --------------------------------------------------------


def pipeline_stages(path):
    """Draw the six stages and the folders each one reads and writes."""
    fig, ax = plt.subplots(figsize=(14, 4.8))
    _canvas(ax, 14, 4.8)

    half = _NODE_W / 2
    y, y_top = 1.8, 3.85
    xs = [1.0 + 2.0 * i for i in range(7)]
    chain = [
        ("stage", "Simulation\ndo_simulate"),
        ("data", "raw CSV frames\nraw_data_dir"),
        ("stage", "Data processing\ndo_process"),
        ("data", "parquet frames\ndata_dir"),
        ("stage", "Prediction\ndo_predict"),
        ("data", "pred. frames\npred_frames_dir"),
        ("stage", "Metrics\ndo_metrics"),
    ]
    for (kind, text), x in zip(chain, xs):
        _node(ax, kind, text, x, y)
    for x0, x1 in zip(xs, xs[1:]):
        _arrow(ax, (x0 + half, y), (x1 - half, y))

    # Training branch: reference window -> model, which prediction loads.
    _node(ax, "data", "ref. window\ntrain_data_dir", xs[2], y_top)
    _node(ax, "stage", "Training\ndo_train", xs[3], y_top)
    _node(ax, "data", "model_path\n+ history.json", xs[4], y_top)
    _arrow(ax, (xs[2] + half, y_top), (xs[3] - half, y_top))
    _arrow(ax, (xs[3] + half, y_top), (xs[4] - half, y_top))
    _arrow(ax, (xs[4], y_top - 0.38), (xs[4], y + 0.38))
    ax.text(xs[2], y_top + 0.58, "prepared beforehand", ha="center", fontsize=8.5,
            style="italic", color=INK)

    # Metrics scores ground truth too, and writes tables that visualization renders.
    _arrow(ax, (xs[3], y - 0.38), (xs[6], y - 0.38), rad=0.18, dashed=True)
    ax.text((xs[3] + xs[6]) / 2, 0.68, "ground truth, for comparison", ha="center",
            fontsize=8.5, style="italic", color=INK)
    _node(ax, "data", "metric tables\n+ JSON", xs[6], y_top)
    _node(ax, "stage", "Visualization\ndo_visualization", xs[5], y_top)
    _arrow(ax, (xs[6], y + 0.38), (xs[6], y_top - 0.38))
    _arrow(ax, (xs[6] - half, y_top), (xs[5] + half, y_top))
    ax.text(xs[5], y_top + 0.58, "also reads history.json and frames", ha="center",
            fontsize=8.5, style="italic", color=INK)

    _legend(ax, [(STAGE, "stage (flag)"), (DATA, "files on disk")], 0.15, 0.25)
    _save(fig, path)


def sliding_window(path):
    """Draw how 20 training frames become 5 overlapping (X, y) windows."""
    n_frames, frames_in = 20, 15
    n_windows = n_frames - frames_in
    fig, ax = plt.subplots(figsize=(12, 4.3))
    _canvas(ax, 12, 4.3)

    x0, w = 1.55, 0.5
    ax.text(0.1, 3.55, "frames\n(3.0-4.0 s)", fontsize=9, va="center", color=INK)
    for t in range(n_frames):
        _cell(ax, x0 + t * w, 3.55, w, DATA)
        ax.text(x0 + t * w, 3.55, str(t), ha="center", va="center", fontsize=8, color=INK)

    for k in range(n_windows):
        yk = 2.8 - k * 0.5
        ax.text(0.1, yk, f"window {k}", fontsize=9, va="center", color=INK)
        for t in range(k, k + frames_in):
            _cell(ax, x0 + t * w, yk, w, INPUT)
        _cell(ax, x0 + (k + frames_in) * w, yk, w, PRED)

    ax.text(
        x0 + n_frames * w + 0.15, 1.8,
        f"X: {frames_in} frames of (x, y, z, r)\ny: next (x, y, z)\n\n"
        f"{n_frames} - {frames_in} = {n_windows} windows per particle,\n"
        "x N particles, stride 1:\nneighbours share 14 of 15 frames",
        fontsize=9, va="center", color=INK,
    )
    _legend(ax, [(INPUT, "input window (X)"), (PRED, "target (y)")], 0.1, 0.32)
    _save(fig, path)


def prediction_modes(path):
    """Draw where each new window frame comes from: ground truth vs. own prediction."""
    shown, steps = 5, 3
    fig, ax = plt.subplots(figsize=(12, 5.2))
    _canvas(ax, 12, 5.2)

    rows = [("Teacher-forced (autoregressive=False)", 4.35, False),
            ("Autoregressive (autoregressive=True)", 1.85, True)]
    w = 0.42
    for title, ytop, autoregressive in rows:
        ax.text(0.1, ytop + 0.55, title, fontsize=10.5, weight="bold", color=INK)
        for s in range(steps):
            ys = ytop - s * 0.5
            ax.text(0.1, ys, f"step {s}", fontsize=9, va="center", color=INK)
            for j in range(shown):
                frame = s + j  # position in time; frames >= shown are new
                own = autoregressive and frame >= shown
                color = PRED if own else GT
                label = f"p{frame - shown + 1}" if own else f"f{frame}"
                _cell(ax, 1.2 + (s + j) * w, ys, w, color)
                ax.text(1.2 + (s + j) * w, ys, label, ha="center", va="center", fontsize=7.5, color=INK)
            xs = 1.2 + (s + shown) * w
            _arrow(ax, (xs - 0.15, ys), (xs + 0.55, ys))
            ax.text(xs + 0.62, ys, "GRU", fontsize=8.5, va="center", color=INK)
            _cell(ax, xs + 1.25, ys, w, PRED)
            ax.text(xs + 1.25, ys, f"p{s + 1}", ha="center", va="center", fontsize=7.5, color=INK)

    note = (
        f"frames_in = 15 ({shown} drawn).\n\n"
        "Teacher-forced: the next window always\n"
        "slides in the next ground-truth frame, so\n"
        "errors never compound (one-step accuracy).\n\n"
        "Autoregressive: each prediction becomes\n"
        "input, as when replacing DEM; errors can\n"
        "accumulate over the rollout."
    )
    ax.text(7.6, 2.75, note, fontsize=9, va="center", color=INK)
    _legend(ax, [(GT, "ground-truth frame"), (PRED, "model prediction")], 0.1, 0.32)
    _save(fig, path)


# --- Private helper functions ------------------------------------------------


def _canvas(ax, width, height):
    """Set data coordinates to inches and hide the axes."""
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.axis("off")


def _node(ax, kind, text, x, y):
    """Draw a stage (filled) or a file set (pale) box centred at ``(x, y)``."""
    face, color = (STAGE, "white") if kind == "stage" else (DATA, INK)
    ax.add_patch(FancyBboxPatch(
        (x - _NODE_W / 2, y - 0.38), _NODE_W, 0.76,
        boxstyle="round,pad=0.02,rounding_size=0.12",
        facecolor=face, edgecolor=STAGE, linewidth=1.2,
    ))
    ax.text(x, y, text, ha="center", va="center", fontsize=8.5 if kind == "stage" else 8, color=color,
            family="monospace" if kind == "data" else None,
            weight="bold" if kind == "stage" else "normal")


def _cell(ax, x, y, w, face):
    """Draw one frame square centred at ``(x, y)``."""
    ax.add_patch(FancyBboxPatch(
        (x - w / 2 + 0.03, y - 0.18), w - 0.06, 0.36,
        boxstyle="round,pad=0,rounding_size=0.05",
        facecolor=face, edgecolor="white", linewidth=0.8,
    ))


def _arrow(ax, start, end, rad=0.0, dashed=False):
    """Draw an arrow from ``start`` to ``end``."""
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=12, color=INK, linewidth=1.1,
        connectionstyle=f"arc3,rad={rad}", linestyle="--" if dashed else "-",
    ))


def _legend(ax, items, x, y):
    """Draw a one-row legend of colour swatches starting at ``(x, y)``."""
    for color, label in items:
        _cell(ax, x + 0.2, y, 0.4, color)
        ax.text(x + 0.5, y, label, fontsize=8.5, va="center", color=INK)
        x += 0.75 + 0.075 * len(label)


def _save(fig, path):
    """Write ``fig`` to ``path`` with a white background and close it."""
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {path}")


# --- Script entry point ------------------------------------------------------

if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pipeline_stages(OUT_DIR / "pipeline_stages.png")
    sliding_window(OUT_DIR / "sliding_window.png")
    prediction_modes(OUT_DIR / "prediction_modes.png")
