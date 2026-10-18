"""Tests for the parametric mill geometry (no YADE needed)."""

from __future__ import annotations

import math

import pytest

from bppm_dem_sm.simulation import mill_geometry as geom


def test_shell_vertices_lie_on_circle_and_span_depth():
    tris = geom.shell_triangles(diameter=4.0, depth=0.5, n_segments=12, z0=0.1)
    assert len(tris) == 24
    for tri in tris:
        for x, y, z in tri:
            assert math.hypot(x, y) == pytest.approx(2.0)
            assert z in (pytest.approx(0.1), pytest.approx(0.6))


def test_lifters_reach_their_height_and_stay_outside_inner_radius():
    d, h = 4.0, 0.2
    tris = geom.lifter_triangles(d, 0.5, n_lifters=6, height=h, base_width=0.3, top_width=0.1)
    assert len(tris) == 36
    radii = [math.hypot(x, y) for tri in tris for x, y, _ in tri]
    assert min(radii) == pytest.approx(math.hypot(d / 2 - h, 0.05))
    assert max(radii) > d / 2


def test_lifters_are_evenly_spaced():
    tris = geom.lifter_triangles(4.0, 0.5, n_lifters=4, height=0.2, base_width=0.3, top_width=0.1)
    centers = []
    for k in range(4):
        pts = [p for tri in tris[6 * k:6 * k + 6] for p in tri]
        centers.append(math.atan2(sum(p[1] for p in pts), sum(p[0] for p in pts)))
    gaps = [(centers[(k + 1) % 4] - centers[k]) % (2 * math.pi) for k in range(4)]
    assert gaps == [pytest.approx(math.pi / 2)] * 4


def test_end_wall_covers_the_shell():
    (a, b, c), (_, _, d) = geom.end_wall_triangles(4.0, z=0.3)
    xs = [p[0] for p in (a, b, c, d)]
    assert min(xs) < -2.0 and max(xs) > 2.0
    assert {p[2] for p in (a, b, c, d)} == {0.3}


def test_lifter_face_angle():
    assert geom.lifter_face_angle_deg(0.1, 0.3, 0.1) == pytest.approx(45.0)
    assert geom.lifter_face_angle_deg(0.1, 0.2, 0.2) == pytest.approx(0.0)
