"""GRU -> Dense regression model architecture (TensorFlow imported lazily)."""

from __future__ import annotations


def build_model(frames_in, n_features=4, gru_units=20, dense_units=15, learning_rate=0.01):
    """Build and compile the GRU -> Dense regression model.

    Architecture: ``Input(frames_in, n_features)`` → GRU → Dense(tanh) →
    Dense(3, linear) predicting next ``(x, y, z)``. Compiled with Adam and MSE.

    Args:
        frames_in: Temporal window length (input sequence length).
        n_features: Features per timestep (typically 4: ``x, y, z, r``).
        gru_units: Hidden size of the GRU layer.
        dense_units: Units in the intermediate Dense layer.
        learning_rate: Adam optimizer learning rate.

    Returns:
        keras.Model: Compiled sequential GRU surrogate model.
    """
    from ...tf_quiet import silence_tensorflow

    silence_tensorflow()
    import tensorflow as tf

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(frames_in, n_features)),
            tf.keras.layers.GRU(gru_units),
            tf.keras.layers.Dense(dense_units, activation="tanh"),
            tf.keras.layers.Dense(3, activation="linear"),
        ]
    )
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate), loss="mse")
    return model
