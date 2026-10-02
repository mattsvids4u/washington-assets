# DC-F01 — Federal background building assemblies — PASS PLAN

Claimant: claude-cloud-agent · Lane: AGENTS · Set: DC-EXT1 Exterior Standard · Priority P1 · Kind: PCG assembly
Request revision: WASHINGTON-2026-09-22-v001 + Road Plan 05 integration addendum (doc modified 2026-09-25T10:29Z, text sha256 3c7747bd…1bcb)
Brief WASHINGTON-2026-09-22-v001 · Stage standard WASHINGTON-2026-09-22-v001 · Road plans canon WASHINGTON-ROADPLANS-v002 (2026-09-30)
Claimed 2026-10-02T10:30Z — Drive folder `DC-F01 — claude-cloud-agent` (1hgbMAOhZ10dSx2hVuvX77L9x7wBwlE5f), CLAIM.json 1WLLiZbaP2XxED8WP4e-rD1_0xMeuX42x
Work branch `claude/adoring-pasteur-25ccu0`; delivery branch pattern `asset/DC-F01-v###`.

Status: **PASS 1 (evidence) IN PROGRESS** — updated 2026-10-02.

## Problem

Reference-led background assemblies for named federal and institutional buildings along the
White House → Library corridor, as they stood in **Oct–Nov 1963**. Each named building keeps its
own identity (footprint, silhouette, facade rhythm, 1963 name); kits C18/C19/C20 are used only
where that building's evidence supports the construction language. EXT1 read target: correct at
gameplay distance and from a moving car at night (stage standard §6) — silhouette, cornice
lines, real window openings with glazing (lit/unlit), entrances and material tone matter more than
close-up carving.

Named scope from the request: IRS, Post Office Department, Senate Office Building / New Senate
Office Building, U.S. Courthouse (C2–C7), and the C10 hard-locks Library of Congress Annex, Folger
Shakespeare Library and Cannon House Office Building.

## Version plan (staged; one pass plan, several deliveries)

| Version | Scope | Why this order |
|---|---|---|
| **v001** | C10 hard-locks: **Library of Congress Annex**, **Folger Shakespeare Library**, **Cannon House Office Building** | Road Plan 05 addendum names F01 the C10 hard-lock owner; these frame the C9 arrival (both route options pass them); none needs C20, and C18 is not yet approved |
| v002 | U.S. Courthouse (C4/C5) + Post Office Department + IRS (C2–C4) | needs C18 (federal limestone bay, not yet approved) and C20 (red tile roof, v005 APPROVED per Drive) for honest Federal Triangle vocabulary |
| v003 | SOB / NSOB only if Matt confirms they stay with F01 | Road Plans canon v002 assigns SOB/NSOB to DC-F02; request text lists them under F01 — **ownership conflict raised, not built** |

## Locked sources (filled in during Pass 1 — see EVIDENCE.md)

- Drive: References/DC-F01 starter photos `01_Exterior_view_Folger_Shakespeare_Library_June_2025` (Commons, CC BY-SA 4.0, 2025-06-03) and `02_Adams_Building_Exterior_Stairs` (US Capitol, public domain, 2017-01-03). **Images could not be opened in this sandbox** (connector returns no image data; egress blocks Wikimedia) — metadata only.
- DC-R02 v001 (APPROVED) is the footprint/height authority, but its data package is on Matt's PC only; v001 uses published dimensions and must be re-snapped to the R02 evidence cards before placement.
- DC-C19 v004 (APPROVED): order vocabulary and interface for the Cannon colonnade (meshes not reused — see DEPENDENCY_LOCK.json).
- Moodbook pp. 10–12 (text): object logic, material separation, palette relationships, staged review evidence.

## Measurable deliverable (v001)

Three GLBs in `out/`, Blender metres (UE glTF import → cm), Z-up source / glTF Y-up:

- `SM_F01_LOCAnnex.glb`, `SM_F01_Folger.glb`, `SM_F01_Cannon.glb`, each containing
  - `<name>_LOD0` (full facade articulation: real recessed window openings with frames/glazing, entrances, cornices, columns, steps), `<name>_LOD1` (openings kept, small ornament dropped), `<name>_LOD2` (massing + inset glazing, no reveals);
  - `UCX_<name>_NN` convex collision per mass; `SOCKET_*` empties (entrances, lamps, typed kit swap slots);
  - stable material slots `M_F01_*` with generated portable PBR textures (base colour, roughness, normal);
  - pivot at footprint centre, grade level; +X east, +Y north (map-aligned).
- `SM_F01_C10_ReviewLayout.glb` — the three buildings in approximate relative position for review renders only (NOT a placement source).
- Renders: clay + textured front/profile/rear/¾ per building (tools/render_views.py), plus street-level review views, a night lit-window view, and base-colour/roughness/normal passes (moodbook p12).

## Passes

1. **Evidence** — EVIDENCE.md per building: dated sources with URL/archive ID, rights, what each supports, 1963 vs later changes, APPROXIMATE/FICTIONALISED labels; evidence card per building (footprint, height, storeys, bays, materials). *(in progress)*
2. **Build** — `python jobs/DC-F01/build.py` rebuilds everything from scratch (geometry, textures, GLBs, layout).
3. **Verify** — `tools/qa_check.py` on every GLB (fix every FAIL); clay + textured renders; harsh comparison against evidence and moodbook; iterate; clean rebuild from empty `out/`.
4. **Deliver** — `deliveries/DC-F01/asset-v001/`, `package_delivery.py`, branch `asset/DC-F01-v001` + PR, Drive `Incoming Deliveries/DC-F01 — asset — v001`.

## Acceptance checks

- qa_check.py: all PASS for all GLBs (bounds, ground contact, UVs, materials, no degenerate faces, outward normals, LOD1 present, UCX present, transforms applied).
- Dimensions within ±5 % of the evidence card values used (bbox printed by build.py and recorded in HANDOFF.md).
- Each building's renders show its identifying features (listed per building in EVIDENCE.md) — not a box with a window texture: real openings, depth, cornice shadow lines.
- No post-1963 elements (e.g. Folger 2020s entrance pavilions/ramps, Adams-era signage, Cannon Renewal changes).
- Clean rebuild from empty `out/` reproduces the same files (hash comparison).
- Unreal import/readback and motion tests: **NOT_RUN — needs local Unreal (UE 5.8)**.

## Dependencies

- DC-C19 v004 APPROVED — vocabulary/interface only (Cannon colonnade).
- DC-C18 — not approved; typed swap slots left where it could apply. DC-C20 v005 — APPROVED on Drive (register stale); not used by v001 (no tile roofs on C10 buildings).
- DC-R02 v001 APPROVED — placement/footprint authority (data not reachable from this sandbox).
- DC-B01 — target level/placement; nothing is placed by this job.

## Uncertainties (running list)

- Reference images not inspected (environment egress allowlist); every dimension from text sources is at best PROBABLE and facade rhythm details are APPROXIMATE until Matt (or a local run) compares renders with the photos.
- R02 footprints not available here → footprint outlines APPROXIMATE.
- 1930s federal/institutional sculpture (Lee Lawrie doors on the Annex, John Gregory reliefs on the Folger): rights unconfirmed → accurate massing with labelled simplified stand-ins (stage standard §7).
- SOB/NSOB F01-vs-F02 ownership (see version plan).
