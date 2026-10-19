# 13 -- Initial conditions (SIC and RMIC)

## Decision

Two initial-condition (IC) types, generated with the same charge, materials
and geometry as the dataset runs:

| IC | Construction | Status |
|---|---|---|
| **RMIC** (randomly mixed) | Chord-box batches in which each sphere is randomly assigned rock or ball in the global proportion; masses and inertias recomputed after resizing | Fixed |
| **SIC** (segregated) | **Rock poured first (bottom layer), balls poured on top** -- the orientation of `ingress_segregated` and of the existing dataset | Fixed (decided 2026-10-18; deliberate deviation from Kishida's Fig. 6b, see analysis) |

Common protocol for both:

1. Pour with damping 0.5 (PPT slides 17-18); mill not rotating.
2. Settle until unbalanced force < 1e-3.
3. **Zero all velocities** ("all particles stationary", as in Kishida).
4. Save positions (CSV) **and** the YADE scene (`.yade.gz`), with the seed,
   counts, phi and material set in a manifest.
5. 30 replicates per IC type (PPT slide 30), differing only in the seed.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Kishida 2025 | "All particles were stationary under the initial conditions. Two types of initial particle positions of binary-sized particles, which were (a) randomly mixed initial condition (RM-IC) and (b) segregated initial condition (S-IC) along the Z-direction" | §3, PDF p6 | Yes |
| Kishida 2025 | Fig. 6(b): in the S-IC the **large particles (red) fill the bottom and the small particles (cyan) form the top layer**; Z is the vertical axis (Fig. 2a / 6 side and front views) | Fig. 6, PDF p6; Fig. 2(a), PDF p4 | Yes (figure read) |
| Kishida 2025 | Table 2: case 1 RM -> RM, case 2 RM -> S, case 3 S -> RM, case 4 S -> S (surrogate-modelling IC -> prediction IC) | Table 2, PDF p6 | Yes |
| Kishida 2025 | Training data from RM-IC generalised to S-IC; data from S-IC did not generalise: "the RNNSR constructed based on the data initiated from S-IC could not predict the mixing and segregation initiated from RM-IC ... attributed to the uniformity of the spatial arrangement" (in RM-IC data "both large and small particles were uniformly distributed") | §4.2, PDF p10 | Yes |
| Kishida 2025 | Single particle density for both sizes (2500 kg/m^3) | Fig. 2(b), PDF p4 | Yes |
| Kishida 2025 | Equal-density drum: "large particles were observed more in the peripheral region of the powder bed, while small particles were observed more in the central core ... This is a typical segregation pattern in a rotating drum"; attributed to percolation | §4.1, PDF p7; §2.2.2, PDF p5 | Yes |
| Govender 2015 | Los Bronces SAG (ore 2850, balls 7800 kg/m^3): "We also see radial segregation with the smallest particles moving to the mill shell as predicted by theory and experiment" | §3, PDF p14 / j.165 | Yes |

## PPT

| Slide | Content |
|---|---|
| 17 | "Simulacion de Generacion de Condicion Inicial en Segregacion (SIC)": dt = 1e-4, gravity_damping = 0.5, unbalanced_forces < 0.001, 26 % del slice; script `new_ingress_rmic.py`; output `sic.csv` |
| 18 | RMIC: same settings; output `rmic.csv` |
| 30 | Datasets: SIC 400 frames x 30 simulations, RMIC 200 frames x 30 simulations |

## Current state

| Where | What |
|---|---|
| `main` `particles.py:178-205` | `ingress_segregated` pours **SMALL first, then LARGE** -> rock at the bottom, balls on top |
| `main` `particles.py:147,158,162` | `ingress_random`: batches sized for 60 % solids (makeCloud cannot reach it), and resized spheres keep the **mass of a steel ball** (radius and material changed, mass / inertia not recomputed) -- fixed on the branch (commit `543208a`) |
| Existing SIC dataset, frame 0 | ore_rock mean y = -4.42 m, ball_steel mean y = -2.10 m -> rock bottom, balls top (opposite of Kishida's S-IC) |

## Analysis

- **Why not copy Kishida's orientation.** Kishida's S-IC puts the large
  particles at the bottom (Fig. 6b). In a resting bed the bottom layer lies
  against the shell, i.e. on the *periphery* of the circulating charge -- and
  in Kishida's equal-density drum the large particles do migrate to the
  periphery (§4.1, PDF p7). In a SAG mill the large particles (balls) are also
  ~3x denser, and the observed segregation is the opposite: "the smallest
  particles moving to the mill shell" (Govender 2015, PDF p14), i.e. balls
  towards the core. The SAG analogue of Kishida's layering is therefore the
  species that migrates to the shell (rock) at the bottom and the balls on
  top. This is the orientation chosen.
- **Percolation at rest.** A 2:1 size ratio does **not** let rock fall
  through a resting ball bed by gravity alone: the pore throats of a packed
  sphere bed only pass spheres smaller than ~0.15 of the large diameter (a
  classical geometric result; no paper in the Zotero library covers it --
  add a reference if this argument is used). So the "rock would go in
  between" argument applies to the **sheared** charge (kinetic sieving, the
  percolation mechanism Kishida cites, §2.2.2 PDF p5), in either orientation,
  not to the IC itself. With rock at the bottom the IC is static and well
  defined.
- **Consequence of balls on top.** Dense balls above light rock is
  gravitationally unstable once the charge is sheared: from t = 0 both density
  (balls sink) and size (balls rise) act, so the SIC exercises both
  mechanisms -- relevant for the SAG case, and a documented difference from
  Kishida's single-density system.
- **RMIC bug impact.** With the mass bug, every small rock created by
  resizing had the mass of a 0.1397 m steel ball (~24x too heavy). Any RMIC
  generated by `main`'s `ingress_random` is invalid.
- **Damping during IC generation** is legitimate: the IC is a static state;
  velocities are zeroed afterwards.
- **Training IC.** Kishida's main finding for this design is that the
  surrogate must be trained on RM-IC data (uniform spatial coverage) to
  predict both ICs; SIC runs are mainly prediction / test cases.

## Verdict and how to defend it

"Both initial conditions are static packings (Kishida et al. 2025, §3): the
charge is poured, settled with artificial damping to an unbalanced force below
1e-3 and all velocities are set to zero. The randomly mixed IC assigns
species at random in the global proportion. In the segregated IC the rock
forms the bottom layer and the balls the top layer. This differs from the
layering of Kishida et al. (large particles at the bottom, Fig. 6b) on
purpose: there, with equal densities, the large particles migrate to the
periphery (§4.1); in a SAG mill the denser balls migrate to the core and the
ore to the shell (Govender et al. 2015, §3), so placing the ore at the
bottom (against the shell) is the equivalent configuration. Thirty replicates
per IC differ only in the random seed."

## Open items

- Define "unbalanced force < 1e-3" reachability: in the 360-particle smoke
  test YADE's unbalanced-force ratio plateaued at ~0.2-0.3 with kinetic
  energy ~1 cm/s rms; a kinetic-energy criterion may be needed in addition.
- Store ICs under versioned names including the material-set id, so an IC is
  never reused with different materials.
- Confirm in a calibrated run that balls do migrate towards the core (as in
  Govender) for this charge; if not, revisit the SIC orientation argument.
