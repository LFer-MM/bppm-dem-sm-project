# Scientific rationale for the DEM simulation parameters

This directory justifies every parameter of the YADE SAG-mill simulations used
to generate the SIC / RMIC datasets. Each topic file has the same structure:

1. **Decision** -- the value or rule we use.
2. **Evidence** -- one table row per source: what it says, the exact location
   (PDF page, journal page, section, table / figure, or PPT slide), and whether
   the quote was verified against the PDF.
3. **Current state** -- what the code (`main`) and the existing dataset do.
4. **Analysis** -- how the evidence and the numbers lead to the decision.
5. **Verdict and how to defend it** -- the argument to use in the thesis.
6. **Open items / validation** -- what still has to be measured.

All page locations below were checked by text search in the PDFs stored in
Zotero (`/home/pher/Zotero/storage/<key>/`). "PDF p" is the page index of the
file; "j." is the printed journal page. Slide numbers refer to
`avances_tt.pptx` (Zotero `J8ID6KEP`) in presentation order (slide *N* is the
*N*-th slide; verified against `ppt/presentation.xml`).

## Topics

| # | File | Decision in one line |
|---|------|----------------------|
| 01 | [01_contact_model.md](01_contact_model.md) | Hertz-Mindlin with pair-wise restitution, pair-wise friction and rolling resistance |
| 02 | [02_time_step.md](02_time_step.md) | dt = 2.5e-5 s with the slide-12 moduli (not 1e-4 s) |
| 03 | [03_stiffness_young_modulus.md](03_stiffness_young_modulus.md) | E_steel = 33.16 GPa, E_rock = 2.868 GPa (reduced; overlap-controlled) |
| 04 | [04_numerical_damping.md](04_numerical_damping.md) | NewtonIntegrator damping = 0 whenever the mill rotates |
| 05 | [05_friction.md](05_friction.md) | Calibrate; baseline mu = 0.5, pair-wise and liner friction as calibration variables |
| 06 | [06_rolling_resistance.md](06_rolling_resistance.md) | Add rolling resistance for rock (spheres stand in for angular ore); calibrate |
| 07 | [07_restitution.md](07_restitution.md) | e = 0.3 / 0.5 / 0.8 (rock-rock / rock-steel / steel-steel) |
| 08 | [08_density.md](08_density.md) | 7850 / 2650 kg/m^3 (literature; no plant measurement); not calibrated; sensitivity 2650 vs 2850 |
| 09 | [09_poisson_ratio.md](09_poisson_ratio.md) | 0.292 steel, 0.25 rock |
| 10 | [10_mill_geometry.md](10_mill_geometry.md) | STL slice, 30 lifters, D = 11.8375 m, 0.375 m depth; test end-wall friction |
| 11 | [11_mill_speed.md](11_mill_speed.md) | 9 rpm = 72.8 % of critical |
| 12 | [12_charge_fill_and_particles.md](12_charge_fill_and_particles.md) | Jb = 17 %, Jc = 26 %, 2:1 sizes, counts from measured in-slice packing |
| 13 | [13_initial_conditions.md](13_initial_conditions.md) | SIC / RMIC at rest, damped settle, velocities zeroed; SIC = rock bottom, balls top |
| 14 | [14_dataset_runs_and_recording.md](14_dataset_runs_and_recording.md) | Record from rest; durations in revolutions; training window after measured quasi-steady state |
| 15 | [15_calibration_targets.md](15_calibration_targets.md) | Match SAG_B bulk toe 215 / shoulder 24.6 deg (0 deg at 3 o'clock, CCW); three mills show it is typical; power only for energy balance / sanity check |
| 16 | [16_validation_checks.md](16_validation_checks.md) | Acceptance tests every run must pass |

## Source registry

| Key used in docs | Reference | Zotero folder | Page mapping |
|---|---|---|---|
| **Kishida 2025** | N. Kishida, H. Nakamura, S. Ohsaki, S. Watano, *Surrogate model of DEM simulation for binary-sized particle mixing and segregation*, Powder Technol. 455 (2025) 120811 | `U6NKB3KZ` | PDF p = article p (1-13) |
| **Kishida 2025 SM** | Supplementary material of the above (Figs. S1-S2) | `LZXF23SG` | 3 pages |
| **Cleary & Morrison 2016** | P.W. Cleary, R.D. Morrison, *Comminution mechanisms, particle shape evolution and collision energy partitioning in tumbling mills*, Miner. Eng. 86 (2016) 75-95 | `9S5TJQ2P` | j. = PDF p + 74 |
| **Owen & Cleary 2015** | P. Owen, P.W. Cleary, *The relationship between charge shape characteristics and fill level and lifter height for a SAG mill*, Miner. Eng. 83 (2015) 19-32 | `AYIPPK53` | j. = PDF p + 18 |
| **Boemer & Ponthot 2017** | D. Boemer, J.-P. Ponthot, *DEM modeling of ball mills with experimental validation: influence of contact parameters on charge motion and power draw*, Comp. Part. Mech. 4 (2017) 53-67 | `4LNBNEIZ` | j. = PDF p + 52 |
| **Cleary 2001** | P.W. Cleary, *Charge behaviour and power consumption in ball mills: sensitivity to mill operating conditions, liner geometry and charge composition*, Int. J. Miner. Process. 63 (2001) 79-114 (**2D** DEM) | `VRMUBFRG` | j. = PDF p + 78 |
| **Govender 2015** | N. Govender et al., *Discrete element simulation of mill charge in 3D using the BLAZE-DEM GPU framework*, Miner. Eng. 79 (2015) 152-168 | `W9YT6FNT` | j. = PDF p + 151 |
| **Thakur 2016** | S.C. Thakur, J.Y. Ooi, H. Ahmadian, *Scaling of discrete element model parameters for cohesionless and cohesive solid*, Powder Technol. 293 (2016) 130-137 | `AJF55YJ2` | j. = PDF p + 129 |
| **Gercek 2007** | H. Gercek, *Poisson's ratio values for rocks*, Int. J. Rock Mech. Min. Sci. 44 (2007) 1-13 | `JPTAYGXS` | PDF p = j. |
| **Vergara et al.** | M.R. Vergara, A. Arismendy, A. Libreros, A. Brzovic, *Numerical investigation into strength and deformability of veined rock mass* (manuscript, El Teniente andesite) | `QR9D245M` | manuscript pages |
| **Shigley** | R.G. Budynas, J.K. Nisbett, *Diseno en ingenieria mecanica de Shigley* | `4RP3VQXB` | inside-cover table = PDF p3 |
| **Shi & Zhang 2008** | Y. Shi, Y. Zhang, *Simulation of random packing of spherical particles with different size distributions*, Appl. Phys. A 92 (2008) 621-626 | `ZNTAYS7X` | j. = PDF p + 620 |
| **Brouwers 2024** | H.J.H. Brouwers, *Random packing fraction of binary similar particles: Onsager's excluded volume model revisited* (arXiv:2209.09873v5) | `TS9GXXKP` | arXiv pages |
| **PPT** | `avances_tt.pptx` (project progress deck) | `J8ID6KEP` | slide numbers |

Govender et al. 2016 (Blaze-DEMGPU framework, `FQ4KKWQN`) and Chou et al. 2017
(mixing index, `475694QA`) were searched but give no DEM parameter used here.

## Citation problems found in the PPT

These do not change the values, but the references must be corrected before
they go into the thesis:

| Slide | As written | Problem | Correct support |
|---|---|---|---|
| 8 | "Se busca mantener ... dt = 1e-4 [5]" (Boemer & Ponthot) | Boemer uses 1e-5, 2.5e-6, 1e-6 s (§3.1, PDF p7 / j.59); 1e-4 does not appear in the paper | Cleary 2001 §2, PDF p5 / j.83 gives "typically 1e-4 to 1e-6 s" **with** 15-25 steps per collision -- see [02](02_time_step.md) |
| 8, 9, 11, 12 | "[3] Thakur et al. (2014) ... Powder Technology, 293" for reducing E | Year is 2016; the paper is about **coarse-graining** (stiffness scales linearly with particle size, abstract PDF p1); it does not discuss lowering E to enlarge dt | Cleary & Morrison 2016 §2 PDF p3 / j.77; Boemer §3.1.2 PDF p8 / j.60 and §4 PDF p13; Owen & Cleary §3 PDF p3 / j.21 -- see [03](03_stiffness_young_modulus.md) |
| 8 | "[7] Vergara & Mork (2017) ... J. Rock Mech. Geotech. Eng., 9(2)" | The Zotero file is Vergara, Arismendy, Libreros & Brzovic, *Numerical investigation into strength and deformability of veined rock mass* | Cite that paper, Table 1 (PDF p3): E_i = 55 GPa, nu = 0.25 |
| 8 | "Segun Cleary (2015), Boehmer & Ponthot (2017) y Thakur (2016) la influencia ... se ordena: friccion, restitucion y rigidez" | No "Cleary (2015)" in the library (Owen & Cleary 2015 is meant?); Thakur says nothing about this ordering; Cleary 2001 says friction and restitution are "relatively unimportant" (PDF p22) | Boemer abstract (PDF p1) and §3.1.4 (PDF p10) -- see [05](05_friction.md) |
| 8 | "En Cleary & Owen (2016) utilizan ... Cundall-Strack ... [1]" | [1] is Cleary & **Morrison** 2016; it uses a linear spring-dashpot with restitution (PDF p7 / j.81), which in YADE is **not** `Law2_ScGeom_FrictPhys_CundallStrack` (that law has no dashpot) | see [01](01_contact_model.md) |
| 8 vs 10 | Overlap target "< 0.1 %" (slide 8) vs "between 0.1 % and 0.5 %" (slide 10) | Inconsistent; literature gives 0.1-1 % of the diameter (Boemer) and ~0.8 % (Owen) | see [03](03_stiffness_young_modulus.md) |
| 7, 16 | Rock count line divides by 0.001429 (ball volume) | Typo only: the result 19,888 / 11,171 uses the rock volume 0.0001786 m^3 | see [12](12_charge_fill_and_particles.md) |

## How the derived numbers were computed

Every derived number (Rayleigh time step, Hertz collision time, peak overlap,
critical speed, particle counts) uses the formulas written out in the topic
file, with the PPT slide-12 material set: steel rho = 7850, E = 33.16e9,
nu = 0.292, r = 0.06985 m; rock rho = 2650, E = 2.868e9, nu = 0.25,
r = 0.034925 m. Particle masses: ball 11.206 kg, rock 0.4729 kg.

## Code state referenced

"`main`" means the `main` branch at commit `bb04dfd` (the code that produced
or will produce the datasets). Branch `worktree-yade-sim-structure` contains
the structural rework and the bug fixes referenced in some files.
