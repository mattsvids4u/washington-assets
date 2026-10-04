# DC-V01 — MPD patrol car 1963 — PASS PLAN

Claimant: claude-cloud-agent · claimed 2026-10-02T10:18Z · set DC-EXT1 (AGENTS lane) · P2
Brief WASHINGTON-2026-09-22-v001 · stage standard v001 · road-plans canon v002 · request doc modified 2026-09-29 (vehicle benchmark addendum, Matt 2026-09-26)

## Problem
Build the 1963 Washington Metropolitan Police (MPD) patrol sedan as the **whole vehicle**: a
convincing period full-size four-door sedan (real body curvature, genuine window apertures with
visible glazing, real wheel openings, pillars, interior silhouette, grille, lamps, bumpers), with a
city-neutral base body plus a detachable MPD livery/equipment layer, structured for Unreal 5.8
vehicle use (separate wheels with hub pivots, steering pivots, separate doors/hood/trunk with hinge
pivots, driver/steering sockets, simple collision, LOD0–LOD2, stable material slots).
This job also establishes the vehicle production benchmark (Matt, 2026-09-26) and the shared base
that DALLAS V07 (Dallas police sedan, a 1963 Ford Galaxie — Tippit's squad car) and DC-V02 (taxi
rebuild) need. The earlier worker proxies were rejected for box-like bodies, occluded glass and
missing openings; that bar is the acceptance gate here.

## Locked sources (see EVIDENCE.md)
- SAVE_JFK_Visual_Benchmark_Moodbook.pdf (Drive 11YkCsfarp_oZ-ylqn0sN3ahHHr-G5QNr), all 12 pages inspected as images; pp. 10–12 relied on.
- Project reference photo `01_MPD_patrol_sedan_rooftop_lettering_and_light_mpd32.jpg` (1962 MPD fleet, elevated view, dcmetropolicecollector.com; rights not stated → inspected, not redistributed).
- MPD FY1967 annual report (new colour scheme designed FY1967 → 1962 scheme is the correct 1963 default).
- 1963 full-size Ford (Galaxie / Ford 300) published dimensions: wheelbase 119 in, length 209–209.9 in, width 79.9 in, height 55.5 in, tread 61/60 in, tyres 7.50-14 (OD ≈ 28.4 in).
- DALLAS V07 identity: Dallas PD 1963 squad cars were 1963 Ford Galaxies (Tippit car #10) → shared base = 1963 Ford-pattern full-size sedan.

## Measurable deliverable
`jobs/DC-V01/out/SM_V01_PatrolSedan_MPDC.glb` (MPD variant, full hierarchy) and
`SM_V01_Sedan_Base_Neutral.glb` (city-neutral base), each rebuilt from scratch by
`python jobs/DC-V01/build.py`, passing `tools/qa_check.py`, with clay + textured renders that read
as a 1962–63 full-size sedan at street distance: overall 533 × 203 × 141 cm (±3 %), wheelbase
302 cm, tread 155/152 cm, four doors, six real window apertures with glass, four real wheel
openings with wheels inside them, dual headlights, grille, bumpers, taillights, interior visible
through the glass, MP/DC roof letters, single red beacon, POLICE trunk marking, door seal.

## Passes
1. **Evidence** — done 2026-10-02 (EVIDENCE.md). Identity gate: exact MPD make/model for 1963 is
   NOT proven; body modelled as a 1963 Ford-pattern full-size sedan (APPROXIMATE, justified by the
   DALLAS V07 shared-base relationship and the in-map Galaxie-derived civilian cars).
2. **Build** — `build.py` (bpy 4.5): lofted body skin from parametric cross-sections → subdivision →
   solidified shell → boolean window apertures, wheel wells, panel gaps → doors/hood/trunk split into
   separate hinged objects → glazing, chrome, lamps, grille, bumpers, wheels (tyre/whitewall/rim/cap),
   interior (floor, dash, column, wheel, benches, door cards), MPD layer (roof-ID decal, beacon,
   trunk POLICE decal, door seal decal, antenna), decals via shrinkwrap, procedural textures (PIL),
   LOD1/LOD2 (decimate), UCX collision, sockets as empties; export GLB (metres; UE imports as cm).
3. **Verify** — qa_check on every GLB; clay + textured renders (front/profile/rear/¾) compared to
   the reference photo and moodbook; harsh self-review; clean rebuild from empty `out/`; package.
   Unreal import/readback, wheel/steer/door motion: NOT_RUN (no Unreal in the cloud sandbox).

## Acceptance checks
- qa_check: 0 FAIL on each GLB (bounds, ground contact, UVs, materials, normals, LODs, UCX).
- Dimensions within ±3 % of 533 × 203 × 141 cm; wheelbase 302 cm; tyre OD 71 cm.
- Clay renders: silhouette reads as the sedan (roof arc, belt line, fender/door surfaces, real
  apertures, wheels sitting inside arches, no box-like forms). Textured: glass visibly transparent
  with interior behind it; chrome/paint/rubber/glass separate under neutral light.
- Hierarchy: BODY, DOOR_FL/FR/RL/RR (+ glass children), HOOD, TRUNK, WHEEL_FL/FR/RL/RR under
  STEER_FL/FR pivots (front), SOCKET_DRIVER, SOCKET_STEERING, SOCKET_BEACON, SOCKET_ANTENNA,
  SOCKET_PLATE_R, all police parts prefixed POLICE_ and detachable.
- Rebuild from clean `out/` reproduces byte-identical GLBs (deterministic generator).

## Dependencies
- None blocking. DALLAS V07 is FUTURE_UNASSIGNED (no parent mesh) → this build is proposed as the
  shared base (HANDOFF.md, UNIFICATION PROPOSALS). DC-V02 can derive from the neutral base.

## Uncertainties (labelled in EVIDENCE.md)
- Make/model/year of the 1963 MPD scout cars (APPROXIMATE: Ford-pattern 1963 full-size sedan).
- Exact roof-letter typeface/dimensions, seal artwork, POLICE lettering size (APPROXIMATE).
- Beacon model (Federal Sign & Signal Beacon Ray 17-class, ~28 cm tall: APPROXIMATE), antenna,
  siren, spotlight fit (APPROXIMATE / omitted where unevidenced).
- Interior colour/trim (APPROXIMATE), licence plate (FICTIONALISED).

## Status log
- 2026-10-02 10:18Z claimed; Pass 1 evidence complete.
- 2026-10-02 10:30–11:05Z Pass 2 build: first boolean pipeline abandoned (bpy exact booleans
  flaky on the shell → empty meshes); replaced by deterministic plane-bisect cutting on the open
  skin + per-piece solidify. Three shape iterations from clay renders (slab sides → shoulder crease
  + rocker tuck + fender tips; pillars lost → greenhouse re-laid with A/B/C pillars, backlight
  moved aft; door glass parenting, decal orientation, plate text, glyph rotation fixed).
- 2026-10-02 11:10Z Pass 3 verify: QA 445/445 + 375/375, clean rebuild byte-identical, clay +
  textured + top + posed renders reviewed against E1 and moodbook p.10–12. Delivered as asset-v001.
- Next pass (after Matt's review): identity correction if the 1963 make is established; body
  side sculpting (side spear / fender character line), engine-bay and trunk dressing, siren and
  spotlight, DPD livery layer for V07, lit beacon state as a material switch in UE.
