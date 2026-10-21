"""The RNN half of the extended-RNNSR method: GRU model, training, loading.

One module per concern, mirrored by the SR half in
:mod:`pm_dem_sm.model.sr`:

- :mod:`~pm_dem_sm.model.rnn.model` -- :class:`RNNModel`, the GRU network
  wrapped with ``build``, ``predict``, and ``save``/``load``.
- :mod:`~pm_dem_sm.model.rnn.training` -- gradient training on sliding
  windows of the local mean trajectories (Eq. 1).
- :mod:`~pm_dem_sm.model.rnn.loading` -- resolving the saved model path
  and loading it back.

Prediction combines both halves, so it lives one level up, in
:mod:`pm_dem_sm.model.prediction`.
"""

from .model import RNNModel

__all__ = ["RNNModel"]
