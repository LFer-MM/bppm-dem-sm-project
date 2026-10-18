"""The SR half of the extended-RNNSR method: model, fitting, loading.

Implements the stochastic random (SR) model of Kishida, Nakamura, Ohsaki &
Watano (2025), "Surrogate model of DEM simulation for binary-sized particle
mixing and segregation", Powder Technology 455, 120811. The GRU predicts the
deterministic local mean component of a particle's trajectory (Lagrangian
behavior); the SR model supplies the local variability component (Eulerian
behavior). One module per concern, mirroring :mod:`bppm_dem_sm.model.rnn`:

- :mod:`~bppm_dem_sm.model.sr.model` -- :class:`SRModel`, the sigma_v(x)
  lookup table and its Gaussian draw (Eq. 3).
- :mod:`~bppm_dem_sm.model.sr.fitting` -- the closed-form fit of sigma_v(x)
  from reference DEM frames (Eq. 2).
- :mod:`~bppm_dem_sm.model.sr.loading` -- where the fitted model is saved,
  next to the GRU, and loading it back.

Combining the two halves, ``x = x_bar_RNN + v_tilde * Delta t_RNN`` (Eq. 4),
is the job of :func:`bppm_dem_sm.model.prediction.predict_frames`.
"""

from .model import SRModel

__all__ = ["SRModel"]
