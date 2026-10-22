# 11 -- Mill speed

## Decision

**9 rpm**, the median speed of **SAG_A, the reference mill**, i.e.
**72.8 % of critical speed**. SAG_B and SAG_C are evidence that this value is
typical: across the three mills the usual range is 8.6-10 rpm (slide 4). Rotation direction:
counter-clockwise seen from +Z (positive angular velocity in YADE), so the
charge rises on the +X side. Angles are measured counter-clockwise from the
3 o'clock position (+X); fixed 2026-10-18, see [15](15_calibration_targets.md).
The liner is symmetric, so the orientation is a free choice in simulation.

- Provisional until the plant time series (author to-do A1): the target is
  SAG_A's median speed in the same post-reline operating window used for
  the toe / shoulder target ([15](15_calibration_targets.md), claim 2).
- The % of critical speed is quoted with N_c = 42.3 / sqrt(D - d); it moves
  with SAG_A's report diameter ([10](10_mill_geometry.md)).

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Owen & Cleary 2015 | "the same rotational speed of 11 rpm (75% critical speed)" for an 8.4 m SAG mill | §3, PDF p3 / j.21 | Yes |
| Govender 2015 | Los Bronces SAG 10.12 m "rotating at 10 rpm" (~75 % critical by the formula below) | §3, PDF p12 / j.163 | Yes |
| Boemer & Ponthot 2017 | Calibration at 70 % critical, validation at 70 % and 80 % | Table 1, PDF p3 / j.55 | Yes |
| Cleary 2001 (2D) | Behaviour vs. speed; at N <= 70-75 % power insensitive to lifter pattern and to particle shape | §5, PDF p7 / j.85; §10, PDF p29 / j.107; §11, PDF p34 / j.112 | Yes |
| Kishida 2025 | Drum 120 mm at 15 rpm, i.e. ~12 % of critical (rolling / cascading regime, not cataracting) | Fig. 2(a), PDF p4 | Yes (figure read) |

## PPT

| Slide | Content |
|---|---|
| 4 | "Rangos de Velocidad de Rotacion (RPM) usuales: Valor Superior = 10 RPM, Valor Inferior = 8.6 RPM, Valor Seleccionado -> SAG_B = 8.99 RPM ~ 9 RPM" (plant data, box plots; the PPT's SAG_B is SAG_A in these docs) |
| 33, 34 | Snapshots "VELOCIDAD 8 RPM", "VELOCIDAD 6 RPM" |

## Current state

| Where | What |
|---|---|
| `scenario.py:78` | `speed_rpm = 9.0` (positive = counter-clockwise seen from +Z) -- matches |
| `scenario.py:370-434` | `critical_speed_rpm()` and `fraction_critical` use `mill.diameter_m`, still defaulting to 11.0 m, so the reported fraction is wrong (70.1 % instead of 72.8 %) until C10-1 ([10](10_mill_geometry.md)) |
| Existing dataset | Shell-contact particles move at ~8.7 rpm, consistent with 9 rpm |

## Analysis

Critical speed N_c = 42.3 / sqrt(D - d) rpm (D, d in m), equivalent to
(60 / 2 pi) sqrt(g / (R - r)):

| Case | N_c | 9 rpm | 8.6 rpm | 10 rpm |
|---|---|---|---|---|
| D = 11.8375 m, d = 0.1397 m | 12.37 rpm | **72.8 %** | 69.5 % | 80.9 % |

Convention: with N_c = 42.3 / sqrt(D) (no ball-diameter correction, also
common in plant practice) 9 rpm is 73.2 % instead of 72.8 % -- a 0.4-point
difference, small next to the 70-81 % operating band. The plant's own
definition is collected with the mill data (author to-do A2); the
literature comparisons hold under either: Owen & Cleary 74.7-75.4 %,
Govender 74.7-75.2 %.

The plant range 8.6-10 rpm is 70-81 % of critical, the band of the SAG DEM
references (Owen 75 %, Govender ~75 %). One revolution takes 6.667 s; the
shell speed is 5.58 m/s.

Kishida's drum runs at ~12 % of critical, a different flow regime. The
surrogate method is transferable, but time scales must be compared in
**revolutions**, not seconds ([14](14_dataset_runs_and_recording.md)).

## Verdict and how to defend it

"The mill turns at 9 rpm, the median operating speed of SAG_A, the reference
mill; SAG_B and SAG_C are evidence that this value is typical, as the three
mills normally operate between 8.6 and 10 rpm (slide 4). 9 rpm is 72.8 % of
the critical speed of the 11.84 m mill -- the same regime
as the SAG DEM studies of Owen & Cleary (75 %) and Govender et al. (10 rpm,
~75 %)."
