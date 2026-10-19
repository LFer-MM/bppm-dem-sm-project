# 09 -- Poisson's ratio

## Decision

| Material | nu |
|---|---|
| Steel | **0.292** |
| Rock | **0.25** |

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Shigley | Carbon steel ("Acero al carbono"): nu = 0.292 (with E = 207 GPa, G = 79.3 GPa) | Inside-cover table "Constantes fisicas de materiales", PDF p3 | Yes |
| Gercek 2007 | Fig. 4 "Typical ranges of values for Poisson's ratio of some rock types": andesite ~0.20-0.35, basalt ~0.10-0.35, diabase ~0.10-0.28, granite ~0.10-0.33, diorite ~0.20-0.30 (read from the bar chart) | Fig. 4, PDF p6 (j.6); referenced in §4.1 text, PDF p5 | Yes (figure read) |
| Vergara et al. | Intact El Teniente (CMET) andesite: nu = 0.25 | Table 1, PDF p3 | Yes |
| Kishida 2025 | nu = 0.3 | Fig. 2(b), PDF p4 | Yes |

## PPT

| Slide | Content |
|---|---|
| 8, 9, 12 | Steel 0.292 [2] (Shigley), rock 0.25 [4][7] (Gercek Fig. 4; Vergara) |
| 9 | Used in E_eff = E / (1 - nu^2) for the dt / E_reduced calculation |

## Current state

`main` `config.py:90,97`: 0.292 / 0.25 -- matches.

## Analysis

nu enters Hertz-Mindlin through E* and G* (Kishida Table A-1), so it changes
contact stiffness by a few percent only; the macroscopic results are
insensitive to stiffness (see [03](03_stiffness_young_modulus.md)). 0.25 sits
inside Gercek's andesite range and equals Vergara's value for El Teniente
andesite. Since the plant ore type is not stated in the PPT, the defence
relies on 0.25 being central for the igneous rocks of porphyry copper
deposits.

## Verdict and how to defend it

"Poisson's ratios are physical values: 0.292 for carbon steel (Shigley) and
0.25 for the ore, within the typical range for andesite and other igneous
rocks (Gercek 2007, Fig. 4) and equal to the value for El Teniente andesite
(Vergara et al., Table 1). Their influence is limited to the contact
stiffness, to which the mill response is insensitive."
