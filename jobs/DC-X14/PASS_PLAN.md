# DC-X14 — Staff offices and Legislative Reference Service room — PASS PLAN

Claimant: claude-cloud-agent · Lane: AGENTS · Set: DC-INT1 Interior Standard · Priority P2
Request revision: WASHINGTON-2026-09-22-v001 (+ Road Plan 04 integration addendum, doc modified 2026-09-25)
Brief revision: WASHINGTON-2026-09-22-v001 · Stage standard: WASHINGTON-2026-09-22-v001 · Road plans canon: v002 (2026-09-30)
Claimed 2026-10-02T09:38Z (Drive folder `DC-X14 — claude-cloud-agent`, id 1k-ktTUY1Yvj3nxDKM6ZYCOuzWSeOkiom)

## Problem

Modular office-room kit for Library of Congress staff offices and the Legislative Reference
Service (LRS; renamed CRS in 1970) as they stood in Oct–Nov 1963, for eavesdrop gameplay.
Daytime institutional back-of-house identity; must not become a gala reception room (Road
Plan 04 addendum). Furniture is DC-I09's (sockets only here). ITS ALIVE: WD + plaster.

## Locked sources (Pass 1)

- 1963 identity: LRS occupied the Main Building (today's Jefferson) and the Annex (today's
  Adams). 1967 memoir (LCIB May 1997, Helen Dalrymple): LRS units sat in "rabbit warrens of
  temporary partitioned offices in the northwest and southwest curtains and pavilions, the
  upper level of the Great Hall, and around the upper galleries of the Main Reading Room ...
  dropped ceilings, temporary light fixtures and gray partitions". GGR Division in the east
  corridor of the first floor. See EVIDENCE.md for every record and its date/rights.
- Photo record: "Employees of the Legislative Reference Service at their desks", Sept 1953,
  LoC Photoduplication Service, loc.gov/item/2009631159 (150 px thumbnail inspected via Matt's
  Drive upload; full resolution still wanted).
- Moodbook pages 10–12 (text read via Drive connector; image pages not viewable in sandbox).

## Measurable deliverable

A kit of modular GLBs, metres in Blender (UE 5.8 imports glTF as cm), each with LOD0–LOD2,
UCX collision, UVs, stable named material slots, named sockets:

Layer A — 1897 Main Building office shell (ARCH):
- `X14_ARCH_Wall_Plain_300`, `X14_ARCH_Wall_Window_300` (round-arched deep reveal, double-hung sash, glazing, sill, radiator),
  `X14_ARCH_Wall_Door_300` (oak panelled door + glazed transom, door pivot), `X14_ARCH_Corner`,
  `X14_ARCH_Floor_300` (oak strip; linoleum slot), `X14_ARCH_Ceiling_300` (plaster, cove, pendant socket).
Layer B — 1950s/60s temporary partition overlay (PART):
- `X14_PART_Panel_Solid_120`, `X14_PART_Panel_Glazed_120`, `X14_PART_Door_090`, `X14_PART_Post`,
  `X14_PART_DropCeiling_120`, `X14_PART_Fluorescent_120`, `X14_PART_Sign_Door` (1963 name "LEGISLATIVE REFERENCE SERVICE").
Assembly: `X14_DEMO_LRS_Room` — a 9 × 6 m division room assembled from the kit with I09 furniture sockets.

## Passes

1. Evidence — **DONE 2026-10-02.** Web-search leads first; Matt then supplied the FY1963 Annual
   Report, the LCIB 1997 memoir text and photos, HABS DC-351 frames, the first-floor plan and
   the 1953 LRS photo thumbnail (EVIDENCE.md E12–E18). Naming gate cleared; dimensions gate closed by Matt's direction (set dressing, see pass 6).
2. Build — **DONE 2026-10-02.** `build.py` v1: 16 modules + demo. Iterations: (a) exact boolean
   failed on multi-shell walls → cut the bare slab, add trims after; (b) degenerate faces from a
   duplicated cornice profile point → cleaned; (c) sign text used the 1967 division name → 1963
   "History and Government Division"; (d) coplanar post/cap faces z-fought → posts inset;
   (e) sign letters faced into the wall → rotated; (f) 0.6 m filler panel added so the 9 m demo
   run closes exactly; (g) corner module reduced to a notch filler (wall trims mitre by union).
3. Verify — **DONE 2026-10-02.** QA: 17/17 GLBs PASS. Renders: 128 module orbit images +
   9 interior views, every one looked at; six defects found and fixed (list in HANDOFF.md render
   review), then re-rendered. Clean rebuild: `out/` deleted and rebuilt, QA PASS, all 17 GLBs and
   22 textures byte-identical to the packaged set.
4. Deliver — **DONE 2026-10-02.** `deliveries/DC-X14/asset-v001/` (193 files, DELIVERY_MANIFEST +
   SHA256SUMS), branches `claude/eager-cray-vpg2j3` (PR #1) and `asset/DC-X14-v001`, Drive
   Incoming Deliveries folder `DC-X14 — asset — v001` (12zNk-c-3YVCSfuQgys4T8SxVHwQvpU5L) with
   the text files, RENDER_INDEX and PAYLOAD_LINK (GLBs/PNGs exceed the connector's upload limit).
   Matt reviewed the same day (see HANDOFF review notes).
5. v002 (same day, from Matt's review + new evidence E19–E22) — **DONE 2026-10-02.** Added dark-wood
   panelled partitions (`X14_PART_Panel_Wood_090/_060`, `X14_PART_Door_Wood_090`), torchère floor
   lamp, wall sconce, painted coffered beam ceiling, and a second demo room `X14_DEMO_LRS_Room_1953`
   (wood partitions, torchères, sconces, pendants, coffered ceiling, linoleum; no drop ceiling). v001
   modules are byte-identical in v002. Delivered as `deliveries/DC-X14/asset-v002/` (complete kit).

## Acceptance checks

- Every GLB passes `tools/qa_check.py` (bounds, ground contact, UVs, materials, normals, LODs, UCX).
- Module seams: 3.000 m wall modules butt with no gap; partition panels 1.200 m; posts fill corners.
- Renders read as a 1890s federal office with 1960s partition overlay, not a box: real window reveal and sash, door panels, mouldings, partition framing, ceiling grid and fixtures.
- Clean rebuild from empty `out/` reproduces the files.

## Dependencies

- DC-I09 Office furniture set v005 (Drive `DC-I09 — asset — v005`, 1MUveU1GrHxPHtkQB6FiVWbJmhCVJTQG3; ZIP 1ajFUC-Ivz_gn2ZFsKyK1X3WM9w9NQTfX, 6,707,841 bytes; register: DELIVERED / VERIFIED / approval PENDING). Locked by ID in DEPENDENCY_LOCK.json; sockets only, no furniture built here.
- DC-X15 may route staff access through these rooms; no gala dressing.

## Uncertainties

- Sandbox egress blocks loc.gov, tile.loc.gov, Wikipedia/Commons, archive.org, HathiTrust. Matt
  supplied the key files by hand (EVIDENCE.md E12–E18); still missing: HABS DC-351 data pages and
  frames 22/23, the 1953 photo at full size, Annual Report Ch. V. Everything dimensional stays
  APPROXIMATE until those are compared.
- Exact 1963 room assignment of LRS divisions in the Main Building: PROBABLE (NW/SW curtains and
  pavilions, Great Hall upper level, first-floor east corridor) from a 1967 account; not a 1963 document.
- Partition colour, height and glazing pattern: gray steel kit APPROXIMATE (c. 2.13 m, clear uppers); wood kit from the 1953 photo (c. 1.9 m, solid, two flat panels per 0.9 m section) — proportions scaled by eye, APPROXIMATE ±10 %.
- Ceiling heights, window sizes, cornice profiles: APPROXIMATE (no HABS data pages reachable).
- Sign text uses the 1963 name "Legislative Reference Service" (historical signage rule); room numbers FICTIONALISED.

## Pass 6 — evidence gates closed (Matt, 2026-10-02)

Matt's direction in chat: "this is set dressing … just go for it". The outstanding archive
requests (HABS DC-351 data pages, Annual Report FY1963 Ch. V / App. XII, the five unsaved HABS
frames) are **waived**. The approximate dimensions in `build.py` stand as the delivered values;
no v003 is planned for dimension checks. Everything labelled APPROXIMATE stays labelled that way.
This is a scoping decision, not an approval: asset_user_approval remains PENDING.

## Pass 7 — asset-v003 full surfacing pass (Matt, 2026-10-03: "yep do a full pass. go for it.")

Trigger: Matt asked whether v002 was done; the honest review of the renders said no, because the
procedural oak read as wavy zebra stripes and the lamp shades were faceted. Changes (build.py):
1. New tileable oak grain (uneven ring spacing, gentle drift, open pores, slow tone) for trim,
   doors, partitions, mahogany variant and strip floor; new `T_X14_OakDark_BC` for the dark
   partitions (E19).
2. Grain-aligned UVs on every wood face (`orient_wood_uvs`): rails, baseboards and sash bars run
   horizontal, stiles, posts and panels vertical.
3. Smooth-shaded lathes at 48/24/12 segments for the pendant, torchère and sconce shades; all
   round cylinder sides smooth with hard cap edges.
4. Furniture socket fixes: file cabinets faced the wall (and collided with a torchère in the 1953
   room), the wall clock sat on the door leaf, and the typewriter was on the far edge of the desk.
5. Faint 2 m sheet seams in the linoleum (E19).
6. Preview-only DC-I09 stand-ins (`preview_dressing.py`, `render_interior.py --dress`) so the rooms
   can be judged dressed; never exported.
Acceptance: QA 24/24 PASS; clean rebuild byte-identical (24 GLBs + 24 textures); every render
reviewed. Delivered as `deliveries/DC-X14/asset-v003/`.

## Pass 8 — asset-v004: fit test with the real DC-I09 furniture (Matt, 2026-10-03: "find the already completed desk assets and try them")

- Found DC-I09 deliveries v002–v005 in Incoming Deliveries (DC-INT1 set). The v005 ZIP is too large for the
  Drive connector's transfer; v004 (2.2 MB) and v003 came through and decoded byte-exact.
- Placed the real I09 desk, filing cabinet, typewriter, rotary phone, desk lamp and wall clock on the X14
  sockets in both demo rooms (`render_interior.py --dress --i09 <meshes>`); chair, fan, papers and boxes stay
  as stand-ins because I09 has none.
- Fixes this exposed in X14 (demo rooms only): cabinet and clock socket orientation and the desk-top socket
  positions now follow the I09 INTERFACE_CONTRACT; the 1953 room's 156 ".001"-suffixed node names are gone.
- Findings for the I09 owner (not changed here): I09 GLBs lie on their backs in any glTF importer (Z-up data
  in a Y-up format), and the desk floats 2 cm.
- Acceptance: QA 24/24 PASS; clean rebuild byte-identical; 22 modules + textures byte-identical to v003;
  12 new furnished interior views reviewed. Delivered as `deliveries/DC-X14/asset-v004/`.


## Pass 9 — asset-v005: set dressing (Matt, 2026-10-03: "anything on the walls? plants in the corners? nothin???")

Problem: both demo rooms had bare walls and empty corners. Furniture is DC-I09's job, but nothing in
the kit covered the wall and floor dressing a 1963 government office would carry.
Deliverable: ten new `X14_DRESS_*` modules built like every other kit module (LOD0–2, UCX_, UVs,
stable `MI_X14_*` slots, base pivots), placed in both demo rooms:
- Walls: large framed print (oak frame, engraved river view), small framed photograph (metal frame,
  generic domed civic building), November 1963 wall calendar, 0.9 m cork bulletin board with typed memos.
- Floor: 0.9 m oak bookcase (five shelves of cloth-bound books; E19 shows bookcases between desk
  groups), rubber plant in terracotta pot, small pothos on each bookcase, oak coat tree with a felt
  fedora, U.S. flag (50 stars, correct since 4 July 1960) on an oak pole with a weighted base, olive
  steel wastebasket per cubicle.
Locked sources: E19 (1953 LRS photo: bookcases between desk groups), the moodbook palette. Everything else
is period-typical APPROXIMATE; picture subjects and the room layout are FICTIONALISED.
Acceptance: QA PASS on all 34 GLBs; the 22 v004 modules and 24 v004 textures byte-identical; clean
rebuild byte-identical; module orbits and every interior view looked at.
Defects found and fixed during the pass (before any delivery):
1. Wastebasket LOD0 lost its steel body: `bmesh.ops.create_icosphere` reallocates the bmesh elements,
   so the set-difference "new verts" trick returned every vertex and the body was retagged as paper and
   moved. Fixed by using the op's returned verts.
2. Bookcase: top-shelf books (up to 0.30 m) poked through the top; book height now capped by each
   shelf's clearance.
3. Rubber plant read as sparse bamboo: four stems, 0.24–0.32 m leaves at 6 cm spacing, darker glossy
   leaf material, petioles and rolled tip sheaths.
4. Fedora hung sideways off a hook; now seated on the finial.
5. Prints and calendar were mirrored when seen from the room (fit_uv u flipped on +Y faces).
6. First-draft print textures read as blobs: the photo is now a tonal render of a domed civic building
   with trees and lawn; the engraving is a hatched river view with plate mark and caption.
