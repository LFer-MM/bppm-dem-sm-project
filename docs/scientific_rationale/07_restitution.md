# 07 -- Coefficient of restitution

## Decision

| Pair | e |
|---|---|
| rock-rock | **0.3** |
| rock-steel | **0.5** |
| steel-steel | **0.8** |
| liner-steel | **0.8** |
| liner-rock | **0.5** |

- The liner material ([05](05_friction.md)) is **steel** (SAG_B shell liners
  and lifters are steel, stated by the author 2026-10-21), so its pairs take
  the steel values; only its friction differs. The frictionless end walls
  take their restitution from the liner.
- Applied per pair through a `MatchMaker` on
  `Ip2_FrictMat_FrictMat_MindlinPhys.en`, built from material **labels**.
  `es` is not set, so YADE uses the same value tangentially (es = en).
- Fixed, not calibrated.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Cleary & Morrison 2016 | e = 0.3 (rock-rock), 0.5 (rock-steel), 0.8 (steel-steel) | Table 2, PDF p7 / j.81 | Yes |
| Owen & Cleary 2015 | e = 0.75 steel-steel, 0.5 steel-rock, 0.3 rock-rock; "highest for steel-steel collisions which are relatively elastic and lowest for rock-rock collisions which have significant local fracture at contacts" | Table 4 and §3 text, PDF p3 / j.21 | Yes |
| Boemer & Ponthot 2017 | Influence of e "becomes important for values close to 1; apart from that, the charge motion is again relatively insensitive"; e = 0.3, 0.6, 0.9 tested; stiffness and e "only have a relatively small impact on the power draw" | §3.1.3-3.1.4, PDF p10 / j.62 | Yes |
| Govender 2015 | e particle 0.75, lifter 0.75 for Los Bronces; power could be matched "exactly by changing the coefficient of restitution" | Table 8 and §3 text, PDF p14 / j.165 | Yes |
| Kishida 2025 | e = 0.75 (single material) | Fig. 2(b), PDF p4 | Yes |
| Cleary 2001 (2D) | Friction and restitution "relatively unimportant" (citing Cleary 1998a) | §9, PDF p22 / j.100 | Yes |
| Govender 2015 | Los Bronces: e = 0.75 for particles **and** lifters (steel lifters get the particle value) | Table 8, PDF p14 / j.165 | Yes |
| YADE source (`7c8d01e`) | With `en` given, the normal damping ratio is computed from "formula (B6) of [Thornton2013], written specifically for the Hertz-Mindlin model (no-slip solution) where the end of contact is considered to take place once the normal force is zero"; alpha from Eq. (B7); dashpot c_n = beta_n 2 sqrt(m* k_n) with the current Hertz stiffness k_n | `pkg/dem/HertzMindlin.hpp:90`; `HertzMindlin.cpp:184-207, 458-463` | Yes (source read) |
| YADE source / docs 2021 | "If neither e_s nor beta_s is given, the value of en is used for es" | `HertzMindlin.hpp:97`; docs printed p. 562 (PDF p569) | Yes |
| Thornton et al. 2013 | Origin of the e -> beta mapping (Eqs. B6-B7) | via the YADE source only | **No** (not read) |

## PPT

| Slide | Content |
|---|---|
| 8, 9, 12 | "Coeficientes de Restitucion (Pares): Roca-Roca = 0.3 [1], Roca-Acero = 0.5 [1], Acero-Acero = 0.8 [1]" ([1] = Cleary & Morrison 2016, Table 2) |
| 8 | Reason to use Hertz-Mindlin: pair-wise restitution |

## Current state

| Where | What |
|---|---|
| `config.py:107` (`RESTITUTION_COEFFICIENTS`) | 0.8 / 0.5 / 0.3 -- matches the decision; no liner pairs yet |
| `simulation/yade_dem/materials.py:39` | `restitution_matchmaker(pairs)` builds the MatchMaker from material **labels** (fixed since the old review) |
| `simulation/scenario.py:326-330` | Validation: every material pair in use must have an e, otherwise the scenario fails |
| `simulation/yade_dem/run_simulation.py:145-169` | End-wall material derives from the liner; its restitution pairs copy the liner's |
| `config.py:482-499` | Old `restitution_matchmaker()` with hard-coded ids 0 = steel, 1 = rock: **unused** (no callers), still in the code |

## Analysis

The PPT values come directly from Cleary & Morrison 2016 and agree with Owen
& Cleary 2015 (only steel-steel differs: 0.8 vs 0.75). Boemer shows the
charge is insensitive to e unless e approaches 1, so the 0.75-0.8 difference
is immaterial. Govender's remark that e can tune power is a reason to keep e
fixed: tuning it would hide errors elsewhere (e.g. damping).

- **Liner pairs.** The liners and lifters are steel, so steel values apply
  (Govender also gives lifters the particle e, Table 8). The separate liner
  material exists only to carry its own friction ([05](05_friction.md)).
- **Velocity independence.** YADE's Hertz-Mindlin maps e to a damping ratio
  with Thornton et al.'s formula for Hertzian contacts and scales the dashpot
  with the current stiffness, so the input e should be recovered at any
  impact speed. The binary-collision test (C01-4) confirms it at the
  run's dt.
- **Tangential damping.** With es = en the tangential dashpot uses the same
  ratio. Accepted (the friction limit governs most tangential dissipation in
  a mill); recorded so it is not mistaken for an omission.
- **Slurry.** A SAG charge is wet; the source values (Cleary & Morrison,
  Owen & Cleary) come from dry DEM. This is standard in those studies and is
  stated as a limitation, not corrected.

## Verdict and how to defend it

"Restitution coefficients follow Cleary & Morrison (2016, Table 2), consistent
with Owen & Cleary (2015, Table 4): rock-rock collisions are strongly
dissipative because of local fracture, steel-steel ones nearly elastic.
Charge motion is insensitive to e away from 1 (Boemer & Ponthot 2017, §3.1),
so e is fixed rather than calibrated. The steel liners and lifters take
the steel values, as in Govender et al. (2015, Table 8). YADE converts each
e into a viscous damping ratio with the Hertz-specific relation of Thornton
et al. (2013), so the coefficient holds at all impact velocities."

## Open items / validation

- Binary-collision test in YADE at the chosen dt: measured e must match the
  input within ~2 % for each pair ([16](16_validation_checks.md)).
- Interstitial slurry not modelled (limitation, see Analysis).

## Pending code changes

| ID | Change | Current code | When |
|---|---|---|---|
| C07-1 | Add liner-steel 0.8 and liner-rock 0.5 to `RESTITUTION_COEFFICIENTS` (with C05-3) | Steel / rock pairs only | Before calibration |
| C07-2 | Delete the unused id-based `config.restitution_matchmaker()` | `config.py:482-499` | Any time |
