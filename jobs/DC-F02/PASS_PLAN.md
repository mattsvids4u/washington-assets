# DC-F02 — PASS PLAN

Job: DC-F02 - Existing corridor building uplifts · Set DC-EXT1 (AGENTS lane) · Claimant claude-cloud-agent
(claimed 2026-10-02T11:14Z) · Brief WASHINGTON-2026-09-22-v001 · Canon WASHINGTON-ROADPLANS-v002.

## Problem

F02 owns nine named, reference-led corridor buildings (road-plans canon v002): Willard, Hotel
Washington, District Building, Riggs, American Security (C1/C2, already in the map as uplifts — preserve,
version up, never overwrite), National Press Building and National Theatre (C3/C4), Senate Office
Building and New Senate Office Building (C7). They must read correctly from a moving car, day and night,
at EXT1 standard, and must keep their named 1963 silhouettes.

That is too much for one honest delivery. The job is split into bounded versions:

| Version | Scope | Why this order |
|---|---|---|
| **asset-v001** | **Senate Office Building (C7)** | On the north-loop escort route (Constitution Ave), not in the map, best-documented parti, and no F01/H overlap |
| asset-v002 | New Senate Office Building (C7, 1958) | Same street face; pairs with v001 |
| asset-v003 | National Theatre + National Press Building (C3/C4) | Needs R02 C3/C4 frontage fields (R02 v002 owed) |
| asset-v004+ | C1/C2 uplift revisions (Willard, Hotel Washington, District Bldg, Riggs, American Security) | Need the existing in-map meshes, which can't be reached from the cloud. Local / Unreal side first |

## Locked sources

- Live brief, register (sheet modified 2026-10-01T12:31Z), stage standard, moodbook guide, road-plans
  canon v002, and the DC-R02 v001 HANDOFF (CONTEXT_ACK.json).
- Moodbook PDF 11YkCsfarp_oZ-ylqn0sN3ahHHr-G5QNr, pp.10–12 (text). Palette charcoal #131D1B,
  olive #667363, walnut #6B4734, tungsten #C49D63, cold paper #DFDFD4.
- EVIDENCE.md, E01–E14.

## Measurable deliverable (v001)

`SM_F02_SenateOfficeBuilding.glb` containing:

- `SM_F02_SenateOfficeBuilding_LOD0/1/2`, plus `SM_F02_SOB_SiteGrade_LOD0` (optional sloped site
  apron and terrace), `UCX_` collision and `SOCKET_` empties.
- Real-world scale: about 143 × 110 m, about 29 m from C St grade to balustrade top.
- Real geometry: window openings with depth, frames, sash bars and glazing. 34 free-standing fluted
  Doric columns in a recessed loggia. Rusticated courses with real channel joints. Triglyph frieze,
  cornice and balustrade. Pilastrades and central pavilions on the secondary fronts. Corner rotunda
  entrance.
- Stable named material slots, world-scale UVs, generated portable PBR textures, and a seeded
  window-state atlas for the night read.
- Reproducible build: `python jobs/DC-F02/build.py`.

## Passes

1. **Evidence** — DONE 2026-10-02. Link-cited only (egress block); see EVIDENCE.md access limits.
2. **Build** — generator `build.py`, all dimensions in `PARAMS`.
3. **Verify** — qa_check, clay and textured renders, a street-level camera from Constitution Ave,
   self-review against E01–E05 and the moodbook pp.10–12, then a clean rebuild.
4. Package asset-v001, then the PR, then Drive Incoming Deliveries.

## Acceptance checks

- qa_check: 0 FAIL. Bounds within 15% of the PARAMS footprint.
- Renders show a readable colonnade of 34 columns, depth in every window, and no boxes standing in
  for facade detail.
- The Constitution front reads three storeys above grade and the C St front five (E02).
- Clean rebuild from an empty `out/` gives the same vertex counts.

## Dependencies

- DC-R02 (APPROVED) is the footprint, height and year authority. Its SOB card can't be reached from
  here, so `PARAMS` must be reconciled to it locally.
- DC-C19 (APPROVED classical orders) is a candidate swap for the column/pilaster order (proposal).
- DC-B01 owns placement. Nothing is placed in the map.

## Uncertainties (carry into HANDOFF)

- Exact footprint and wing depth; how the grade falls along the Delaware and First St sides.
- External form of the SW rotunda corner (chamfer vs. curved, how many columns).
- Column height, intercolumniation and loggia depth. "Double colonnade" in E02 may mean a second,
  inner column row; v001 builds one row in front of a recessed wall.
- Roof and attic state in 1963. Window sash pattern.

## Status log

- 2026-10-02 11:15Z: claimed. Pass 1 evidence written (link-cited).
- 2026-10-02: Pass 2 build started.
