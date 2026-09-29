"""Overlap checks and particle inventory counting (YADE)."""

from __future__ import annotations

from yade import Sphere
from yade.wrapper import O


def check_overlaps():
    """Max relative sphere–sphere penetration depth.

    Scans real interactions, ignoring facet contacts. Relative overlap is
    ``penetrationDepth / min(r1, r2)``.

    Returns:
        float: Maximum relative overlap ratio among sphere–sphere contacts.
    """
    max_rel = 0.0
    worst_pair = None
    for i in O.interactions:
        if not i.isReal:
            continue
        b1 = O.bodies[i.id1]
        b2 = O.bodies[i.id2]
        # skip any contact involving a facet (non-sphere)
        if not isinstance(b1.shape, Sphere) or not isinstance(b2.shape, Sphere):
            continue
        depth = i.geom.penetrationDepth
        r1 = b1.shape.radius
        r2 = b2.shape.radius
        rel = depth / min(r1, r2)
        if rel > max_rel:
            max_rel = rel
            worst_pair = (i.id1, i.id2)
    print(f"Max overlap: {max_rel*100:.3f}% — between bodies {worst_pair}. Depth: {depth}")
    return max_rel


def get_particle_inventory(r_small, r_large, tol=1e-6, verbose=True):
    """Count spheres per size class (small/large) within tol of each radius.

    Args:
        r_small: Expected small-species radius (meters).
        r_large: Expected large-species radius (meters).
        tol: Absolute radius tolerance for classification.
        verbose: If ``True``, print the inventory summary.

    Returns:
        dict: Counts with keys ``"small"``, ``"large"``, and ``"unclassified"``.
    """
    inv = {"small": 0, "large": 0, "unclassified": 0}
    for b in O.bodies:
        if type(b.shape).__name__ != "Sphere":
            continue
        r = b.shape.radius
        if abs(r - r_small) <= tol:
            inv["small"] += 1
        elif abs(r - r_large) <= tol:
            inv["large"] += 1
        else:
            inv["unclassified"] += 1
    if verbose:
        print(f"Inventory: {inv['small']} small, {inv['large']} large, {inv['unclassified']} unclassified")
    return inv
