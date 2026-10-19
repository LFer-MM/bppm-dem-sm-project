# 04 -- Numerical ("gravity") damping

## Decision

`NewtonIntegrator.damping = 0` in **every run in which the mill rotates**
(calibration runs and SIC / RMIC dataset runs). Non-zero damping (0.2-0.5) is
allowed only while pouring and settling an initial condition; particle
velocities are zeroed before the IC is saved.

Energy is dissipated only by the contact law: normal / tangential dashpots set
from restitution ([07](07_restitution.md)), friction ([05](05_friction.md))
and rolling resistance ([06](06_rolling_resistance.md)).

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Cleary & Morrison 2016 | Power draw = torque x rotation speed; "For long duration mill simulations that have reached steady state operation, the energy dissipated and the energy supplied by the mill should be equal. In practice, balances within a few percent indicate an accurate DEM simulation." | §2, PDF p3 / j.77 | Yes |
| Boemer & Ponthot 2017 | dt chosen "in order to limit the percentage of artificial numerical power with respect to the total power to 1 %" -- any non-physical energy sink is treated as an error to be kept below 1 % | §3.1, PDF p7 / j.59 (criterion explained in §2.2.3, PDF p5) | Yes |
| Kishida 2025 | Equations of motion m dv/dt = F_cn + F_ct + m g and I dw/dt = M + M_rf: no global damping term; dissipation only through the dashpots eta_n, eta_t (from e) and rolling friction | Appendix A, Eqs. (A-1)-(A-6), PDF p11-12 | Yes |
| Govender 2015 | Power can be matched "exactly by changing the coefficient of restitution" -- dissipation is controlled through restitution | §3, PDF p14 / j.165 | Yes |
| YADE (installed build) | `NewtonIntegrator.damping`: "damping coefficient for Cundall's non viscous damping", **default 0.2**; it reduces every particle's acceleration each step, including in free flight | Attribute docstring of the installed class | Yes (run on this machine) |
| YADE (installed build) | `FrictPhys` (Cundall-Strack law) has only `kn`, `ks`, `tangensOfFrictionAngle`: no collisional dashpot | Attribute list of the installed class | Yes |

## PPT

| Slide | Content |
|---|---|
| 10, 13 | "Gravity Damping Ingreso 0.2 -> Asentado 0.0" (overlap and packing tests) |
| 17, 18 | SIC / RMIC generation: `gravity_damping = 0.5`, `unbalanced_forces < 0.001`, dt = 1e-4 |
| 19 | Dataset runs: **`gravity_damping = 0.2`**, 20 s (SIC) / 10 s (RMIC) |

## Current state

| Where | What |
|---|---|
| `main` `engines.py:69,84` | Engines created with `damping=0` |
| `main` `run_simulation.py:38` | Immediately set to 0.2 (`set_gravity_damping(0.2)`) |
| `main` `run_simulation.py:63` | The reset to 0.0 is commented out (manual step) |
| Existing `sic_dataset_20s_dt0p0001` | Generated with 0.2 according to slide 19 |

## Analysis

- 0.2 is YADE's default, designed for quasi-static problems. It is not a
  physical property of rock or steel.
- In a rotating mill it removes energy from the cataracting stream and from
  every collision on top of the restitution dashpot. The charge throws less
  far and the toe moves up; the power-vs-dissipation balance of Cleary &
  Morrison cannot close. Any calibration of friction or restitution made with
  0.2 compensates for this artefact and is not transferable.
- With Cundall-Strack in YADE (no dashpot), damping is the only way to
  dissipate normal-impact energy, which explains its historical use. With
  Hertz-Mindlin and pair-wise `en` it is not needed.

## Verdict and how to defend it

"Artificial (non-viscous) damping is used only to bring the poured charge to
rest when generating initial conditions. All rotating simulations use zero
artificial damping; energy is dissipated exclusively through the contact
model (restitution, friction, rolling resistance), as in the mill DEM
literature, where the energy dissipated in collisions must balance the energy
supplied by the mill within a few percent (Cleary & Morrison 2016, §2) and
artificial numerical power is kept below 1 % (Boemer & Ponthot 2017)."

## Open items / validation

- Energy balance per run: integral of power (torque x omega) vs. the sum of
  contact dissipation (YADE energy tracker `O.trackEnergy = True`); see
  [16](16_validation_checks.md).
- Re-generate the datasets: those made with 0.2 do not represent undamped
  mill dynamics.
