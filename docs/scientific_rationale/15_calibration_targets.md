# 15 -- Calibration targets (charge shape and power)

## Decision

**Angle convention (fixed 2026-10-18):** 0 deg at the **3 o'clock** position
(right side, +X in YADE), angles increasing **counter-clockwise**, mill
rotating **counter-clockwise** seen from +Z (positive angular velocity about
Z in YADE). The charge therefore rises on the right: shoulder in the first
quadrant (~25 deg), toe in the third quadrant (~215 deg). Liner designs are
symmetric, so this orientation can be chosen freely in simulation.

**Calibration (SAG_B):** friction and rolling resistance
([05](05_friction.md), [06](06_rolling_resistance.md)) are tuned so the
steady-state charge reproduces SAG_B at SAG_B's operating point
(Jb 17 %, Jc 26 %, 9 rpm):

| Target | SAG_B median | SAG_B interquartile range (box) |
|---|---|---|
| Toe angle | **215 deg** | ~214.6-215.8 deg |
| Shoulder angle | **24.6 deg** | ~22-26.4 deg |

**Validation (SAG_A, SAG_C):** with the calibrated parameters frozen, run
SAG_A and SAG_C at their own Jb / Jc / speed and compare toe and shoulder
(medians: SAG_A 212 / 27 deg, SAG_C 206 / 38.2 deg). Only valid if the three
mills share shell diameter and liner / lifter design (to confirm).

**Power:** secondary, consistency check only (see analysis) -- used if the
plant power draw and mill length are available.

Simulated toe / shoulder are measured on the steady charge from the **liner
contact-force distribution** around the shell (Owen & Cleary §4.3) -- what
plant liner sensors observe -- with Boemer's position-density contour as a
cross-check.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Owen & Cleary 2015 | Charge structure characterised by head, shoulder, bulk toe and impact toe, found (1) visually from particle streaks and (2) from mean liner pressure distributions | Abstract PDF p1 / j.19; §1, PDF p2 / j.20 | Yes |
| Owen & Cleary 2015 | Angles "given as an angle of anti-clockwise rotation from the 3 o'clock position"; Table 5 gives head / shoulder / bulk toe / impact toe for 12 cases | §4.1 and Table 5, PDF p4 / j.22 | Yes |
| Owen & Cleary 2015 | Key positions "can also be determined, in principle, directly from the level of liner impact forces predicted by the DEM simulation" | §4.3, PDF p8 / j.26; §4.4, PDF p9 / j.27 | Yes |
| Owen & Cleary 2015 | Plant measurement by instrumented lifters, lifter-bolt accelerometers, acoustics, incl. Sensomag (Keshav et al. 2011) | §1, PDF p2 / j.20 | Yes |
| Owen & Cleary 2015 | Predictive model of fill level and lifter height from key charge locations | §5, PDF p12 / j.30 | Yes |
| Boemer & Ponthot 2017 | Calibrate on one case (case 1), validate on others (cases 2-4: other speed, fill, liner) | Table 1, PDF p3 / j.55 | Yes |
| Boemer & Ponthot 2017 | "Position density limit" contour; toe and shoulder read from it; power predicted within ~5 % | §2.3, PDF p6 / j.58; Fig. 9, PDF p7 / j.59; abstract, PDF p1 | Yes |
| Govender 2015 | Full-length Los Bronces SAG simulation: computed 6.8 MW vs reported 7.1 MW; "we showed we could match the power consumption exactly by changing the coefficient of restitution"; ~68 % of power through lifters | §3, PDF p14 / j.165 | Yes |
| Cleary & Morrison 2016 | Power = torque applied to the mill by all particle contacts x rotation speed | §2, PDF p3 / j.77 | Yes |

## PPT

| Slide | Content |
|---|---|
| 2 | Jb and Jc box plots for SAG_A/B/C |
| 3 | Toe and shoulder box plots for SAG_A/B/C; SAG_B toe 215 deg, shoulder 24.6 deg |
| 4 | Speed box plots; SAG_B 8.99 rpm |
| 31 | Simulation snapshot annotated 212 deg / 26.5 deg (read by eye with a protractor overlay; likely run with the friction bug, see [05](05_friction.md)) |

## Current state

No toe / shoulder measurement exists in code. The branch's `monitor.py`
already logs the torque of all particle contacts on the mill facets and the
drive power P = -T_z * omega (Cleary & Morrison §2 definition) every monitor
interval, so slice power **is** computed in YADE.

## Analysis

### Plant values vs. Owen & Cleary in this convention

Owen's mill turns the other way (charge on the left), so their angles map to
this convention as theta' = 180 deg - theta:

| Feature | Owen Table 5, all 12 cases (their convention) | In this convention | Owen case 2/5/7/9 (27.5 % fill, 175 mm lifters) | SAG_B |
|---|---|---|---|---|
| Head | 98-130 | 50-82 | 68-70 | -- |
| Shoulder | 146-164 | **16-34** | 28-32 | **24.6** |
| Bulk toe | 306-324 | **216-234** | 226 | -- |
| Impact toe | 306-338 | **202-234** | 208-210 | **215** |

SAG_B lies inside Owen's simulated ranges: the shoulder within 16-34 deg,
the toe inside both toe ranges and, for Owen's closest case (27.5 % fill),
between the impact toe (208-210 deg) and the bulk toe (226 deg). This supports both the
convention and the targets. Which toe the plant reports (impact or bulk) is
worth confirming; a liner sensor most likely detects the **impact** toe
region, so the simulated toe should be extracted the same way (liner force).

### Why calibrate on SAG_B and validate on SAG_A / SAG_C

All other inputs (Jb, Jc, speed) are SAG_B's, so the charge-shape targets
must be too. Using the other two mills as **independent validation** -- as
Boemer & Ponthot calibrate on case 1 and validate on cases 2-4 -- turns the
calibration into a prediction test: if the frozen parameters reproduce SAG_A
and SAG_C's shoulders (27 and 38.2 deg) from their own operating points,
the material model is shown to be predictive, not just fitted.

### How power would be used

YADE computes the slice power directly from the contact torque on the mill
(logged by `monitor.py`). To compare with a plant reading:

P_mill,DEM ~ P_slice x (L_eff / 0.375 m)

where L_eff is the effective grinding length of the belly. Limitations:
the plant figure includes motor / drive losses (gross vs. net power), the
conical ends, slurry and the real PSD; Govender's full 3D SAG model still
differed by ~4 % and could be tuned by restitution alone. Power is therefore
a **consistency check** (order of magnitude, ~10-20 %), and especially useful
as a **ratio** across mills: P_A / P_B and P_C / P_B from DEM vs. plant,
where most of those systematic factors cancel. It needs, per mill, the
average power (kW, net / at pinion if possible) over the same period as the
toe / shoulder data, and the belly length.

## Verdict and how to defend it

"Contact parameters were calibrated so that the steady-state toe and
shoulder angles, extracted from the simulated liner contact-force
distribution as in Owen & Cleary (2015, §4.3), match the SAG_B plant medians
(215 deg and 24.6 deg, measured counter-clockwise from 3 o'clock with
counter-clockwise rotation). These lie within the ranges of Owen & Cleary's
SAG simulations in the same convention (shoulder 16-34 deg, toe 202-234 deg).
The calibrated model was then validated, without re-tuning, against SAG_A
and SAG_C at their own operating points."

## Open items

- Confirm SAG_A / SAG_C share the 40 ft shell and the 30-lifter liner design
  (otherwise they cannot validate a SAG_B-geometry model).
- Confirm whether the plant toe is impact toe or bulk toe.
- If available: average power and belly length per mill.
- Implement toe / shoulder extraction (liner-force angular bins + position
  density) for calibration runs.
