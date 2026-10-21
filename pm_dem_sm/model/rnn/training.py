"""GRU training: fits the GRU and persists it with its loss history (TensorFlow imported lazily).

No rendering happens here. ``train_and_save_rnn`` persists ``history.history``
to a ``<model_path stem>.history.json`` sibling of the saved model, so the
loss curve survives a ``do_train``-only run;
:func:`pm_dem_sm.visualization.training_curves.plot_training_history`
reads that file, gated by ``ExperimentConfig.do_visualization``, same as
every other plot in this project (see ``project_structure_proposal.md``
section 6, "Persist everywhere, render only in Visualization").
"""

from __future__ import annotations

import json
from pathlib import Path

from ...config import ExperimentConfig
from ...data_processing import dataset as data_ds
from .model import RNNModel


def train_and_save_rnn(pos, rad, vel, config: ExperimentConfig):
    """Train the GRU on stacked training frames; save it and its loss history.

    Converts the training trajectories to their local mean components
    (Kishida et al. 2025, Eq. 1) when ``training.local_mean_conversion`` is
    set, builds a supervised sliding-window dataset, fits the model, writes a
    ``.keras`` artifact to ``config.model_path`` and a sibling
    ``<name>.history.json`` with the per-epoch ``loss``/``val_loss`` arrays.

    Args:
        pos: Raw position tensor of shape ``(T, N, 3)``.
        rad: Radius tensor of shape ``(T, N, 1)``.
        vel: DEM velocity tensor of shape ``(T, N, 3)``, used by the Eq. 1
            conversion.
        config: Pipeline settings (model path, epochs, batch size, etc.).

    Returns:
        tuple: ``(model, history)`` -- the trained
        :class:`~pm_dem_sm.model.rnn.model.RNNModel` and the Keras
        ``History`` object.
    """
    train = config.training
    if train.local_mean_conversion:
        pos = data_ds.local_mean_positions(pos, vel, config.prediction.dt_step)
    X, y = data_ds.build_supervised_dataset(pos, rad, config.frames_in)
    Xtr, ytr, Xval, yval = data_ds.train_test_split(X, y, train.val_fraction, train.seed)

    model = RNNModel.build(
        config.frames_in,
        n_features=X.shape[-1],
        gru_units=train.gru_units,
        dense_units=train.dense_units,
        learning_rate=train.learning_rate,
    )
    model.network.summary()

    print("Fitting GRU surrogate...")
    history = model.network.fit(
        Xtr, ytr,
        validation_data=(Xval, yval),
        epochs=train.epochs,
        batch_size=train.batch_size,
        verbose=1,
    )

    save_path = Path(config.model_path)
    if save_path.suffix != ".keras":
        save_path = save_path.with_suffix(".keras")
    model.save(save_path)
    print(f"Saved model to: {save_path}")

    history_path = save_path.with_suffix(".history.json")
    history_path.write_text(json.dumps(history.history), encoding="utf-8")
    print(f"Saved training history to: {history_path}")

    return model, history
