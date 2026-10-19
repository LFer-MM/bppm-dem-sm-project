# 08 -- Particle density

## Decision

| Material | Density |
|---|---|
| Steel (balls) | **7850 kg/m^3** |
| Rock (ore) | **2650 kg/m^3**, or the measured ore SG of the plant if available |

Densities are **physical inputs, not calibration variables**.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Cleary & Morrison 2016 | Density of rock 2650, of ball 7850 kg/m^3; rock "at an SG of 2.65", balls "at an SG of 7.85" | Table 2, PDF p7 / j.81; Table 1, PDF p7 / j.81 | Yes |
| Owen & Cleary 2015 | Ore 3000 kg/m^3, steel balls 7850 kg/m^3 | §3 text and Table 4, PDF p3 / j.21 | Yes |
| Govender 2015 | Los Bronces SAG: ore 2850 kg/m^3, balls 7800 kg/m^3 | Table 7, PDF p14 / j.165 | Yes |
| Shigley | Carbon steel unit weight 76.5 kN/m^3 (= 7800 kg/m^3) | Inside-cover table, PDF p3 | Yes |
| Cleary 2001 (2D) | "The ball density itself has almost no effect on the charge behaviour or on the specific power draw." | §11 Conclusion, PDF p34 / j.112 | Yes |
| Kishida 2025 | Single density 2500 kg/m^3 for both sizes (size-only segregation) | Fig. 2(b), PDF p4 | Yes |

## PPT

| Slide | Content |
|---|---|
| 8, 9, 12 | Steel 7850 kg/m^3 [1], rock 2650 kg/m^3 [1] ([1] = Cleary & Morrison 2016, Table 2 -- slide says "Page 81, Table 2", which is correct: PDF p7 = j.81) |
| 30 | "Busqueda manual para Angulos de Friccion y **Densidades** (respecto a Acomodo de Carga)" |

## Current state

`main` `config.py:88,95`: 7850 / 2650 -- matches the decision.

## Analysis

- Ore SG in the literature ranges 2650-3000 kg/m^3 depending on the deposit;
  the plant's own value should be used if known.
- Tuning density to match toe / shoulder (slide 30) is not defensible:
  density is measurable, Cleary 2001 shows ball density barely affects charge
  behaviour, and adjusting it would absorb errors from friction / shape.
- The density ratio steel / rock (~3) matters for **segregation**: unlike
  Kishida's single-density system, here the large particles (balls) are also
  the dense ones, so size and density segregation compete
  (see [13](13_initial_conditions.md)).

## Verdict and how to defend it

"Densities are physical: steel 7850 kg/m^3 and ore 2650 kg/m^3 (Cleary &
Morrison 2016, Table 2); the literature range for SAG ore is 2650-3000 kg/m^3
(Owen & Cleary 2015; Govender et al. 2015). They are not calibrated, since
ball density has almost no effect on charge behaviour (Cleary 2001, §11) and
calibration is carried by friction and rolling resistance."

## Open items

- Obtain the measured ore SG of SAG_B if possible.
