"""The RNN half of the extended-RNNSR method: GRU architecture, training, loading, prediction.

Split out of the former ``training.py``/``prediction.py`` pair by concern.
The SR (stochastic-random) half lives one level up, at
:mod:`bppm_dem_sm.model.sr` -- it's a distinct component applied after
this subpackage's prediction step, not part of the RNN itself.
"""
