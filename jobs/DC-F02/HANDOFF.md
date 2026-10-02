# DC-F02 — HANDOFF — asset-v003 (Senate Office Building, C7) — detail and accuracy pass

**Status: DELIVERED FOR REVIEW. Not approved.** Only Matt approves. Nothing has been imported into
Unreal or placed in a map.

- **Supersedes** asset-v002 ([PR #6](https://github.com/mattsvids4u/washington-assets/pull/6)) and
  asset-v001 ([PR #4](https://github.com/mattsvids4u/washington-assets/pull/4)) for review. Both
  are kept unchanged.
- **Claimant:** claude-cloud-agent. Claim folder `Claimed / DC-F02 — claude-cloud-agent`
  (10XO2Q6ojh0ux0fU8WTWsSwp9klgD47tV).
- **Context:** brief WASHINGTON-2026-09-22-v001 · road-plans canon WASHINGTON-ROADPLANS-v002 ·
  CONTEXT_ACK.json.
- **DALLAS:** NEW. No DALLAS file was touched.

## Why v003

Matt asked for another detail and accuracy pass. I re-read enlarged crops of E11 (LoC 2003655456,
c.1909: corner, colonnade, Delaware front) against the modern views E15 and E16; see EVIDENCE.md,
"Pass 5 close reading". That reading found three v002 errors and several missing details.

## What changed (v002 → v003)

| Area | v003 | Was in v002 | Evidence |
|---|---|---|---|
| Chamfer piers | **Plain** solid piers | Framed windows and cartouches on the piers (wrong) | E11, E15, E16 |
| Corner returns (Constitution and Delaware) | **New 12 m return on each front** repeating the corner motif: framed-window pier (hood, consoles, **low pediment**, carved oval cartouche above) / **recessed bay with 2 Doric columns in antis before a tall arched window** with a balconette / framed-window pier, over 3 arched base windows, with entablature and solid attic. The colonnade and pilastrade now start after the return | One plain 8 m pavilion bay (Constitution); nothing on Delaware | E11, E15, E16 |
| Columns in antis | Stand in the pier plane, with the architrave flush to the pier faces | Set back, with the architrave behind the piers | E11, E16 |
| Tall arched windows | Small-pane grid (4 lights wide, about 0.75 m rows), radiating fanlight bars, keystone, **dark glazing** | 6/6 sash with a random "blinds" state that read as blank | E11 |
| Ground-storey arches | **Tall and narrow:** 1.2 m wide × 4.1 m high | Widened to 1.5 m (wrong direction) | E11 colonnade crop |
| Chamfer base | Plain rustication, one arched bronze doorway, **console brackets** flanking the door head under the balconette, stair between **wide granite podium blocks** across the chamfer | Two arched windows beside the door; narrow cheek blocks | E11, E15, E16 |
| Corner attic | Raised block lowered to **+0.5 m** above the parapet; the flag socket moved down to z 31.2 m | +1.1 m | E16 |
| Delaware centre pavilion | Pier / columns in antis / pier motif | Projecting pilastrade with a solid attic | E11, low resolution: **APPROXIMATE** |
| Basement under the pavilions | Slope-exposed basement windows added | Windowless granite | Consistency with the adjoining pilastrade |

Unchanged:

- the 34-column Constitution loggia (now spaced 3.18 m c/c across 26–133 m), with responds behind,
  which is the "double colonnade";
- the 7 m N–S grade (3 storeys on Constitution, 5 on C St), courts, roof, materials, LOD scheme,
  UCX and the other sockets.

## Build facts (asset-v003)

- `meshes/SM_F02_SenateOfficeBuilding.glb` is about 51 MB. Regenerate it with
  `python jobs/DC-F02/build.py` (seed 1963).
- LOD0 is 178,793 faces, LOD1 66,719 and LOD2 9,077. The site helper is 41 faces.
  There are 5 `UCX_` collision boxes.
- Bounds are 161.0 × 128.0 × 31.2 m, including the optional 9 m site apron.

## Verification (this sandbox)

| Gate | Result |
|---|---|
| `tools/qa_check.py --expect-size-cm 16100 12800 3120` | **26/26 PASS** (QA_REPORT.txt) |
| Clean rebuild, twice | **Byte-identical** GLB and textures (SHA-256 compared) |
| Renders | Clay and textured (front / profile / rear / ¾); street views; photo-matched corner (E11 viewpoint); corner close-up; new Delaware centre-pavilion view; night; aerial; `COMPARE_E11_vs_v003.png` |
| Unreal 5.8 import / readback | **NOT_RUN — needs local Unreal (UE 5.8)** |
| UCX recognition via the UE glTF/Interchange importer | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Motion test (drive-by, day and night) | **NOT_RUN — needs local Unreal (UE 5.8)** |

## Remaining mismatches and gaps

1. **Footprint, wing depth and the grade drop are still APPROXIMATE.** The DC-R02 SOB card is still
   unread (Matt's PC only). Return width (12 m) and corner-bay width (7 m) are photo estimates.
2. **C St and First St fronts** have no photo. A pilastrade with arched base windows is assumed.
   E12 (Horydczak, LoC 2019683168) would confirm the NW corner and the C St slope.
3. **Delaware centre pavilion** is from a blurry corner of E11. A straight-on Delaware Ave photo
   would settle it.
4. **Carving is simplified:** cartouches are oval shields, capitals are generic Roman Doric, and the
   attic tablet is blank. E15 shows lettering on it today, but the 1963 inscription is not legible
   in E11, so no name is asserted.
5. Stone is clean, as restored. 1963 grime belongs to Age + Use (DC-F02-W01).

## APPROXIMATE / FICTIONALISED

- **APPROXIMATE:**
  - everything in PARAMS (footprint, storeys, column spacing, `corner_bay`, `return_w`,
    `return_recess`, `base_win_w`, `attic_raise`);
  - the C St / First St details and the Delaware centre pavilion;
  - skylight ridges, court floor level and the frame paint colour.
- **FICTIONALISED:** window interior states (glazing atlas) only.

## Expected register changes (head agent; not edited by me)

- DC-F02: asset_status → CLAIMED (in progress; 1 of 9 named uplifts delivered).
  claim_owner "claude-cloud-agent — DC-F02". delivery_integrity "asset-v003 (Senate Office Building,
  detail pass vs LoC 2003655456) SHA256SUMS; QA 26/26; clean rebuild byte-identical; UE NOT_RUN".
  asset_user_approval stays PENDING.

## UNIFICATION PROPOSALS

1. **DC-C19 classical orders:** swap in its Doric order if it matches (same diameter/height params).
2. **DC-G10 balustrade:** share one Capitol Hill baluster profile.
3. **Reusable functions:**
   - `recessed_bay()`, `framed_pier()`, `corner_return()`, `pavilion_base()`, `arched_window()`
     (now with a `tall` grid) and `window(pediment=True)`;
   - these make up a reusable Beaux-Arts pavilion kit for DC-H09, DC-H10 and the Cannon building in
     F01 (Cannon is the SOB's twin design by Carrère & Hastings).
4. **DC-S16 flag:** mount on `SOCKET_Flag_Corner_Attic`.

## What Matt should look at

1. `renders/SM_F02_SenateOfficeBuilding_COMPARE_E11_vs_v003.png`: the c.1909 photo against v003 at
   a matched viewpoint.
2. `renders/…_detail_corner_pavilion.png`: the chamfer and both returns, against E15 and E16.
3. `renders/…_street_delaware_centre_pavilion.png`: the APPROXIMATE Delaware centre pavilion.
4. `renders/…_street_constitution_east.png` and `…_street_constitution_night.png`: the drive-by read.
