"""End-to-end orchestration for one reproducible run of the study.

``run_experiment_pipeline`` can span all six stages -- Simulation, Data
Processing, Training, Prediction, Metrics, Visualization -- or any subset,
gated by ``ExperimentConfig``'s ``do_*`` flags. Each stage is also
importable on its own. Renamed from ``pipeline.py``/``run_pipeline`` because
it now configures a physics simulation too, not just the ML side; see
:class:`bppm_dem_sm.config.ExperimentConfig`.

``do_simulate`` differs from every other stage: ``yade_dem/run_simulation.py``
runs under YADE's own patched Python, not this venv, so it goes through
:func:`bppm_dem_sm.simulation.launcher.launch_simulation` (a subprocess),
not a direct import -- and it's the only stage with an external, optional
dependency (YADE itself). ``launch_simulation`` already raises
``FileNotFoundError`` if YADE isn't on PATH, and ``NotImplementedError`` for
``dem_backend="blaze"`` (not implemented yet); this function lets both
propagate rather than swallowing them, same as any other stage failure.

Rendering happens nowhere but ``do_visualization`` -- ``do_train``,
``do_process``, ``do_predict``, and ``do_metrics`` only compute and persist.
See project_structure_proposal.md section 6.
"""

from __future__ import annotations

import time

from .config import ExperimentConfig
from .data_processing import run_data_processing
from .metrics import computing_speed, run_metrics
from .model.rnn import prediction, training
from .progress import complete, plan, stage
from .simulation import launcher
from .tf_quiet import silence_tensorflow
from .visualization import run_visualization


def run_experiment_pipeline(config: ExperimentConfig | None = None, **overrides):
    """Run the configurable six-stage experiment; returns a dict of artifacts.

    Stages (each gated by the corresponding ``do_*`` flag on ``config``, in
    execution order):

    1. Launch a DEM simulation (``config.dem_backend``; YADE implemented,
       BlazeDEM not yet)
    2. Convert raw CSV frames to parquet + an integrity check
    3. Train the GRU surrogate
    4. Predict frames with a sliding window
    5. Compute mixing/segregation metrics: Lacey's mixing index, radial/axial
       large-particle fraction profile, particle velocity distribution,
       granular temperature, and dimensionless computing speed vs. a
       user-supplied DEM reference time
    6. Render every plot: training curves, both cell grids, the metrics
       comparisons, and the prediction animation

    Training and prediction wall-clock time are recorded automatically; the
    DEM side of the computing-speed comparison is not, unless
    ``do_simulate`` itself is timed by the caller (see
    :class:`~bppm_dem_sm.config.ComputingSpeedOptions`).

    Args:
        config: Base pipeline configuration; ``None`` uses defaults.
        **overrides: Field overrides applied via
            :meth:`ExperimentConfig.with_overrides`. Accepts core fields
            (``do_train=True``), nested leaf names (``epochs=5``), or whole
            option groups (``training=TrainingOptions(epochs=5)``).

    Returns:
        dict: Artifacts keyed by stage (``config``, and optionally
        ``dem_simulation``, ``data_processing``, ``model``, ``history``,
        ``predictions``, ``metrics``, ``visualizations``, ``timing`` with
        ``train_seconds``/``predict_seconds`` for stages run).
    """
    silence_tensorflow()
    config = (config or ExperimentConfig()).with_overrides(**overrides)

    results: dict = {"config": config}
    timing: dict = {}
    model = None

    titles = [
        name
        for enabled, name in (
            (config.do_simulate, "Simulation"),
            (config.do_process, "Data Processing"),
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

    if config.do_simulate:
        step += 1
        stage(step, n_stages, "Simulation")
        results["dem_simulation"] = launcher.launch_simulation(backend=config.dem_backend)

    if config.do_process:
        step += 1
        stage(step, n_stages, "Data Processing")
        results["data_processing"] = run_data_processing.process_frames(config)

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
        metrics["computing_speed"] = computing_speed.compute_computing_speed(timing, config)
        results["metrics"] = metrics

    if config.do_visualization:
        step += 1
        stage(step, n_stages, "Visualization")
        results["visualizations"] = run_visualization.generate_visualizations(
            config, metrics=results.get("metrics")
        )

    complete()
    return results
