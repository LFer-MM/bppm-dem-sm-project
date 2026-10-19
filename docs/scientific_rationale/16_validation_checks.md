# 16 -- Validation checks (acceptance criteria per run)

Every calibration and dataset run must pass these checks; the results are
written to the run manifest so each dataset can be defended individually.

| # | Check | Criterion | Basis |
|---|---|---|---|
| V1 | Restitution recovery | Binary collision test per pair at the run's dt: measured e within ~2 % of input | Cleary 2001 §2, PDF p5 / j.83 ("If the integration is accurate then the coefficient of restitution ... should be recovered") |
| V2 | Steps per collision | >= ~20 for the 99th-percentile impact velocity of the run | Cleary 2001 §2, PDF p5 (15-25); Boemer & Ponthot §2.2.3, PDF p5 / j.57 (20-70); see [02](02_time_step.md) |
| V3 | Overlap | Mean <= ~0.5 %, P99 <= ~2 %, max < 10 % of the smaller **diameter** | Boemer §3.1.2, PDF p8 / j.60 (0.1-1 %); §4, PDF p13 (max ~10 %); Owen & Cleary §3, PDF p3 (~0.8 %) |
| V4 | Energy balance | Energy supplied (integral of torque x omega) vs. energy dissipated in contacts: within a few % over the steady part | Cleary & Morrison §2, PDF p3 / j.77 |
| V5 | No artificial damping | `NewtonIntegrator.damping == 0` during rotation | [04](04_numerical_damping.md) |
| V6 | Inventory | Same particle counts per species in every frame; no particle outside the shell | Integrity check of `data_processing` |
| V7 | Quasi-steady time | Kinetic energy / power / charge angle quasi-steady before the training window | Kishida 2025 §3, PDF p6; SM Fig. S1 |
| V8 | Charge shape (calibration runs) | Toe and shoulder within the SAG_B interquartile range | [15](15_calibration_targets.md) |
| V9 | dt sensitivity (once) | dt vs dt/2: toe, shoulder, power within run-to-run scatter | [02](02_time_step.md) |
| V10 | Stiffness sensitivity (once) | E x 0.5 and E x 2: toe, shoulder, power within scatter | Boemer abstract and §3.1.2; [03](03_stiffness_young_modulus.md) |
| V11 | End-wall sensitivity (once) | Liner-friction vs frictionless end walls | [10](10_mill_geometry.md) |
| V11b | Ore-density sensitivity (once) | 2650 vs 2850 kg/m^3: toe, shoulder, power within scatter | [08](08_density.md) |
| V11c | Independent validation (once) | Calibrated parameters frozen; SAG_A and SAG_C toe / shoulder at their own Jb / Jc / speed | Boemer & Ponthot Table 1, PDF p3 (calibrate on case 1, validate on 2-4); [15](15_calibration_targets.md) |
| V12 | Replicate scatter | Spread of toe / shoulder / Lacey curves over seeds reported | Owen & Cleary Table 5 / §4.1 (4 centre-point replicates, PDF p4) |

## Notes

- V4 uses YADE's energy tracker (`O.trackEnergy = True`) for contact
  dissipation and the mill torque logged by `monitor.py` for the input.
- V1 and V2 are cheap and should run automatically before any long run with a
  new material set or dt.
- V9-V11 are one-off studies; their results go in the thesis as evidence that
  the numerical choices do not drive the conclusions.
