# 04 -- Numerical ("gravity") damping

## Decision

`NewtonIntegrator.damping = 0` in **every run in which the mill rotates**
(calibration runs and SIC / RMIC dataset runs). Non-zero damping (0.2-0.5) is
allowed only while pouring and settling an initial condition; particle
velocities are zeroed before the IC is saved.

The value is **always set explicitly** in the code, never left to YADE's
default: the default differs between YADE versions (0.0 in the 3rd-edition
documentation, 0.2 in the `yadedaily` build installed here).

Energy is dissipated only by the contact law: normal / tangential dashpots set
from restitution ([07](07_restitution.md)), friction ([05](05_friction.md))
and rolling resistance ([06](06_rolling_resistance.md)).

## What YADE's numerical damping does

YADE docs 2021, §2.1 "DEM formulation", "Numerical damping", printed
pp. 70-71 (PDF pp. 77-78), Eq. (2.9): for each particle and each axis
w in {x, y, z}, the force is modified by

(Delta F)_w = -lambda_d sgn(F_w u_dot_w) F_w,

i.e. a force that would **increase** the particle's speed is reduced by the
fraction lambda_d, and a force that would **decrease** it is increased by
lambda_d. With `dampGravity = true` (the default, PDF p277) this applies to
gravity too. Consequences for a particle in free flight with lambda_d = 0.2:

| Phase | Physical acceleration | With damping 0.2 |
|---|---|---|
| Falling (cataracting stream, towards the toe) | g | **0.8 g** |
| Rising (thrown from the shoulder) | g | **1.2 g** |

A particle falling from the shoulder therefore reaches the toe with ~20 %
less kinetic energy than physics dictates, and its trajectory is distorted
-- a direct bias on the toe angle, the impact energies and the mixing that
the datasets are meant to capture.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| YADE docs 2021 | "In simulations of **quasi-static** phenomena, it is desirable to dissipate kinetic energy of particles. Since most constitutive laws ... do not include velocity-based damping ..., it is possible to use artificial numerical damping." | §2.1, "Numerical damping", printed p. 70 (PDF p77) | Yes |
| YADE docs 2021 | "This is done by component, which makes the damping scheme **clearly non-physical**, as it is not invariant with respect to coordinate system rotation" | Same section, printed p. 71 (PDF p78), before Eq. (2.9) | Yes |
| YADE docs 2021 | `NewtonIntegrator.dampGravity(=true)`: "By default, numerical damping applies to ALL forces, even gravity"; `damping(=0.0)`: "damping coefficient for Cundall's non viscous damping" | `yade.wrapper.NewtonIntegrator` entry, printed p. 270 (PDF p277) | Yes |
| YADE (installed `yadedaily` 20260115) | `NewtonIntegrator.damping` docstring: "damping coefficient for Cundall's non viscous damping", default **0.2** | Attribute docstring of the installed class | Yes (run on this machine) |
| YADE (installed build) | `FrictPhys` (Cundall-Strack law) has only `kn`, `ks`, `tangensOfFrictionAngle`: no velocity-based (dashpot) damping, which is the case the YADE docs have in mind | Attribute list of the installed class | Yes |
| Cleary & Morrison 2016 | Power draw = torque x rotation speed; "For long duration mill simulations that have reached steady state operation, the energy dissipated and the energy supplied by the mill should be equal. In practice, balances within a few percent indicate an accurate DEM simulation." -- a non-physical energy sink makes this balance impossible to close | §2, PDF p3 / j.77 | Yes |
| Boemer & Ponthot 2017 | dt chosen "in order to limit the percentage of artificial numerical power with respect to the total power to 1 %" -- non-physical energy is treated as an error to be kept below 1 % | §3.1, PDF p7 / j.59 (criterion in §2.2.3, PDF p5) | Yes |
| Kishida 2025 | Equations of motion m dv/dt = F_cn + F_ct + m g and I dw/dt = M + M_rf: no global damping term; dissipation only through the contact dashpots and rolling friction | Appendix A, Eqs. (A-1)-(A-6), PDF p11-12 | Yes |
| Govender 2015 | Dissipation controlled through restitution: power could be matched "exactly by changing the coefficient of restitution" | §3, PDF p14 / j.165 | Yes |
| All mill papers (Kishida, Cleary & Morrison, Owen & Cleary, Boemer & Ponthot, Cleary 2001, Govender 2015) and Thakur 2016 | None mentions global, local, non-viscous, numerical or artificial damping (full-text search) | -- | Yes (negative result) |

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

- **Purpose of the tool.** YADE's own documentation introduces numerical
  damping for quasi-static simulations with contact laws that lack
  velocity-based damping, and calls the scheme "clearly non-physical". A
  rotating mill is a dynamic, cataracting flow, and the Hertz-Mindlin law
  used here ([01](01_contact_model.md)) has velocity-based damping
  (restitution dashpots). Neither condition for using it holds in the
  rotating runs.
- **Effect on the physics.** With 0.2 the cataracting stream falls at 0.8 g
  and is thrown up at 1.2 g (table above); impacts at the toe lose ~20 % of
  their energy on top of the restitution losses. The charge throws less far,
  the toe moves, and the Cleary & Morrison energy balance (supplied =
  dissipated in contacts) cannot close because part of the energy disappears
  outside the contacts.
- **Effect on calibration.** Any friction / restitution values tuned with
  0.2 compensate for this artefact and are not transferable to undamped
  runs.
- **Where damping is legitimate.** Pouring and settling an IC is a
  quasi-static process -- exactly YADE's intended use -- and its velocities
  are zeroed before the IC is saved, so the damping leaves no trace in the
  dataset runs.
- **Historical reason.** With YADE's Cundall-Strack law (no dashpot), the
  integrator damping is the only way to dissipate normal-impact energy, which
  explains its use in earlier versions of the setup. With Hertz-Mindlin and
  pair-wise `en` it is not needed.

## Verdict and how to defend it

"Artificial (non-viscous) damping is used only to bring the poured charge to
rest when generating initial conditions -- the quasi-static use for which
YADE provides it (YADE documentation, 3rd ed., §2.1 'Numerical damping') --
and particle velocities are reset to zero afterwards. All rotating
simulations use zero artificial damping: YADE's scheme is 'clearly
non-physical' (ibid.) and, applied to gravity, would make particles fall at
0.8 g and rise at 1.2 g for a coefficient of 0.2. Energy is therefore
dissipated exclusively through the contact model (restitution, friction,
rolling resistance), as in all the mill DEM studies consulted, where the
energy dissipated in collisions must balance the energy supplied by the mill
within a few percent (Cleary & Morrison 2016, §2) and artificial numerical
power is kept below 1 % (Boemer & Ponthot 2017, §3.1)."

## Open items / validation

- Energy balance per run (V4): integral of power (torque x omega) vs. the
  sum of contact dissipation (YADE energy tracker `O.trackEnergy = True`); see
  [16](16_validation_checks.md).
- V5: assert `NewtonIntegrator.damping == 0` whenever the mill's angular
  velocity is non-zero.
- Re-generate the datasets: those made with 0.2 do not represent undamped
  mill dynamics.
