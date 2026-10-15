"""RNNSR training (Step 3): fits the GRU and the SR model, persists both (TensorFlow imported lazily).

No rendering happens here. ``train_and_save`` persists ``history.history``
to a ``<model_path stem>.history.json`` sibling of the saved model, so the
loss curve survives a ``do_train``-only run;
:func:`bppm_dem_sm.visualization.training_curves.plot_training_history`
reads that file, gated by ``ExperimentConfig.do_visualization``, same as
every other plot in this project (see ``project_structure_proposal.md``
section 6, "Persist everywhere, render only in Visualization").

The SR model is fitted on the same short-time frames, as in Step 3 of
Kishida et al. (2025), and saved as a ``<model_path stem>.sr.npz`` sibling
so prediction can load it instead of refitting.
"""

from __future__ import annotations

import json
from pathlib import Path

from ...config import ExperimentConfig
from ...data_processing import dataset as data_ds
from ...data_processing import frames as data_io
from .. import sr
from .architecture import build_rnn


def train_and_save(config: ExperimentConfig):
    """Train the GRU and fit the SR model on ``config.train_data_dir``; save both.

    Fits the SR model's sigma_v(x) on the raw positions and DEM velocities
    (Eq. 2) and saves it to ``sr.sr_path_for(model_path)``. Then converts the training trajectories to their local mean components
    (Kishida et al. 2025, Eq. 1) when ``training.local_mean_conversion`` is
    set, builds a supervised sliding-window dataset, fits the model, writes a
    ``.keras`` artifact to ``config.model_path`` and a sibling
    ``<name>.history.json`` with the per-epoch ``loss``/``val_loss`` arrays.
    The SR model is fitted whether or not ``stochastic.enabled`` is set, so
    the saved pair is always complete.

    Args:
        config: Pipeline settings (train data dir, epochs, batch size, etc.).

    Returns:
        tuple: ``(model, history)`` -- the trained Keras model and its
        ``History`` object.
    """
    train = config.training
    pos, rad, _ = data_io.load_frames_stacked(config.train_data_dir, config.frame_glob, config.feature_cols)
    vel = data_io.load_velocities_stacked(config.train_data_dir, config.frame_glob)

    sc = config.stochastic
    sr_model = sr.fit_sr(
        pos, vel, cell_size=sc.velocity_cell_size, min_particles_per_cell=sc.velocity_min_particles_per_cell
    )

    if train.local_mean_conversion:
        pos = data_ds.local_mean_positions(pos, vel, config.prediction.dt_step)
    X, y = data_ds.build_supervised_dataset(pos, rad, config.frames_in)
    Xtr, ytr, Xval, yval = data_ds.train_test_split(X, y, train.val_fraction, train.seed)

    model = build_rnn(
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

    sr_path = sr.sr_path_for(save_path)
    sr_model.save(sr_path)
    print(f"Saved SR model to: {sr_path}")

    return model, history
