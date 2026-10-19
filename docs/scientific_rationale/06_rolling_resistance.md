# 06 -- Rolling resistance

## Decision

Add a rolling-resistance torque for **rock** particles (spheres representing
angular ore) and treat its coefficient as a calibration variable, starting
from 0 and searching up to ~0.1. Steel balls stay without rolling resistance
unless calibration requires it.

YADE implementation: `Law2_ScGeom_MindlinPhys_Mindlin(includeMoment=True)`
with `Ip2_FrictMat_FrictMat_MindlinPhys(krot=..., eta=...)` and the 6-DOF
geometry functors `Ig2_Sphere_Sphere_ScGeom6D`, `Ig2_Facet_Sphere_ScGeom6D`.
YADE documents `eta` only as "Coefficient to determine the plastic bending
moment" and states "if eta is 0.0, no plastic condition is applied"; its
exact relation to Kishida's mu_rf (M_max = mu_rf r |F_n|) must be confirmed
in the YADE source before quoting equivalence.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Kishida 2025 | Rotational equation includes "torque due to the rolling resistance" M_rf; M_rf = -mu_rf r |F_cn| omega / |omega| | Appendix A, Eqs. (A-2) and (A-6), PDF p11-12 | Yes |
| Kishida 2025 | Rolling friction coefficient 0.01 | Fig. 2(b), PDF p4 | Yes |
| Thakur 2016 | Particle rolling friction 0.001 (uniaxial-test simulations) | Parameter table, PDF p5 / j.134 | Yes |
| Cleary 2001 (2D) | "Increasing the angularity or aspect ratios of the rock ... strengthens the charge and makes slope failure more difficult. For sub-critical speeds, this leads to higher dynamic angles of repose ..., to higher shoulder positions and to higher power consumption." | §11 Conclusion, PDF p34 / j.112 | Yes |
| Cleary 2001 (2D) | Non-circular particles: charge "significantly dilated"; for N <= 75 % critical "there is no change in the mill power draw" because the centre of mass changes little | §10 "Effect of particle shape", PDF p28-29 / j.106-107 | Yes |
| Cleary & Morrison 2016 | Particles are **super-quadrics** (non-spherical), so their mu = 0.5 already includes shape interlocking | §3.2, PDF p3 / j.77 | Yes |
| Boemer & Ponthot 2017 | Spheres without rolling resistance -- but the media are "almost spherical" steel balls | §2.1, PDF p2 / j.54; §2.2, PDF p3 / j.55 | Yes |
| Govender 2015 | Spheres (sphere-face / sphere-edge contacts) | Abstract, PDF p1 / j.152 | Yes |
| YADE (installed build) | `includeMoment`: "bool to consider rolling resistance (if eta is 0.0, no plastic condition is applied.)"; `krot`: "Rotational stiffness for moment contact law"; `eta`: "Coefficient to determine the plastic bending moment" | Attribute docstrings, installed classes | Yes (run on this machine) |

## PPT

No slide mentions rolling resistance. Slide 42 (structure map) lists
"Materials -> Mechanical Properties / Physical Interactions" without it.

## Current state

| Where | What |
|---|---|
| `main` `engines.py:76-82` | `Ig2_Sphere_Sphere_ScGeom` (no 6-DOF), `includeMoment` not set: **no rolling resistance** |

## Analysis

- Rock in a SAG mill is angular. Here it is a sphere. A sphere with sliding
  friction only rolls freely, so the charge has less shear strength than the
  real one: lower shoulder and power at sub-critical speeds (Cleary 2001
  conclusion). At 72.8 % of critical, Cleary 2001 also reports little power
  change from shape (N <= 75 %), so the effect shows mainly in charge shape
  (dilation, shoulder) -- exactly the calibration targets.
- The mill papers that reach good agreement either use real shapes (Cleary &
  Morrison: super-quadrics) or model media that really are spheres (Boemer:
  steel balls). Spheres standing in for rock is the case where the DEM
  literature adds rolling resistance, as Kishida does even for powders.
- No paper in the library gives a value for coarse ore spheres in a mill, so
  the value must come from calibration, not from a citation.

## Verdict and how to defend it

"Rock particles are spheres, while the ore is angular; particle shape
controls the shear strength of the charge and hence the shoulder position
(Cleary 2001, §10-11), and the mill studies that use mu ~ 0.5 do so with
non-spherical particles (Cleary & Morrison 2016, §3.2). We therefore include
a rolling-resistance torque of the form used in the reference surrogate study
(Kishida et al. 2025, Eq. A-6) and calibrate its coefficient against the
plant charge shape."

## Open items / validation

- Confirm in YADE source how `eta` and `krot` define the plastic moment
  (and choose `krot` so the elastic rolling stage does not limit dt).
- Calibrate mu_roll(rock) jointly with friction ([05](05_friction.md)).
- Check that rolling resistance does not create a static repose angle larger
  than the observed dynamic one.
