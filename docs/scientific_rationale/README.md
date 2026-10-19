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

## Plant data: one reference mill, two supporting mills

Operational data from three SAG mills (SAG_A, SAG_B, SAG_C; PPT slides 2-5)
is used in one specific way throughout these documents:

- **SAG_B is the reference.** Its operating point (9 rpm, Jb 17 %, Jc 26 %)
  sets the simulation, and its bulk toe and shoulder angles (215 deg,
  24.6 deg) are the targets the simulation is compared to.
- **SAG_A and SAG_C are evidence that the selected values are typical.**
  Their designs and dimensions differ slightly from SAG_B, so they are not
  simulated or used as validation cases; their box plots show that SAG_B's
  values sit inside the normal operating ranges of SAG mills (speed
  8.6-10 rpm, Jb 15.2-18.5 %, Jc 24.9-35.1 %, bulk toe 206-215 deg,
  shoulder 24.6-38.2 deg).

Plant power and mill lengths are not used (decided 2026-10-18; see
[15](15_calibration_targets.md) for why power would not be a determining
target anyway).

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
| 15 | [15_calibration_targets.md](15_calibration_targets.md) | Match the SAG_B (reference) bulk toe 215 / shoulder 24.6 deg (0 deg at 3 o'clock, CCW); SAG_A / SAG_C show these values are typical; power only for the internal energy balance |
| 16 | [16_validation_checks.md](16_validation_checks.md) | Acceptance tests every run must pass |

## Source registry

Bibliographic data below is taken from the Zotero records (checked against
the Zotero database on 2026-10-19). "Item" is the Zotero item key, "File" the
storage folder of the PDF actually read. Page references in these documents
are to that PDF ("PDF p") and, where the PDF is the published version, to
the printed page ("j.").

| Key used in docs | Reference | DOI | Item / File | Page mapping |
|---|---|---|---|---|
| **Kishida 2025** | N. Kishida, H. Nakamura, S. Ohsaki, S. Watano, *Surrogate model of DEM simulation for binary-sized particle mixing and segregation*, Powder Technol. 455 (2025) 120811 | 10.1016/j.powtec.2025.120811 | `U6DHI89A` / `U6NKB3KZ` | PDF p = article p (1-13) |
| **Kishida 2025 SM** | Supplementary material of the above (Figs. S1-S2) | -- | `U6DHI89A` / `LZXF23SG` | 3 pages |
| **Cleary & Morrison 2016** | P.W. Cleary, R.D. Morrison, *Comminution mechanisms, particle shape evolution and collision energy partitioning in tumbling mills*, Miner. Eng. 86 (2016) 75-95 | 10.1016/j.mineng.2015.12.006 | `BQR6XF9R` / `9S5TJQ2P` | j. = PDF p + 74 |
| **Owen & Cleary 2015** | P. Owen, P.W. Cleary, *The relationship between charge shape characteristics and fill level and lifter height for a SAG mill*, Miner. Eng. 83 (2015) 19-32 | 10.1016/j.mineng.2015.08.009 | `GZR4AELH` / `AYIPPK53` | j. = PDF p + 18 |
| **Boemer & Ponthot 2017** | D. Boemer, J.-P. Ponthot, *DEM modeling of ball mills with experimental validation: influence of contact parameters on charge motion and power draw*, Comp. Part. Mech. 4(1) (2017) 53-67 | 10.1007/s40571-016-0125-4 | `HFTDYRM2` / `4LNBNEIZ` | j. = PDF p + 52 |
| **Cleary 2001** | P.W. Cleary, *Charge behaviour and power consumption in ball mills: sensitivity to mill operating conditions, liner geometry and charge composition*, Int. J. Miner. Process. 63(2) (2001) 79-114 (**2D** DEM) | 10.1016/S0301-7516(01)00037-0 | `APTRYTA5` / `VRMUBFRG` | j. = PDF p + 78 |
| **Govender 2015** | N. Govender, R.K. Rajamani, S. Kok, D.N. Wilke, *Discrete element simulation of mill charge in 3D using the BLAZE-DEM GPU framework*, Miner. Eng. 79 (2015) 152-168 | 10.1016/j.mineng.2015.05.010 | `ALAZVPIQ` / `W9YT6FNT` | j. = PDF p + 151 |
| **Thakur 2016** | S.C. Thakur, J.Y. Ooi, H. Ahmadian, *Scaling of discrete element model parameters for cohesionless and cohesive solid*, Powder Technol. 293 (2016) 130-137 | 10.1016/j.powtec.2015.05.051 | `Y4CWQDST` / `AJF55YJ2` | j. = PDF p + 129 |
| **Gercek 2007** | H. Gercek, *Poisson's ratio values for rocks*, Int. J. Rock Mech. Min. Sci. 44(1) (2007) 1-13 | 10.1016/j.ijrmms.2006.04.011 | `56ASD2GS` / `JPTAYGXS` | PDF p = j. |
| **Vergara et al. 2020** | M. Vergara, A. Arismendy Agudelo, A. Libreros, A. Brzovic, *Numerical investigation into strength and deformability of veined rock mass*, Int. J. Rock Mech. Min. Sci. 135 (2020) 104510 | 10.1016/j.ijrmms.2020.104510 | `5HS5T7DE` / `QR9D245M` | The PDF is the **author manuscript**: page numbers are manuscript pages, not journal pages |
| **Shigley** | R.G. Budynas, J.K. Nisbett, *Diseno en ingenieria mecanica de Shigley*, 8th ed. (Spanish), McGraw-Hill Interamericana, 2008, ISBN 978-970-10-6404-7 (translation of *Shigley's Mechanical Engineering Design*, 8th ed., 2008) | -- | `2WRCXH99` / `4RP3VQXB` (also `V3V5BMNV`, English edition, no file) | inside-cover table = PDF p3 |
| **Shi & Zhang 2008** | Y. Shi, Y. Zhang, *Simulation of random packing of spherical particles with different size distributions*, Appl. Phys. A 92 (2008) 621-626 | 10.1007/s00339-008-4547-6 | `DWL7JH3T` / `ZNTAYS7X` | j. = PDF p + 620 |
| **Brouwers 2024** | H.J.H. Brouwers, *Random packing fraction of binary similar particles: Onsager's excluded volume model revisited*, Physics-Uspekhi 67(5) (2024) 510-529 | 10.3367/UFNe.2023.11.039606 | `SFYYQ45R` / `TS9GXXKP` | The PDF is the **arXiv:2209.09873v5 preprint** (27 Jun 2024): page numbers are arXiv pages |
| **Johnson 1985** | K.L. Johnson, *Contact Mechanics*, Cambridge University Press, 1985 (digital ed. 2012) | 10.1017/CBO9781139171731 | -- / `LECT8BKG` (**standalone PDF without a parent record**, see below) | book p = PDF p - 10 (scanned, no text layer) |
| **Li et al. 2005** | Y. Li, Y. Xu, C. Thornton, *A comparison of discrete element simulations and experiments for 'sandpiles' composed of spherical particles*, Powder Technol. 160(3) (2005) 219-228 | 10.1016/j.powtec.2005.09.002 | `BN556RC8` / `6CHXZ76U` | j. = PDF p + 218 |
| **Nan et al. 2022** | W. Nan, W.P. Goh, M.T. Rahman, *Elasto-plastic and adhesive contact: an improved linear model and its application*, Powder Technol. 407 (2022) 117634 | 10.1016/j.powtec.2022.117634 | `M78ZRT88` / `MEHLVFKI` | The PDF is the **author manuscript** (49 pages, same text as arXiv:2202.09520): page numbers are manuscript pages |
| **McLaskey & Glaser 2010** | G.C. McLaskey, S.D. Glaser, *Hertzian impact: Experimental study of the force pulse and resulting stress waves*, J. Acoust. Soc. Am. 128(3) (2010) 1087-1096 | 10.1121/1.3466847 | `J45IS7SQ` / `PWTRWT5T` | j. = PDF p + 1086 |
| **YADE docs 2021** | V. Smilauer et al. (27 authors), *Yade documentation*, 3rd ed., 2021 (the latest official edition; PPT ref. [8] cites the 2nd ed., 2015, DOI 10.5281/zenodo.34073) | 10.5281/zenodo.5705394 | `4NJP35ET` / `86JYU2WN` | printed p = PDF p - 7 |
| **PPT** | `avances_tt.pptx` (project progress deck) | -- | `YM2798IJ` / `J8ID6KEP` | slide numbers |

Govender et al. 2016 (Blaze-DEMGPU framework, SoftwareX 5 (2016) 62-66,
`2GMEKA42`) and Chou et al. 2017 (mixing index, KONA 34 (2017) 275-281,
`4GN5HB5Y`) were searched but give no DEM parameter used here.

### References added on 2026-10-19 (verified in the PDFs)

| Reference | Used for | Exact location (verified) |
|---|---|---|
| Johnson 1985 | Hertz force law, maximum overlap, impact duration | §11.4 "Elastic impact", (a) "Collinear impact of spheres", book pp. 351-353 (PDF pp. 361-363): Eq. (11.20) P = (4/3) R^(1/2) E* delta^(3/2) with 1/R = 1/R1 + 1/R2, 1/E* = (1-nu1^2)/E1 + (1-nu2^2)/E2, 1/m = 1/m1 + 1/m2 (p. 352); Eq. (11.22) delta* = (15 m V^2 / (16 R^(1/2) E*))^(2/5) (p. 353); Eq. (11.24) T_c = 2.94 delta*/V = 2.87 (m^2 / (R E*^2 V))^(1/5) (p. 353). Force law originally Eq. (4.23), Ch. 4. |
| Li et al. 2005 | Rayleigh critical time step | End of §2, Eqs. (8)-(10), j.221 (PDF p3): Delta t_c = (pi R_bar / beta) sqrt(rho / G); beta from the exact Eq. (9), approximated by beta = 0.8766 + 0.163 nu (Eq. 10); R_bar = average particle radius, G = shear modulus |
| Nan et al. 2022 | Open statement of the Rayleigh step; practical dt fraction | Eq. (71), manuscript p18 (credited to Raji 1999, PhD thesis, Newcastle); same page: "much smaller time step should be used, i.e. Delta t = 0.01~0.1 Delta T_R" to resolve contact details |
| YADE docs 2021 | P-wave critical step used by YADE | Ch. 2 "Yade for users", §2.1 "DEM formulation", "Stability considerations -- Critical timestep", Eqs. (2.12)-(2.13), printed p. 72 (PDF p79); `yade.utils.SpherePWaveTimeStep(radius, density, young)`: "Delta t_c = r / sqrt(E / rho)", printed p. 838 (PDF p845), example `SpherePWaveTimeStep(1e-3, 2400, 30e9)` = 2.83e-7 s (confirms plain E) |
| McLaskey & Glaser 2010 | Secondary pointer to Johnson | Reference list, PDF p10: "Johnson, K. (1985). Contact Mechanics (Cambridge University Press, Cambridge), pp. 351-369"; derivation pointer in section "B. The source function and Hertzian impact", PDF p3 (j.1089) |

**Zotero housekeeping:** the Johnson PDF (`LECT8BKG`) is a standalone
attachment with no bibliographic record. Create a parent item from the DOI
(Add Item by Identifier: `10.1017/CBO9781139171731`) and drag the PDF onto
it, so the reference exports with author, title and publisher.

## Citation problems found in the PPT

These do not change the values, but the references must be corrected before
they go into the thesis:

| Slide | As written | Problem | Correct support |
|---|---|---|---|
| 8 | "Se busca mantener ... dt = 1e-4 [5]" (Boemer & Ponthot) | Boemer uses 1e-5, 2.5e-6, 1e-6 s (§3.1, PDF p7 / j.59); 1e-4 does not appear in the paper | Cleary 2001 §2, PDF p5 / j.83 gives "typically 1e-4 to 1e-6 s" **with** 15-25 steps per collision -- see [02](02_time_step.md) |
| 8, 9, 11, 12 | "[3] Thakur et al. (2014) ... Powder Technology, 293" for reducing E | Year is 2016; the paper is about **coarse-graining** (stiffness scales linearly with particle size, abstract PDF p1); it does not discuss lowering E to enlarge dt | Cleary & Morrison 2016 §2 PDF p3 / j.77; Boemer §3.1.2 PDF p8 / j.60 and §4 PDF p13; Owen & Cleary §3 PDF p3 / j.21 -- see [03](03_stiffness_young_modulus.md) |
| 8 | "[7] Vergara & Mork (2017) ... J. Rock Mech. Geotech. Eng., 9(2)" | The Zotero item is Vergara, Arismendy Agudelo, Libreros & Brzovic, *Numerical investigation into strength and deformability of veined rock mass*, Int. J. Rock Mech. Min. Sci. 135 (2020) 104510 | Cite that paper, Table 1 (manuscript PDF p3): E_i = 55 GPa, nu = 0.25 |
| 8 | "[8] Smilauer et al. (2015). Yade Documentation, 2nd ed. doi:10.5281/zenodo.34073" | Not wrong, but superseded | Cite the 3rd ed. (2021, DOI 10.5281/zenodo.5705394) held in Zotero, the latest official edition |
| 9 | dt_cr = R_min sqrt(rho / E_eff), E_eff = E / (1 - nu^2), presented as YADE's P-wave step | YADE's `PWaveTimeStep` uses plain E (YADE docs 2021, printed p. 838) | Use dt_cr = r / sqrt(E / rho) -- see [02](02_time_step.md) |
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
