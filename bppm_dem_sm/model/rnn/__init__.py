"""The RNN half of the extended-RNNSR method: GRU architecture, training, loading, prediction.

One module per concern. The SR (stochastic-random) half lives one level
up, at
:mod:`bppm_dem_sm.model.sr` -- it's a distinct component applied after
this subpackage's prediction step, not part of the RNN itself.
"""
