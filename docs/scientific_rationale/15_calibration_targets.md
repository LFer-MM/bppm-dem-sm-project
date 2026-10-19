# 15 -- Calibration targets (charge shape and power)

## Decision

Calibrate friction and rolling resistance ([05](05_friction.md),
[06](06_rolling_resistance.md)) so that the steady-state simulated charge
reproduces **SAG_B**:

| Target | SAG_B median | SAG_B interquartile range (box) | Other mills (medians) |
|---|---|---|---|
| Toe angle | **215 deg** | ~214.6-215.8 deg | SAG_A 212, SAG_C 206 |
| Shoulder angle | **24.6 deg** | ~22-26.4 deg | SAG_A 27, SAG_C 38.2 |
| Power (if available) | -- | -- | -- |

Angle convention (inferred from the protractor overlay on slide 31): degrees
**clockwise from 12 o'clock**, viewed with the charge rising on the right.
**To confirm** with the plant's measurement system before calibrating (see
analysis -- the shoulder value only makes sense if it is a liner-contact
measurement).

Simulated toe / shoulder are measured on the steady charge (after spin-up)
from the **liner pressure / contact distribution** around the shell (Owen &
Cleary §4.3), which is what plant liner-mounted sensors observe, with the
position-density contour (Boemer & Ponthot) as a cross-check.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Owen & Cleary 2015 | Charge structure characterised by head, shoulder, bulk toe and impact toe, found (1) visually from particle streaks and (2) from mean liner pressure distributions | Abstract PDF p1 / j.19; §1, PDF p2 / j.20 | Yes |
| Owen & Cleary 2015 | Angles "given as an angle of anti-clockwise rotation from the 3 o'clock position"; Table 5 (case 2, 27.5 % fill, 175 mm lifters): head 110, shoulder 148, bulk toe 314, impact toe 330 deg | §4.1 and Table 5, PDF p4 / j.22 | Yes |
| Owen & Cleary 2015 | "The key charge positions ... can also be determined, in principle, directly from the level of liner impact forces predicted by the DEM simulation"; the angle where the mean pressure becomes non-zero relates to the head | §4.3, PDF p8 / j.26; §4.4, PDF p9 / j.27 | Yes |
| Owen & Cleary 2015 | Plant measurements by instrumented lifters / lifter-bolt accelerometers / acoustics, incl. Sensomag (Keshav et al. 2011) | §1, PDF p2 / j.20 | Yes |
| Owen & Cleary 2015 | Predictive model of fill level and lifter height from key charge locations | §5, PDF p12 / j.30 | Yes |
| Boemer & Ponthot 2017 | "Position density limit": contour of the time-averaged particle position density separating the main charge from the region where particles are ~10x less likely; toe and shoulder angles read from it; validated against photographs and power (~5 %) | §2.3, PDF p6 / j.58; Fig. 9, PDF p7 / j.59; abstract, PDF p1 | Yes |
| Govender 2015 | Friction tuned to reproduce a reference shoulder position; restitution can tune power | §1.6.1, PDF p7 / j.158; §3, PDF p14 / j.165 | Yes |
| Cleary & Morrison 2016 | Power = torque applied by all contacts x rotation speed | §2, PDF p3 / j.77 | Yes |

## PPT

| Slide | Content |
|---|---|
| 3 | "Acomodo de Carga": box plots of toe and shoulder angle for SAG_A/B/C; text: toe usual range 206-216 deg, SAG_B 215 deg; shoulder "Valor Superior = 22.9, Valor Inferior = 36.2" (labels swapped), SAG_B 24.6 ~ 25 deg |
| 31 | Simulation snapshot with protractor overlay (0 at 12 o'clock, increasing clockwise) annotated 212 deg / 26.5 deg |
| 30 | Manual search of friction / density "respecto a Acomodo de Carga"; GridSearch in development |

## Current state

No toe / shoulder measurement exists in code; slide 31 values were read by
eye on a snapshot. The branch's `monitor.py` logs the charge centre-of-mass
angle and drive power, not toe / shoulder.

## Analysis

- **Convention check.** Owen's shoulder at ~148-152 deg (anticlockwise from
  3 o'clock, charge rising on the left) is ~30 deg above the horizontal,
  i.e. ~60 deg from 12 o'clock. A shoulder at 24.6 deg from 12 o'clock would
  be 65 deg above the horizontal -- much higher than any DEM bulk shoulder in
  Owen's Table 5. Owen's bulk toe (~314 deg) is ~44 deg from 6 o'clock;
  SAG_B's toe (215 deg clockwise from 12) is 35 deg from 6 o'clock --
  comparable. So the toe is consistent; the shoulder needs the plant's
  definition (e.g. the angle where a liner sensor stops feeling the charge,
  which lies above the bulk shoulder, nearer Owen's "head"). This must be
  settled before calibrating, or the calibration will chase the wrong
  feature.
- **Which simulated quantity.** Because plant sensors are on the liner, the
  simulated targets should be extracted the same way: mean normal force on
  the shell / lifter facets binned by angle (Owen §4.3), taking the angles
  where it rises above / falls below a threshold.
- **Power** is the second independent target used by every validated mill
  study (Boemer ~5 %; Govender; Cleary & Morrison). For a slice:
  P_slice ~ P_mill x (slice length / effective mill length). Needs plant
  power and mill length.
- **Owen's §5 model** can serve as an independent sanity check: given fill
  and lifter height it predicts the key locations for a generic SAG mill.

## Verdict and how to defend it

"Contact parameters were calibrated so that the simulated steady-state toe
and shoulder angles, measured from the liner contact-force distribution as
in Owen & Cleary (2015, §4.3), match the plant values of SAG_B (toe 215 deg,
shoulder 24.6 deg; slide 3), in the same angular convention as the plant
measurement system."

## Open items

- **Confirm the plant angle convention and sensor definition** (which feature
  is "shoulder"; zero and direction).
- Obtain SAG_B power draw and mill length if available.
- Implement toe / shoulder extraction (liner-force bins + position density),
  usable on calibration runs.
