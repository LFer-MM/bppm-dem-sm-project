"""Tests for the standalone particle animation helpers (no display)."""

from __future__ import annotations

import numpy as np

from bppm_dem_sm.visualization.animate_particles import LARGE_COLOR, SMALL_COLOR, radius_colors


def test_radius_colors_maps_small_and_large():
    r = np.array([0.1, 0.2, 0.1, 0.2])
    colors = radius_colors(r)
    assert list(colors) == [SMALL_COLOR, LARGE_COLOR, SMALL_COLOR, LARGE_COLOR]


def test_radius_colors_all_same_radius_is_small():
    r = np.array([0.1, 0.1, 0.1])
    colors = radius_colors(r)
    assert all(c == SMALL_COLOR for c in colors)
