"""RNNSR prediction (Step 4): sliding-window GRU prediction plus the SR model's noise."""

from __future__ import annotations

from collections import deque
import os

import numpy as np
import pandas as pd

from ..config import ID_COL, ExperimentConfig
from ..data_processing import frames as data_io
from ..progress import track
from .rnn.loading import load_rnn
from .sr.loading import load_sr


def predict_frames(config: ExperimentConfig, model=None, sr_model=None) -> pd.DataFrame:
    """Slide a window over frames, predict next positions, and save parquets.

    This is the RNNSR's Step 4: the GRU predicts the local mean position
    ``x_bar`` and, when ``stochastic.enabled`` is set, the SR model's local
    variability velocity ``v_tilde`` is added as
    ``x = x_bar + v_tilde * dt_step`` (Kishida et al. 2025, Eq. 4).

    Writes one ``pred_frame_XXXXX.parquet`` per step under
    ``config.prediction.pred_frames_dir`` and a combined
    ``predictions_all.parquet`` under ``config.prediction.pred_out_dir``.

    Args:
        config: Pipeline settings (data dir, model path, window length, dt, etc.).
        model: Optional pre-loaded model; if ``None``, loads ``config.model_path``.
        sr_model: Optional fitted :class:`~bppm_dem_sm.model.sr.model.SRModel`; if
            ``None`` and SR is enabled, loads the one saved next to
            ``config.model_path`` by training.

    Raises:
        FileNotFoundError: If SR is enabled, ``sr_model`` is ``None``, and no
            saved SR model sits next to ``config.model_path``.

    Returns:
        pandas.DataFrame: Combined predictions with ``frame_pred``, ``step``,
        ``id``, ``x``, ``y``, ``z``, ``dt``, and ``r`` columns.
    """
    pred = config.prediction
    pred.pred_frames_dir.mkdir(parents=True, exist_ok=True)

    feature_cols = config.feature_cols
    cols_needed = [ID_COL] + feature_cols
    frame_files = data_io.sorted_frame_files(config.data_dir, config.frame_glob)
    T = len(frame_files)
    start, seq_len = pred.start_frame, config.frames_in

    if model is None:
        model = load_rnn(config.model_path)
    print("Model input_shape:", model.input_shape, "output_shape:", model.output_shape)

    sr_opts = config.stochastic
    rng = None
    if sr_opts.enabled:
        if sr_model is None:
            sr_model = load_sr(config.model_path)
        rng = np.random.default_rng(sr_opts.stochastic_seed)

    base_df = data_io.load_frame(frame_files[start], cols_needed)
    base_ids = base_df[ID_COL].to_numpy()
    base_r = base_df["r"].to_numpy()

    window: deque = deque(maxlen=seq_len)
    for k in track(range(seq_len), desc="Loading seed frames", unit="frame"):
        df = data_io.load_frame(frame_files[start + k], cols_needed)
        window.append(df[feature_cols].to_numpy(np.float32))

    steps = T - (start + seq_len) if pred.predict_until_end else pred.max_steps

    all_rows = []
    for step in track(range(steps), desc="Predicting frames", unit="frame"):
        target_frame_idx = start + seq_len + step
        x_in = np.stack(window, axis=1)  # (N, seq_len, F)

        yhat = model.predict(x_in, batch_size=pred.predict_batch_size, verbose=0)
        xyz = yhat[:, :3].astype(np.float32)

        if sr_opts.enabled:
            v_tilde = sr_model.sample(window[-1][:, :3], rng)  # Eq. 3, at the current cell
            xyz = xyz + v_tilde * pred.dt_step  # Eq. 4

        pred_df = pd.DataFrame(
            {
                "id": base_ids,
                "x": xyz[:, 0],
                "y": xyz[:, 1],
                "z": xyz[:, 2],
                "dt": pred.dt0 + step * pred.dt_step,
                "r": base_r,
            }
        )
        pred_path = os.path.join(str(pred.pred_frames_dir), f"pred_frame_{target_frame_idx:05d}.parquet")
        pred_df.to_parquet(pred_path, index=False)

        row = pred_df.copy()
        row.insert(0, "frame_pred", target_frame_idx)
        row.insert(1, "step", step)
        all_rows.append(row)

        if pred.autoregressive:
            last_feats = window[-1].copy()
            last_feats[:, :3] = xyz  # x, y, z are the first 3 feature columns
            window.append(last_feats)
        else:
            next_df = data_io.load_frame(frame_files[target_frame_idx], cols_needed)
            window.append(next_df[feature_cols].to_numpy(np.float32))

    combined = pd.concat(all_rows, ignore_index=True)
    combined.to_parquet(str(pred.pred_combined_parquet), index=False)
    print(f"Saved predictions under: {pred.pred_out_dir}")
    return combined
