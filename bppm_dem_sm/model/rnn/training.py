"""GRU surrogate training: persists the model and its loss history (TensorFlow imported lazily).

No rendering happens here. ``train_and_save`` persists ``history.history``
to a ``<model_path stem>.history.json`` sibling of the saved model, so the
loss curve survives a ``do_train``-only run;
:func:`bppm_dem_sm.visualization.training_curves.plot_training_history`
reads that file, gated by ``ExperimentConfig.do_visualization``, same as
every other plot in this project (see ``project_structure_proposal.md``
section 6, "Persist everywhere, render only in Visualization").
"""

from __future__ import annotations

import json
from pathlib import Path

from ...config import ExperimentConfig
from ...data_processing import dataset as data_ds
from ...data_processing import frames as data_io
from .architecture import build_model


def train_and_save(config: ExperimentConfig):
    """Train the GRU surrogate on ``config.train_data_dir``; save it and its loss history.

    Builds a supervised sliding-window dataset, fits the model, writes a
    ``.keras`` artifact to ``config.model_path`` and a sibling
    ``<name>.history.json`` with the per-epoch ``loss``/``val_loss`` arrays.

    Args:
        config: Pipeline settings (train data dir, epochs, batch size, etc.).

    Returns:
        tuple: ``(model, history)`` -- the trained Keras model and its
        ``History`` object.
    """
    train = config.training
    pos, rad, _ = data_io.load_frames_stacked(config.train_data_dir, config.frame_glob, config.feature_cols)
    X, y = data_ds.build_supervised_dataset(pos, rad, config.frames_in)
    Xtr, ytr, Xval, yval = data_ds.train_test_split(X, y, train.val_fraction, train.seed)

    model = build_model(
        config.frames_in,
        n_features=X.shape[-1],
        gru_units=train.gru_units,
        dense_units=train.dense_units,
        learning_rate=train.learning_rate,
    )
    model.summary()

    print("Fitting GRU surrogate...")
    history = model.fit(
        Xtr, ytr,
        validation_data=(Xval, yval),
        epochs=train.epochs,
        batch_size=train.batch_size,
        verbose=1,
    )

    save_path = Path(config.model_path)
    if save_path.suffix != ".keras":
        save_path = save_path.with_suffix(".keras")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(save_path))
    print(f"Saved model to: {save_path}")

    history_path = save_path.with_suffix(".history.json")
    history_path.write_text(json.dumps(history.history), encoding="utf-8")
    print(f"Saved training history to: {history_path}")

    return model, history
