"""Plot of GRU training/validation loss curves."""

from __future__ import annotations


def plot_training_history(history, show=True):
    """Plot train/validation loss curves from a keras History.

    Args:
        history: Keras ``History`` from ``model.fit`` (expects ``loss`` and
            ``val_loss`` keys).
        show: If ``True``, call ``plt.show()``.

    Returns:
        matplotlib.figure.Figure: The loss-curve figure.
    """
    import matplotlib.pyplot as plt

    fig = plt.figure()
    plt.plot(history.history["loss"], label="train_loss")
    plt.plot(history.history["val_loss"], label="val_loss")
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.title("Training History")
    plt.legend()
    plt.grid(True, alpha=0.3)
    if show:
        plt.show()
    return fig
