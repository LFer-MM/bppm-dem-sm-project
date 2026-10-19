# 05 -- Friction coefficient

## Decision

Friction is the **primary calibration variable**.

- Baseline: mu = 0.5 for every pair (rock-rock, rock-steel, steel-steel),
  as in Cleary & Morrison 2016.
- Calibration space: particle-particle friction per pair (including the Owen &
  Cleary set 0.4 / 0.5 / 0.8) and a separate particle-liner friction, scored
  against the plant toe / shoulder ([15](15_calibration_targets.md)).
- Implementation: friction angles in **radians** (mu = tan(angle)), assigned
  per pair with a `frictAngle` `MatchMaker`. Without it YADE takes the
  **minimum** of the two materials' angles.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Cleary & Morrison 2016 | Friction 0.5 for rock-rock, rock-steel and steel-steel (super-quadric particles) | Table 2, PDF p7 / j.81; shape model §3.2, PDF p3 / j.77 | Yes |
| Owen & Cleary 2015 | Friction steel-steel 0.4, steel-rock 0.5, rock-rock 0.8: "smallest at 0.4 for the ball-ball collisions and highest for the rock-rock ones since the rocks are typically quite rough" | Table 4 and §3 text, PDF p3 / j.21 | Yes |
| Owen & Cleary 2015 | "DEM simulation of mill behaviour has been shown to be only weakly sensitive to the specific choices of these material parameters (Cleary, 2001a)" | §3, PDF p3 / j.21 | Yes |
| Boemer & Ponthot 2017 | "the coefficient of friction has a strong influence since it controls the sliding propensity of the charge" | Abstract, PDF p1 / j.53 | Yes |
| Boemer & Ponthot 2017 | Power draw 1311, 1382, 1391 W for mu = 0.25, 0.5, 0.75; default mu = 0.75 | §3.1.4 "Influence of the friction", PDF p10 / j.62; Table 2, PDF p7 / j.59 | Yes |
| Kishida 2025 | Friction coefficient 0.575 | Fig. 2(b), PDF p4 | Yes |
| Govender 2015 | Slice mill: mu particle 0.15 / shell 0.20 (GPU), 0.14 / 0.39 (CPU); Los Bronces SAG: mu particle 0.40, lifter 0.70; friction tuned to reproduce a reference shoulder position | Table 6, PDF p12 / j.163; Table 8, PDF p14 / j.165; §1.6.1, PDF p7 / j.158 | Yes |
| Cleary 2001 (2D) | "Changes in the material properties such as the friction coefficient and the coefficient of restitution have previously been shown to be relatively unimportant (Cleary, 1998a)" | §9, PDF p22 / j.100 | Yes |

The sources disagree on sensitivity: Cleary (2D, and Owen quoting it) finds
friction weakly important; Boemer & Ponthot (3D, experimentally validated
lab mill, run in YADE) and Govender (used friction as the tuning knob for the
shoulder) find it decisive. Since this project calibrates against plant charge
shape, friction is treated as the main calibration variable.

## PPT

| Slide | Content |
|---|---|
| 8, 9, 12 | "Angulo de Friccion = atan(coef. fric.) = atan(0.5) [1]" for steel and rock ([1] = Cleary & Morrison 2016, Table 2) |
| 8 | Claimed influence order "friccion, restitucion y rigidez" citing Cleary (2015), Boemer & Ponthot, Thakur. Only Boemer supports it (see the citation table in [README](README.md)) |
| 30 | "Busqueda manual para Angulos de Friccion y Densidades (respecto a Acomodo de Carga) <- AQUI ACTUALMENTE"; "Desarrollando GridSearch" |
| 31 | Simulation snapshot annotated 212 deg / 26.5 deg (toe / shoulder) |

## Current state

| Where | What |
|---|---|
| `main` `config.py:91,98` | `"friction_angle": math.atan(0.5)` -> 0.4636 rad (already radians) |
| `main` `yade_dem/materials.py:30` | `frictionAngle=radians(material_properties["friction_angle"])` -> converts **again**: 0.4636 deg -> 0.00809 rad, **mu = 0.0081** |
| `main` engines | No `frictAngle` MatchMaker: steel-rock contacts get min(mu_steel, mu_rock) |
| Branch `worktree-yade-sim-structure` | Double conversion fixed (commit `543208a`) |

Consequence: any run made with `main` -- including, if it used this code,
the 212 deg / 26.5 deg match of slide 31 -- had practically frictionless
particles and liner. The lifters (30 rows) can still lift such a charge,
which is why a plausible toe / shoulder may have been reached, but those
parameters are not valid once friction is correct. The manual friction and
density search of slide 30 must be repeated after the fix.

## Analysis

- Densities are not a calibration variable ([08](08_density.md)); friction
  (and rolling resistance, [06](06_rolling_resistance.md)) is what the
  literature tunes to match the shoulder.
- With spheres, friction alone cannot provide the interlocking of angular
  ore. Cleary & Morrison's mu = 0.5 was used with super-quadric shapes; with
  spheres the same mu gives a weaker charge, which rolling resistance
  compensates.
- Owen's pair-wise set needs a `frictAngle` MatchMaker in YADE; with
  per-material angles and the min rule, steel-rock would get 0.4, not 0.5.

## Verdict and how to defend it

"Friction is calibrated because it controls the sliding of the charge and the
power draw (Boemer & Ponthot 2017, abstract and §3.1.4) and is the parameter
used to match the shoulder position (Govender et al. 2015, §1.6.1). The
search is bracketed by literature values: mu = 0.5 for all pairs (Cleary &
Morrison 2016, Table 2), 0.4 / 0.5 / 0.8 for steel-steel / steel-rock /
rock-rock (Owen & Cleary 2015, Table 4), 0.575 (Kishida et al. 2025) and
0.40 particle / 0.70 lifter for a SAG mill (Govender et al. 2015, Table 8)."

## Open items / validation

- Calibration grid (proposal): mu_particle in {0.3, 0.5, 0.7} x mu_liner in
  {0.3, 0.5, 0.7} x mu_roll(rock) in {0, 0.05, 0.1}; 3 revolutions each to
  steady state; score = distance to SAG_B toe / shoulder.
- Re-measure the packing fraction after calibration ([12](12_charge_fill_and_particles.md)):
  packing depends on friction.
