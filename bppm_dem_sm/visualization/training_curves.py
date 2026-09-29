"""Plot of GRU training/validation loss curves.

Reads a persisted training history rather than requiring a live Keras
``History`` object in the same process, so it can run standalone in a
``do_visualization``-only pass after ``do_train`` produced
``models/<name>.history.json`` in an earlier run (see
project_structure_proposal.md section 6, "Persist everywhere, render only
in Visualization").
"""

from __future__ import annotations

import json
from pathlib import Path


def plot_training_history(history, save_path=None, show=True):
    """Plot train/validation loss curves from a persisted training history.

    Args:
        history: A ``models/<name>.history.json`` path (``Path`` or ``str``),
            an already-loaded ``{"loss": [...], "val_loss": [...]}`` dict, or
            a Keras ``History`` object (its ``.history`` attribute is used).
            Accepting all three lets this run from a live ``train_and_save``
            call in the same process, or from the file it left behind, in a
            later, separate call.
        save_path: Optional path to save the figure (PNG); ``None`` skips save.
        show: If ``True``, call ``plt.show()``.

    Returns:
        matplotlib.figure.Figure: The loss-curve figure.
    """
    import matplotlib.pyplot as plt

    if hasattr(history, "history"):
        history = history.history
    elif isinstance(history, (str, Path)):
        history = json.loads(Path(history).read_text(encoding="utf-8"))

    fig = plt.figure()
    plt.plot(history["loss"], label="train_loss")
    plt.plot(history["val_loss"], label="val_loss")
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.title("Training History")
    plt.legend()
    plt.grid(True, alpha=0.3)
    if save_path:
        fig.savefig(str(save_path), dpi=140)
        print(f"Saved figure: {save_path}")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return fig
