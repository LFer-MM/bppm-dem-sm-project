# 03 -- Stiffness (Young's modulus)

## Decision

Use the reduced moduli of PPT slide 12:

| Material | Physical E | Simulation E | Reduction |
|---|---|---|---|
| Steel (balls, lifters, shell) | 207 GPa | **33.16 GPa** | 6.2x |
| Rock | 55 GPa | **2.868 GPa** | 19x |

Confirmed 2026-10-18 together with dt = 2.5e-5 s (option A in
[02](02_time_step.md)).

Acceptance (all relative to the smaller particle **diameter**):

- **mean** overlap <= 0.5 % (the strictest average in the literature,
  Cleary & Morrison 2016);
- **maximum** overlap < 10 % (Boemer & Ponthot's sensitivity limit); the
  predicted worst case is 3.3 %;
- macroscopic results (toe, shoulder, power) unchanged when E is halved or
  doubled.

## Overlap criteria in the literature

| Source | Criterion | Kind | Relative to | Where |
|---|---|---|---|---|
| Cleary 2001 | "Typically, average overlaps of 0.1-1.0% are desirable" (hence kn = 8e6 N/m) | average, practice | not stated (diameter in the same group's later papers) | §2, PDF p4 / j.82 |
| Cleary & Morrison 2016 | "Typically, average overlaps of 0.1-0.5% are adequate to ensure a balance between computing speed and realistic predictions" | average, practice | not stated | §2, PDF p3 / j.77 |
| Owen & Cleary 2015 | kn chosen "to give an average overlap of the order of 0.8% of the average particle diameter" | average, used value | average diameter | §3, PDF p3 / j.21 |
| Boemer & Ponthot 2017 | Limit "the average overlap ... to a value between 0.1 and 1 % with respect to the diameter of the ball ... maybe 10 % would still lead to satisfying results" | average, practice | ball diameter | §3.1.2, PDF p8 / j.60 |
| Boemer & Ponthot 2017 | Results "relatively insensitive to the normal stiffness provided that the maximum overlap percentage ... is smaller than about 10 %" | **maximum, measured sensitivity** | diameter | §4, PDF p13 / j.65 |
| Boemer & Ponthot 2017 | Method: maximum overlap from the analytic collision (Eqs. 8-9) at the worst-case impact speed v_r = sqrt(2 g D) (free fall across the mill) | method | -- | §3.1.2, PDF p8 / j.60 |
| Govender 2015 | "Typical DEM simulations use a spring stiffness and time-step that limits the maximum penetration depth to d_max ~ 0.05 r where r is the radius of the smallest particle" (= 2.5 % of its diameter); lifter contacts accepted only for penetration < 5 % of the radius (Algorithm 1) | maximum, practice | smallest radius | §1.5, PDF p6 / j.157; Algorithm 1, PDF p5 / j.156 |
| Kishida 2025, Thakur 2016 | No overlap criterion stated | -- | -- | -- |

Two kinds of number appear: **average** overlaps (practice, 0.1-1 %, the
strictest being 0.1-0.5 %) and **maximum** overlaps (Govender's typical
practice 2.5 % of the diameter; Boemer's tested sensitivity limit ~10 %).
Only Boemer's 10 % is an actual sensitivity result; the others are
customary values.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Shigley | Carbon steel: E = 207 GPa, G = 79.3 GPa, nu = 0.292 (table "Constantes fisicas de materiales"); also "el acero tiene un modulo de elasticidad de alrededor de 30 Mpsi (207 GPa)" | Inside-cover table, PDF p3; Ch. 2 text, PDF p59 | Yes |
| Vergara et al. | Intact El Teniente (CMET) andesite: E_i = 55 GPa, nu = 0.25 | Table 1, PDF p3 (repeated in the table on PDF p6) | Yes |
| Cleary & Morrison 2016 | "the stiffness is used as a numerical rather than a physical parameter ... This is generally possible as long as the numerical contact deformations remain small and the contact force networks are not altered by the moderate softening of the springs." (the sentence says "chosen to be larger than the real material stiffness so as to maximise the timestep", which given the rest of the sentence reads as a wording slip for softer) | §2, PDF p3 / j.77 | Yes |
| Cleary & Morrison 2016 | kn = 500,000 N/m, ks = 250,000 N/m for a 1.12 m pilot mill | Table 2, PDF p7 / j.81 | Yes |
| Owen & Cleary 2015 | kn = 20e6 N/m "chosen to give an average overlap of the order of 0.8 % of the average particle diameter. This is sufficient to give accurate mill simulations" | §3, PDF p3 / j.21 | Yes |
| Boemer & Ponthot 2017 | "A common technique to choose the value of the normal stiffness kn is to limit the average overlap ... to a value between 0.1 and 1 % with respect to the diameter of the ball ... maybe 10 % would still lead to satisfying results" | §3.1.2 "Influence of the stiffness", PDF p8 / j.60 | Yes |
| Boemer & Ponthot 2017 | Charge motion and power "relatively insensitive to the normal stiffness provided that the maximum overlap percentage of two colliding spheres is smaller than about 10 %" | §4, PDF p13 / j.65 | Yes |
| Govender 2015 | Typical DEM limits the maximum penetration to ~0.05 r of the smallest particle | §1.5, PDF p6 / j.157 | Yes |
| Kishida 2025 | E = 1.0e7 Pa for 0.25-0.5 mm particles (strong reduction is standard practice even in the reference study) | Fig. 2(b), PDF p4 | Yes |
| Thakur 2016 | Contact stiffness scales **linearly with particle size** for coarse-grained (scaled-up) particles | Abstract, PDF p1 / j.130; §2, PDF p3 / j.132 | Yes -- but **not** about reducing E for dt |

## PPT

| Slide | Content |
|---|---|
| 8 | Physical moduli: steel 207 GPa [Shigley], rock 55 GPa [Vergara]; "-> ? Pa [3]" (Thakur). Text: stiffness can be reduced "siempre y cuando se mantenga un bajo overlap de particulas (< 0.1 %)" citing [3][5][6] |
| 9 | E_reduced = rho (R_min / dt_target)^2 (1 - nu^2); for dt_target = 1e-4: rock 3.03e8 Pa, steel 3.50e9 Pa |
| 10 | YADE overlap check (994 rocks, 234 balls, settled): original moduli max overlap 0.039 %; 3.5e9 / 3e8 Pa max overlap **1.085 %**. Target stated: dt_crit between 1.36e-5 and 1e-4 with overlap between 0.1 % and 0.5 % |
| 11 | E_reduced table for dt_crit = 1.5e-5, 2e-5, 3e-5, 3.25e-5, 3.5e-5, 5e-5 s (the 3e-5 row's formula text shows 0.00002 but the value is computed with 3e-5) |
| 12 | Final: steel 33.16e9 Pa, rock 28.68e8 Pa (= 2.868e9 Pa) |

Note on slide 10: `diagnostics.check_overlaps()` divides the penetration by
`min(r1, r2)` (a **radius**), so 1.085 % of the radius is 0.54 % of the
diameter. The papers quote overlap relative to the **diameter**.

## Current state

| Where | What |
|---|---|
| `main` `config.py:89` | steel young = 155,709,722,558 Pa (slide 11, dt_crit = 1.5e-5 row) |
| `main` `config.py:96` | rock young = 13,468,135,026 Pa (same row) |
| -- | Slide 12's final set is not in the code yet. |

## Analysis

Estimated **peak** overlaps for elastic Hertz impacts with the slide-12 set
(delta_max = (15 m* v^2 / (16 E* R*^0.5))^(2/5), relative to the smaller
diameter):

| Pair | 1 m/s | 5 m/s | 8 m/s | 12 m/s | **15.2 m/s (worst case)** |
|---|---|---|---|---|---|
| steel-steel | 0.21 % | 0.78 % | 1.13 % | 1.56 % | **1.89 %** |
| steel-rock | 0.36 % | 1.30 % | 1.89 % | 2.61 % | **3.16 %** |
| rock-rock | 0.37 % | 1.35 % | 1.97 % | 2.72 % | **3.30 %** |

The worst case follows Boemer's method: v_r = sqrt(2 g D) =
sqrt(2 x 9.81 x 11.8375) = 15.2 m/s, a particle falling from the top of the
mill to the bottom. Real impacts are slower (the old dataset's fastest
particle moved at 12.6 m/s).

Against the criteria:

- **Maximum overlap.** Worst case 1.9-3.3 %: well below Boemer's ~10 %
  sensitivity limit. The rock contacts exceed Govender's *customary* 0.05 r
  (2.5 % of the diameter) only for impacts above ~12 m/s, which are rare. To
  meet 2.5 % even at 15.2 m/s, E would have to double (overlap scales as
  E^-0.4) and dt shrink by a further ~25 %; not justified by any sensitivity
  evidence.
- **Average overlap.** Average overlaps come from the enduring contacts of the
  bulk charge, loaded by gravity rather than impacts, and are far smaller than
  impact peaks (slide 10's settled-bed check gave 0.54 % of the diameter even
  for the 9-11x softer 3.5e9 / 3e8 set). The slide-12 set is therefore
  expected to sit inside 0.1-0.5 %, the strictest average range (Cleary &
  Morrison). This must be measured, not assumed (see open items).

The slide-8 target "< 0.1 %" is below the lower end of every average range
in the library (0.1-0.5 % to 0.1-1 %); it should be replaced by these ranges.

## Verdict and how to defend it

"Young's moduli are reduced from their physical values (steel 207 GPa,
Shigley; El Teniente andesite 55 GPa, Vergara et al.) to 33.16 and 2.868 GPa.
In mill DEM the stiffness is a numerical parameter (Cleary & Morrison 2016,
§2), chosen to keep the average overlap within the customary 0.1-1 % of the
diameter (Cleary 2001, §2; Boemer & Ponthot 2017, §3.1.2), and within the
stricter 0.1-0.5 % of Cleary & Morrison (2016, §2); Owen & Cleary (2015) use
~0.8 %. The maximum overlap, estimated with Boemer & Ponthot's worst-case
impact speed sqrt(2 g D) = 15.2 m/s, is 3.3 %, well below the ~10 % up to
which charge motion and power are insensitive to stiffness (Boemer & Ponthot
2017, §4). Measured overlaps (mean X %, max Y %) are within these limits."

Replace the Thakur citation for this argument: Thakur 2016 concerns stiffness
scaling with particle size in coarse-grained DEM, not softening for dt.

## Open items / validation

- Measure mean / P99 / max overlap relative to the diameter, per contact
  pair type, in a steady-rotation run with the slide-12 set.
- Sensitivity: E x 0.5 and E x 2 for 3 revolutions; toe, shoulder and power
  must not change beyond run-to-run scatter.
- Update `config.MATERIALS` to the slide-12 values (code change, pending).
