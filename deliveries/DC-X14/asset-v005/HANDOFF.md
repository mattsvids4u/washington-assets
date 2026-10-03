# DC-X14 — Staff offices and Legislative Reference Service room — HANDOFF (asset-v005 current; earlier sections kept as history, newest at the end)

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

See "Render review" at the end: every module orbit (clay + textured) and all nine interior
views were looked at; the defects found were fixed in the generator and re-rendered.

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

## Render review (every image in `renders/` was looked at; defects fixed before delivery)

Defects found and fixed during Pass 3 (all in `build.py`, all re-rendered from the final build):
1. Exact boolean on the multi-shell wall mesh returned the opening instead of the wall → cut the bare slab first, add mouldings after. Confirmed by signed volumes (window wall 5.75 m³, door wall 3.36 m³).
2. Duplicated cornice profile point → 4 zero-area faces (QA FAIL) → removed; QA PASS.
3. Coincident faces (post ends vs cap/channel ends, sash rails over stiles, door muntin over lock rail, grid bars at crossings) rendered as pure black squares because Cycles' shadow rays self-block on coplanar twins → all joinery now butts rather than overlaps; cover post is 60 mm so it shares no plane with the 50 mm panel posts.
4. Sign letters faced into the wall (mirrored from the room) → rotated to face +Y; 1967 division name replaced by the 1963 "History and Government Division".
5. Fluorescent reflector was a solid wedge with the tubes buried inside → thin open-bottom trough; tubes now visible and emissive (KHR_materials_emissive_strength 6 survives the GLB round trip).
6. Marble sill end flush with the exterior face → inset 10 mm.

What the final images show (module orbits, 960 px, 24 samples; interiors 1152 px, 32 samples):
- `X14_ARCH_Wall_Window_300` — reads as a deep-reveal arched window: stained oak two-light double-hung sash, arched transom with radial muntins, marble sill proud of the reveal, column radiator under it; picture rail stops at the reveal, cove cornice above. Exterior face is plaster (never seen in-game; granite belongs to DC-H04). Still APPROXIMATE: proportions, sash lights, radiator pattern.
- `X14_ARCH_Wall_Door_300` — four-panel oak door with raised fields, brass knob and hinges, glazed two-light transom, stepped architraves both faces, baseboard returning into the architrave. The leaf's wood grain (procedural stripes at 1 m tiling) reads a little like veneer plywood at close range — fine at gameplay distance; swap in a photographed oak albedo locally if it bothers.
- `X14_ARCH_Wall_Plain_300`, `Corner`, `Floor_300` (+ linoleum), `Ceiling_300` — correct, plain; floor strip joints read; corner is a notch filler by design (the inside mitre is formed by the two walls' trims).
- `X14_ARCH_Pendant_Lamp` — opal bowl on a chain with canopy; bowl is a 20-segment lathe and shows facets in close-up (standard tier; raise `segs` in `build_pendant` for hero use).
- `X14_PART_Panel_*`, `Door_090`, `Post` — gray enamel steel partitions with base channel, top cap, horizontal sheet seam, glazed uppers with beads, flush door with knobs both sides, cover post with foot plate. No artifacts after fix 3.
- `X14_PART_DropCeiling_120` — exposed T-grid, four fissured tiles recessed, hanger wires. From eye level only the underside is seen; the overview camera at 4.2 m looks over the top, which no player camera does.
- `X14_PART_Fluorescent_120` — two glowing tubes in an open reflector on chains, end plates; lit state only (unlit = material swap, documented in PCG_INTERFACE.json).
- `X14_PART_Sign_Door` — brass plate, four screws, raised black lettering legible at ~1 m: "LEGISLATIVE REFERENCE SERVICE / HISTORY AND GOVERNMENT DIVISION / ROOM 128".
- Interiors (`X14_DEMO_LRS_Room_textured_int_*`): corridor east/west show the whole idea in one frame — 4.6 m plaster room with trim, arched windows and radiators, pendants above, and the gray glazed cubicle fronts under a floating acoustic grid with chain-hung strips. Cubicle view: window, radiator, drop ceiling and two fixtures from inside a cubicle. Door view: door, transom, sign. Ceiling view: grid, hangers, fixture undersides. Clay views confirm silhouettes without materials.

Known limitations left on purpose (say if you want them changed): no furniture (I09 sockets only, so the room is empty); the drop ceiling is an island with no perimeter closure strip, matching the "temporary" reading of the memoir but not a documented detail; exterior faces are untextured plaster; no dirt/wear (that is the Age + Use stage).

## Review notes — Matt, 2026-10-02 (chat)

1. **1963 condition:** "whichever is most probable" → keep the gray-partition / drop-ceiling overlay as delivered (PROBABLE per E4/E6/E12). The 1953 cabinet-divider condition stays available as ARCH layer + I09 only.
2. **Partition finish:** "whatever is most accurate" → gray stays the default. The memoir ties *gray* partitions to the LRS areas (curtains, pavilions, Great Hall upper level, MRR galleries); *faux mahogany* is documented only for the old House Reading Room cubicles (E5), so the mahogany albedo is reserved for a DC-X10 director's-office variant.
3. **Missing records:** Matt will fetch them from the links in the run summary (HABS DC-351 data pages + photos 22/23; 1953 LRS photo full size; Annual Report FY1963 Ch. V / App. XII). Dimensions stay APPROXIMATE until compared; v002 only if they disagree with the build.

These are review notes, not an approval. asset_user_approval remains PENDING.

## asset-v002 (2026-10-02, same run) — what changed and why

Trigger: Matt's review ("most probable condition, most accurate finish") plus the full-size 1953
LRS photograph and HABS DC-351-23 (EVIDENCE.md E19–E22). The photo shows the LRS dividers of
record as **dark wood panelled partitions** with **torchère lamps and opal sconces**, no
dropped ceiling and no fluorescents; the HABS office shows a **painted coffered beam ceiling**.
Wooden partitions are documented in 1953 and again in Nov 1966, so for 1963 they are the
evidence-led choice; the 1967 "gray partitions" overlay stays available.

New modules (all with LOD0–2, UCX, sockets; QA PASS; v001 modules byte-identical):
- `X14_PART_Panel_Wood_090`, `X14_PART_Panel_Wood_060` — 1.95 m dark-oak framed partitions, 60 mm posts, bottom/mid/top rails, two recessed flat panels with bolection beads (LOD0).
- `X14_PART_Door_Wood_090` — same frame with a four-panel 1.84 m leaf on `PIVOT_X14_WoodDoorHinge`.
- `X14_ARCH_Torchere_Lamp` — brass floor lamp, weighted base, knopped column, opal bowl (emissive 1.5).
- `X14_ARCH_Wall_Sconce` — brass backplate (pivot at its bottom on the wall face), arm, upturned opal shade; place at z ≈ 2.32 m.
- `X14_ARCH_Ceiling_Coffered_300` — 3 × 3 coffers per 3 m tile, 0.30 m beams, cove at the junction (LOD0–1), painted panels (`MI_X14_Paint_Coffer`), rosettes (LOD0); pivot on the beam underside → place at z = ROOM_H − 0.30.
- `X14_DEMO_LRS_Room_1953` — the same 9 × 6 m shell with coffered ceilings, three wood cubicles (0.9 + door + 0.9 fronts; 4 × 0.9 + 0.6 dividers), six pendants, three torchères, three sconces, linoleum floor, I09 sockets plus `SOCKET_I09_PedestalFan_NN`.

Decision record: default LRS room = **v002 wood condition**; alternate = v001 gray overlay. Both
ship in asset-v002 (complete kit, 24 modules + 2 demo rooms). Register row unchanged except
delivery_integrity → "v002 complete kit; v001 modules byte-identical; QA PASS; UE import NOT_RUN".

Still wanted: HABS DC-351 data pages (dc0221data.pdf) for room heights and joinery; Annual
Report FY1963 printed pp. 59–70 and 125–126 (the excerpt received was pp. 35–46 and 101–102).

Render review v002: see `renders/` (`X14_DEMO_LRS_Room_1953_*`) and `renders/modules/` for the
six new modules — notes appended after the images were checked (below).

### Render review v002 (every new image looked at)

- `X14_DEMO_LRS_Room_1953_textured_int_*` — corridor views: dark panelled partitions with framed flat panels, coffered beam ceiling with painted panels, pendants, arched windows, green sheet linoleum, oak baseboard; reads as the 1953 photo's construction in the kit's room. Overview: three cubicles of wood panels, torchères and sconces glowing, pendants. Cubicle view: torchère + sconce + window + radiator.
- `X14_PART_Panel_Wood_090/060`, `X14_PART_Door_Wood_090` — rails, posts and recessed panels read; the procedural grain is coarse at close range (same note as the oak door; swap albedo locally if wanted). LOD0 beads are subtle but present.
- `X14_ARCH_Torchere_Lamp` — weighted base, knopped column, fitter cup, opal bowl; emissive reads soft, tune in UE.
- `X14_ARCH_Wall_Sconce` — backplate, arm, upturned bowl; the bowl lathe is 16 segments (facets visible in close-up; standard tier).
- `X14_ARCH_Ceiling_Coffered_300` — the orbit renders show only the slab top (the tool shoots from above); the coffers, coves and rosettes are visible in the 1953 room interiors and in `_clay_rear`/`_front` views from below.
- No coincident-face artifacts found in the new modules (checked the panel ends, rails and beam crossings).

Known limitations v002: the sconce and torchère shades are plain bowls (no etched pattern); coffer panel ornament is reduced to a rosette; partition and door grain is procedural; pedestal fans, desks, chairs and files remain DC-I09 (sockets provided, including `SOCKET_I09_PedestalFan_NN`).

## Review notes — Matt, 2026-10-02 (chat, after v002)

"this is set dressing chill chill just go for it" → the remaining record requests are dropped:
HABS DC-351 data pages, Annual Report FY1963 printed pp. 59–70 / 125–126, and the five unsaved
HABS frames. The dimensions gate is closed; all dimensions stay APPROXIMATE as built and labelled.
No further passes are planned on this job unless Matt reviews and asks for changes.

Register expectation (head agent applies): unchanged from the v002 note — DELIVERED,
delivery_integrity "v002 complete kit; v001 modules byte-identical; QA PASS; UE import NOT_RUN";
evidence note "dimensions APPROXIMATE, archive gate waived by Matt 2026-10-02".
asset_user_approval remains PENDING — this note is scoping, not approval.

## asset-v003 (2026-10-03) — full surfacing pass

Matt asked "youd say its done? send screenshots"; the screenshots showed the procedural oak reading
as wavy zebra stripes on every wood surface and faceted opal shades. He then asked for a full pass.

What changed (all in `build.py`, reproducible, seed 1963):
- **Oak:** new tileable grain with uneven ring spacing, gentle drift and open pores. Trim is golden
  oak, doors walnut-stained, partitions dark oak (new `T_X14_OakDark_BC`, E19). Floor strips carry
  their own offset grain; joints lighter.
- **Grain direction:** every wood face is re-projected so the grain runs along the member. This was
  the root cause of the "zebra" look on rails, baseboards and sash bars, where it previously ran across.
- **Lamps:** pendant, torchère and sconce shades are smooth-shaded Catmull-Rom lathes at 48/24/12
  segments (sconce 40/20/10) with a hard rim; cylinder sides kit-wide are smooth with hard cap edges.
- **Linoleum:** faint sheet seam every 2 m.
- **Sockets:** file cabinets now stand back-to-wall facing into the cubicle (they faced the wall and,
  in the 1953 room, collided with a torchère); the wall clock moved off the door leaf to the south
  wall at x 7.2 m; typewriter, lamp and phone sockets moved to sensible desk positions. Names and
  counts unchanged.
- **Preview dressing (not exported):** `preview_dressing.py` drops simple period stand-ins — flat-top
  pedestal desk, wooden swivel armchair, 4-drawer steel file, typewriter, telephone, banker's lamp,
  pedestal fan, wall clock, paper and document boxes — on the `SOCKET_I09_*` empties via
  `render_interior.py --dress`. They exist only in renders named `*_dressed_*`; DC-I09 owns furniture.
  The DC-I09 v005 ZIP is a Drive binary the sandbox connector cannot transfer, so the real set was not used.

Unchanged: module names, dimensions, pivots, material slot names, LODs, UCX, the 1953-default /
gray-alternate decision. Every GLB changed bytes (UVs, normals, textures), so v003 supersedes v002.

Gates: QA 24/24 PASS; clean rebuild in an isolated copy byte-identical (24 GLBs + 24 textures);
Unreal 5.8 import and motion tests NOT_RUN — needs local Unreal (UE 5.8). Approval PENDING.

Expected register change (head agent applies): delivery_integrity → "v003 complete kit (surfacing
pass); QA PASS; clean rebuild identical; UE import NOT_RUN". asset_user_approval stays PENDING.

What Matt should look at: `renders/*_dressed_*` (the room as it will read in game once I09 is placed),
then `renders/modules/X14_PART_Panel_Wood_090_*`, `X14_ARCH_Wall_Door_300_*` and
`X14_ARCH_Pendant_Lamp_*` for the grain and shade fixes.

### Render review v003 (every image looked at: 30 interior views, 176 module orbits)

- Oak now reads as varnished oak, not stripes: rings run along every rail, baseboard, picture rail
  and sash bar, and up every stile, post and panel; partitions are the dark oak of the 1953 photo,
  doors walnut-stained, trim golden. Texture tiles seamlessly at 1 m (checked 2 × 2).
- Pendant, torchère and sconce shades are smooth at the overview camera; no facets in silhouette.
- Dressed views (`*_dressed_*`): desks, chairs, files, typewriters, phones, banker's lamps, fans,
  paper and document boxes sit on their sockets with no collisions; the clock hangs on plain wall.
  These stand-ins are rough by design and are not part of the kit.
- Clay views: no coincident-face black patches in either room.
- Left as is: the drop-ceiling island still has no perimeter closure strip (memoir says "temporary");
  sconce and torchère shades are plain bowls; partition-top faces catch grazing light from the
  render's fill lights a little (normal-map strength halved in v003).

## asset-v004 (2026-10-03) — fit test with the real DC-I09 furniture

Matt: "find the already completed desk assets and try them". DC-I09 (Office furniture set) has
deliveries v002–v005 in DC-INT1 Incoming Deliveries. v005 (6.7 MB ZIP) is too large for the Drive
connector's transfer; v004 (2.2 MB) came through byte-exact, so the fit test uses **DC-I09 v004**.
Re-check against v005 locally.

What was tried: the real I09 LOD0 desk, filing cabinet, typewriter, rotary phone, desk lamp and wall
clock instanced on the X14 sockets in both demo rooms (`render_interior.py --dress --i09 <meshes>`;
renders `renders/*_i09_*`). I09 has no chair or pedestal fan, so those, the papers and the document
boxes stay as preview stand-ins. Nothing from I09 is exported in any X14 GLB.

Fixes this forced in X14 (demo rooms only; all 22 modules and textures byte-identical to v003):
- **Sockets now follow the I09 INTERFACE_CONTRACT.** I09 fronts face local -Y, so the file-cabinet
  sockets are unrotated (back to the north wall, drawers into the cubicle) and the clock socket is
  rotated 180° (face into the room, z 2.2 at the clock's bottom). Typewriter, phone and lamp sockets
  are now exactly the I09 desk's own SOCKET_TYPEWRITER / SOCKET_PHONE / SOCKET_LAMP carried through
  the desk socket. In v003 the cabinets would have faced the wall with the real I09 files.
- **1953 room node names.** Since v002 the 1953 room exported 156 of its 417 node names with Blender
  ".001" suffixes (every SOCKET_I09_*, UCX_ and part node), because both rooms were built in one
  scene. Unreal looks sockets up by name, so these would not have been found. Fixed; both rooms now
  have unique, suffix-free names.

Findings for the DC-I09 owner (reported, not changed — I09 is not this job's asset):
1. **Axis:** the I09 GLBs (trimesh exporter) store height on glTF +Z with an unrotated root node;
   glTF is +Y-up by spec, so Blender and UE import every piece lying on its back. Previews apply a
   -90° X correction on import.
2. **Desk float:** desk LOD0's lowest point is z 0.02 m, so it hovers 2 cm above its pivot.
3. **Desk lamp:** the arm lamp's flat disc shade reads large at desk scale in the cubicle views.
Footprints fit the X14 sockets as assumed: desk 1.52 × 0.78 × 0.76 m, file 0.47 × 0.71 × 1.33 m.

Gates: QA 24/24 PASS; clean rebuild byte-identical; Unreal import and motion NOT_RUN — needs local
Unreal (UE 5.8). Approval PENDING.

Carried over from v003 unchanged (the GLB geometry they depict is identical): module orbit renders
and the kit-only and clay interior views. Replaced: the stand-in `_dressed_` views by `_i09_` views.

Expected register change (head agent applies): delivery_integrity → "v004: I09 fit test, sockets
aligned to I09 contract, 1953 node names fixed; QA PASS; UE import NOT_RUN". I09 row: note the axis
and desk-float findings for its owner. asset_user_approval stays PENDING.

What Matt should look at: `renders/*_i09_*` (the rooms with the real I09 furniture).

### Render review v004 (all 12 new views looked at)

- Both rooms, all six cameras: I09 desks walnut-topped with olive pedestals, drawers toward the chair;
  olive four-drawer files back to the north wall facing in; typewriter, rotary phone and arm lamp on
  the I09 desk sockets; clock on plain south wall facing the room. No interpenetration seen.
- The 1953 room reads closest to the Sept 1953 photo (E19): dark partitions, torchères, light steel
  files, wooden desks. The I09 files are olive rather than the photo's light finish (I09's call).


## asset-v005 (2026-10-03) — set dressing: walls, corners, bookcases

Matt: "anything on the walls? plants in the corners? nothin???". Fair: v004 had furniture and lamps
but bare plaster and empty corners. v005 adds a **set-dressing layer to the kit**: ten `X14_DRESS_*`
modules built like every other module (LOD0–LOD2, `UCX_` collision, UVs, stable `MI_X14_*` slots,
base pivots, QA PASS), placed in both demo rooms.

| Module | What it is | Evidence status |
|---|---|---|
| `X14_DRESS_Frame_Print_Large` | 0.66 × 0.52 m oak frame, cream mat, sepia engraving "A View on the Potomac" | APPROXIMATE object; picture FICTIONALISED |
| `X14_DRESS_Frame_Photo_Small` | 0.48 × 0.40 m black metal frame, silver-gelatin style photo of a generic domed civic building | APPROXIMATE; picture FICTIONALISED (no specific building) |
| `X14_DRESS_Wall_Calendar_1963_11` | November 1963 sheet (1 Nov = Friday, 30 days) on a tin strip and nail | dates VERIFIED (E24); design FICTIONALISED, no publisher imprint |
| `X14_DRESS_Bulletin_Board_090` | 0.90 × 0.60 m oak-framed cork board, typed memos, yellow notes, red pins | APPROXIMATE |
| `X14_DRESS_Bookcase_Oak_090` | 0.90 × 0.30 × 1.80 m open oak bookcase, five shelves of cloth-bound books, a lying stack | VERIFIED type (E19: bookcases between desk groups); size APPROXIMATE |
| `X14_DRESS_Plant_Rubber` | rubber plant (Ficus elastica), ~1.6 m, terracotta pot | APPROXIMATE (period-typical; not in sources) |
| `X14_DRESS_Plant_Pothos_Small` | small trailing pothos in a clay pot (bookcase tops, sills) | APPROXIMATE |
| `X14_DRESS_Coat_Tree` | oak coat tree, brass double hooks, felt fedora on the finial | APPROXIMATE |
| `X14_DRESS_Flag_Stand_US` | 3 × 5 ft 50-star flag drawn to EO 10834 proportions, oak pole, brass finial, weighted base | flag VERIFIED for 1963 (E23); stand APPROXIMATE |
| `X14_DRESS_Wastebasket` | olive steel wastebasket with crumpled paper | APPROXIMATE |

Placement in both rooms (layout FICTIONALISED, shared by `place_dressing()` in `build.py`):
- Corridor (south) wall: bulletin board, large print, flag beside the door, coat tree, calendar
  next to the I09 clock; rubber plants in both south corners, clear of the window radiators.
- Each cubicle: framed picture on the north wall centred under the sconce, bookcase against the
  west divider with a pothos on top, wastebasket beside the desk.

Defects found and fixed before delivery (all in the generator):
1. Wastebasket LOD0 lost its steel body (bmesh op reallocation made the "new verts" set return every vertex).
2. Top-shelf books poked through the bookcase top (heights now capped per shelf).
3. Rubber plant read as sparse bamboo (now four stems, larger, denser, glossier, darker leaves).
4. Fedora hung sideways off a hook (now seated on the finial).
5. Pictures and calendar were mirrored seen from the room (UV u flipped on the room face).
6. First-draft print textures read as blobs (both redrawn).
7. In the 1953 room the coat tree hid the door sign (moved 0.22 m east). Bookcases moved to clear the 4 cm partition skins and the baseboards.

Unchanged: all 22 v004 modules and all 24 v004 textures are byte-identical; the I09 sockets are
unchanged. Only the two demo rooms change (they now include the dressing).

Renders: two new interior cameras, `int_south_wall` (corridor wall dressing) and
`int_cubicle_dress` (bookcase, picture, wastebasket). Each room is rendered three ways: kit only,
clay, and with the real DC-I09 v004 furniture (`_i09_`). Orbits for the ten new modules are in
`renders/modules/`. The earlier modules' orbits are carried over from v004 (identical geometry).

Gates: QA 34/34 GLBs PASS; clean rebuild in an isolated copy byte-identical (34 GLBs + 30
textures); Unreal import / motion **NOT_RUN — needs local Unreal (UE 5.8)**. Approval PENDING.

Expected register change (head agent applies): delivery_integrity → "v005: set-dressing layer
(10 DRESS modules), QA PASS 34/34, clean rebuild byte-identical; UE import NOT_RUN".
asset_user_approval stays PENDING.

UNIFICATION PROPOSAL (v005): the DRESS modules are generic 1963 U.S. office stock. Propose a
shared `DRESS` component family for every DC office interior (X10, X11, X13, I-sets) and, with the
calendar and flag, the DALLAS office interiors. Picture textures swap per room via the
`MI_X14_Print_*` slots (UVs fitted 0..1, so any 4:3 image drops in).

What Matt should look at:
1. `renders/*_i09_int_south_wall.png` and `*_i09_int_corridor_east.png`: corridor wall dressing, flag, coat tree, corner plants.
2. `renders/*_i09_int_cubicle_dress.png`: bookcase, pothos, framed picture, wastebasket in a cubicle.
3. Whether you want more clutter (papers pinned everywhere, maps, a second flag, curtains) or less.

### Render review v005 (every new image looked at: 16 `_i09_` interiors, 6 kit-only, 6 clay, 80 module orbits)

- **Corridor (south) wall, both rooms** (`int_corridor_east`, `int_corridor_west`, `int_south_wall`):
  the bulletin board, the oak-framed engraving, the flag beside the door, the coat tree with its fedora,
  the November 1963 calendar under the I09 clock, and the rubber plant in the far corner all read at
  dialogue distance. The calendar month and the print caption read the right way round. Nothing
  intersects the door casing, sign, radiators or baseboard.
- **Cubicles** (`int_cubicle_dress`, `int_high_overview`): bookcase against the west divider with a
  pothos on top; framed picture centred under the sconce above the file cabinet; wastebasket beside
  the desk; no collision with the desk, chair, torchère, fan or file socket. In the gray room the
  neighbouring cubicle's bookcase shows through the glazed upper panel, as it should.
- **Modules**: rubber plant reads as a glossy Ficus, not bamboo; the wastebasket shows its steel body;
  books sit under every shelf; the flag's union is at the hoist and top.
- Weak points, not fixed: in `int_door_and_sign` the flag fills the right foreground (the camera
  stands close to it); the engraving is a stylised hatch, convincing at wall distance but not in
  close-up; the plants are low-poly cards with no leaf texture.
