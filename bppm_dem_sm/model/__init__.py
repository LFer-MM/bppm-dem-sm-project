"""The extended-RNNSR surrogate: a GRU plus the stochastic-random (SR) model.

Each half is its own subpackage, split by concern:

- :mod:`bppm_dem_sm.model.rnn` -- the GRU: architecture, training, loading.
- :mod:`bppm_dem_sm.model.sr` -- the SR model: model, fitting, loading.

The two steps that combine both halves live at this level:
:mod:`~bppm_dem_sm.model.training` (Step 3, train the GRU and fit the SR)
and :mod:`~bppm_dem_sm.model.prediction` (Step 4, GRU prediction plus SR
noise).
"""
