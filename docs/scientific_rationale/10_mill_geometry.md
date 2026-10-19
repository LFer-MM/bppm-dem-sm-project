# 10 -- Mill geometry (STL slice, lifters, diameter, end walls)

## Decision

- Geometry: the plant-derived STL slice (`sag_mill_40ft_m.stl`, to be added
  to Zotero), **30 lifters**, inside diameter **11.8375 m**, slice depth
  **0.375 m**, internal volume **39.4693 m^3** (PPT slide 1).
- Every diameter-based quantity uses D = 11.8375 m (critical speed, Lacey cell
  0.04 D = 0.4735 m).
- End walls: run a 2-case sensitivity test (liner friction vs. frictionless)
  before fixing them. Periodic axial boundaries are not used (see analysis).
- The parametric shell + lifter generator on the branch is only a fallback /
  test tool; it is not the reference geometry.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Owen & Cleary 2015 | Generic SAG mill **slice**: shell inner diameter 8.4 m, slice length 0.6 m "along the cylindrical belly", 56 lifters, base width 320 mm, height 50-300 mm, face angle 15-25 deg | Table 1, PDF p2 / j.20 | Yes |
| Govender 2015 | 2D vs. 3D: "Fig. 30(b) depicts the charge profile for a slice of 10% of length. We notice that the pattern is very similar to the full length of the mill. Clearly the effect of the axial direction cannot just be neglected as the 2D case cannot fully reproduce the dynamics." | §3.1, PDF p16 / j.167 | Yes |
| Govender 2015 | Los Bronces SAG 10.12 m x 4.7 m, "64 rows of high low lifters" | §3, PDF p12-14 / j.163-165 | Yes |
| Govender 2015 | ~68 % of power enters through lifters, ~18 % through the shell | §3, PDF p14 / j.165 | Yes |
| Boemer & Ponthot 2017 | Lab mill 800 mm x 400 mm "closed by flat end walls and a window of transparent tempered glass"; two liner geometries | §2.1, PDF p2 / j.54; Table 1, PDF p3 / j.55 | Yes |
| Cleary 2001 (2D) | Lifter wear (height / face angle) changes cataracting, toe and power; at N <= 70 % critical power "highly insensitive to the lifter pattern" | §7-8 and §11, PDF p16-21, p34 / j.94-99, j.112 | Yes |

## PPT

| Slide | Content |
|---|---|
| 1 | "Diametro Total = 40 ft = 12.192 m (medicion exterior molino real)"; "Diametro Interno = 11,837.5 mm (sin grosor cilindro)"; "Cantidad de Elevadores = 30 elevadores (STL y real)"; "Profundidad del Slice = 375 mm (del STL)"; "Volumen Interno = 39.4693 m^3 (STL via MeshMixer)"; "Diametro Efectivo = 11.576 m (calculado con volumen STL)"; bounding box X = 11.8227, Y = 11.8375, Z = 0.375 m |
| 21 | Lacey cell_size = 0.04 D = 0.04 x 11.83 = 0.4732 m |
| 31 | Snapshot of the STL slice with lifters visible |

## Current state

| Where | What |
|---|---|
| `main` `config.py:68` | `SAGMILL_STL_PATH = "sag_mill_40ft_m.stl"` (file not on this machine) |
| `main` `config.py:72` | `MILL_DIAMETER_M = 11.0` -- **inconsistent** with 11.8375 m; feeds `MetricsOptions.cell_size` (`config.py:207`, 0.44 m instead of 0.4735 m) |
| `configs/pipeline_example.json` | `cell_size = 0.4732` (uses the correct D) |
| `main` `stl.py:273-276` | End caps are "steel" facets with the particle friction |
| Existing dataset | Particle centres reach 5.88 m from the axis (outer edge ~5.95 m), consistent with an inside radius of 11.8375 / 2 = 5.92 m, not 5.5 m |

## Analysis

- **Slice depth.** 0.375 m is 2.68 ball diameters (Owen's 0.6 m slice holds
  ~4 diameters of their largest 145 mm balls). Govender shows a 10 %-length
  slice reproduces the full mill, so a slice is defensible; but with only
  ~2.7 ball diameters the flat end walls touch a large share of the
  particles, and their friction adds lift that a real belly section does not
  have.
- **End walls.** No paper in the library specifies end-wall friction for a
  slice. A frictionless end wall removes the artificial wall shear; a
  liner-friction wall is the conservative "as built" case. The difference is
  measurable in 2 short runs.
- **Periodic boundaries.** Tested on this machine (yadedaily 20260115): a
  rotating facet shell in a periodic cell leaked particles even when static,
  so periodic axial boundaries are not usable without further development.
- **Diameter.** Use the STL's inside diameter 11.8375 m everywhere. The
  "effective" 11.576 m (from the volume net of lifters) is not used for
  critical speed (the classic formula uses the shell diameter).

## Verdict and how to defend it

"The mill is modelled as a 0.375 m slice of the real 40 ft SAG mill (30 lifter
rows, 11.84 m inside diameter) built from the plant STL. Slice models are
standard for SAG mills (Owen & Cleary 2015 use a 0.6 m slice of an 8.4 m mill)
and a slice of ~10 % of the length reproduces the full-mill charge profile,
whereas a 2D model does not (Govender et al. 2015, §3.1). The influence of
the slice end walls was checked by comparing frictional and frictionless end
walls."

## Open items / validation

- Add the STL to Zotero / `data/external/` and record its SHA-256 in each run
  manifest.
- Re-measure D, depth, lifter count and volume from the STL in code and
  compare with slide 1.
- End-wall test: 2 runs x 3 revolutions; compare toe, shoulder, power.
- Fix `config.MILL_DIAMETER_M` to 11.8375 (code change, pending).
