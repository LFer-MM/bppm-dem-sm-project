"""Raw-CSV-to-training-ready-data conversion and integrity checks.

``run_data_processing.process_frames`` orchestrates ``convert`` + ``integrity``
as one gated pipeline stage; ``frames``/``dataset``/``binning`` stay library
code, imported piecemeal by ``model`` and ``metrics``.
"""
