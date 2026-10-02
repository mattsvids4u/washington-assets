# DC-V01 — MPD patrol car 1963 — HANDOFF (asset-v002)

Claimant: claude-cloud-agent (AGENTS lane) · delivered 2026-10-02 · stage A (asset) · set DC-EXT1
Brief WASHINGTON-2026-09-22-v001 · stage standard v001 · road-plans canon v002 · request doc
1CGp5evRrPST1P3r5soqPHBGuvm9VatvnqqleL0stpU8 (incl. vehicle benchmark addendum, Matt 2026-09-26).
**Not approved. Matt's review decides.** Delivery integrity and visual quality are separate.

## What changed in asset-v002 (Pass 4 — "realism and geometry pass: fine beveling and grounding")
- **Fine bevelling.** Every body panel edge, door/hood/trunk edge and aperture flange now carries a
  rolled 3.5 mm two-segment bevel; grille bars, bumper guards, handles, dash, floor, trims, engine
  bay, radio, visors, seats and underbody parts carry 4 mm bevels; armrests 8 mm. Edges catch
  light instead of reading as razor-sharp CAD (moodbook p.10 "edges that catch light").
- **Grounding.** Tyres now have three circumferential tread grooves, a 1 cm loaded deflection
  (hubs at 34.5 cm) and a flat contact patch with a slight sidewall bulge, so the car sits on the
  road instead of touching it at a tangent. A full underbody was added — exhaust and muffler,
  driveshaft, live rear axle with differential, leaf springs, fuel tank, front cross-member and
  control-arm block-ins, front and rear valance pans — and the floor pan reads as dark undercoat.
  `renders/..._underside.png` and `..._detail_rear_wheel_kerb.png` show it.
- **Realism fixes found by the new close-up renders** (`tools/render_detail.py`): the engine-bay
  radiator support poked through the hood lip as a dark bar above the grille (this was in v001's
  final GLB but not in its renders, which predated the engine bay — my miss); the rocker strip
  floated 8 cm off the body (v001 too) and is now shrink-wrapped between the arches; door-seal
  text was mirrored on the driver side; headlamps read as chrome plugs and are now glassy lenses;
  door skins slightly more convex; door armrests added; smoother fender-tip blend.
- **Determinism regression caught and fixed**: bevelling the licence-plate boxes produced
  run-to-run UV differences; plates are no longer bevelled. Both GLBs again rebuild byte-identical
  from a clean `out/`. A zero-area sliver on the body is now removed by the cleanup step.
- Unchanged: identity (APPROXIMATE 1963 Ford-pattern sedan), hierarchy and socket names, decals,
  MPD layer, LOD/UCX scheme. v001 remains frozen in `deliveries/DC-V01/asset-v001/`.

## What was built
A complete 1963-setting Metropolitan Police (MPD) patrol sedan as a **whole vehicle**, generated
from scratch by `source/build.py` (bpy 4.5, deterministic: two clean rebuilds are byte-identical):

- `meshes/SM_V01_PatrolSedan_MPDC.glb` — MPD variant, full articulated hierarchy, LOD0–LOD2, UCX.
- `meshes/SM_V01_Sedan_Base_Neutral.glb` — the same body with no POLICE_* parts and neutral paint:
  the proposed **city-neutral shared base** for DALLAS V07 and the DC-V02 taxi rebuild.
- Body: lofted 1963 Ford-pattern full-size four-door sedan skin (46 cross-sections, Catmull-Clark,
  solidified 2.5 cm shell) with **real apertures** — windshield, backlight, four door windows,
  four wheel openings with inner wheel-houses, grille opening, four headlamp and two tail-lamp
  openings. Doors, hood and trunk are **separate panels cut from the same skin**, with 3.5 mm
  panel gaps and hinge pivots at their origins (see Hierarchy).
- Glazing: six glass panes (6 mm solid, transmissive glass material) sitting in the apertures with
  chrome mouldings; interior is visible through them (floor, firewall, dash with instrument hood,
  tilted column and 17-in three-spoke wheel, front/rear bench seats, parcel shelf, visors, police
  radio under the dash, engine-bay placeholder under the hood).
- Exterior: wrap-around chrome bumpers with guards, recessed dark grille with five horizontal
  chrome bars and surround, four 5¾-in sealed-beam headlamps in bezels, round tail lamps with
  back-up lenses, hood-lip and rear-panel trim, rocker strips, push-button door handles, driver
  mirror, wipers, front/rear plates (FICTIONALISED "MP 1963").
- Wheels: four separate wheels (7.50-14 tyre, OD 71 cm, narrow whitewall on the outboard
  sidewall, painted steel rim, chrome dog-dish cap), origins at hub centres, fronts parented to
  STEER_FL/FR pivots.
- MPD layer (all `POLICE_*`, detachable): roof identifier decal "M/P" over the front seat and
  "D/C" over the rear seat in turquoise (layout and letter orientation taken from the 1962 fleet
  photo E1), single small red roof beacon (Beacon Ray 17 class, APPROXIMATE size), "POLICE" trunk
  decal readable from behind, round door seals (generic text, APPROXIMATE), roof whip antenna
  (APPROXIMATE), radio set.
- Textures (procedural PIL, embedded in the GLB, also in `textures/`): roof ID, door seal, trunk
  POLICE, plate. All other materials are flat PBR constants.

Dimensions (from QA): body 207 × 533 cm, 141 cm high (217 cm over mirrors, 546 cm over bumpers,
antenna tip at 189 cm); wheelbase 302 cm; tread 155/152 cm; sits on Z = 0.

## Hierarchy (glTF nodes; Blender metres, UE imports as cm; nose = −Y, driver side = +X)
```
SM_V01_PatrolSedan_MPDC
  BODY (+ BODY_LOD1/_LOD2)             static shell incl. pillars, roof, fenders, floor
  DOOR_FL / DOOR_FR  origin = hinge (±97, −46, 62) cm   → GLASS_DOOR_*, TRIM_WINDOW_DOOR_*, HINGE_*
  DOOR_RL / DOOR_RR  origin = hinge (±99,  53, 62) cm
  HOOD   origin = rear hinge line (0, −62, 91) cm        (rotate about X, negative = open)
  TRUNK  origin = front hinge line (0, 162, 96) cm       (rotate about X, positive = open)
  STEER_FL / STEER_FR (±77.5, −151, 34.5) → WHEEL_FL / WHEEL_FR (origin = hub, loaded height)
  WHEEL_RL / WHEEL_RR (±76, 151, 34.5)
  UNDER_EXHAUST_DRIVELINE, UNDER_AXLES_TANK                (v002 underbody)
  INT_ARMREST_FL/FR/RL/RR                                   (v002, children of their doors)
  GLASS_WINDSHIELD, GLASS_REAR, TRIM_WINDOW_*, GRILLE_*, HEADLAMP_*, TAILLAMP_*, BUMPER_*, TRIM_*,
  WHEELHOUSES, INT_* (interior), PLATE_FRONT/REAR, MIRROR_DRIVER, WIPERS, DOOR_HANDLES
  POLICE_DECAL_ROOF_ID, POLICE_DECAL_TRUNK, POLICE_DECAL_SEAL_FL/FR, POLICE_BEACON_BASE/DOME,
  POLICE_ANTENNA, POLICE_RADIO                         (detachable MPD layer)
  SOCKET_DRIVER, SOCKET_STEERING, SOCKET_BEACON, SOCKET_ANTENNA, SOCKET_ROOF_SIGN,
  SOCKET_PLATE_F/R, SOCKET_SPOTLIGHT_L, SOCKET_SIREN   (empties; coordinates in PCG_INTERFACE.json)
  UCX_BODY_01..04                                       simple convex collision
```
`renders/SM_V01_PatrolSedan_MPDC_posed_open.png` is the exported GLB re-imported and posed
(doors, hood, trunk open, front wheels steered 22°) — the hinges and steering pivots work as nodes.
Full lists: `HIERARCHY.txt`, `MESH_STATS.txt`. LOD0 is heavier in v002 because of the bevels
(see MESH_STATS.txt); LOD1 ≈ 45 %, LOD2 ≈ 18 % on every part above 300 / 1500 faces.

## Material slots (stable names; ITS ALIVE families)
MT: `MI_V01_Chrome`, `MI_V01_Steel_Painted`, `MI_V01_Headlamp` · GL: `MI_V01_Glass`,
`MI_V01_Lens_Red`, `MI_V01_Lens_Clear`, `MI_V01_Beacon_Red_Unlit` (`MI_V01_Beacon_Red_Lit`
is defined in build.py for the lit state; swap on the dome) · CT: `MI_V01_Paint_Body` (cream),
`MI_V01_Paint_Neutral` (base GLB), `MI_V01_Decal_RoofID`, `MI_V01_Decal_DoorSeal`,
`MI_V01_Decal_Trunk`, `MI_V01_Plate` · support: `MI_V01_Rubber_Tyre`, `MI_V01_Whitewall`,
`MI_V01_Interior_Trim`, `MI_V01_Interior_Vinyl`, `MI_V01_Interior_Dark`, `MI_V01_Undercoat`,
`MI_V01_Grille_Dark`.

## Evidence gaps, APPROXIMATE and FICTIONALISED (see EVIDENCE.md)
- **Make/model of the 1963 MPD scout car is not proven.** The body is a 1963 Ford-pattern
  full-size sedan (119-in wheelbase class) — APPROXIMATE, chosen because DALLAS V07 (Tippit's car)
  was a 1963 Ford Galaxie and the map's civilian cars are Galaxie-derived. No Ford badges or
  wordmarks anywhere.
- APPROXIMATE: letter typeface/size, seal artwork (generic words, no copied emblem), beacon model
  and mount, antenna, interior colours/trim, hubcap style, rocker chrome, engine-bay dressing.
- FICTIONALISED: plate number "MP 1963", seal text layout.
- Not modelled: siren, spotlight, radiator badge, exhaust, underbody detail (sockets provided for
  siren and spotlight).
- Photo evidence could not be downloaded from this sandbox (egress proxy blocks LoC, Commons,
  Truman Library, mpdc.dc.gov, dcmetropolicecollector.com); E1 was inspected from the project's
  Drive References copy; others are link-cited.

## Gates
| Gate | Result |
|---|---|
| Pass 1 evidence | done (EVIDENCE.md) |
| Clean rebuild | PASS — `out/` deleted, `python jobs/DC-V01/build.py`, both GLBs byte-identical to the previous build (SHA256 compared) |
| GLB reopen QA (`tools/qa_check.py`) | PASS 515/515 (MPDC), 455/455 (neutral base): bounds, ground contact, UVs, materials, degenerate faces, outward normals, applied transforms, LODs, UCX |
| Actual-output renders | clay + textured front/profile/rear/¾, orthographic top and underside, posed-open view, four close-up detail views (front fender, door belt, rear wheel at kerb height, grille low) (`renders/`) |
| Visual self-review vs E1 + moodbook p.10–12 | roof layout/orientation, beacon, trunk marking, seal, light body, chrome, whitewalls match E1; silhouette reads as a 1962–63 full-size sedan; see "What Matt should look at" |
| Unreal 5.8 import / native readback | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Wheel rotation / steering / suspension / door motion in engine | **NOT_RUN — needs local Unreal (UE 5.8)**; pivots verified only by re-import + pose render |
| Matt approval | PENDING |

## Expected register status changes (head agent edits the sheet; not done by this agent)
- DC-V01: asset_status CLAIMED → DELIVERED; claim_owner "claude-cloud-agent — DC-V01" (prior
  "V01 - MPD Patrol Car / Lu / ChatGPT" is RELEASED per Drive); delivery_integrity
  "v002 SHA256 verified; clean rebuild byte-identical; QA 515/515; Unreal NOT_RUN" (v001 superseded);
  asset_user_approval PENDING; integration_status NOT_STARTED.
- DC-V02 "Depends on": a candidate production sedan base now exists
  (`SM_V01_Sedan_Base_Neutral.glb`, asset/DC-V01-v001) — not approved until Matt says so.

## UNIFICATION PROPOSALS
1. Register `SM_V01_Sedan_Base_Neutral` as the shared body for **DALLAS V07** (Dallas police
   sedan, 1963 Ford Galaxie): same generator, DPD livery as a second `POLICE_*` layer
   (black/white two-tone + door roundel + "DALLAS POLICE" lettering) — build.py already separates
   paint, decals and equipment from the base.
2. **DC-V02 taxi**: derive from the neutral base; add roof sign at `SOCKET_ROOF_SIGN`, fictional
   livery decals at the door-seal decal positions, lit/unlit sign materials as done for the beacon.
3. **DC-V05 parked sedans**: the loft cross-section table `K` in build.py is a compact way to make
   silhouette variants (roofline, deck length) without new modelling.
4. Hinge/steer/socket naming (`DOOR_xx`, `HOOD`, `TRUNK`, `STEER_Fx`, `WHEEL_xx`, `SOCKET_*`) is
   proposed as the WASHINGTON/DALLAS vehicle contract for V03–V09.

## What Matt should look at
0. v002 first: `renders/..._detail_*.png` (bevels, panel gaps, contact patch, rocker strip), and
   `..._underside.png` / `..._detail_rear_wheel_kerb.png` for grounding. Say if the bevel radius
   should be larger (3.5 mm is a stamped-steel roll; 6–8 mm would read softer at game distance).
1. `renders/SM_V01_PatrolSedan_MPDC_textured_three_quarter.png` and `_profile.png` against the
   1962 fleet photo (E1) — does the body read as the right era/class? If a different make is
   known for 1963 MPD, say which and the cross-section table can be re-authored.
2. `renders/SM_V01_PatrolSedan_MPDC_top.png` — roof letter layout/orientation and beacon position
   vs E1 (M/P over the front seat, D/C over the rear, tops toward the driver's side).
3. `renders/..._posed_open.png` — hinge and steering pivots; interior visibility.
4. Colour: cream body + turquoise graphics are read from a colour-shifted 1962 slide; confirm or
   give target hex values (moodbook palette on p.11 used for interior/undercoat tones).
5. Whether the beacon should be larger (true Beacon Ray 17 ≈ 24 cm base) — the photo suggests a
   smaller dome, which was followed.
6. Whether the engine bay / trunk should be dressed further before the weathering stage.

## Files
PASS_PLAN.md · CONTEXT_ACK.json · EVIDENCE.md · HANDOFF.md · DEPENDENCY_LOCK.json ·
PCG_INTERFACE.json · REUSABLE_COMPONENTS.json · HIERARCHY.txt · MESH_STATS.txt ·
source/build.py · meshes/*.glb · textures/*.png · renders/*.png · DELIVERY_MANIFEST.json ·
SHA256SUMS.txt. Repo branch `asset/DC-V01-v002` (PR link in PAYLOAD_LINK.txt on Drive).
