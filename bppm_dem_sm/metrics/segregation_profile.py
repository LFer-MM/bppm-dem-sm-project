"""Radial/axial large-particle fraction profiles (paper Figs. 8b/c, 11b/c, 12b, 14b).

Complements Lacey's mixing index with a spatial breakdown: the fraction of
large (tracer) particles as a function of distance from the mill's central
axis (radial) and position along that axis (axial), following Kishida et al.
(2025), "Surrogate model of DEM simulation for binary-sized particle mixing
and segregation", Powder Technology 455, 120811, Section 4.1.

The mill's circular cross section is assumed to lie in the XY plane (as in
:mod:`bppm_dem_sm.visualization.cell_grid`, which plots the full charge on XY with an
equal-aspect grid), with Z as the axial direction. Override
``MetricsOptions.center_x`` / ``center_y`` / ``center_z`` if that does not
match your geometry.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def radial_bin_edges(df, center_x=0.0, center_y=0.0, n_bins=12):
    """Return equal-width radial bin edges spanning the observed extent of ``df``.

    Args:
        df: Frame table with ``x``, ``y`` columns.
        center_x: Mill central-axis X coordinate.
        center_y: Mill central-axis Y coordinate.
        n_bins: Number of equal-width radial bins.

    Returns:
        numpy.ndarray: ``n_bins + 1`` bin edges from 0 to the max observed
        radial distance.
    """
    x = df["x"].to_numpy(float) - center_x
    y = df["y"].to_numpy(float) - center_y
    radial = np.sqrt(x**2 + y**2)
    return np.linspace(0.0, radial.max(), n_bins + 1)


def axial_bin_edges(df, center_z=0.0, n_bins=12):
    """Return equal-width axial bin edges spanning the observed extent of ``df``.

    Args:
        df: Frame table with ``z`` column.
        center_z: Mill central-axis Z reference (zero point of axial distance).
        n_bins: Number of equal-width axial bins.

    Returns:
        numpy.ndarray: ``n_bins + 1`` bin edges spanning the observed
        (signed) axial distance.
    """
    axial = df["z"].to_numpy(float) - center_z
    return np.linspace(axial.min(), axial.max(), n_bins + 1)


def _fraction_by_bin(distance, is_tracer, bin_edges):
    """Bin ``distance`` by ``bin_edges`` and report the tracer fraction per bin."""
    n_bins = len(bin_edges) - 1
    bin_idx = np.clip(np.digitize(distance, bin_edges[1:-1], right=False), 0, n_bins - 1)
    rows = []
    for b in range(n_bins):
        mask = bin_idx == b
        n = int(mask.sum())
        rows.append(
            {
                "bin": b,
                "bin_center": float((bin_edges[b] + bin_edges[b + 1]) / 2.0),
                "fraction_large": float(is_tracer[mask].mean()) if n else np.nan,
                "n_particles": n,
            }
        )
    return pd.DataFrame(rows)


def radial_fraction_profile(df, tracer_radius, bin_edges, center_x=0.0, center_y=0.0):
    """Compute the large-particle fraction vs. radial distance from ``(center_x, center_y)``.

    Args:
        df: Frame table with ``x``, ``y``, ``r`` columns.
        tracer_radius: Radius identifying the large/tracer species.
        bin_edges: Radial bin edges, e.g. from :func:`radial_bin_edges` (pass
            the same edges for every frame being compared, so bins align).
        center_x: Mill central-axis X coordinate.
        center_y: Mill central-axis Y coordinate.

    Returns:
        pandas.DataFrame: One row per bin with ``bin``, ``bin_center`` (radius,
        m), ``fraction_large``, and ``n_particles``.
    """
    x = df["x"].to_numpy(float) - center_x
    y = df["y"].to_numpy(float) - center_y
    radial = np.sqrt(x**2 + y**2)
    is_tracer = np.round(df["r"].to_numpy(float), 12) == np.round(tracer_radius, 12)
    return _fraction_by_bin(radial, is_tracer, bin_edges)


def axial_fraction_profile(df, tracer_radius, bin_edges, center_z=0.0):
    """Compute the large-particle fraction vs. axial distance from ``center_z``.

    Args:
        df: Frame table with ``z``, ``r`` columns.
        tracer_radius: Radius identifying the large/tracer species.
        bin_edges: Axial bin edges, e.g. from :func:`axial_bin_edges` (pass
            the same edges for every frame being compared, so bins align).
        center_z: Mill central-axis Z reference (zero point of axial distance).

    Returns:
        pandas.DataFrame: One row per bin with ``bin``, ``bin_center`` (signed
        distance along the axis, m), ``fraction_large``, and ``n_particles``.
    """
    axial = df["z"].to_numpy(float) - center_z
    is_tracer = np.round(df["r"].to_numpy(float), 12) == np.round(tracer_radius, 12)
    return _fraction_by_bin(axial, is_tracer, bin_edges)
