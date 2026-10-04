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
2. **Build** — `build.py` (bpy 4.5). From v003: a structured body grid (stations × rows around a
   filleted section outline with C1 key curves) → wheel openings, pillar plane cuts, grille and lamp
   openings → openings, mouldings and panels selected on the grid → glass taken from the skin →
   solidified shell with panel gaps → doors/hood/trunk split into separate hinged objects → glazing, chrome, lamps, grille, bumpers, wheels (tyre/whitewall/rim/cap),
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
  spotlight fit (v004: modelled, APPROXIMATE), siren (omitted, socket only).
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
  v002 (Pass 4) delivered 2026-10-02 — see below.
- 2026-10-02 14:15–15:40Z **Pass 4 (asset-v002) — realism, fine bevelling, grounding** (Matt:
  "do another realism and geometry pass. fine beveling and grounding"):
  rolled 3.5 mm bevels on every body panel edge and aperture flange, 4 mm bevels on hard-surface
  props; tyres with three tread grooves, a 1 cm loaded deflection and a flat contact patch with
  sidewall bulge; underbody (exhaust, muffler, driveshaft, axle + differential, leaf springs, fuel
  tank, cross-member, control arms, front/rear valance pans) and a dark undercoat floor pan so the
  car reads grounded from kerb height; door armrests; slightly more convex door skins. Defects found
  by new close-up renders and fixed: radiator support poking through the hood lip (shipped unnoticed
  in v001's final GLB), floating rocker strip (v001 too), mirrored door-seal text, chrome-plug
  headlamps. Determinism regression (bevelled plate UVs) found and fixed; sliver-face cleanup added (meshes now
  exported pre-triangulated, QA 585/585 + 520/520); rocker strip wrap target extended to the door skins.
- 2026-10-03 05:00–06:40Z **Pass 5 (asset-v003) — shape and text** (Matt on v002: "still needs
  hella work. next pass. shape is wonky. text is wacked out."). Diagnosis from v002 renders:
  - ripples and lumps from the smoothstep key blending, plus a dented fender-tip push;
  - torn A-pillar and "horns" from flat-plane window cuts on a subdivided loft;
  - floating flat glass with spikes at the corners;
  - grey valance bricks;
  - mirrored and rotated roof letters, and a crowded seal.
  Rebuilt:
  - the body as a structured filleted-section grid with C1 curves;
  - openings and panels selected on the grid, plus pillar plane cuts;
  - glass taken from the skin, with straight chrome surrounds;
  - a flat front face with a full-width grille and lamps inside it;
  - U-shaped wheel openings and liners, a thinner shell and rounded whitewall tyres.
  Also:
  - roof text fixed and verified from the GLB UVs (D M / C P per E1), beacon and antenna moved to
    E1 positions, seal and plate text redrawn;
  - interior and underbody parts that clipped the wheels moved inboard (clash probe clean).
  Results: QA 645/645 + 580/580; clean rebuild byte-identical.
- 2026-10-04 00:30–01:40Z **Pass 6 (asset-v004) — body character, rear end, trim, A-pillar fix**
  (scheduled run; no new Matt feedback since v003, so this continues v003's next-pass list under his
  v002 direction "next pass. shape is wonky"). Harsh review of the v003 renders found:
  - plan view pulled in ~8 cm per side at nose and tail, so the ends read boat-like from the front and
    rear; E1 (re-inspected) shows a near-rectangular plan;
  - the rear bumper read as an 11 cm round pipe; tail lamps (16.6 cm) read as marker lights;
  - **torn-looking slivers along the A-pillar** (also present in v003): the 2–3 cm painted door-frame
    strip between the door edge and the chrome frame was shrunk and bevelled into a zig-zag;
  - no hood crease or hood emblem although E1 shows both; no spotlight.
  Changes:
  - plan taper cut to ~4–5 cm per side at nose and tail (x4–x9 keys); grille opening 158 → 168 cm wide,
    headlamp pairs moved out;
  - hood: narrow crown + steeper fall → central longitudinal crease (E1); small generic chrome hood
    emblem parented to HOOD (no brand artwork);
  - bumpers: 15 cm '63-pattern blade section (rolled top, curved face, lower lip), wrap tips thinning
    out, rounded guards; set 3.5 cm off the sheet metal so length over bumpers stays 546 cm (a first
    attempt reached 558 cm, outside ±3 %, and was pulled back);
  - tail lamps: 20.4 cm round lamps with deep chrome bezel and centre boss; the lower half-moon of each
    lens is the clear back-up lamp (separate back-up dots removed); rear moulding raised to clear the
    bezels; generic trunk-lock escutcheon;
  - A-pillar/C-pillar: the door's window-band edge now IS the chrome frame's outer edge
    (L_DOOR_F/R = L_TRIM_F/R), so the chrome frame meets the pillar cleanly; diagnosed with a
    per-object false-colour render;
  - POLICE_SPOTLIGHT (+ _LENS) on the driver A-pillar base: boss, swivel arm, 16 cm rounded bowl,
    bezel, lens (APPROXIMATE, period-typical; detachable; socket moved to its pivot);
  - lower body tucks in less at nose/tail (x8/x9).
  New close-up cameras `detail_spotlight`, `detail_tail_lamp` (tools/render_detail.py) and
  `report.py` (HIERARCHY.txt / MESH_STATS.txt from the exported GLB).
  Results: QA 675/675 (MPDC) + 595/595 (neutral); clean rebuild byte-identical (2 GLBs + 4 textures);
  217.3 × 546.1 × 190.3 cm over mirror/bumpers/antenna (body 203 × 141). Delivered as asset-v004.
- Next pass (after Matt's review): identity correction if the 1963 make is established; side
  character line / spear if Matt wants Galaxie-500 trim rather than fleet trim; siren (socket only);
  DPD livery layer for V07; lit beacon state as a material switch in UE.
