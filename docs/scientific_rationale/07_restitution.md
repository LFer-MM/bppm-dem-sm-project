# 07 -- Coefficient of restitution

## Decision

| Pair | e |
|---|---|
| rock-rock | **0.3** |
| rock-steel | **0.5** |
| steel-steel | **0.8** |

Applied per pair through a `MatchMaker` on `Ip2_FrictMat_FrictMat_MindlinPhys.en`,
built from material **labels** (not hard-coded ids). Not a primary
calibration variable.

## Evidence

| Source | What it says | Where | Verified |
|---|---|---|---|
| Cleary & Morrison 2016 | e = 0.3 (rock-rock), 0.5 (rock-steel), 0.8 (steel-steel) | Table 2, PDF p7 / j.81 | Yes |
| Owen & Cleary 2015 | e = 0.75 steel-steel, 0.5 steel-rock, 0.3 rock-rock; "highest for steel-steel collisions which are relatively elastic and lowest for rock-rock collisions which have significant local fracture at contacts" | Table 4 and §3 text, PDF p3 / j.21 | Yes |
| Boemer & Ponthot 2017 | Influence of e "becomes important for values close to 1; apart from that, the charge motion is again relatively insensitive"; e = 0.3, 0.6, 0.9 tested; stiffness and e "only have a relatively small impact on the power draw" | §3.1.3-3.1.4, PDF p10 / j.62 | Yes |
| Govender 2015 | e particle 0.75, lifter 0.75 for Los Bronces; power could be matched "exactly by changing the coefficient of restitution" | Table 8 and §3 text, PDF p14 / j.165 | Yes |
| Kishida 2025 | e = 0.75 (single material) | Fig. 2(b), PDF p4 | Yes |
| Cleary 2001 (2D) | Friction and restitution "relatively unimportant" (citing Cleary 1998a) | §9, PDF p22 / j.100 | Yes |

## PPT

| Slide | Content |
|---|---|
| 8, 9, 12 | "Coeficientes de Restitucion (Pares): Roca-Roca = 0.3 [1], Roca-Acero = 0.5 [1], Acero-Acero = 0.8 [1]" ([1] = Cleary & Morrison 2016, Table 2) |
| 8 | Reason to use Hertz-Mindlin: pair-wise restitution |

## Current state

| Where | What |
|---|---|
| `main` `config.py:106-108` | 0.8 / 0.5 / 0.3 -- matches the decision |
| `main` `config.py:485-488` | MatchMaker with material ids 0 = steel, 1 = rock hard-coded: breaks if any other material (end walls, test boxes) is registered first |

## Analysis

The PPT values come directly from Cleary & Morrison 2016 and agree with Owen
& Cleary 2015 (only steel-steel differs: 0.8 vs 0.75). Boemer shows the
charge is insensitive to e unless e approaches 1, so the 0.75-0.8 difference
is immaterial. Govender's remark that e can tune power is a reason to keep e
fixed: tuning it would hide errors elsewhere (e.g. damping).

## Verdict and how to defend it

"Restitution coefficients follow Cleary & Morrison (2016, Table 2), consistent
with Owen & Cleary (2015, Table 4): rock-rock collisions are strongly
dissipative because of local fracture, steel-steel ones nearly elastic.
Charge motion is insensitive to e away from 1 (Boemer & Ponthot 2017, §3.1),
so e is fixed rather than calibrated."

## Open items / validation

- Binary-collision test in YADE at the chosen dt: measured e must match the
  input within ~2 % for each pair ([16](16_validation_checks.md)).
