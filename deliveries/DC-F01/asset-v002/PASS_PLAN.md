# DC-F01 — Federal background building assemblies — PASS PLAN

Claimant: claude-cloud-agent · Lane: AGENTS · Set: DC-EXT1 Exterior Standard · Priority P1 · Kind: PCG assembly
Request revision: WASHINGTON-2026-09-22-v001 + Road Plan 05 integration addendum (doc modified 2026-09-25T10:29Z, text sha256 3c7747bd…1bcb)
Brief WASHINGTON-2026-09-22-v001 · Stage standard WASHINGTON-2026-09-22-v001 · Road plans canon WASHINGTON-ROADPLANS-v002 (2026-09-30)
Claimed 2026-10-02T10:30Z — Drive folder `DC-F01 — claude-cloud-agent` (1hgbMAOhZ10dSx2hVuvX77L9x7wBwlE5f), CLAIM.json 1WLLiZbaP2XxED8WP4e-rD1_0xMeuX42x
Work branch `claude/adoring-pasteur-25ccu0`; delivery branch pattern `asset/DC-F01-v###`.

Status (2026-10-03, scheduled run): **asset-v002 DELIVERED for Matt's review (not approved): Cannon corrected against
Matt's HABS photo (ref 03); Annex and Folger byte-identical to v001.** `deliveries/DC-F01/asset-v002`, branch
`asset/DC-F01-v002` + PR, Drive `EXT1 / Incoming Deliveries / DC-F01 — asset — v002`. See Pass log 10.

Earlier status (2026-10-02): **Pass 1 DONE · Pass 2 DONE · Pass 3 DONE (incl. the Folger photo comparison by the second, scheduled run) · v001 DELIVERED for Matt's review (not approved)**: `deliveries/DC-F01/asset-v001`, branch `asset/DC-F01-v001` + PR, Drive `EXT1 / Incoming Deliveries / DC-F01 — asset — v001`. Two sessions worked this claim on the same branch; the first session packaged v001.

| Pass | Result |
|---|---|
| 1 Evidence | EVIDENCE.md + research/ fact sheets (WebSearch text). Second run: the Drive starter photos (Folger 2025, Adams stair 2017) and the moodbook pp. 10–12 images were inspected via the Drive connector. Outside archives are still blocked, so there is no 1963-dated photo |
| 2 Build | build.py → 3 GLBs (LOD0-2, UCX, sockets, PBR textures); ~50 s full rebuild |
| 3 Verify | qa_check 20/20 on all three; per-shell orientation audit 0 inward-wound shells on all 9 LOD meshes; exposed-coplanar gate PASS on all 9 (`out/coplanar_report.txt`); clean rebuild byte-identical (32 files: GLBs, textures, reports); clay/textured/street/night/pass/LOD renders inspected; fixes applied (see Pass log) |

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
| **v002** | **Cannon correction pass** against HABS ref 03 (Matt's photo, 2026-10-03): the five v001 errors in PHOTO_FINDINGS.md | evidence arrived that v001 was wrong; fixing a delivered asset comes before new scope |
| v003 | U.S. Courthouse (C4/C5) + Post Office Department + IRS (C2–C4) | needs C18 (federal limestone bay, not yet approved) and C20 (red tile roof, v005 APPROVED per Drive) for honest Federal Triangle vocabulary |
| (dropped) | SOB / NSOB: DECISIONS row 4, F02 keeps both | Road Plans canon v002 assigns SOB/NSOB to DC-F02; request text lists them under F01 — **ownership conflict raised, not built**. Update 2026-10-02: DC-F02 (another claude-cloud-agent session) delivered the SOB as F02 asset-v001 and plans the NSOB as its v002 → recommend F01 drops v003 |

## Locked sources (filled in during Pass 1 — see EVIDENCE.md)

- Drive: References/DC-F01 starter photos `01_Exterior_view_Folger_Shakespeare_Library_June_2025` (Commons, CC BY-SA 4.0, 2025-06-03) and `02_Adams_Building_Exterior_Stairs` (US Capitol, public domain, 2017-01-03). First run: the images could not be opened (the connector returned no image data, and egress blocks Wikimedia). Second run: both were inspected through the Drive connector and copied to `refs/` (`references/SOURCES.md`); ref 01 drove the Folger corrections in Pass log 8.
- DC-R02 v001 (APPROVED) is the footprint/height authority, but its data package is on Matt's PC only; v001 uses published dimensions and must be re-snapped to the R02 evidence cards before placement.
- DC-C19 v004 (APPROVED): order vocabulary and interface for the Cannon colonnade (meshes not reused — see DEPENDENCY_LOCK.json).
- Moodbook pp. 10–12: object logic, material separation, palette relationships, staged review evidence (read as text in the first run; page images inspected in the second run).

## Measurable deliverable (v001)

Three GLBs in `out/`, Blender metres (UE glTF import → cm), Z-up source / glTF Y-up:

- `SM_F01_LOCAnnex.glb`, `SM_F01_Folger.glb`, `SM_F01_Cannon.glb`, each containing
  - `<name>_LOD0` (full facade articulation: real recessed window openings with frames/glazing, entrances, cornices, columns, steps), `<name>_LOD1` (openings kept, small ornament dropped), `<name>_LOD2` (massing + inset glazing, no reveals);
  - `UCX_<name>_NN` convex collision per mass; `SOCKET_*` empties (entrances, lamps, typed kit swap slots);
  - stable material slots `M_F01_*` with generated portable PBR textures (base colour, roughness, normal);
  - pivot at footprint centre, grade level; +X east, +Y north (map-aligned).
- (A planned `SM_F01_C10_ReviewLayout.glb` was dropped from v001. Relative placement belongs to DC-R02/DC-B01, so each building was reviewed on its own.)
- Renders: clay + textured front/profile/rear/¾ per building (tools/render_views.py), plus street-level review views, a night lit-window view, and base-colour/roughness/normal passes (moodbook p12).

## Passes

1. **Evidence** — EVIDENCE.md per building: dated sources with URL/archive ID, rights, what each supports, 1963 vs later changes, APPROXIMATE/FICTIONALISED labels; evidence card per building (footprint, height, storeys, bays, materials). *(done; photo inspection blocked, see EVIDENCE.md)*
2. **Build** — `python jobs/DC-F01/build.py` rebuilds everything from scratch (geometry, textures, GLBs, layout).
3. **Verify** — `tools/qa_check.py` on every GLB (fix every FAIL); per-shell orientation audit and `run_coplanar.sh` (visible z-fighting) on every LOD; clay + textured renders; harsh comparison against evidence and moodbook; iterate; clean rebuild from empty `out/`.
4. **Deliver** — `deliveries/DC-F01/asset-v001/`, `package_delivery.py`, branch `asset/DC-F01-v001` + PR, Drive `Incoming Deliveries/DC-F01 — asset — v001`.

## Acceptance checks

- qa_check.py: all PASS for all GLBs (bounds, ground contact, UVs, materials, no degenerate faces, outward normals, LOD1 present, UCX present, transforms applied).
- Every closed shell wound outward (build.py `orientation_audit`, reported as `inward_wound_shells` in build_report.json): 0 on every LOD. qa_check's signed-volume test only checks the whole-LOD sum, which can hide inverted parts.
- No coincident same-direction faces a viewer can see (`coplanar_check.py` via `run_coplanar.sh`; the gate fails above 0.05 m² visible per LOD) — these z-fight in Unreal and render as black bands in Cycles.
- Materials single-sided (glTF `doubleSided: false`).
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

## Pass log (what changed after each review)

1. Folger first build: z-fighting risks at end-section/pilaster junctions and corners found by code review → corner rule + mitred sweeps; LOD2 details moved proud of the core (were hidden).
2. Folger review: blocky "robot" relief stand-ins rejected → smooth domed low-relief figure forms; alternating tall/short ashlar courses (S4 wording); larger inscriptions; per-view raking review light (north facades get no sun in November).
3. Annex review: read as a generic office block → pavilions 0.9 m proud, deep sunk strips, darker statuary bronze, owl stand-ins moved onto the stair cheek walls (were buried), one figure panel per door leaf (six Lawrie figures per three-pair entrance), then **bronze spandrels** (SAH contrasts "window bays" with "marble-clad" piers) and taller windows → vertical bays now read.
4. Cannon review: dense attic window grid looked modern → one attic window per bay below; geometry budget 417k → 226k LOD0 tris (two-segment flutes, turned balusters only on visible fronts, glass-only court windows, lighter LOD1).
5. Pass-3 render review: a black vertical band at the Cannon's SE base corner. Cause: the right-angle corner flags were shifted by one edge. SE was treated as obtuse, adding an overlapping wedge; the N/chamfer corner was treated as a right angle, so its slab stopped short. Fixed (`right = [True, True, False, False, False]`); SE and NW corners re-rendered clean, and the Cannon standard and street views were re-rendered from the fixed GLB.
6. Pass-3 render review, second round: black bands along the Annex parapets (coping and attic coping overlapping the slab tops), Cannon window openings sitting 0.15–0.3 m off their frames on the oblique fronts (inset slab polygons slide their vertices along the edges; openings now shifted into each slab's own frame), and a Cannon cornice strip overlapping the entablature ring (profiles now start at the core face). All fixed in the generator.
7. Automated geometry gates, because eyeballing renders kept missing defects:
   - **Inside-out boxes (serious).** `coplanar_check.py` showed glass panes coincident with walls. The cause: `lbox`, the facade-frame box used for most detail on all three buildings, wound every face inward, because the facade frame is left-handed and the face list was mirrored twice. Cycles shades back faces, so renders never showed it. The GLBs only looked right because every material was exported double-sided. Fixed `lbox`; added a per-shell orientation audit to build.py (0 inward shells on every LOD); materials now export single-sided.
   - **The checker itself.** It ray-tests each coincident same-direction overlap from just off the face, with glass treated as transparent and a terrain plane, so it reports only what a viewer can see. Across the three buildings, visible overlaps fell from ~1,620 m² before the winding fix to 0.004 m².
   - **Fixes it found:** Folger window sills (top coplanar with the opening floor), stoops (a zero-height third step), relief frames (buried in the reveal, now lining the sunk field), grille and door glazing-bar crossings, and moulding end caps. Annex LOD2 pavilion corners (corner rule was off at LOD2, so 11 m² faces z-fought at distance). Cannon LOD2 cornice top coplanar with the core ring top. Cannon entrance-stair top tread coplanar with the plinth. Mullion and transom crossings on all three buildings.
   - **Left as is:** two same-material slivers (15 cm² and 12 cm²) at the Cannon's obtuse SW corner, where full-length slabs meet. Both are below the gate threshold.
8. **Folger photo comparison (second run, 2026-10-02; scheduled routine session, merged into this branch).** The Drive connector now returns image data, so starter photo ref 01 (Commons 2025, NE corner) was inspected. Review camera `photo01_ne` was added to match it, and heights were measured along vertical lines on the facade plane. Five corrections followed:
   - Windows were 1.2 m too tall: glass head 10.42 → 9.25 m, incised frieze 10.88–11.72 → 9.85–10.75 m.
   - Each window now sits in a 2.4 m sunk field running up to the frieze, between 1.4 m eight-flute pilasters (were 0.86 m, with broad plain ashlar between them).
   - Grilles are now a rectilinear interlocking-rectangle fret. The chevron heads were wrong.
   - The end entrances are now a tall sunk panel with the mask just above a 4.5 m door, fluted strips each side, and a projecting canopy whose top meets the frieze, with a lantern.
   - The inscriptions moved from over the end doors to the attic over the window row. Johnson is legible over the east half, so the run 1 positions had the two quotes swapped.

   Gates were re-run: qa 20/20, 0 inward shells, coplanar PASS (two new recess-edge overlaps found and fixed), clean rebuild byte-identical.

9. Final render review of the LOD2 meshes (first session, after integrating 8). Two identity cues were missing at distance:
   - **Annex.** The LOD2 mesh showed punched windows on white marble, the "generic office block" read rejected in log 3. It now carries one bronze card per vertically linked bay, with the glass proud of it.
   - **Cannon.** LOD2 had no loggia, and its columns stood 0.6 m in front of the facade instead of 0.85 m inside it, so they would jump 1.45 m at the LOD switch. The LOD2 mass now has the loggia notched out between the pavilions, with the columns and loggia windows at their LOD0 positions.
   - LOD0, LOD1 and collision are byte-for-byte unchanged (per-mesh buffer hashes). The full rebuild is still byte-identical, and all gates still pass.

10. **asset-v002: Cannon corrected against HABS ref 03 (scheduled run, 2026-10-03).** Matt supplied the HABS DC-2 colour view of
    the NW corner (1976). Matched camera `photo03_nw` (level, rising front); side-by-side `renders/review/CMP_ref03_vs_photo03_nw.png`.
    `cannon_bays` now returns a facade composition per edge, and the generator was rewritten around it:
    - **NW chamfer:** a full-height recess with two fluted columns in antis, a 3.4 m arched window with archivolt and keystone, a
      balustraded balcony on two consoles, plain piers. Door moved up to the terrace (sill 3.2 m), bronze pair + fanlight.
    - **Corner pavilions (14.2 m on each street):** pilaster, tall pedimented window with balustered apron, an antis bay (two
      columns, 2.4 m arched window, balcony, consoles), second pedimented window.
    - **Street terrace** on Independence Ave, the corner and New Jersey Ave: solid wall (0–2.2 m) and panelled parapet with coping
      (to 3.35 m) in front of a 2.6 m basement areaway; two-flight corner stair (11 + 6 risers, cheek blocks); a straight 18-riser
      side stair with sloped cheeks to a new base door on Independence Ave; end returns at NE and SW.
    - **Single giant pilasters** everywhere (17 bays on New Jersey Ave between the corner and SW pavilions; ~5 m bays on First St and
      C St); a small cornice over each 2nd-floor window.
    - **Colonnade:** 34 single, evenly spaced columns (2.83 m c/c) with a respond and a loggia window in each intercolumniation.
      PROBABLE, not photo-confirmed (tree in ref 03).
    - **Skyline:** solid blocking course with dies over pilasters and every second column; balusters only in the two chamfer panels;
      attic set back 7.0 m and lowered (roof 25.5 m, coping 25.9 m) so nothing shows above the parapet from `photo03_nw`, as in ref 03.
    - **LOD2:** loggia and all antis recesses notched out of the middle band, so columns keep their LOD0 positions; terrace and
      stairs kept at every LOD (they are the street-level read).
    - Collision: 5 wing hulls + 3 terrace hulls + 2 stair hulls (10 UCX). New socket `SOCKET_Entrance_Independence_W`; the main
      entrance socket keeps its v001 name and moves to the door sill (z 3.2 m).
    - Gates: qa 20/20 ×3; 0 inward shells on all 9 LODs; coplanar PASS (Cannon LOD1 0.0012 m² SW-corner sliver, all else 0);
      clean rebuild byte-identical (32 files); Annex and Folger GLBs hash-identical to v001. Cannon LOD0 225,852 → 218,240 tris.

## Uncertainties (running list)

- Folger north facade checked against a 2025 photo; Cannon NW corner, New Jersey Ave and skyline checked against HABS ref 03 (1976). The Annex is still unchecked (ref 04 is 530 px). Outside archives are still blocked here (re-checked 2026-10-03).
- Cannon colonnade pairing: single built in v002 (PROBABLE); confirm with the HABS colonnade close-up. Attic height/setback: needs an aerial. First St / C St fronts and the terrace ends: not photographed.
- Folger east-end door: shown in the 2025 photo but not modelled, because SAH says the east end is a blank wall. Needs a pre-2019 photo.
- R02 footprints not available here → footprint outlines APPROXIMATE.
- 1930s federal/institutional sculpture (Lee Lawrie doors on the Annex, John Gregory reliefs on the Folger): rights unconfirmed → accurate massing with labelled simplified stand-ins (stage standard §7).
- SOB/NSOB F01-vs-F02 ownership (see version plan); F02 has now built the SOB.
- Cannon colonnade: v002 now agrees with F02's single-column SOB (HANDOFF UNIFICATION PROPOSAL 0).

## Decisions after delivery (2026-10-02)
Matt delegated open questions 1–5 and said yes to a separate interactive claimant name. See
`DECISIONS.md`: Cannon stays coupled, Annex spandrels stay bronze, Folger east door stays
unmodelled, F02 owns SOB/NSOB, R02 re-snap is deferred. v001 geometry is unchanged.
