"""Loading a saved GRU surrogate model, including legacy SavedModel exports."""

from __future__ import annotations

from pathlib import Path


class _SavedModelWrapper:
    """Thin adapter for legacy TensorFlow SavedModel exports (Keras 3 cannot load these directly).

    Exposes a Keras-like ``predict`` API and ``input_shape`` / ``output_shape``
    attributes so the prediction loop can treat SavedModel and ``.keras``
    artifacts uniformly.
    """

    def __init__(self, path: Path):
        """Load a SavedModel directory and bind the ``serving_default`` signature.

        Args:
            path: Directory containing ``saved_model.pb`` (and assets/variables).
        """
        from ...tf_quiet import silence_tensorflow

        silence_tensorflow()
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
        import numpy as np

        parts = []
        for start in range(0, x.shape[0], batch_size):
            batch = x[start : start + batch_size]
            out = self._fn(**{self._input_key: batch})
            if isinstance(out, dict):
                out = out[self._output_key]
            parts.append(out.numpy())
        return np.concatenate(parts, axis=0)


def _resolve_model_path(path: Path) -> Path:
    """Return an existing `.keras`, `.h5`, or SavedModel directory path.

    Args:
        path: Requested model path (file or directory); alternate suffixes are tried.

    Returns:
        Path: Resolved artifact path that exists on disk.

    Raises:
        FileNotFoundError: If no Keras file or SavedModel directory is found.
    """
    candidates = [path]
    if path.suffix in {".keras", ".h5"}:
        candidates.append(path.with_suffix(""))
    else:
        candidates.extend([path.with_suffix(".keras"), path.with_suffix(".h5")])

    for candidate in candidates:
        if candidate.is_dir() and (candidate / "saved_model.pb").exists():
            return candidate
        if candidate.is_file() and candidate.suffix in {".keras", ".h5"}:
            return candidate

    raise FileNotFoundError(f"No Keras or SavedModel artifact found for: {path}")


def load_model(path):
    """Load a saved Keras model (``.keras``/``.h5``) or legacy SavedModel directory.

    Args:
        path: Path to a ``.keras``/``.h5`` file or SavedModel directory.

    Returns:
        keras.Model or _SavedModelWrapper: Loaded model with a ``predict`` method.
    """
    from ...tf_quiet import silence_tensorflow

    silence_tensorflow()
    import keras

    resolved = _resolve_model_path(Path(path))
    if resolved.is_dir():
        return _SavedModelWrapper(resolved)
    return keras.models.load_model(str(resolved))
