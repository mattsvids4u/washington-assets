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
| asset-v001 | Senate Office Building (C7), text-evidence build | On the north-loop escort route (Constitution Ave), not in the map, best-documented parti, and no F01/H overlap |
| **asset-v002** | **Senate Office Building, photo-matched revision** | Matt supplied photos (E10, E11, E15–E17). Corner pavilion and base windows corrected |
| **asset-v003** | **Senate Office Building, detail and accuracy pass** | Close reading of E11/E15/E16: plain chamfer piers, corner returns, tall narrow base arches, Delaware centre pavilion |
| asset-v004 | New Senate Office Building (C7, 1958) | Same street face; pairs with the SOB. E17 is a lead (Alamy, so a permitted photo is needed) |
| asset-v005 | National Theatre + National Press Building (C3/C4) | Needs R02 C3/C4 frontage fields (R02 v002 owed) |
| asset-v006+ | C1/C2 uplift revisions (Willard, Hotel Washington, District Bldg, Riggs, American Security) | Need the existing in-map meshes, which can't be reached from the cloud. Local / Unreal side first |

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
- 2026-10-02: Pass 2 build done. `build.py` builds LOD0/1/2, the site helper, UCX and sockets.
- 2026-10-02: Pass 3 verify. Two defects found in self-review: coplanar roof slabs and coplanar
  corner end caps rendered black. Fixed with non-overlapping slabs and mm offsets on the W/E/chamfer
  frames. Stone albedo lowered; rustication channels deepened. QA 26/26. Clean rebuild twice:
  byte-identical. Clay, textured and street renders reviewed.
- 2026-10-02: asset-v001 packaged (deliveries/DC-F02/asset-v001).
- **Next pass (v001 review loop):** photo match once Matt adds SOB photos and/or the R02 card to
  References/DC-F02. Then the rotunda corner form, column spacing and footprint reconciliation.
  After that, asset-v002, the New Senate Office Building.
- 2026-10-02: **Pass 4 (photo match).** Matt supplied 5 photos (EVIDENCE.md "Inspected photographs").
  The v001 corner was wrong (4 columns / 3 doors). It was rebuilt per E11/E15/E16: 2 columns before a
  tall arched window, solid piers with framed windows and cartouches, one arched doorway over a
  projecting stair, raised attic, flag socket. Base windows are now round-arched with stone
  spandrels. QA 26/26; clean rebuild byte-identical; photo-matched camera added.
  Packaged as asset-v002 (v001 untouched).
- **Next:** Matt reviews v002 against E11. Then reconcile PARAMS with the R02 card when available,
  and check the C St front against E12. Then asset-v003, the New SOB.
- 2026-10-02: **Pass 5 (detail and accuracy, per Matt).** Enlarged E11 crops re-read against E15/E16
  (EVIDENCE.md "Pass 5 close reading"). Fixed:
  - Chamfer piers made plain; the framed windows and cartouches moved to the returns.
  - Corner returns built on both fronts (pier / columns in antis / pier).
  - Columns in antis now stand in the pier plane, with a flush architrave.
  - Tall arched windows given a small-pane grid and dark glazing.
  - Pediments on the framed windows.
  - Base arches tall and narrow (1.2 × 4.1 m).
  - Console brackets at the door; podium blocks across the chamfer; attic raise lowered to 0.5 m.
  - Delaware centre pavilion with columns in antis (APPROXIMATE).
  - Slope-exposed basement windows under the pavilions.
  Packaged as asset-v003; the New SOB moves to asset-v004.
- 2026-10-03 (scheduled run, claimant claude-cloud-agent): **asset-v004 Pass 1 (New SOB): text evidence
  only.** All four claude-cloud-agent claims (X14, V01, F01, F02) are delivered and waiting on Matt; no
  Reviews entry exists for any of them. F02 v004 (the New SOB) is the only pass that is planned and not
  waiting on a review, so this run resumed it. Result: EVIDENCE.md E23–E28 (WebSearch text). **Build
  NOT started.** The request requires "expand the exact-photo pack before building each added anchor;
  never genericise a named silhouette". The network policy blocks every image and archive host
  (loc.gov, wikimedia, aoc.gov, senate.gov), so no NSOB photo can be inspected from this sandbox.
  **Blocked on:** an NSOB photo pack (the list is in EVIDENCE.md) and/or an allowed-domains change for
  loc.gov / upload.wikimedia.org / aoc.gov. Once photos are available, v004 = `SM_F02_NewSenateOfficeBuilding.glb`
  in a new build module that shares MB/material/texture helpers with build.py.
