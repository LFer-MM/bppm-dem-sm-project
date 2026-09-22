"""Tests for the radial/axial large-particle fraction profile."""

from __future__ import annotations

import numpy as np
import pandas as pd

from bppm_dem_sm.metrics import segregation_profile as sp


def _frame(x, y, z, r):
    return pd.DataFrame({"x": x, "y": y, "z": z, "r": r})


def test_radial_bin_edges_span_zero_to_max():
    df = _frame(x=[0.0, 3.0, 4.0], y=[0.0, 4.0, 0.0], z=[0.0, 0.0, 0.0], r=[0.1, 0.1, 0.1])
    edges = sp.radial_bin_edges(df, n_bins=4)
    assert edges[0] == 0.0
    assert edges[-1] == 5.0  # max radial dist = sqrt(3^2+4^2) = 5
    assert len(edges) == 5


def test_radial_fraction_profile_matches_expected_bins():
    # Two particles per radial ring (small, large), rings at r=0.5 and r=2.5.
    x = [0.5, 0.5, 2.5, 2.5]
    y = [0.0, 0.0, 0.0, 0.0]
    z = [0.0, 0.0, 0.0, 0.0]
    r = [0.1, 0.2, 0.1, 0.2]  # tracer (large) radius = 0.2
    df = _frame(x, y, z, r)
    edges = np.array([0.0, 1.0, 2.0, 3.0])

    profile = sp.radial_fraction_profile(df, tracer_radius=0.2, bin_edges=edges)
    assert list(profile["n_particles"]) == [2, 0, 2]
    assert profile.loc[0, "fraction_large"] == 0.5
    assert np.isnan(profile.loc[1, "fraction_large"])
    assert profile.loc[2, "fraction_large"] == 0.5


def test_axial_fraction_profile_uses_signed_distance():
    x = [0.0, 0.0]
    y = [0.0, 0.0]
    z = [-1.0, 1.0]
    r = [0.1, 0.2]
    df = _frame(x, y, z, r)
    edges = np.array([-2.0, 0.0, 2.0])

    profile = sp.axial_fraction_profile(df, tracer_radius=0.2, bin_edges=edges)
    assert profile.loc[0, "fraction_large"] == 0.0  # small particle in [-2, 0)
    assert profile.loc[1, "fraction_large"] == 1.0  # large particle in [0, 2]


def test_radial_fraction_profile_respects_custom_center():
    # Particle at (5, 5) is at radial distance 0 from center (5, 5).
    df = _frame(x=[5.0], y=[5.0], z=[0.0], r=[0.2])
    edges = sp.radial_bin_edges(df, center_x=5.0, center_y=5.0, n_bins=1)
    assert edges[-1] == 0.0
