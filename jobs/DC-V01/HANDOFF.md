# DC-V01 — MPD patrol car 1963 — HANDOFF (asset-v003)

Claimant: claude-cloud-agent (AGENTS lane) · delivered 2026-10-03 · stage A (asset) · set DC-EXT1
Brief WASHINGTON-2026-09-22-v001 · stage standard v001 · road-plans canon v002 · request doc
1CGp5evRrPST1P3r5soqPHBGuvm9VatvnqqleL0stpU8 (incl. vehicle benchmark addendum, Matt 2026-09-26).
**Not approved. Matt's review decides.** Delivery integrity and visual quality are separate.

## What changed in asset-v003 (Pass 5 — Matt on v002: "still needs hella work. next pass. shape is wonky. text is wacked out.")
**Shape — body surface rebuilt.**
- Root cause of the "wonky" shape: the v001/v002 generator blended its cross-section keys with a
  per-segment smoothstep, which has zero slope at every key. That put a flat spot and a ripple at
  every key along the hood, fenders and roof, and a 0.07 m "fender-tip push" dented the front corners.
  The keys are now blended with a C1 monotone cubic, and the push is gone.
- The skin is no longer a 46-section loft that is Catmull-Clark subdivided and then cut with planes.
  It is a structured grid: about 180 stations along the car × 114 rows around a **filleted section
  outline**. Each control point has its own fillet radius, giving a crisp drip rail and belt line,
  a 0.9 cm shoulder crease and soft roof and side curvature.
- Every opening and panel line is selected along the grid's own rows and stations: windshield,
  backlight, four side windows, doors, hood and trunk. Six straight plane cuts handle the slanted
  A- and C-pillar edges. Pillars keep a constant width, and the torn/twisted A-pillar and the
  "horns" at the roof corners are gone.
- New front end: a flat front face with a 2.5 cm rolled edge and a **full-width '63-pattern grille
  opening** with the quad sealed-beam lamps inside it (chrome buckets and bezels, fine horizontal
  bars and dividers, chrome surround). The rear is a flat panel with rolled edges, round tail lamps
  in chrome bezels and back-up lamps.
- **Glass now follows the body.** Each pane is the body's own surface inside its opening, set 9 mm
  in, so the windshield and backlight wrap with the body instead of being flat trapezoids.
  Window surrounds are straight-edged 2 cm chrome bands cut along their own lines, with bright drip
  rails along the roof. An intermediate v003 build picked the mouldings by face adjacency, which
  gave a sawtooth A-pillar edge; it was caught in a close-up render and replaced before delivery.
- Thinner sheet (1.2 cm shell, was 2.5 cm), so door gaps, window reveals and arch lips read as
  stamped panels rather than slabs.
- Wheel openings are round over the tyre and straight down below the hub. The wheel-house liners
  follow that shape and end at the rocker, so no tabs hang down.
- Defects found in v002 and fixed:
  - the grey "brick" valances that stuck out under the bumpers;
  - the interior floor slab poking out through the rear wheel wells;
  - the engine splash pan, inner fender walls and control arms clipping the front tyres;
  - the rear bench passing through the rear wheel houses.
  A wheel-clash probe now finds nothing inside any tyre except the rear axle ending in its hub.
- Tyres: rounded shoulder and bulging sidewall (bias-ply section), with a proper ~6 cm whitewall
  band instead of a hairline.

**Text — livery redone.**
- Roof: v002's letters were turned the wrong way and mirrored. The PIL glyph rotation and the
  decal's row order were both wrong. Fixed and verified from the exported GLB's UVs and a top render.
  From above with the nose to the right, the roof now reads **D M over C P**, exactly as E1:
  - letter tops toward the driver side;
  - 39 cm cap height, 40–47 cm wide;
  - Helvetica-class bold sans (FreeSans Bold), sized and placed from the photo.
- Beacon moved to y = +14 cm, between M and P as in E1 (was +32). Antenna moved to y = +55 cm,
  the dark dot at the roof centre in E1 (was +68).
- Door seal redrawn at 1024 px with evenly spaced ring text: "METROPOLITAN POLICE" over the top
  and "WASHINGTON, D.C." under the bottom, both reading left to right, plus a centre star. It reads
  correctly on both doors. It is still generic, with no copied artwork.
- Plate text no longer overflows ("MP 1963" was clipped at the right edge). Trunk "POLICE" now uses
  the same typeface.

**Kept:** hierarchy and socket names, material slots, LOD/UCX scheme, MPD/neutral split,
determinism. Exception: `TRIM_HOOD_FRONT` was removed, because the front face no longer has room
for it. Door hinge x moved with the new skin, and the beacon, antenna, spotlight and siren sockets
moved (PCG_INTERFACE.json). v001 and v002 stay frozen in `deliveries/DC-V01/`.

v002 summary (superseded): fine 3.5 mm bevels, tyre contact patch, underbody, close-up renders.

## What was built
A complete 1963-setting Metropolitan Police (MPD) patrol sedan as a **whole vehicle**, generated
from scratch by `source/build.py` (bpy 4.5, deterministic: two clean rebuilds are byte-identical):

- `meshes/SM_V01_PatrolSedan_MPDC.glb` — MPD variant, full articulated hierarchy, LOD0–LOD2, UCX.
- `meshes/SM_V01_Sedan_Base_Neutral.glb` — the same body with no POLICE_* parts and neutral paint:
  the proposed **city-neutral shared base** for DALLAS V07 and the DC-V02 taxi rebuild.
- Body: 1963 Ford-pattern full-size four-door sedan skin. A structured grid of ~180 stations ×
  114 rows around a filleted section outline, solidified as a 1.2 cm shell, with **real
  apertures**:
  - windshield, backlight and four door windows;
  - four U-shaped wheel openings with inner wheel-house liners;
  - full-width grille opening and two tail-lamp openings.
  Doors, hood and trunk are **separate panels cut along the same grid**, with 3.5 mm panel gaps,
  2.5 mm rolled edges and hinge pivots at their origins (see Hierarchy).
- Glazing: six panes taken from the body surface inside each opening (they wrap with the body),
  5 mm thick, with transmissive glass. Straight 2 cm chrome surrounds (`TRIM_WINDOW_*`) and bright
  drip rails. The interior is visible through the glass: floor, firewall, dash with instrument
  hood, tilted column and 17-in three-spoke wheel, front/rear bench seats, parcel shelf, visors,
  police radio under the dash, and an engine-bay placeholder under the hood.
- Exterior:
  - wrap-around chrome bumpers with guards;
  - full-width recessed grille with fine horizontal bars, dividers and a chrome surround;
  - four 5¾-in sealed-beam headlamps in chrome buckets and bezels inside the grille;
  - round tail lamps with back-up lenses, and rear-panel trim;
  - rocker strips, push-button door handles, driver mirror, wipers;
  - front/rear plates (FICTIONALISED "MP 1963").
- Wheels: four separate wheels with hub-centre origins. Fronts are parented to the STEER_FL/FR
  pivots. Each has:
  - a 7.50-14 bias-ply tyre (OD 71 cm), rounded sidewall, three tread grooves and a loaded contact
    patch;
  - a ~6 cm whitewall band on the outboard sidewall;
  - a painted steel rim and a chrome dog-dish cap.
- MPD layer (all `POLICE_*`, detachable):
  - roof identifier decal in turquoise: M/P over the front seat and D/C over the rear. Tops point
    to the driver side, so from above with the nose to the right it reads "D M / C P" (E1);
  - single small red beacon between M and P (Beacon Ray 17 class, APPROXIMATE size);
  - "POLICE" trunk decal, readable from behind;
  - round door seals with ring text and a star (generic, APPROXIMATE);
  - roof whip antenna at the roof centre (APPROXIMATE);
  - radio set.
- Textures (procedural PIL, embedded in the GLB, also in `textures/`): roof ID, door seal, trunk
  POLICE, plate. All other materials are flat PBR constants.

Dimensions:
- body 203 × 533 cm, 141 cm high;
- from QA bounds: 216 cm wide over mirror and bumper ends, 546 cm over bumpers, antenna tip at
  190 cm;
- wheelbase 302 cm, tread 155/152 cm; sits on Z = 0.

## Hierarchy (glTF nodes; Blender metres, UE imports as cm; nose = −Y, driver side = +X)
```
SM_V01_PatrolSedan_MPDC
  BODY (+ BODY_LOD1/_LOD2)             static shell incl. pillars, roof, fenders, floor
  DOOR_FL / DOOR_FR  origin = hinge (±101.0, −46, 62) cm → GLASS_DOOR_*, TRIM_WINDOW_DOOR_*, INT_ARMREST_*, HINGE_*
  DOOR_RL / DOOR_RR  origin = hinge (±101.4,  52, 62) cm
  HOOD   origin = rear hinge line (0, −62, 92.3) cm      (rotate about X, negative = open)
  TRUNK  origin = front hinge line (0, 162, 97.3) cm     (rotate about X, positive = open)
  STEER_FL / STEER_FR (±77.5, −151, 34.5) → WHEEL_FL / WHEEL_FR (origin = hub, loaded height)
  WHEEL_RL / WHEEL_RR (±76, 151, 34.5)
  UNDER_EXHAUST_DRIVELINE, UNDER_AXLES_TANK                (v002 underbody)
  INT_ARMREST_FL/FR/RL/RR                                   (v002, children of their doors)
  GLASS_WINDSHIELD, GLASS_REAR, TRIM_WINDOW_WINDSHIELD/REAR, GRILLE_*, HEADLAMP_*, TAILLAMP_*,
  BACKUP_LENSES, BUMPER_*, TRIM_REAR_PANEL, TRIM_ROCKER_L/R,
  WHEELHOUSES, INT_* (interior), PLATE_FRONT/REAR, MIRROR_DRIVER, WIPERS, DOOR_HANDLES
  POLICE_DECAL_ROOF_ID, POLICE_DECAL_TRUNK, POLICE_DECAL_SEAL_FL/FR, POLICE_BEACON_BASE/DOME,
  POLICE_ANTENNA, POLICE_RADIO                         (detachable MPD layer)
  SOCKET_DRIVER, SOCKET_STEERING, SOCKET_BEACON, SOCKET_ANTENNA, SOCKET_ROOF_SIGN,
  SOCKET_PLATE_F/R, SOCKET_SPOTLIGHT_L, SOCKET_SIREN   (empties; coordinates in PCG_INTERFACE.json)
  UCX_BODY_01..04                                       simple convex collision
```
`renders/SM_V01_PatrolSedan_MPDC_posed_open.png` is the exported GLB re-imported and posed
(doors, hood, trunk open, front wheels steered 22°) — the hinges and steering pivots work as nodes.
Full lists: `HIERARCHY.txt`, `MESH_STATS.txt`. LOD1 ≈ 45 %, LOD2 ≈ 18 % on every part above
300 / 1500 faces.

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
- APPROXIMATE:
  - letter typeface: FreeSans Bold, a Helvetica-class stand-in for the painted letters. Sizes and
    placement are measured from E1 with ±10 % perspective uncertainty;
  - seal artwork: generic words and a star, no copied emblem;
  - beacon model and mount, antenna;
  - interior colours and trim, hubcap style, rocker chrome, engine-bay dressing;
  - grille bar pattern (generic, no Ford wordmark or crest).
- FICTIONALISED: plate number "MP 1963", seal text layout.
- Not modelled: siren, spotlight, radiator badge, side-spear trim (sockets provided for siren and
  spotlight).
- Photo evidence could not be downloaded from this sandbox (egress proxy blocks LoC, Commons,
  Truman Library, mpdc.dc.gov, dcmetropolicecollector.com); E1 was inspected from the project's
  Drive References copy; others are link-cited.

## Gates
| Gate | Result |
|---|---|
| Pass 1 evidence | done (EVIDENCE.md) |
| Clean rebuild | PASS — `out/` deleted twice, `python jobs/DC-V01/build.py`; both GLBs and all four textures byte-identical between the two runs (SHA256 compared) |
| GLB reopen QA (`tools/qa_check.py`) | PASS 645/645 (MPDC), 580/580 (neutral base): bounds, ground contact, UVs, materials, degenerate faces, outward normals, applied transforms, LODs, UCX |
| Wheel clash probe (v003) | PASS — no body/interior/underbody vertex inside any tyre envelope (only the rear axle tube ends in its hub, by design) |
| Actual-output renders | clay + textured front/profile/rear/¾, orthographic top and underside, posed-open view, four close-up detail views (front fender, door belt, rear wheel at kerb height, grille low) (`renders/`) |
| Visual self-review vs E1 + moodbook p.10–12 | roof letters: layout, orientation and size read like E1 (zoomed top render checked letter by letter). Beacon between M/P; seal readable both sides. Silhouette: long flat hood, flat full-width grille face, formal roof, straight belt, round tail lamps. See "What Matt should look at" |
| Unreal 5.8 import / native readback | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Wheel rotation / steering / suspension / door motion in engine | **NOT_RUN — needs local Unreal (UE 5.8)**; pivots verified only by re-import + pose render |
| Matt approval | PENDING |

## Expected register status changes (head agent edits the sheet; not done by this agent)
- DC-V01: asset_status CLAIMED → DELIVERED; claim_owner "claude-cloud-agent — DC-V01" (prior
  "V01 - MPD Patrol Car / Lu / ChatGPT" is RELEASED per Drive); delivery_integrity
  "v003 SHA256 verified; clean rebuild byte-identical; QA 645/645; Unreal NOT_RUN" (v001, v002
  superseded); asset_user_approval PENDING; integration_status NOT_STARTED.
- DC-V02 "Depends on": a candidate production sedan base now exists
  (`SM_V01_Sedan_Base_Neutral.glb`, asset/DC-V01-v001) — not approved until Matt says so.

## UNIFICATION PROPOSALS
1. Register `SM_V01_Sedan_Base_Neutral` as the shared body for **DALLAS V07** (Dallas police
   sedan, 1963 Ford Galaxie): same generator, DPD livery as a second `POLICE_*` layer
   (black/white two-tone + door roundel + "DALLAS POLICE" lettering) — build.py already separates
   paint, decals and equipment from the base.
2. **DC-V02 taxi**: derive from the neutral base; add roof sign at `SOCKET_ROOF_SIGN`, fictional
   livery decals at the door-seal decal positions, lit/unlit sign materials as done for the beacon.
3. **DC-V05 parked sedans**: the section table `K` (control points + fillet radii per station) in
   build.py makes silhouette variants (roofline, deck length, crease sharpness) without new
   modelling, and openings/panels follow automatically because they are selected on the grid.
4. Hinge/steer/socket naming (`DOOR_xx`, `HOOD`, `TRUNK`, `STEER_Fx`, `WHEEL_xx`, `SOCKET_*`) is
   proposed as the WASHINGTON/DALLAS vehicle contract for V03–V09.

## What Matt should look at
1. `renders/SM_V01_PatrolSedan_MPDC_textured_three_quarter.png`, `_profile.png` and
   `clay_three_quarter.png`: is the shape still wonky? The body, front end, pillars and glass are
   new in v003.
2. `renders/SM_V01_PatrolSedan_MPDC_top.png`: roof text. The render has the nose down, so turn it
   90° to match E1 (nose right); it should read D M over C P. Also check letter size and weight
   against the photo, and the beacon between M and P.
3. `renders/..._detail_door_belt.png`: door seal text, window chrome, panel gaps.
   `..._detail_grille_low.png`: the new full-width grille with lamps in it.
4. `renders/..._posed_open.png`: hinges and steering still articulate on the new panels.
5. Open questions:
   - Whether the 1963 MPD cars carried side-spear chrome (E1 shows only a thin rocker strip, which
     is what is modelled).
   - Whether the hood needs the centre crease E1 hints at (not modelled; the hood is a smooth crown).
   - Colour hex values for cream and turquoise, if known.

## Files
PASS_PLAN.md · CONTEXT_ACK.json · EVIDENCE.md · HANDOFF.md · DEPENDENCY_LOCK.json ·
PCG_INTERFACE.json · REUSABLE_COMPONENTS.json · HIERARCHY.txt · MESH_STATS.txt ·
source/build.py · meshes/*.glb · textures/*.png · renders/*.png · DELIVERY_MANIFEST.json ·
SHA256SUMS.txt. Repo branch `asset/DC-V01-v003` (PR link in PAYLOAD_LINK.txt on Drive).
