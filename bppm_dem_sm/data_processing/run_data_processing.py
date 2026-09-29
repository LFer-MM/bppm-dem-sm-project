"""Orchestrates the Data Processing stage: raw CSVs -> parquet + integrity check.

``frames.py``/``dataset.py`` stay library code, imported piecemeal by
``model.rnn.training``, ``model.rnn.prediction``, and
``metrics.run_metrics`` for in-memory array building -- only the
CSV-to-parquet conversion step becomes an explicit, gated stage here,
matching the "one call returns everything for this stage" shape of
:func:`bppm_dem_sm.metrics.run_metrics.compute_metrics` and
:func:`bppm_dem_sm.visualization.run_visualization.generate_visualizations`.
"""

from __future__ import annotations

from . import convert, integrity


def process_frames(config):
    """Convert raw CSV frame dumps to parquet, then sanity-check the result.

    Calls :func:`bppm_dem_sm.data_processing.convert.convert_folder_csv_to_parquet`
    on ``config.raw_data_dir`` -> ``config.data_dir``, then
    :func:`bppm_dem_sm.data_processing.integrity.report_particle_integrity`
    on the converted parquet directory as a sanity gate before
    training/prediction ever touch the data.

    Args:
        config: Pipeline settings; uses ``raw_data_dir`` and ``data_dir``.

    Returns:
        dict: ``{"data_dir": config.data_dir, "integrity_report": pd.DataFrame}``
        (the integrity report from
        :func:`~bppm_dem_sm.data_processing.integrity.particle_radius_counts_per_file`).
    """
    convert.convert_folder_csv_to_parquet(str(config.raw_data_dir), str(config.data_dir))
    integrity_report = integrity.report_particle_integrity(str(config.data_dir))
    return {"data_dir": config.data_dir, "integrity_report": integrity_report}
