# 02 -- Time step (dt)

## Decision

**dt = 2.5e-5 s** with the slide-12 moduli (E_steel = 33.16 GPa,
E_rock = 2.868 GPa) -- **option A, decided 2026-10-18**. Acceptance rule:
>= 15-25 integration steps per collision up to the worst-case impact speed
sqrt(2 g D) = 15.2 m/s (17-20 steps with this dt), and an energy balance
within a few percent (see [16](16_validation_checks.md)).

Options considered (contact time and peak overlap both scale as E^-0.4):

| Option | dt | E steel / rock | Peak overlap at 15.2 m/s | Cost vs 1e-4 | Status |
|---|---|---|---|---|---|
| **A** | 2.5e-5 s | 33.16 / 2.868 GPa (slide 12) | 1.9-3.3 % | 4x | **chosen** |
| C | 5e-5 s | 5.86 / 0.507 GPa (slide 12 / 5.66) | 3.8-6.6 % | 2x | fallback if compute is short |
| B | 1e-4 s | 1.04 / 0.090 GPa (slide 12 / 32) | 7.6-13 % | 1x | rejected: exceeds Boemer's ~10 % limit |

## Evidence

The references are grouped by the argument they support. Every quote was
checked in the PDF.

### E1. Stability is necessary but not sufficient; accuracy sets dt

| Source | What it says | Where | Verified |
|---|---|---|---|
| Boemer & Ponthot 2017 | "To ensure the stability of the algorithm, it is necessary that the time step is smaller than the critical time step tc, e.g. tc = 2/omega_max for an undamped system ... Furthermore, this time step can also be determined in order to limit the creation of numerical energy, i.e. to recover the coefficient of restitution ... By limiting the creation of artificial energy in normal collisions to 1 % with respect to the total energy in the system, **this criterion is more restrictive than the stability requirement**." | §2.2.3 "Time integration", PDF p5 / j.57 | Yes |
| Cleary 2001 | "If the integration is accurate then the coefficient of restitution from which the damping coefficient was chosen should be recovered." | §2, PDF p5 / j.83 | Yes |
| Govender 2015 | Kn (and with it dt) "is chosen such that physical quantities of interest (such as energy) are conserved during integration for the typical range of velocities observed in tumbling mill simulations" | §1.5, PDF p6 / j.157 | Yes |

This is why the critical-step formula of PPT slide 9 (a stability bound)
cannot by itself justify dt: the papers size dt for accuracy, which is
stricter.

### E2. The accuracy criterion: steps per collision

| Source | What it says | Where | Verified |
|---|---|---|---|
| Cleary 2001 | "Between 15 and 25 timesteps are required to accurately integrate each collision." | §2, PDF p5 / j.83 | Yes |
| Boemer & Ponthot 2017 | The 1 % artificial-energy criterion "is equivalent to choosing 20-70 time steps per collision depending on the coefficient of restitution; more time steps per collision are usually required when the coefficient of restitution is important" | §2.2.3, PDF p5 / j.57 | Yes |

### E3. Typical magnitude of dt in mill DEM

| Source | What it says | Where | Verified |
|---|---|---|---|
| Cleary 2001 | The 15-25 steps "necessitates very small timesteps (typically 10^-4 to 10^-6 s depending on the controlling length and time scales of each problem)" -- the range is a consequence of the steps criterion, not a free choice | §2, PDF p5 / j.83 | Yes |
| Govender 2015 | dt = 2e-5 s for the slice mill, GPU and CPU codes | Table 6, PDF p12 / j.163 | Yes |
| Govender 2015 | dt = 2e-5 s for the Los Bronces SAG mill (10.12 m, 10 rpm) -- the closest industrial case to this project | Table 8, PDF p14 / j.165 | Yes |
| Boemer & Ponthot 2017 | dt = 1e-5, 2.5e-6, 1e-6 s for kn = 1e5, 1e6, 1e7 N/m (lab mill, 15 mm balls, run in YADE) | §3.1, PDF p7 / j.59 | Yes |
| Kishida 2025 | dt = 2.0 us (E = 1e7 Pa, 0.25-0.5 mm particles) | Fig. 2(b), PDF p4 | Yes (figure read) |
| Thakur 2016 | dt = 1e-5 s (uniaxial compression of 2-3.75 mm particles; not a mill) | Parameter table, PDF p5 / j.134 | Yes |

### E4. Worst-case impact speed

| Source | What it says | Where | Verified |
|---|---|---|---|
| Boemer & Ponthot 2017 | Maximum relative impact velocity "can be assumed to be equal to sqrt(2 x 9.81 x 0.8) ~ 4 m/s, which corresponds to the terminal velocity when a ball falls from the top of the mill (diameter of 0.8 m) to its lowest position starting from rest" | §3.1.2, PDF p8 / j.60 | Yes |
| Govender 2015 | Kn / dt chosen "for the typical range of velocities observed in tumbling mill simulations" | §1.5, PDF p6 / j.157 | Yes |

Applied here: sqrt(2 x 9.81 x 11.8375) = 15.2 m/s.

### E5. Stiffness and dt are chosen together

| Source | What it says | Where | Verified |
|---|---|---|---|
| Cleary & Morrison 2016 | Stiffness "is used as a numerical rather than a physical parameter and is chosen ... so as to maximise the timestep and therefore minimise the simulation time ... as long as the numerical contact deformations remain small" | §2, PDF p3 / j.77 | Yes |
| Govender 2015 | "Typical DEM simulations use a spring stiffness and time-step that limits the maximum penetration depth to d_max ~ 0.05 r where r is the radius of the smallest particle (Cleary, 2001; ...)" | §1.5, PDF p6 / j.157 | Yes |

The overlap side of this trade-off is documented in
[03](03_stiffness_young_modulus.md).

### E6. Mill-specific bound: lifter motion per step

| Source | What it says | Where | Verified |
|---|---|---|---|
| Govender 2015 | Distance covered by a lifter in one step is R omega dt, so "the maximum time-step for a mill rotating at omega rpm having a maximum penetration distance of d_max is given by dt = d_max / (R omega)" (Eq. 11); with d_max = 0.025 r, dt_max = 1.65e-5 s for their mill | §1.6, Eq. (11), PDF p7 / j.158 | Yes |

### E7. The DEM dt is independent of the dataset frame interval

| Source | What it says | Where | Verified |
|---|---|---|---|
| Kishida 2025 | "The Delta t_RNN was significantly larger than the time step used in the DEM"; Delta t_RNN = 0.05 s | §2.1, PDF p3; §3, PDF p6 | Yes |

So reducing the DEM dt to 2.5e-5 s does not change the 0.05 s frame
interval of the datasets ([14](14_dataset_runs_and_recording.md)); it only
changes run time.

## PPT

| Slide | Content |
|---|---|
| 8 | "Se busca mantener en la simulacion DEM un dt = 0.0001 = 1e-4 [5]" -- [5] = Boemer & Ponthot. **Not supported by [5]**: Boemer uses 1e-5 to 1e-6 s. The closest support is Cleary 2001 (range 1e-4 to 1e-6 s *conditional on* 15-25 steps per collision). |
| 9 | dt_cr = R_min sqrt(rho / E_eff), E_eff = E / (1 - nu^2); with real E_rock = 55 GPa: dt_cr = 7.42e-6 s; E_reduced for dt_target = 1e-4: rock 3.0e8 Pa, steel 3.5e9 Pa |
| 10 | YADE `PWaveTimeStep()` = 1.36e-5 s with original moduli and 1.05e-4 s with 3.5e9 / 3e8 Pa; run used dt = 0.2 dt_crit |
| 11 | Table of E_reduced for dt_crit = 1.5e-5 ... 5e-5 s; aim "dt_crit entre 1.36e-5 y 1e-4" |
| 12 | Chosen moduli 33.16 GPa / 2.868 GPa, i.e. the dt_crit = 3.25e-5 s row of slide 11 |
| 17, 18, 19 | IC generation and dataset runs at **dt = 1e-4** |

## Current state

| Where | What |
|---|---|
| `main` `yade_dem/run_simulation.py:36` | `set_dt(new_dt=0.000015 * 0.2)` = 3e-6 s |
| `main` `config.py:89,96` | Moduli of the dt_crit = 1.5e-5 row (155.7 GPa / 13.47 GPa), not slide 12 |
| `data/raw/sic_dataset_20s_dt0p0001_csv.zip` | Generated at dt = 1e-4 s (folder name `sic_dataset_20s0.0001_`) |

## Analysis

### Formulas used and the status of their sources

The critical-step formulas are **not** the basis of the decision: they bound
*stability*, while the papers size dt by *accuracy*, which is stricter
(E1). They are reported only to show the stability bound is respected.

| Formula | Role here | Source | In Zotero? |
|---|---|---|---|
| t_c = 2 / omega_max (generic stability limit, undamped) | Stability bound | Boemer & Ponthot 2017 §2.2.3, PDF p5 (citing their ref. [30]) | **Yes** |
| P-wave step dt = r sqrt(rho / E_eff), E_eff = E / (1 - nu^2) (YADE `PWaveTimeStep`; PPT slides 9-11) | Stability bound (PPT's own) | YADE documentation, Smilauer et al. (PPT ref. [8]) | **No -- add the YADE documentation** |
| Rayleigh step dt_R = pi r sqrt(rho / G) / (0.1631 nu + 0.8766) | Stability bound commonly used for Hertz-Mindlin | Standard in the DEM literature; no paper in the library states it | **No -- find and add a source** |
| Hertz impact duration t_c = 2.87 (m*^2 / (R* E*^2 v))^(1/5) | Steps per collision (the governing criterion) | Hertz impact theory (e.g. K.L. Johnson, *Contact Mechanics*) | **No -- add a contact-mechanics source** |
| Hertz maximum overlap delta_max = (15 m* v^2 / (16 E* R*^0.5))^(2/5) | Peak overlap ([03](03_stiffness_young_modulus.md)) | Same as above | **No** |
| Linear-spring contact time / maximum overlap | Used by the mill papers (linear models) | Govender 2015 §1.5 Eq. (7), PDF p6; Boemer & Ponthot 2017 Eqs. (8)-(9), PDF p8 | Yes (but for the linear, not the Hertz, model) |

Until the missing sources are in Zotero, the Hertz numbers in this file and in
[03](03_stiffness_young_modulus.md) rest on textbook formulas without a
citable reference in the library. The candidate references named above must
be located and checked before they are cited.

### Critical step with the slide-12 moduli

| Estimate | Steel (r = 0.06985) | Rock (r = 0.034925) |
|---|---|---|
| PPT formula r sqrt(rho (1 - nu^2) / E) | 3.25e-5 s | 3.25e-5 s |
| Rayleigh pi r sqrt(rho / G) / (0.1631 nu + 0.8766), G = E / (2 (1 + nu)) | 1.86e-4 s | 1.82e-4 s |

By the PPT's own formula, **dt = 1e-4 s is 3.1x the critical step** of the
material set chosen on slide 12. (Slide 9's 1e-4 target was paired with the
much softer 3.5e9 / 3e8 Pa set, which slide 10 then rejected for overlap.)

The chosen dt = 2.5e-5 s respects both stability bounds: it is 0.77x the PPT's
P-wave step and 0.14x the Rayleigh step. The binding constraint is the
accuracy criterion below, not stability.

### Steps per collision (the criterion the papers actually use)

Hertz elastic impact duration t_c = 2.87 (m*^2 / (R* E*^2 v))^(1/5):

| Pair | v (m/s) | t_c (s) | steps @ 1e-4 | steps @ 4e-5 | steps @ 2.5e-5 |
|---|---|---|---|---|---|
| steel-steel | 1 | 8.8e-4 | 8.8 | 22.0 | 35.3 |
| steel-steel | 8 | 5.8e-4 | 5.8 | 14.5 | 23.3 |
| steel-rock | 5 | 5.3e-4 | 5.3 | 13.3 | 21.3 |
| steel-rock | 8 | 4.9e-4 | 4.9 | 12.1 | 19.4 |
| steel-rock | 12 | 4.5e-4 | 4.5 | 11.2 | 17.9 |
| rock-rock | 8 | 5.1e-4 | 5.1 | 12.7 | 20.3 |
| steel-steel | **15.2** (worst case) | 5.1e-4 | 5.1 | 12.8 | **20.5** |
| steel-rock | **15.2** | 4.3e-4 | 4.3 | 10.7 | **17.1** |
| rock-rock | **15.2** | 4.5e-4 | 4.5 | 11.1 | **17.8** |

The worst case uses Boemer & Ponthot's choice of impact speed (§3.1.2,
PDF p8): free fall across the mill, sqrt(2 g D) = 15.2 m/s for D = 11.84 m.
Even there dt = 2.5e-5 s gives 17-20.5 steps, inside Cleary's 15-25. The
contacts below 20 steps are the rock ones, whose low restitution (0.3-0.5)
needs the fewest steps: Boemer notes "more time steps per collision are
usually required when the coefficient of restitution is important" (§2.2.3,
PDF p5).

Impact speeds of 8-12 m/s occur: the shell moves at 5.58 m/s at 9 rpm and the
old dataset shows particle speeds up to 12.6 m/s (frame 399). At 1e-4 s a
collision is resolved in ~5 steps -- far below Cleary's 15-25 and Boemer's
20-70. At **2.5e-5 s** the fast collisions get ~18-23 steps and slow ones
~30-35, inside both criteria.

### Govender's lifter-motion bound

dt_max = d_max / (R omega) with R = 5.92 m, omega = 0.942 rad/s:
3.1e-4 s (d_max = 0.05 r_rock) or 1.6e-4 s (0.025 r_rock). Not binding.

### Option B: keep dt = 1e-4 s

t_c and peak overlap both scale as E^(-2/5). Making 1e-4 s give the same
~20 steps needs t_c x4, i.e. E / 32 (E_steel ~ 1.0 GPa, E_rock ~ 0.09 GPa).
Peak overlaps then grow x4: ~4.5 % (steel-steel, 8 m/s) to ~11 % (rock pairs,
12 m/s), and 7.6-13 % at the 15.2 m/s worst case, of the smaller diameter.
Boemer (§4, PDF p13) finds results insensitive "provided that the maximum
overlap percentage ... is smaller than about 10 %", so option B exceeds the
only measured sensitivity limit and is rejected. All overlap criteria in the
literature are compared in [03](03_stiffness_young_modulus.md).

### Cost

Throughput measured on this machine (24 cores, 16 threads) during the fill
of the full-scale lifter benchmark, with part of the charge loaded: ~400
steps/s (expect somewhat less with the full ~14k particles). A 33 s run at 2.5e-5 s is 1.33 M steps (~55 min); at 1e-4 s it
would be ~14 min. The 4x cost buys a collision resolution that the cited
literature requires.

## Verdict and how to defend it

"The time step was set by integration accuracy rather than stability alone,
since recovering the coefficient of restitution is more restrictive than the
stability limit (Boemer & Ponthot 2017, §2.2.3; Cleary 2001, §2). Every
collision is integrated with 15-25 steps or more (Cleary 2001, §2; 20-70 in
Boemer & Ponthot 2017, §2.2.3, more steps being needed at high restitution).
With the reduced moduli -- stiffness being a numerical parameter chosen
jointly with dt (Cleary & Morrison 2016, §2; Govender et al. 2015, §1.5) --
the Hertz contact time at the worst-case impact speed sqrt(2 g D) = 15.2 m/s
(the free-fall estimate of Boemer & Ponthot 2017, §3.1.2) is 4.3-5.1e-4 s,
so dt = 2.5e-5 s gives 17-20.5 steps per collision. The lifter-motion bound
of Govender et al. (2015, Eq. 11) gives 1.6-3.1e-4 s and is not limiting.
The resulting dt is consistent with the 1e-4 to 1e-6 s range of Cleary (2001)
and close to the 2e-5 s used by Govender et al. (2015, Table 8) for the
Los Bronces SAG mill. The DEM time step is independent of the 0.05 s
interval at which frames are stored for the surrogate model (Kishida et al.
2025, §2.1)."

## Open items / validation

- Measure the impact-velocity distribution in a pilot run (99th percentile of
  normal relative velocity at contact) and recompute the steps-per-collision
  table with it.
- dt-halving test: run 2.5e-5 vs 1.25e-5 s for 2 revolutions; toe, shoulder
  and power must agree within the run-to-run scatter.
- Restitution recovery and energy balance (see [16](16_validation_checks.md)).
- **Add missing formula sources to Zotero** (see "Formulas used and the
  status of their sources"): the YADE documentation (P-wave step), a source
  for the Rayleigh time step, and a contact-mechanics reference for the Hertz
  impact duration and maximum overlap. Verify each before citing.
