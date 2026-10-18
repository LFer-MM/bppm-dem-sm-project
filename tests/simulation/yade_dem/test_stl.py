"""Tests for YADE mill-geometry helpers (skipped when YADE is not installed)."""

from __future__ import annotations

import pytest

pytest.importorskip("yade")

from bppm_dem_sm.simulation.yade_dem import stl as sim


def test_chord_box_3d_geometry_and_corners():
    d, y, h, depth = 10.0, 0.0, 2.0, 5.0
    box = sim.chord_box_3d(d, y, h, depth)
    half = (5.0**2 - 2.0**2) ** 0.5  # chord at the top face, the farther from the axis
    assert box["x_min"] == pytest.approx(-half)
    assert box["x_max"] == pytest.approx(half)
    assert box["y_bottom"] == pytest.approx(y)
    assert box["y_top"] == pytest.approx(y + h)
    assert box["z_min"] == 0.0
    assert box["z_max"] == depth
    assert box["width"] == pytest.approx(2 * half)
    assert box["height"] == h
    assert box["depth"] == depth
    mc, xc = box["min_corner"], box["max_corner"]
    assert float(mc[0]) == pytest.approx(box["x_min"])
    assert float(xc[1]) == pytest.approx(box["y_top"])


def test_chord_box_3d_clamps_y_to_radius():
    box = sim.chord_box_3d(4.0, 10.0, 1.0, 1.0)
    assert abs(box["y_bottom"]) <= 2.0 + 1e-9


def test_chord_box_3d_corners_stay_inside_circle():
    for y in (-4.5, -1.0, -0.5, 1.0):
        box = sim.chord_box_3d(10.0, y, 1.0, 1.0)
        for yy in (box["y_bottom"], box["y_top"]):
            assert box["x_max"] ** 2 + yy**2 <= 25.0 + 1e-9
