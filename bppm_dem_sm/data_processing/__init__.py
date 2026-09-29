"""Raw-CSV-to-training-ready-data conversion and integrity checks.

``run_data_processing.process_frames`` orchestrates ``convert`` + ``integrity``
as one gated pipeline stage; ``frames``/``dataset`` stay library code,
imported piecemeal by ``model.rnn`` and ``metrics.run_metrics``.
"""
