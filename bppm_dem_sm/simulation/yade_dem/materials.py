"""Steel/rock material definitions and per-body material labeling (YADE)."""

from __future__ import annotations

from math import radians

from yade import FrictMat
from yade.wrapper import O

MATERIALS_MAP = {}


def initialize_simulation_materials(materials):
    """Register FrictMat entries from dict values into O.materials and MATERIALS_MAP.

    Args:
        materials: Mapping of material name to property dicts with keys
            ``density``, ``young``, ``poisson``, ``friction_angle``, ``label``.
    """
    for material_properties in materials.values():
        m = FrictMat(density=material_properties["density"],
                     young=material_properties["young"],
                     poisson=material_properties["poisson"],
                     frictionAngle=radians(material_properties["friction_angle"]),
                     label=material_properties["label"])

        O.materials.append(m)
        MATERIALS_MAP[material_properties["label"]] = m
        print("Added material:", material_properties["label"])


def _mat_label(b):
    """Material label string for body ``b``, or empty.

    Args:
        b: YADE body.

    Returns:
        str: Material ``label``, or ``""`` if missing.
    """
    m = getattr(b, "material", None)
    if m is None:
        return ""
    return str(getattr(m, "label", ""))
