# DC-V01 — MPD patrol car 1963 — HANDOFF (asset-v004)

Claimant: claude-cloud-agent (AGENTS lane) · delivered 2026-10-04 · stage A (asset) · set DC-EXT1
Brief WASHINGTON-2026-09-22-v001 · stage standard v001 · road-plans canon v002 · request doc
1CGp5evRrPST1P3r5soqPHBGuvm9VatvnqqleL0stpU8 (incl. vehicle benchmark addendum, Matt 2026-09-26).
**Not approved. Matt's review decides.** Delivery integrity and visual quality are separate.
v003 had no review from Matt when this pass started (Reviews EXT1, the claim folder and PR #9 were
checked). v004 continues v003's next-pass list under his v002 direction ("next pass. shape is
wonky"). If v003 is already preferred, v004 can be ignored; every version stays frozen.

## What changed in asset-v004 (Pass 6 — body character, rear end, trim, A-pillar fix)
Found by a harsh review of the v003 renders and a full-resolution re-read of E1:
- **Torn A-pillar edge fixed (present in v003 too).** A 2–3 cm painted door-frame strip sat between
  the door's front edge and the chrome window frame. The panel-gap shrink and bevel turned it into a
  zig-zag sliver along the A-pillar (and a thinner one at the C-pillar). The door's window-band edge
  is now the chrome frame's outer edge, so the frame meets the pillar cleanly, as on the real car
  (`renders/..._detail_spotlight.png`, `..._detail_door_belt.png`).
- **Plan view squared up.** v003 pulled the body in ~8 cm per side at nose and tail, so the car read
  boat-like from front and rear. E1 shows a near-rectangular plan; v004 pulls in ~4–5 cm. The grille
  opening is 10 cm wider, and the headlamp pairs moved out with it.
- **Hood crease + emblem (E1).** E1 shows a thin central longitudinal line on the hood and a small
  bright emblem at its front centre. v004 has a narrow-crown crease and a small generic chrome oval
  (`TRIM_HOOD_EMBLEM`, parented to HOOD). No brand artwork.
- **Blade bumpers.** v003's bumpers were an 11 cm round tube and read as a pipe from behind. v004 has
  a 15 cm '63-pattern blade (rolled top, curved face, lower lip). The wrap tips thin out round the
  fender corners, with rounded guards. Length over bumpers stays 546 cm (+2.4 % on the published
  533 cm); a first try reached 558 cm and was pulled back.
- **'63 tail lamps.** v003's 16.6 cm lamps read as marker lights. v004 has 20.4 cm round lamps with a
  deep chrome bezel and centre boss, and the lower half-moon of each lens is the clear back-up lamp
  (published 1963 styling: round tail lamps with half-moon lower lenses). The separate back-up dots
  are gone. The rear moulding moved up to clear the bezels, and there is a generic trunk-lock
  escutcheon.
- **Spotlight.** `POLICE_SPOTLIGHT` + `_LENS` on the driver A-pillar base: boss, swivel arm, 16 cm
  rounded bowl, bezel and lens. It is period-typical but **APPROXIMATE**: E1 can't show the driver
  side. It is detachable, and SOCKET_SPOTLIGHT_L moved to its pivot.
- Lower body tucks in less at nose and tail.
- Unchanged: roof/door/trunk/plate text and textures (byte-identical), wheels, interior, underbody,
  hinge pivots, material slots, LOD/UCX scheme (UCX_BODY_03/04 enlarged to the new bumpers).
  Plate sockets moved 2.5 cm out with the plates. The bumpers are now below the 300-face LOD1
  threshold, so they have no LOD1 (LOD policy unchanged).

v003 summary (superseded): body rebuilt as a structured filleted-section grid; glass from the skin;
full-width grille; roof text fixed (D M / C P from above, nose right); seal and plate redrawn.

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
  - '63-pattern chrome blade bumpers wrapping round the corners, with rounded guards (v004);
  - full-width recessed grille with fine horizontal bars, dividers and a chrome surround;
  - four 5¾-in sealed-beam headlamps in chrome buckets and bezels inside the grille;
  - 20.4 cm round tail lamps in deep chrome bezels, lower half-moon back-up lenses, rear moulding and
    trunk-lock escutcheon (v004);
  - small generic chrome hood emblem and hood centre crease (v004, E1);
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
  - driver A-pillar spotlight (v004, APPROXIMATE);
  - radio set.
- Textures (procedural PIL, embedded in the GLB, also in `textures/`): roof ID, door seal, trunk
  POLICE, plate. All other materials are flat PBR constants.

Dimensions:
- body 203 cm wide, 518 cm sheet metal, 141 cm high;
- from QA bounds: 217 cm wide over mirror and bumper ends, 546 cm over bumpers (published 533 cm,
  +2.4 %), antenna tip at 190 cm;
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
  POLICE_ANTENNA, POLICE_RADIO, POLICE_SPOTLIGHT(_LENS)  (detachable MPD layer)
  TRIM_HOOD_EMBLEM (child of HOOD)                      (v004)
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
- APPROXIMATE (v004): spotlight fit and presence (not visible in E1), hood emblem shape, tail-lamp
  size, bumper section.
- Not modelled: siren (socket only), radiator badge, side-spear trim.
- Photo evidence could not be downloaded from this sandbox (egress proxy blocks LoC, Commons,
  Truman Library, mpdc.dc.gov, dcmetropolicecollector.com); E1 was inspected from the project's
  Drive References copy; others are link-cited.

## Gates
| Gate | Result |
|---|---|
| Pass 1 evidence | done (EVIDENCE.md) |
| Clean rebuild | PASS — `out/` deleted twice, `python jobs/DC-V01/build.py`; both GLBs and all four textures byte-identical between the two runs (SHA256 compared). The four textures are also byte-identical to v003 |
| GLB reopen QA (`tools/qa_check.py`) | PASS 675/675 (MPDC), 595/595 (neutral base): bounds, ground contact, UVs, materials, degenerate faces, outward normals, applied transforms, LODs, UCX |
| A-pillar sliver check (v004) | PASS — per-object false-colour render of the A-pillar: only BODY and the chrome frame meet there; the painted door-frame sliver is gone |
| Wheel clash probe (v003) | PASS in v003; not re-run in v004 (wheels, wheel houses, interior and underbody unchanged; body change near the arches < 1 cm) |
| Actual-output renders | clay + textured front/profile/rear/¾, orthographic top and underside, posed-open view, six close-up detail views (front fender, door belt, rear wheel at kerb height, grille low, spotlight/A-pillar, tail lamp) (`renders/`) |
| Visual self-review vs E1 + moodbook p.10–12 | roof letters: layout, orientation and size read like E1 (zoomed top render checked letter by letter). Beacon between M/P; seal readable both sides. Silhouette: long flat hood, flat full-width grille face, formal roof, straight belt, round tail lamps. See "What Matt should look at" |
| Unreal 5.8 import / native readback | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Wheel rotation / steering / suspension / door motion in engine | **NOT_RUN — needs local Unreal (UE 5.8)**; pivots verified only by re-import + pose render |
| Matt approval | PENDING |

## Expected register status changes (head agent edits the sheet; not done by this agent)
- DC-V01: asset_status CLAIMED → DELIVERED; claim_owner "claude-cloud-agent — DC-V01" (prior
  "V01 - MPD Patrol Car / Lu / ChatGPT" is RELEASED per Drive); delivery_integrity
  "v004 SHA256 verified; clean rebuild byte-identical; QA 675/675; Unreal NOT_RUN" (v001–v003
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
1. `renders/SM_V01_PatrolSedan_MPDC_detail_spotlight.png`: the A-pillar. The torn-looking edge that
   v003 still had is gone, and the new spotlight is visible. Keep the spotlight or drop it? (It is
   APPROXIMATE.)
2. `renders/..._detail_tail_lamp.png` and `..._textured_rear.png`: '63-style round tail lamps with
   half-moon back-up lenses, and the blade bumper.
3. `renders/..._textured_three_quarter.png`, `_front.png`, `clay_three_quarter.png`: squarer ends,
   wider grille, hood crease. Is the shape still wonky?
4. `renders/..._posed_open.png`: doors (now with full chrome window frames), hood and trunk still
   articulate.
5. Open questions:
   - Did 1963 MPD cars carry a spotlight? Not visible in E1.
   - Do you want side-spear chrome (Galaxie 500 trim)? E1 shows only a thin rocker strip, which is
     what is modelled.
   - Colour hex values for cream and turquoise, if known.
   - The make/model is still unproven (Ford-pattern APPROXIMATE). A dated Nov-1963 MPD photo would
     settle it.

## Files
PASS_PLAN.md · CONTEXT_ACK.json · EVIDENCE.md · HANDOFF.md · DEPENDENCY_LOCK.json ·
PCG_INTERFACE.json · REUSABLE_COMPONENTS.json · HIERARCHY.txt · MESH_STATS.txt ·
source/build.py · meshes/*.glb · textures/*.png · renders/*.png · DELIVERY_MANIFEST.json ·
SHA256SUMS.txt. source/report.py. Repo branch `asset/DC-V01-v004` (PR link in PAYLOAD_LINK.txt on Drive).
