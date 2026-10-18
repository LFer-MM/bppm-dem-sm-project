"""The GRU model: :class:`RNNModel` wraps the Keras network (TensorFlow imported lazily).

Mirrors :class:`bppm_dem_sm.model.sr.model.SRModel`: one object that holds
the fitted model, predicts with it, and saves/loads it. The Keras network is
wrapped rather than subclassed, so importing this module never imports
TensorFlow and saved ``.keras`` files stay plain Keras models.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

# --- Public classes ----------------------------------------------------------


class RNNModel:
    """GRU surrogate: predicts each particle's next local mean ``(x, y, z)``.

    Attributes:
        network: The underlying Keras model, for direct Keras use
            (``summary``, ``fit``, ``layers``); a predict-only adapter when
            loaded from a legacy SavedModel directory.
    """

    def __init__(self, network):
        """Wrap an already built (or loaded) network.

        Args:
            network: Keras model, or any object with Keras-style ``predict``,
                ``input_shape``, and ``output_shape``.
        """
        self.network = network

    @classmethod
    def build(cls, frames_in, n_features=4, gru_units=20, dense_units=15, learning_rate=0.01) -> RNNModel:
        """Build and compile the GRU -> Dense regression network.

        Architecture: ``Input(frames_in, n_features)`` -> GRU -> Dense(tanh) ->
        Dense(3, linear) predicting next ``(x, y, z)``. Compiled with Adam and MSE.
        Matches Table 1 of Kishida et al. (2025): with the defaults and 4 input
        features the layers hold 1560, 315, and 48 parameters, and the input
        weights use He initialization (the GRU's recurrent weights keep Keras's
        orthogonal default, which the paper does not specify).

        Args:
            frames_in: Temporal window length (input sequence length).
            n_features: Features per timestep (typically 4: ``x, y, z, r``).
            gru_units: Hidden size of the GRU layer.
            dense_units: Units in the intermediate Dense layer.
            learning_rate: Adam optimizer learning rate.

        Returns:
            RNNModel: Untrained model wrapping the compiled network.
        """
        from ...tf_quiet import silence_tensorflow

        silence_tensorflow()
        import tensorflow as tf

        network = tf.keras.Sequential(
            [
                tf.keras.layers.Input(shape=(frames_in, n_features)),
                tf.keras.layers.GRU(gru_units, kernel_initializer="he_normal"),
                tf.keras.layers.Dense(dense_units, activation="tanh", kernel_initializer="he_normal"),
                tf.keras.layers.Dense(3, activation="linear", kernel_initializer="he_normal"),
            ]
        )
        network.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), loss="mse")
        return cls(network)

    @property
    def input_shape(self) -> tuple:
        """Network input shape, ``(None, frames_in, n_features)``."""
        return tuple(self.network.input_shape)

    @property
    def output_shape(self) -> tuple:
        """Network output shape, ``(None, 3)``."""
        return tuple(self.network.output_shape)

    def predict(self, windows: np.ndarray, batch_size: int = 32) -> np.ndarray:
        """Predict the next local mean position for each window.

        Args:
            windows: Array of shape ``(N, frames_in, n_features)``.
            batch_size: Number of particles (rows) per forward pass.

        Returns:
            numpy.ndarray: Shape ``(N, 3)`` float32 ``(x, y, z)`` per particle.
        """
        yhat = self.network.predict(windows, batch_size=batch_size, verbose=0)
        return np.asarray(yhat)[:, :3].astype(np.float32)

    def save(self, path) -> None:
        """Write the network to a ``.keras`` file.

        Args:
            path: Destination path ending in ``.keras``.
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.network.save(str(path))

    @classmethod
    def load(cls, path) -> RNNModel:
        """Read a model from a ``.keras``/``.h5`` file or a legacy SavedModel directory.

        Args:
            path: Existing artifact path, e.g. from
                :func:`bppm_dem_sm.model.rnn.loading.load_rnn`'s resolution.

        Returns:
            RNNModel: The loaded model.
        """
        from ...tf_quiet import silence_tensorflow

        silence_tensorflow()
        path = Path(path)
        if path.is_dir():
            return cls(_SavedModelNetwork(path))

        import keras

        return cls(keras.models.load_model(str(path)))


# --- Private classes ---------------------------------------------------------


class _SavedModelNetwork:
    """Predict-only adapter for legacy TensorFlow SavedModel exports (Keras 3 cannot load these directly).

    Exposes a Keras-like ``predict`` API and ``input_shape`` / ``output_shape``
    attributes so :class:`RNNModel` treats SavedModel and ``.keras`` artifacts
    uniformly.
    """

    def __init__(self, path: Path):
        """Load a SavedModel directory and bind the ``serving_default`` signature.

        Args:
            path: Directory containing ``saved_model.pb`` (and assets/variables).
        """
        import tensorflow as tf

        fn = tf.saved_model.load(str(path)).signatures["serving_default"]
        _, input_spec = fn.structured_input_signature
        output_spec = fn.structured_outputs
        self._input_key = next(iter(input_spec))
        self._output_key = next(iter(output_spec))
        self._fn = fn
        self.input_shape = tuple(input_spec[self._input_key].shape.as_list())
        self.output_shape = tuple(output_spec[self._output_key].shape.as_list())

    def predict(self, x, batch_size=32, verbose=0):
        """Run batched inference through the SavedModel signature.

        Args:
            x: Input array of shape matching ``input_shape`` (typically
                ``(N, frames_in, n_features)``).
            batch_size: Number of particles (rows) per forward pass.
            verbose: Unused; kept for Keras ``model.predict`` compatibility.

        Returns:
            numpy.ndarray: Concatenated model outputs along axis 0.
        """
        parts = []
        for start in range(0, x.shape[0], batch_size):
            batch = x[start : start + batch_size]
            out = self._fn(**{self._input_key: batch})
            if isinstance(out, dict):
                out = out[self._output_key]
            parts.append(out.numpy())
        return np.concatenate(parts, axis=0)
