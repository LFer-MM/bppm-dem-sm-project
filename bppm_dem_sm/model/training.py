"""RNNSR training (Step 3): trains the GRU and fits the SR model on the same frames.

Loads the short-time training frames once and hands them to each half:
:func:`bppm_dem_sm.model.rnn.training.train_and_save_rnn` and
:func:`bppm_dem_sm.model.sr.fitting.fit_and_save_sr`. Both models are saved
side by side (``<model>.keras`` and ``<model>.sr.npz``), so prediction can
load the pair instead of refitting.
"""

from __future__ import annotations

from ..config import ExperimentConfig
from ..data_processing import frames as data_io
from .rnn.training import train_and_save_rnn
from .sr.fitting import fit_and_save_sr


def train_and_save(config: ExperimentConfig):
    """Train the GRU and fit the SR model on ``config.train_data_dir``; save both.

    The SR model is fitted on the raw positions and DEM velocities (Eq. 2),
    the GRU on their local mean components (Eq. 1). The SR model is fitted
    whether or not ``stochastic.enabled`` is set, so the saved pair is always
    complete.

    Args:
        config: Pipeline settings (train data dir, epochs, batch size, etc.).

    Returns:
        tuple: ``(model, history)`` -- the trained
        :class:`~bppm_dem_sm.model.rnn.model.RNNModel` and the Keras
        ``History`` object.
    """
    pos, rad, _ = data_io.load_frames_stacked(config.train_data_dir, config.frame_glob, config.feature_cols)
    vel = data_io.load_velocities_stacked(config.train_data_dir, config.frame_glob)

    model, history = train_and_save_rnn(pos, rad, vel, config)
    fit_and_save_sr(pos, vel, config)
    return model, history
