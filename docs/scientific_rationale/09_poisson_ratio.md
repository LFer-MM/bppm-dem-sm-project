# 09 -- Poisson's ratio

## Decision

| Material | nu |
|---|---|
| Steel (balls and the steel liner material) | **0.292** |
| Rock | **0.25** |

- Physical values, used unchanged: the stiffness reduction f = 26
  ([03](03_stiffness_young_modulus.md)) scales Young's moduli only.
- Not calibrated and no sensitivity run of its own: the effect of nu on the
  contact is a few percent, far inside the stiffness range already tested by
  V10 (Analysis).

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Shigley | Carbon steel ("Acero al carbono"): nu = 0.292 (with E = 207 GPa, G = 79.3 GPa) | Inside-cover table "Constantes fisicas de materiales", PDF p3 | Yes |
| Gercek 2007 | Fig. 4 "Typical ranges of values for Poisson's ratio of some rock types": andesite ~0.20-0.35, basalt ~0.10-0.35, diabase ~0.10-0.28, granite ~0.10-0.33, diorite ~0.20-0.30 (read from the bar chart) | Fig. 4, PDF p6 (j.6); referenced in §4.1 text, PDF p5 | Yes (figure read) |
| Vergara et al. 2020 | Intact El Teniente (CMET) andesite: nu = 0.25 (Table 1); the rock-mass model uses the same nu = 0.25 with E = 55 GPa and 28 kN/m^3 (Table 10) | Table 1, manuscript PDF p3; Table 10, manuscript PDF p16 | Yes |
| YADE source (`7c8d01e`) | nu enters the Hertz-Mindlin stiffnesses through E* = 1 / ((1 - nu_a^2)/E_a + (1 - nu_b^2)/E_b) and G* from G = E / (2 (1 + nu)); kn = 4/3 E* sqrt(R), ks = 8 G* sqrt(R) | `pkg/dem/HertzMindlin.cpp:148-157` | Yes (source read) |
| Kishida 2025 | nu = 0.3 | Fig. 2(b), PDF p4 | Yes |

## PPT

| Slide | Content |
|---|---|
| 8, 9, 12 | Steel 0.292 [2] (Shigley), rock 0.25 [4][7] (Gercek Fig. 4; Vergara) |
| 9 | Used in E_eff = E / (1 - nu^2) for the dt / E_reduced calculation |

## Current state

`pm_dem_sm/config.py:92, 99`: 0.292 / 0.25 -- matches the decision.

## Analysis

- **Effect on the contact.** nu enters Hertz-Mindlin through E* and G*
  (Kishida Table A-1; YADE source). Over Gercek's whole andesite range
  (0.20-0.35) the rock-rock E* changes by -2.3 % to +6.8 % relative to
  nu = 0.25, so collision time and peak overlap (both ~ E*^-0.4) change by
  less than 3 %. The tangential / normal stiffness ratio,
  2 (1 - nu) / (2 - nu), is 0.86 for rock and 0.83 for steel. These shifts
  are far smaller than the x0.5 / x2 stiffness changes of V10, under which
  the charge is expected to be insensitive ([03](03_stiffness_young_modulus.md);
  Boemer & Ponthot 2017), so nu needs no sensitivity run of its own.
- **Rock value.** The SAG_A-C ore is Chilean porphyry copper ore
  ([03](03_stiffness_young_modulus.md), [08](08_density.md)). 0.25 is
  Vergara et al.'s value for El Teniente andesite, the same source as the
  rock modulus (55 GPa) and density (2850 kg/m^3), so all three rock
  properties come from one source; it also sits inside Gercek's typical
  ranges for andesite (~0.20-0.35) and the other igneous host rocks of
  porphyry deposits.
- **Steel value.** 0.292 is Shigley's carbon-steel value, given together
  with the E = 207 GPa used in [03](03_stiffness_young_modulus.md). It also
  applies to the steel liner material ([05](05_friction.md)).
- **Time step.** nu enters the Rayleigh step but not YADE's P-wave step;
  both were computed with these values ([02](02_time_step.md)).

## Verdict and how to defend it

"Poisson's ratios are physical values: 0.292 for carbon steel (Shigley) and
0.25 for the ore, within the typical range for andesite and other igneous
rocks (Gercek 2007, Fig. 4) and equal to the value for El Teniente andesite
(Vergara et al. 2020, Table 1), the same source as the ore modulus and
density. Their influence is limited to the contact stiffness, which changes
by less than 7 % over the typical andesite range -- far less than the
stiffness range over which the mill response was shown to be insensitive."

## Open items

None. Covered indirectly by the stiffness sensitivity V10
([16](16_validation_checks.md)).
