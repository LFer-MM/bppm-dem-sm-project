# 15 -- Calibration targets (charge shape and power)

## Decision

**Angle convention (fixed 2026-10-18):** 0 deg at the **3 o'clock** position
(right side, +X in YADE), angles increasing **counter-clockwise**, mill
rotating **counter-clockwise** seen from +Z (positive angular velocity about
Z in YADE). The charge rises on the right: shoulder in the first quadrant
(~25 deg), toe in the third quadrant (~215 deg). Liner designs are
symmetric, so this orientation is a free choice in simulation.

**Role of the three plant mills.** **SAG_B is the reference**: its operating
point sets the simulation and its charge-shape angles are the targets the
simulation is compared to. **SAG_A and SAG_C are evidence that the selected
values are typical**: their designs and dimensions differ slightly, so they
are not simulated or used as validation cases, but their box plots show that
SAG_B's speed, fill, toe and shoulder sit inside the normal operating ranges
of SAG mills.

**Calibration target (SAG_B, at SAG_B's operating point Jb 17 %, Jc 26 %,
9 rpm):**

| Target | SAG_B median | SAG_B interquartile range (box) | Range over the three mills (medians) |
|---|---|---|---|
| **Bulk** toe angle | **215 deg** | ~214.6-215.8 deg | 206-215 deg |
| Shoulder angle | **24.6 deg** | ~22-26.4 deg | 24.6-38.2 deg |

Friction and rolling resistance ([05](05_friction.md),
[06](06_rolling_resistance.md)) are tuned until the simulated steady-state
bulk toe and shoulder fall inside the SAG_B interquartile ranges.

**Measurement in simulation:** the plant reports the **bulk** toe, so the
simulated toe and shoulder are read from the boundary of the main charge
body: the time-averaged position-density contour (Boemer & Ponthot §2.3),
equivalent to Owen & Cleary's visual bulk toe / shoulder (§4.1). The liner
contact-force distribution (Owen & Cleary §4.3) is a cross-check, not the
primary measure, because it mainly detects the impact toe.

**Power:** not a calibration target and no plant power data is used
(decided 2026-10-18). Power is computed in YADE only for the internal energy
balance ([16](16_validation_checks.md), V4). The analysis below records why
plant power would not be a determining target.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Owen & Cleary 2015 | Charge structure: head, shoulder, **bulk toe** and impact toe; bulk toe and shoulder estimated from standard particle visualisations, impact toe and head from streaks | §4.1, PDF p3-4 / j.21-22 | Yes |
| Owen & Cleary 2015 | Angles "given as an angle of anti-clockwise rotation from the 3 o'clock position"; Table 5 gives the four locations for 12 cases | §4.1 and Table 5, PDF p4 / j.22 | Yes |
| Owen & Cleary 2015 | Key positions can also be read from liner impact forces; correlation with the visual positions | §4.3, PDF p8 / j.26; §4.4, PDF p9 / j.27 | Yes |
| Owen & Cleary 2015 | Plant measurement by instrumented lifters / accelerometers / acoustics, incl. Sensomag (Keshav et al. 2011) | §1, PDF p2 / j.20 | Yes |
| Boemer & Ponthot 2017 | "Position density limit": contour of the time-averaged position density separating the main charge from where particles are ~10x less likely; toe and shoulder read from it | §2.3, PDF p6 / j.58; Fig. 9, PDF p7 / j.59 | Yes |
| Boemer & Ponthot 2017 | Power 1311 / 1382 / 1391 W for mu = 0.25 / 0.5 / 0.75 (~6 % over a 3x change of friction); stiffness and restitution "only have a relatively small impact on the power draw"; power predicted within ~5 % | §3.1.4, PDF p10 / j.62; abstract, PDF p1 | Yes |
| Govender 2015 | Full-length Los Bronces SAG: 6.8 MW computed vs 7.1 MW reported; "we could match the power consumption exactly by changing the coefficient of restitution" | §3, PDF p14 / j.165 | Yes |
| Cleary & Morrison 2016 | Power = torque applied to the mill by all particle contacts x rotation speed; must balance collisional dissipation within a few % | §2, PDF p3 / j.77 | Yes |

## PPT

| Slide | Content |
|---|---|
| 2 | Jb and Jc box plots for SAG_A/B/C (operating-range justification) |
| 3 | Toe and shoulder box plots for SAG_A/B/C; SAG_B toe 215 deg, shoulder 24.6 deg |
| 4 | Speed box plots; range 8.6-10 rpm; SAG_B 8.99 rpm |
| 31 | Simulation snapshot annotated 212 deg / 26.5 deg (read by eye; likely run with the friction bug, see [05](05_friction.md)) |

## Current state

No toe / shoulder measurement exists in code. The branch's `monitor.py` logs
the contact torque on the mill facets and the drive power P = -T_z * omega
every monitor interval.

## Analysis

### Plant values vs. Owen & Cleary in this convention

Owen's mill turns the other way (charge on the left), so their angles map to
this convention as theta' = 180 deg - theta:

| Feature | Owen Table 5, 12 cases (their convention) | In this convention | Owen 27.5 % fill, 175 mm lifters | SAG_B |
|---|---|---|---|---|
| Shoulder | 146-164 | **16-34** | 28-32 | **24.6** |
| Bulk toe | 306-324 | **216-234** | 226 | **215** |
| Impact toe | 306-338 | 202-234 | 208-210 | -- |

The SAG_B shoulder lies inside Owen's range. The SAG_B bulk toe (215 deg)
is just past the edge of Owen's bulk-toe range (216 deg, reached in Owen's
highest-fill case, 32.8 %), i.e. the plant charge extends ~10 deg further
round the mill than Owen's 27.5 % case. Plausible causes: different mill
(8.4 m, 56 lifters, 75 % critical, wide PSD vs. 11.84 m, 30 lifters, 72.8 %,
binary charge). This is a quantitative check of the targets, not a
contradiction.

### Why the plant toe must be measured as a bulk toe in simulation

The bulk toe is where the main charge body meets the liner; the impact toe
is where the cataracting stream lands, usually further up. Comparing the
plant's bulk toe with a simulated impact toe would bias the calibration by
the 10-20 deg separating them in Owen's Table 5.

### How important is plant power?

Power is **not a determining support** for the material-parameter decisions,
for three reasons:

1. **Low sensitivity to the calibrated parameters.** In Boemer's validated
   mill a 3x change of friction (0.25 -> 0.75) moves power by ~6 %, and
   stiffness and restitution move it even less. Power mostly reflects charge
   mass and centre-of-mass position, which are fixed by Jc, Jb, density and
   speed, not by friction.
2. **Large comparison uncertainty.** A 0.375 m slice must be scaled to the
   full mill (P_mill ~ P_slice x L_eff / 0.375 m), and the plant figure
   includes motor / drive losses, conical ends, slurry and a real size
   distribution. These systematic differences (likely 10-20 %) exceed the
   ~6 % signal from friction, so power cannot discriminate between candidate
   parameter sets. Govender's full-length SAG model was 4 % off and could be
   "matched exactly" by changing restitution alone -- an example of power
   fitting a parameter it does not really constrain.
3. **Different designs.** With slightly different mills, cross-mill power
   ratios do not cancel the systematic factors either.

What power **is** used for: the **energy balance inside the simulation**
(V4) -- supplied energy (from the YADE contact torque) vs. collisional
dissipation. This needs no plant data and is a strong numerical-quality
check. Plant power would at most have offered an order-of-magnitude sanity
check; it is not pursued.

## Verdict and how to defend it

"SAG_B is the reference mill: the operating point (9 rpm, Jb 17 %, Jc 26 %)
and the charge-shape targets were taken from it. SAG_A and SAG_C are evidence
that the selected values are typical: their operating data place SAG_B's
values within the normal ranges of SAG operation (speed 8.6-10 rpm, bulk toe
206-215 deg, shoulder 24.6-38.2 deg). Contact parameters were calibrated so the simulated
steady-state bulk toe and shoulder, read from the position-density contour
(Boemer & Ponthot 2017, §2.3), fall within the SAG_B interquartile ranges
(215 deg, 24.6 deg; counter-clockwise from 3 o'clock). These targets lie in
or at the edge of the ranges of Owen & Cleary's SAG simulations in the same
convention. Power was not used as a calibration target, since it is
insensitive to the contact parameters (Boemer & Ponthot 2017, §3.1.4); it
was used only to check the internal energy balance of the simulations."

## Open items

- Implement bulk toe / shoulder extraction from the time-averaged position
  density (plus the liner-force cross-check).
