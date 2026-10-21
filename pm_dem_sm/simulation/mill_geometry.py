"""Parametric SAG mill slice geometry: shell, lifters, and end walls as triangles.

Backend-agnostic and stdlib-only: every function returns plain vertex
triples, which a DEM backend turns into its own wall elements (YADE facets in
:mod:`pm_dem_sm.simulation.yade_dem.stl`). The mill axis is the Z axis
through the origin and the slice spans ``z0 <= z <= z0 + depth``.

Lifters are trapezoidal bars running the full slice depth: ``base_width`` at
the shell, ``top_width`` at ``height`` above it, so each face is inclined
``atan((base_width - top_width) / 2 / height)`` from the radial direction.
"""

from __future__ import annotations

from itertools import pairwise
import math


def shell_triangles(diameter, depth, n_segments, z0=0.0):
    """Return the triangles of a polygonal cylinder shell around the Z axis.

    Args:
        diameter: Shell (inside-liner) diameter in meters; vertices lie on it.
        depth: Slice depth along Z (m).
        n_segments: Number of flat segments around the circumference.
        z0: Z of the back end of the slice (m).

    Returns:
        list[tuple]: ``2 * n_segments`` triangles, each three ``(x, y, z)`` tuples.
    """
    r = diameter / 2.0
    z1 = z0 + depth
    tris = []
    for k in range(n_segments):
        a0 = 2.0 * math.pi * k / n_segments
        a1 = 2.0 * math.pi * (k + 1) / n_segments
        p00 = (r * math.cos(a0), r * math.sin(a0), z0)
        p10 = (r * math.cos(a1), r * math.sin(a1), z0)
        p01 = (r * math.cos(a0), r * math.sin(a0), z1)
        p11 = (r * math.cos(a1), r * math.sin(a1), z1)
        tris += [(p00, p10, p11), (p00, p11, p01)]
    return tris


def lifter_triangles(diameter, depth, n_lifters, height, base_width, top_width, z0=0.0,
                     embed=0.02, phase=0.0):
    """Return the triangles of ``n_lifters`` evenly spaced trapezoidal lifters.

    Each lifter contributes its two side faces and its top face (6
    triangles); its ends are closed by the slice end walls. The base sits
    ``embed`` meters outside the shell so no gap opens at the polygonal shell.

    Args:
        diameter: Shell diameter (m).
        depth: Slice depth along Z (m).
        n_lifters: Number of lifter rows.
        height: Lifter height above the shell (m).
        base_width: Width at the shell (m).
        top_width: Width at the top face (m).
        z0: Z of the back end of the slice (m).
        embed: Radial distance the base extends behind the shell (m).
        phase: Angle of the first lifter from ``+X`` (rad).

    Returns:
        list[tuple]: ``6 * n_lifters`` triangles, each three ``(x, y, z)`` tuples.
    """
    r_base = diameter / 2.0 + embed
    r_top = diameter / 2.0 - height
    z1 = z0 + depth
    tris = []
    for k in range(n_lifters):
        theta = phase + 2.0 * math.pi * k / n_lifters
        er = (math.cos(theta), math.sin(theta))
        et = (-math.sin(theta), math.cos(theta))

        def pt(t, rad, z, er=er, et=et):
            return (rad * er[0] + t * et[0], rad * er[1] + t * et[1], z)

        # Trapezoid corners in (tangential, radial): base-, top-, top+, base+.
        corners = [
            (-base_width / 2.0, r_base),
            (-top_width / 2.0, r_top),
            (top_width / 2.0, r_top),
            (base_width / 2.0, r_base),
        ]
        for (t0, rad0), (t1, rad1) in pairwise(corners):
            a, b = pt(t0, rad0, z0), pt(t1, rad1, z0)
            c, d = pt(t1, rad1, z1), pt(t0, rad0, z1)
            tris += [(a, b, c), (a, c, d)]
    return tris


def end_wall_triangles(diameter, z, margin=1.5):
    """Return two triangles covering the mill cross-section at ``z``.

    The pair forms a square of half-size ``margin * diameter / 2`` centered on
    the axis, so it closes the shell and the lifters with room to spare.

    Args:
        diameter: Shell diameter (m).
        z: Z position of the wall (m).
        margin: Half-size of the wall relative to the shell radius.

    Returns:
        list[tuple]: Two triangles, each three ``(x, y, z)`` tuples.
    """
    h = margin * diameter / 2.0
    a, b, c, d = (-h, -h, z), (h, -h, z), (h, h, z), (-h, h, z)
    return [(a, b, c), (a, c, d)]


def lifter_face_angle_deg(height, base_width, top_width):
    """Return the lifter face angle from the radial direction (deg).

    Args:
        height: Lifter height (m).
        base_width: Width at the shell (m).
        top_width: Width at the top face (m).

    Returns:
        float: Face angle in degrees (0 = radial face).
    """
    return math.degrees(math.atan2((base_width - top_width) / 2.0, height))
