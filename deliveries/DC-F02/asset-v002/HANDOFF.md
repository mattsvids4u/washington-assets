# DC-F02 — HANDOFF — asset-v002 (Senate Office Building, C7) — photo-matched revision

**Status: DELIVERED FOR REVIEW. Not approved.** Only Matt approves. Nothing has been imported into
Unreal or placed in a map. asset-v001 is kept unchanged at `deliveries/DC-F02/asset-v001`
([PR #4](https://github.com/mattsvids4u/washington-assets/pull/4)); this version supersedes it for review.

- **Claimant:** claude-cloud-agent. Claim folder `Claimed / DC-F02 — claude-cloud-agent`
  (10XO2Q6ojh0ux0fU8WTWsSwp9klgD47tV).
- **Context:** brief WASHINGTON-2026-09-22-v001 · road-plans canon WASHINGTON-ROADPLANS-v002 ·
  CONTEXT_ACK.json.
- **DALLAS:** NEW. No DALLAS file was touched.

## Why v002

On 2026-10-02 Matt supplied five photographs. They are the first images inspected for this job
(EVIDENCE.md, "Inspected photographs"):

- **E11:** LoC 2003655456, the c.1909 American Press Ass'n view of the SW corner (stored, public domain).
- **E10:** LoC 2024639984, the 27 Mar 1967 Leffler aerial (stored).
- **E15 / E16:** two modern colour views of the corner (described only; rights unconfirmed).
- **E17:** a 1960s Alamy view of the New SOB (link/description only; for the next building).

They showed v001's corner was **wrong**:

- v001 had 4 columns in antis and 3 doors. The photos show **2 free-standing columns before one tall
  round-arched window**, between two solid piers, over **one** round-arched doorway.
- v001's ground-storey windows were rectangular. In the photos they are **round-arched**.

## What changed (v001 → v002)

| Area | v002 | Evidence |
|---|---|---|
| SW corner pavilion | Rebuilt as follows. **Two solid piers**, each with a framed piano-nobile window (hood, consoles, surround), an **oval carved cartouche** above, and pilaster strips at the chamfer arrises. A **recessed central bay** with **2 free-standing Doric columns** before **one tall round-arched window** (fanlight bar, sash grid, low balustraded balconette). One **round-arched bronze doorway** (raised panels, transom, glazed fanlight, keystone, impost band) over a **projecting 6-riser granite stair with cheek blocks**. One arched base window in each pier. A **raised attic block** with coping and a blank tablet. | E11, E15, E16 |
| Ground-storey windows, all street fronts | Round-arched, with real stone spandrels (extruded arcs), a glazed fanlight, a fanlight bar and a keystone. Widened to about 1.5 m to match the rhythm in E11 | E11, E15, E16 (C St / First St assumed the same) |
| Flag | `SOCKET_Flag_Corner_Attic` on the raised corner attic, replacing the roof-centre socket. The flag itself belongs to DC-S16 | E11, E15, E16 |
| Entrance socket | Moved to the new doorway | — |
| Renders | Added `photo_match_E11_corner` (camera matched to E11) and `detail_corner_pavilion`. `COMPARE_E11_vs_v002.png` puts the photo and the render side by side | — |

Unchanged from v001:

- the 34-column Constitution loggia;
- the pilastrade fronts;
- the 7 m N–S grade (3 storeys on Constitution, 5 on C St);
- the courts, the roof, LOD scheme, UCX, materials and textures.

The 1967 aerial (E10) **confirms** the closed quadrangle, the slim wings and the flat roof.

## Build facts (asset-v002)

- `meshes/SM_F02_SenateOfficeBuilding.glb` is about 50 MB. Regenerate it with
  `python jobs/DC-F02/build.py` (seed 1963).
- LOD0 is 173,973 faces, LOD1 66,617 and LOD2 9,065. The site helper is 41 faces.
  There are 5 `UCX_` collision boxes.
- Bounds are 161.0 × 128.0 × 31.8 m, including the optional 9 m site apron. The corner attic now
  reaches 24.5 m above Constitution grade.

## Verification (this sandbox)

| Gate | Result |
|---|---|
| `tools/qa_check.py --expect-size-cm 16100 12800 3180` | **26/26 PASS** (QA_REPORT.txt) |
| Clean rebuild, twice | **Byte-identical** GLB and textures (SHA-256 compared) |
| Renders | Clay and textured (front / profile / rear / ¾); street views including the photo-matched corner; night; aerial. Self-reviewed against E11, E15 and E16 |
| Unreal 5.8 import / readback | **NOT_RUN — needs local Unreal (UE 5.8)** |
| UCX recognition via the UE glTF/Interchange importer | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Motion test (drive-by, day and night) | **NOT_RUN — needs local Unreal (UE 5.8)** |

## Remaining mismatches and gaps (honest list)

1. **Footprint, wing depth and the grade drop are still APPROXIMATE.** The DC-R02 SOB card is still
   unread (Matt's PC only). Reconciling means editing `PARAMS`, not remodelling.
2. **Column order detail:** Doric is per AOC. The corner columns in E11 look similar. Capital and
   base profiles are generic.
3. **Cartouches, window frames and the attic tablet** are simplified. The tablet inscription in E11
   isn't legible, so it is blank (no name asserted).
4. **The arched base windows** may still be slightly small against E11, and the arch depth in the
   rusticated courses is simplified (keystone, but no full voussoir ring).
5. **Corner returns:** in E11, vertical members (columns or pilasters) appear right next to the
   corner piers on the Delaware return. v002 keeps a solid return bay with one framed window there
   (as E15/E16 show on the Constitution return). The scan is too small to settle it; please check.
6. **C St and First St fronts** have no photo yet. Arched base windows and a pilastrade are assumed.
   E12 (Horydczak NW corner, LoC 2019683168) would confirm.
7. Window awnings in E11 are seasonal dressing and not modelled. The photo is also c.1909, so for
   Age + Use (W01), 1963 grime should be heavier than in the modern restored photos.

## APPROXIMATE / FICTIONALISED

- **APPROXIMATE:** everything in PARAMS (footprint, storeys, column spacing, `corner_bay` 7.0 m),
  the C St / First St details, skylight ridges, court floor level and the frame paint colour.
- **FICTIONALISED:** window interior states (glazing atlas) only.

## Expected register changes (head agent; not edited by me)

- DC-F02: asset_status → CLAIMED (in progress; 1 of 9 named uplifts delivered).
  claim_owner "claude-cloud-agent — DC-F02". delivery_integrity "asset-v002 (Senate Office Building,
  photo-matched to LoC 2003655456) SHA256SUMS; QA 26/26; clean rebuild byte-identical; UE NOT_RUN".
  asset_user_approval stays PENDING.

## UNIFICATION PROPOSALS

1. **DC-C19 classical orders:** swap in its Doric order if it matches (same diameter/height params).
2. **DC-G10 balustrade:** share one Capitol Hill baluster profile.
3. **`arched_window()` / `arch_spandrels()` / `window()` + glazing atlas:** reusable for any
   corridor masonry bay (DC-C07 / DC-C18 / DC-H09 / DC-H10), with one night-state convention for
   DC-L01.
4. **DC-S16 flag:** mount on `SOCKET_Flag_Corner_Attic`.

## What Matt should look at

1. `renders/SM_F02_SenateOfficeBuilding_COMPARE_E11_vs_v002.png`: the c.1909 photo against the v002
   render at a matched viewpoint.
2. `renders/…_detail_corner_pavilion.png`: corner detail against E15 and E16.
3. `renders/…_street_constitution_east.png` and `…_street_constitution_night.png`: the drive-by read.
4. If it's close enough, the next step is **asset-v003, the New Senate Office Building**, using E17
   as a lead. It needs a permitted copy of a 1958–65 photo, since E17 is Alamy.
