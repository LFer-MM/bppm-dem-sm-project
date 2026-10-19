# 14 -- Dataset runs, durations and recording

## Decision

| Item | Value |
|---|---|
| Start | Load a saved IC; damping 0; mill starts from rest at t = 0 and turns at 9 rpm |
| Recording | From t = 0, one frame every **0.05 s** (columns `id,x,y,z,r,m,vx,vy,vz`) plus an exact frame-time index and a mill log (charge angle, power, kinetic energy, overlaps) |
| RMIC duration | **>= 2.5 revolutions** (16.7 s at 9 rpm); proposal: 20 s |
| SIC duration | **>= 5 revolutions** (33.3 s at 9 rpm); proposal: 35 s |
| Training window | 20 frames (1 s) starting **after the measured quasi-steady state** of kinetic energy / power -- not a fixed 3-4 s |
| Replicates | 30 per IC type, different seeds |

No spin-up stage before recording: spinning up first would destroy the IC.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Kishida 2025 | "The DEM simulations ... were performed for 10 s starting from (a) the RM-IC and for 20 s starting from (b) the S-IC" | §3, PDF p6 | Yes |
| Kishida 2025 | "time step used in RNN (Delta t_RNN) was set to 0.05 s ... The raw DEM simulation data were extracted every 0.05 s between 3.0 and 4.0 s (20 frames), in which the quasi-steady state of particle kinetic energy was ensured. Subsequently, the time-series data for 15 frames were input into the RNN." | §3, PDF p6 | Yes |
| Kishida 2025 SM | "the particle kinetic energy reached quasi-steady state after 2.0 second" (Fig. S1, RM-IC) | Supplementary, PDF p1 | Yes |
| Kishida 2025 | Drum speed 15 rpm | Fig. 2(a), PDF p4 | Yes |
| Boemer & Ponthot 2017 | "the system reaches the quasi-steady state after 2.5 s according to the position of the global center of gravity; 2.5 additional seconds are necessary to obtain sufficiently representative averages"; recording period 0.01 s | §3.1, PDF p8 / j.60 | Yes |
| Govender 2015 | Los Bronces SAG: "The computed power seems to stabilizes after six revolutions" | §3, PDF p14 / j.165 | Yes |
| Owen & Cleary 2015 | Charge features measured on the **steady** charge distribution | §4.1, PDF p4 / j.22 | Yes |

## PPT

| Slide | Content |
|---|---|
| 19 | "Simulaciones para Generacion de Datasets": dt = 1e-4, gravity_damping = 0.2, duracion_simulacion_sic = 20 s, duracion_simulacion_rmic = 10 s, save_particle_frames_dt = 0.05 s; F2_SIC_0..F2_SIC_400, F2_RMIC_0..F2_RMIC_200 |
| 21 | Lacey index per frame, cell 0.4732 m, min 15 particles per cell |
| 22 | RNN input (N, 15, [x, y, z, d]) |
| 30 | SIC 20 s (400 frames x 30 runs), RMIC 10 s (200 frames x 30 runs) |

## Current state

| Where | What |
|---|---|
| `main` `config.py:162,167,168` | `start_frame = 66`, `dt0 = 4.05`, `dt_step = 0.05` (prediction seeded at ~3.3-4.05 s) |
| `main` `capture.py:55,71` | PyRunner every 50 iterations checks the time; prints "Checking at time" on every call |
| Branch `worktree-yade-sim-structure` | Spin-up to steady state **before** recording -- correct for calibration runs, wrong for SIC / RMIC datasets; to be split into run types |
| Existing dataset | Charge centre-of-mass angle: 0 deg (t = 0), 22 deg (2 s), 38 deg (4 s), 54 deg (10 s), 60 deg (20 s) -- still rising at 3-4 s |

## Analysis

Compare in revolutions, not seconds:

| | Kishida (15 rpm) | SAG (9 rpm) with the PPT durations | SAG with matched revolutions |
|---|---|---|---|
| RM-IC run | 10 s = 2.5 rev | 10 s = 1.5 rev | 16.7 s |
| S-IC run | 20 s = 5 rev | 20 s = 3 rev | 33.3 s |
| Training window | 3-4 s = 0.75-1.0 rev | 3-4 s = 0.45-0.60 rev | 5-6.7 s (if quasi-steady) |
| Quasi-steady KE | 2.0 s = 0.5 rev | ? (measure) | -- |

- Copying Kishida's seconds gives the SAG run only 60 % of the revolutions.
- Kishida chose 3-4 s *because* kinetic energy was quasi-steady there. The
  criterion transfers, the numbers do not: the old SAG dataset's charge angle
  was still rising at 3-4 s. The training window must be placed after the
  measured quasi-steady time of the new runs (kinetic energy and power from
  the mill log).
- 0.05 s frames at 9 rpm are 0.0075 rev per frame (Kishida: 0.0125 rev), i.e.
  finer sampling per revolution; keeping 0.05 s is conservative and keeps the
  RNN Delta t identical.
- Govender's ~6 revolutions for power concerns long-term operation; mixing
  datasets do not need a stationary power, but the training window does need
  quasi-steady flow.

## Verdict and how to defend it

"Dataset runs start from the static IC and are recorded from t = 0 every
0.05 s, as in Kishida et al. (2025, §3). Durations are scaled by revolutions
(2.5 and 5 revolutions for RM-IC and S-IC, as in the reference at 15 rpm),
and the 20-frame training window is placed after the measured quasi-steady
state of kinetic energy, the criterion used by Kishida et al. (§3, Fig. S1)."

## Open items / validation

- Pilot RMIC run: measure the time to quasi-steady kinetic energy / power /
  charge angle; set `start_frame` / `dt0` from it.
- Check the Lacey index curves reach their plateau within the run length
  (SIC 5 rev); extend if not.
- Separate run types in the code: `calibrate` (spin-up, steady state),
  `make_ic`, `dataset` (record from rest).
