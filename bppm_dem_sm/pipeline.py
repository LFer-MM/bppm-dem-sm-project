"""End-to-end orchestration for the RNN surrogate model.

``run_pipeline`` reads frames, optionally trains, predicts, computes mixing
and segregation metrics, and renders visualizations. Each stage is also
importable on its own.
"""

from __future__ import annotations

import time

from .config import PipelineConfig
from .metrics import run_metrics
from .model import prediction, training
from .progress import complete, plan, stage
from .tf_quiet import silence_tensorflow
from .visualization import metrics_plots, run_visualization


def run_pipeline(config: PipelineConfig | None = None, **overrides):
    """Run the configurable surrogate pipeline; returns a dict of artifacts.

    Stages (each gated by the corresponding ``do_*`` flag on ``config``):

    1. Train the GRU surrogate
    2. Predict frames with a sliding window
    3. Compute mixing/segregation metrics: Lacey's mixing index, radial/axial
       large-particle fraction profile, particle velocity distribution,
       granular temperature, and dimensionless computing speed vs. a
       user-supplied DEM reference time
    4. Generate cell-grid and animation visualizations

    Training and prediction wall-clock time are recorded automatically; the
    DEM side of the computing-speed comparison is not (see
    :class:`~bppm_dem_sm.config.ComputingSpeedOptions`).

    Args:
        config: Base pipeline configuration; ``None`` uses defaults.
        **overrides: Field overrides applied via
            :meth:`PipelineConfig.with_overrides`. Accepts core fields
            (``do_train=True``), nested leaf names (``epochs=5``), or whole
            option groups (``training=TrainingOptions(epochs=5)``).

    Returns:
        dict: Artifacts keyed by stage (``config``, and optionally ``model``,
        ``history``, ``predictions``, ``metrics``, ``visualizations``,
        ``timing`` with ``train_seconds``/``predict_seconds`` for stages run).
    """
    silence_tensorflow()
    config = (config or PipelineConfig()).with_overrides(**overrides)

    results: dict = {"config": config}
    timing: dict = {}
    model = None

    titles = [
        name
        for enabled, name in (
            (config.do_train, "Training"),
            (config.do_predict, "Prediction"),
            (config.do_metrics, "Metrics"),
            (config.do_visualization, "Visualization"),
        )
        if enabled
    ]
    plan(titles)
    n_stages = len(titles)
    step = 0

    if config.do_train:
        step += 1
        stage(step, n_stages, "Training")
        t0 = time.perf_counter()
        model, results["history"] = training.train_and_save(config)
        timing["train_seconds"] = time.perf_counter() - t0
        results["model"] = model

    if config.do_predict:
        step += 1
        stage(step, n_stages, "Prediction")
        t0 = time.perf_counter()
        results["predictions"] = prediction.predict_frames(config, model=model)
        timing["predict_seconds"] = time.perf_counter() - t0

    if timing:
        results["timing"] = timing

    if config.do_metrics:
        step += 1
        stage(step, n_stages, "Metrics")
        metrics = run_metrics.compute_metrics(config)
        metrics["computing_speed"] = run_metrics.compute_computing_speed(timing, config)
        results["metrics"] = metrics
        viz = config.visualization
        if viz.show_plots or viz.save_figures:
            metrics_plots.plot_lacey_comparison(metrics, config, show=viz.show_plots)
            metrics_plots.plot_segregation_profile(metrics, config, show=viz.show_plots)
            metrics_plots.plot_velocity_distribution(metrics, config, show=viz.show_plots)
            metrics_plots.plot_granular_temperature(metrics, config, show=viz.show_plots)
            metrics_plots.plot_computing_speed(metrics, config, show=viz.show_plots)

    if config.do_visualization:
        step += 1
        stage(step, n_stages, "Visualization")
        results["visualizations"] = run_visualization.generate_visualizations(config)

    complete()
    return results
