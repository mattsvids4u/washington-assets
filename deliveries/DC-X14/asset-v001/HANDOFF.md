# DC-X14 — Staff offices and Legislative Reference Service room — HANDOFF (asset-v001)

Claimant claude-cloud-agent · DC-INT1 Interior Standard · P2 · AGENTS lane · stage A (asset)
Request revision WASHINGTON-2026-09-22-v001 + Road Plan 04 addendum · built 2026-10-02 in the cloud sandbox (bpy 4.5.14, no GPU, no Unreal)

**Status: DELIVERED FOR REVIEW. Not approved. Only Matt approves.**

## What was built

A modular office-room kit for Library of Congress staff offices and the 1963 Legislative
Reference Service, in two layers that match the documented 1963 condition (EVIDENCE.md E4,
E12, E13, E15): the 1897 Main Building office shell, and the "temporary" 1950s–60s overlay of
gray steel partitions, dropped acoustic ceilings and fluorescent fixtures that the 1967
memoir describes as "rabbit warrens". 16 modules + 1 demo assembly, every one a GLB with
LOD0–LOD2, `UCX_` convex collision, box-mapped UVs, stable `MI_X14_*` slots and named sockets:

| Layer | Modules |
|---|---|
| ARCH (1897 shell, ITS ALIVE WD + plaster) | `Wall_Plain_300`, `Wall_Window_300` (round-arched 0.6 m reveal, marble sill, two-light double-hung sash + arched transom, cast-iron radiator), `Wall_Door_300` (four-panel oak door on a hinge pivot, glazed transom, architraves both faces), `Corner`, `Floor_300` (oak strip) and `Floor_300_Linoleum`, `Ceiling_300` (pendant socket), `Pendant_Lamp` (opal bowl, emissive) |
| PART (1950s–60s overlay, MT + GL) | `Panel_Solid_120`, `Panel_Solid_060`, `Panel_Glazed_120`, `Door_090` (flush leaf on a hinge pivot), `Post`, `DropCeiling_120` (exposed T-grid, 4 fissured tiles, hanger wires), `Fluorescent_120` (2-tube strip on chains, lit/unlit by material), `Sign_Door` (brass plate, raised text "LEGISLATIVE REFERENCE SERVICE / HISTORY AND GOVERNMENT DIVISION / ROOM 128") |
| DEMO | `X14_DEMO_LRS_Room` — 9 × 6 × 4.6 m division room assembled only from kit instances: 3 arched windows on the east wall, oak door on the south wall, corridor + 3 glazed cubicles, dropped ceiling and 11 fluorescents over the cubicle zone, 3 pendants over the corridor, 19 `SOCKET_I09_*` furniture sockets and a `SOCKET_X15_StaffAccess_Door` |

Generator: `jobs/DC-X14/build.py` (deterministic, seed 1963; `python jobs/DC-X14/build.py`
rebuilds textures + all GLBs in ~15 s). Textures are generated PBR sets (BC/R/N, 1024²)
in `out/textures/`, also embedded in each GLB. Demo-room interior renders come from
`jobs/DC-X14/render_interior.py`; module orbits from `tools/render_views.py`.

## Moodbook pages and photo files used

- Moodbook pages 10–12 (text; images not viewable in the sandbox — see CONTEXT_ACK.json).
  Palette applied as a lighting/material system: Cold Paper-leaning buff plaster, Walnut-leaning
  oak door stain, Charcoal metal paint, Tungsten warmth from the pendants; Olive reserved for the
  linoleum variant.
- Photos/records: E15 1953 LRS desks (150 px), E14 LCIB thumbnails, E17 HABS DC-351-3 (arched
  first-story windows), E18 first-floor plan, E12 FY1963 Annual Report text, E13 memoir text,
  starter analog office photos (1960 Portland, Feb 1963 MPD). Full list and dates in EVIDENCE.md.

## Evidence gaps (what is APPROXIMATE / FICTIONALISED)

- VERIFIED: 1963 organisation and division names (sign text); LRS in the Main Building and
  Annex; severe crowding in 1963; no air conditioning in 1963 (new heating/ventilating system
  installed Apr–Jun 1963); steel partitions with glass uppers and painted finishes in Main
  Building rooms; gray partitions / dropped ceilings / temporary fixtures in LRS areas (1967
  memoir); arched first-story windows.
- PROBABLE: that the gray-partition overlay was already in place in autumn 1963 (crowding
  documented 1957–63; the memoir dates it to 1967). If Matt prefers the 1953-photo condition
  (freestanding cabinets as dividers, no drop ceiling), use the ARCH layer alone with I09.
- APPROXIMATE: every dimension (room height 4.6 m, window 1.5 × 3.95 m, door 1.1 × 2.6 + 0.4 m,
  partition 2.13 m, drop ceiling at 2.75 m, cornice/baseboard profiles), oak strip floor in
  offices, sash light pattern, radiator type, partition colour (gray) and glazing (clear).
- FICTIONALISED: room number "128", the demo room's layout, the eavesdrop use.
- NOT OBTAINED: HABS DC-351 data pages and photos 22 (corridor) / 23 (office and conference
  room); the 1953 photo at full resolution; Annual Report FY1963 Ch. V (space/equipment).

## Gates

| Gate | Result |
|---|---|
| `tools/qa_check.py` on all 17 GLBs | PASS (0 FAIL) — bounds, ground contact, UVs, materials, degenerate faces, outward normals, applied transforms, LODs, UCX |
| Clean rebuild (delete `out/`, rerun `build.py`, rerun QA) | PASS — see DELIVERY_MANIFEST.json `gates` |
| Clay + textured orbit renders per module | DONE — `renders/modules/` (self-review below) |
| Interior renders of the demo room | DONE — `renders/` |
| Unreal 5.8 import / readback | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Door-pivot / motion tests in Unreal | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Matt approval | PENDING |

glTF is metres by spec; UE's glTF importer converts to cm (3.0 m module → 300 UU). Verify once
on import that `X14_ARCH_Wall_Plain_300` reads 300 × 30 × 460 UU.

## Self-review of the actual renders (be harsh)

Filled in from the renders in `renders/` — see the "Render review" section at the end.

## Expected register status changes (head agent to apply — I did not edit the sheet)

- DC-X14: asset_status UNCLAIMED → **DELIVERED**; claim_owner → "claude-cloud-agent — DC-X14";
  delivery_integrity → "v001 SHA256SUMS written; clean-reopen QA PASS; UE import NOT_RUN";
  asset_user_approval stays PENDING; integration_status NOT_STARTED.
- DC-X14-W01: none exists in the register (weathering: none) — no change.
- DC-I09 relationship: consumed via sockets; nothing to change on the I09 row.

## UNIFICATION PROPOSALS

1. **Shared 1950s–60s office-partition family (both cities).** `X14_PART_Panel_*`, `Door_090`,
   `Post`, `DropCeiling_120` and `Fluorescent_120` are generic U.S. government office stock of
   the period. Propose registering them as a cross-city component set (candidate DALLAS
   consumers: any office interior in the DALLAS catalog that needs a 1963 institutional overlay)
   with the gray and faux-mahogany albedos as the two documented LOC finishes.
2. **Wooden-partition variant for DC-X07.** The memoir documents *temporary wooden partitions*
   boxing in the Main Reading Room gallery bays from Nov 1966. If the gallery is ever dressed
   in a late-60s state, derive a `X14_PART_Panel_Wood_*` variant rather than a new ID.
3. **DC-I09 furniture scale check.** Sockets assume a desk footprint ≤ 1.6 × 0.8 m and desk-top
   items at 0.75 m; the I09 ZIP could not be opened in the sandbox. Re-qualify locally.
4. **DC-X13 reuse.** `Wall_Plain_300` + `Floor_300_Linoleum` + `Fluorescent_120` cover most of
   the basement service corridor's plain fabric; X13's claimant may want to derive rather than
   rebuild.

## What Matt should look at

1. `renders/X14_DEMO_LRS_Room_textured_int_*.png` — does the room read as a 1890s federal
   office with a shabby 1960s overlay, at the dialogue camera, in the moodbook's language?
2. `renders/modules/X14_ARCH_Wall_Window_300_*` and `X14_ARCH_Wall_Door_300_*` — the two
   silhouette-critical modules: reveal depth, sash, radiator; door panelling and architrave.
3. The partition height (2.13 m) and colour against your memory/evidence of the 1960s LOC
   offices; say if you want the faux-mahogany finish or the wooden variant as default.
4. The decision in "PROBABLE" above: 1963 = partition overlay (as delivered) or the 1953
   furniture-divider condition (ARCH layer only).
5. Open the cited HABS/LoC records locally (EVIDENCE.md) and tell me which dimensions to
   correct; `build.py` has every dimension as a named constant at the top.

## Render review

(see below)
