# 12 -- Charge: fill level, particle sizes, packing and counts

## Decision

| Quantity | Value | Basis |
|---|---|---|
| Ball filling Jb (bulk) | **17 %** | SAG_B, the reference mill (slide 2); SAG_A / SAG_C show it is typical (15.2-18.5 %) |
| Total filling Jc (bulk) | **26 %** | SAG_B, the reference mill (slide 2); SAG_A / SAG_C show it is typical (24.9-35.1 %) |
| Rock bulk volume | Jc - Jb = **9 %** | modelling convention (see analysis) |
| Ball diameter | **0.1397 m** (5.5 in) | plant practice (slide 5) |
| Rock diameter | **0.06985 m** (2.75 in) | 2:1 size ratio (slide 6) |
| Packing fraction phi | **measured in the slice**; currently 0.5617 | slides 13-16; re-measure after calibration |
| Counts | N = phi * J * V / v_sphere | slide 7 / 16 formula |

With V = 39.4693 m^3, v_ball = 1.4275e-3 m^3, v_rock = 1.7844e-4 m^3:

| phi | Balls | Rocks | Total |
|---|---|---|---|
| 1.0 (slide 7, no voids) | 4,700 | 19,907 | 24,607 |
| **0.5617 (slide 16)** | **2,640** | **11,182** | **13,822** |
| 0.60 (literature bulk value, for comparison) | 2,820 | 11,944 | 14,764 |

(Slide 16 reports 2,638 / 11,171 = 13,809; the small difference is rounding of
the intermediate volumes.)

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Owen & Cleary 2015 | SAG fill levels 20-35 % studied ("the majority of the usual operating range for SAG mills"); constant 6 % ball charge, fill varied through rock | §3, PDF p3 / j.21; Table 2, PDF p3 | Yes |
| Govender 2015 | Los Bronces SAG charge "31% ore and 10% balls by volume" | §3, PDF p12 / j.163 | Yes |
| Cleary 2001 (2D) | Filling above 25-30 % gives significantly lower specific power; ball fraction has little effect for rock fractions >= 20 % by volume | §11, PDF p34 / j.112 | Yes |
| Kishida 2025 | Binary system with **2:1 size ratio** (0.5 / 0.25 mm), 1 M large + 2 M small (small = 20 % of solid volume) | Fig. 2(b), PDF p4 | Yes |
| Shi & Zhang 2008 | Monosize loose random packing 0.565-0.578 (Table 1); bimodal packing with d2/d1 = 2.0: 0.581-0.600 depending on number fraction (Table 3); higher size ratio -> denser | Table 1, PDF p4 / j.624; Table 3, PDF p5 / j.625 | Yes |
| Brouwers 2024 | For size ratio u = 2 the maximum binary packing occurs at a large-particle volume fraction c_L between 0.7 and 0.8 | PDF p29 | Yes |

## PPT

| Slide | Content |
|---|---|
| 2 | Plant ranges: Jb 15.2-18.5 % (SAG_B 16.8 % ~ 17 %); Jc 24.9-35.1 % (SAG_B 25.9 % ~ 26 %) |
| 5 | 5.5 in steel balls used in SAG_A/B/C "a lo largo de multiples campanas"; recent trial of 6 in balls in SAG_A/B, not confirmed as permanent |
| 6 | "2.75 pulgadas -> Ratio 2:1"; "relacion 2:1, 3:1, superior 5:1 es ineficiente y 2:1 permite reducir cantidad de particulas" (no citation) |
| 7 | Counts with phi = 1.0: 4,696 balls, 19,888 rocks (text divides the rock volume by the ball volume -- typo; numbers use 1.786e-4 m^3) |
| 13-15 | Packing-factor simulation: random mix of 19,888 rocks + 4,696 balls, damping 0.2 -> 0.0, "Ingresado + Asentado" and "Rotado (10) + Asentado"; bed height at 26 %: Y26% = 3.6826 m; Ydiff = 2.23615 m |
| 16 | Final: phi = 0.5617 -> 2,638 balls + 11,171 rocks = 13,809 |

## Current state

| Where | What |
|---|---|
| `main` `config.py:75-82` | ROCK_COUNT 19,888, BALL_COUNT 4,696 (phi = 1.0, slide 7), ROCK_DIAM_M 0.06985, BALL_DIAM_M 0.1397 |
| `main` `run_simulation.py:44-49` | Test charge: 994 rocks (r 0.034925) + 234 balls (r 0.06985) |
| Existing `sic_dataset_20s_dt0p0001` | 11,581 rocks with **r = 0.0381 m** (3 in) + 3,195 balls -- matches neither slide 7 nor slide 16 |

## Analysis

- **Jc - Jb convention.** Plant Jc is the bulk volume of the whole charge
  (balls + rock + voids); Jb the bulk volume of the ball bed. Treating the
  rock bulk as Jc - Jb puts rock and balls in separate bulk volumes, i.e. no
  rock in the voids of the ball bed. It is the standard simple split; the
  resulting balls are 65.4 % of the solid volume.
- **Packing.** phi = 0.5617 is below the bulk loose values for a 2:1 binary
  mixture (~0.58-0.62, Shi & Zhang Tables 1 and 3), which is expected in a
  slice only 2.7 ball diameters deep with end walls and lifters (wall
  effects loosen the packing). Measuring phi in the actual slice, as the PPT
  does, is therefore correct; a literature value would overfill the mill.
  The ball fraction of 0.654 is close to the densest composition for u = 2
  (c_L ~ 0.75, Brouwers), so phi is near its maximum for this size ratio.
- **phi depends on friction**: it must be re-measured after friction /
  rolling resistance are calibrated ([05](05_friction.md)).
- **Size ratio 2:1** matches Kishida and keeps the particle count tractable
  (a 2:1 instead of a realistic PSD). Owen & Cleary and Govender use full
  PSDs; the binary simplification is a project choice needed for the
  binary-mixing surrogate.
- **Fill check.** Jc = 26 % is inside Owen's 20-35 % and the plant range;
  Cleary 2001 notes specific power falls above 25-30 %.

## Verdict and how to defend it

"The charge reproduces SAG_B, the reference mill: Jb = 17 %, Jc = 26 % (plant
data); SAG_A and SAG_C are evidence that these fillings are typical (Jb
15.2-18.5 %, Jc 24.9-35.1 % across the three mills). Steel
balls and 2.75 in rock (2:1, the ratio used by Kishida et al. 2025). Particle
numbers follow N = phi J V / v with the packing fraction phi measured in the
simulated slice (0.5617), since wall effects in a 0.375 m slice make it lower
than bulk binary packings (0.58-0.62, Shi & Zhang 2008)."

## Open items / validation

- Re-measure phi with the calibrated friction and rolling resistance; fix the
  counts from it; store them in the scenario with phi and the method.
- Write the measurement method precisely (bed height at rest vs. volume of
  the occupied cells) and its repeatability over seeds.
- Update `config.ROCK_COUNT` / `BALL_COUNT` (code change, pending).
- Regenerate the datasets (the existing one uses 3 in rock).
