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

| Source | What it says | Where | Verified |
|---|---|---|---|
| Cleary 2001 | "Between 15 and 25 timesteps are required to accurately integrate each collision. This necessitates very small timesteps (typically 10^-4 to 10^-6 s depending on the controlling length and time scales of each problem). If the integration is accurate then the coefficient of restitution ... should be recovered." | §2 "The discrete element method", PDF p5 / j.83 | Yes |
| Boemer & Ponthot 2017 | Time step chosen to limit artificial numerical power to 1 % of total power; "equivalent to choosing 20-70 time steps per collision depending on the coefficient of restitution" | §2.2.3 "Time integration", PDF p5 / j.57 | Yes |
| Boemer & Ponthot 2017 | "The time step was chosen equal to 1e-5, 2.5e-6 and 1e-6 seconds respectively for kn = 1e5, 1e6 and 1e7 N/m" | §3.1 (before 3.1.1), PDF p7 / j.59 | Yes |
| Govender 2015 | Typical DEM limits penetration to d_max ~ 0.05 r (smallest particle); lifter-motion bound dt_max = d_max / (R omega) (Eq. 11); they use d_max = 0.025 r giving dt_max = 1.65e-5 s | §1.5-1.6, PDF p6-7 / j.157-158 | Yes |
| Govender 2015 | dt = 2e-5 s for the slice mill (Table 6) and for the Los Bronces SAG mill (Table 8) | Table 6, PDF p12 / j.163; Table 8, PDF p14 / j.165 | Yes |
| Kishida 2025 | dt = 2.0 us (with E = 1e7 Pa, 0.25-0.5 mm particles) | Fig. 2(b), PDF p4 | Yes (figure read) |

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

### Critical step with the slide-12 moduli

| Estimate | Steel (r = 0.06985) | Rock (r = 0.034925) |
|---|---|---|
| PPT formula r sqrt(rho (1 - nu^2) / E) | 3.25e-5 s | 3.25e-5 s |
| Rayleigh pi r sqrt(rho / G) / (0.1631 nu + 0.8766), G = E / (2 (1 + nu)) | 1.86e-4 s | 1.82e-4 s |

By the PPT's own formula, **dt = 1e-4 s is 3.1x the critical step** of the
material set chosen on slide 12. (Slide 9's 1e-4 target was paired with the
much softer 3.5e9 / 3e8 Pa set, which slide 10 then rejected for overlap.)

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

"The time step was chosen so that every collision is integrated with at least
~20 steps (Cleary 2001, §2: 15-25; Boemer & Ponthot 2017, §2.2.3: 20-70).
With the reduced moduli of slide 12 the Hertz contact time of the fastest
impacts is ~4.5e-4 s, giving dt = 2.5e-5 s. Govender et al.'s lifter-motion
bound (Eq. 11) gives 1.6-3.1e-4 s and is not limiting. The resulting dt is of
the same order as the 2e-5 s used by Govender et al. for a SAG mill."

## Open items / validation

- Measure the impact-velocity distribution in a pilot run (99th percentile of
  normal relative velocity at contact) and recompute the steps-per-collision
  table with it.
- dt-halving test: run 2.5e-5 vs 1.25e-5 s for 2 revolutions; toe, shoulder
  and power must agree within the run-to-run scatter.
- Restitution recovery and energy balance (see [16](16_validation_checks.md)).
