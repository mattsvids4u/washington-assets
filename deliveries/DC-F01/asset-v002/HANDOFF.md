# DC-F01 — Federal background building assemblies — HANDOFF v002

**Status: DELIVERED FOR MATT'S REVIEW. Not approved.** Only Matt approves. This handoff is
not an approval, and neither is a passing QA run. v001 is still waiting on its own review;
v002 does not replace or overwrite it.

- Claimant: claude-cloud-agent · Lane: AGENTS / DC-EXT1 · Priority P1 · PCG assembly
- Request revision: WASHINGTON-2026-09-22-v001 + Road Plan 05 integration addendum (doc modified 2026-09-25T10:29Z, unchanged)
- Brief WASHINGTON-2026-09-22-v001 · Stage standard v001 · Road plans canon v002. All re-read live on 2026-10-03, all unchanged (CONTEXT_ACK.json → `v002_run`)
- Claim: Drive `EXT1 / Claimed / DC-F01 — claude-cloud-agent` (CLAIM.json 1WLLiZbaP2XxED8WP4e-rD1_0xMeuX42x), 2026-10-02T10:30Z
- Made by: the scheduled routine run of 2026-10-03, which resumed its own claim.
- Source: `python jobs/DC-F01/build.py` rebuilds all three GLBs from scratch.
- Branch: `asset/DC-F01-v002`. The PR link is in `PAYLOAD_LINK.txt` (Drive folder).

## What changed in v002 (the Cannon only)

On 2026-10-03 Matt supplied HABS DC-2 photo **ref 03**: the Cannon NW corner (Independence Ave × New Jersey Ave), 1976,
public domain. It showed five places where v001 was wrong (`PHOTO_FINDINGS.md`). v002 fixes all of them. A matched camera
(`photo03_nw`) gives a like-for-like comparison: **`renders/review/CMP_ref03_vs_photo03_nw.png`** (photo | v001 | v002).

| # | ref 03 shows | v001 had | v002 builds |
|---|---|---|---|
| 1 | NW chamfer: two fluted columns in antis in a full-height recess, framing a tall arched window with archivolt and keystone; a balustraded balcony on consoles | plain chamfer, small arched window | as seen. The corner pavilions on both streets repeat it: pilaster, pedimented window, antis bay with an arched window, pedimented window |
| 2 | door at the top of a wide two-flight stair; a raised terrace with a solid wall and a panelled parapet; a second stair on Independence Ave | door at grade, 3 low steps | terrace wall (2.2 m) + parapet (3.2 m) in front of a basement areaway on Independence Ave, the corner and New Jersey Ave; 11 + 6 riser corner stair with cheek blocks; 18-riser side stair to a new door on Independence Ave |
| 3 | arched windows above the terrace; basement hidden | basement windows at grade on the street fronts | basement windows now light the areaway behind the wall |
| 4 | **single** giant pilasters on New Jersey Ave, ~17 bays; a small cornice over each lower window | coupled pilasters | single pilasters on every front; 17 New Jersey Ave bays between the corner and SW pavilions; window cornices |
| 5 | the parapet is the skyline: a solid blocking course with dies, balusters only on the chamfer; no attic visible | balustrade everywhere; attic reads strongly | solid parapet with dies; attic set back 7.0 m and lowered to 25.5 m, so it is hidden from the ref 03 vantage |

**Colonnade (PROBABLE, not photo-confirmed):** 34 single, evenly spaced Doric columns (2.83 m c/c) replace v001's
17 coupled pairs. A tree hides the colonnade in ref 03. Single is chosen because the corner columns and the pilastrade are single,
and F02 read the twin Senate Office Building as single. This now agrees with F02 (UNIFICATION PROPOSAL 0).

**Unchanged:** the Annex and Folger GLBs are **byte-identical to v001** (sha256 match), and so are all 27 textures. Their
renders in this package are the v001 renders, carried forward.

| Asset | LOD0 / LOD1 / LOD2 tris | Size (m) | GLB |
|---|---|---|---|
| SM_F01_Cannon (v002) | 218,240 / 72,420 / 6,836 | 137.72 × 122.63 × 25.90 incl. terrace and stairs | 22.5 MB |
| SM_F01_LOCAnnex (= v001) | 103,476 / 41,836 / 5,556 | 126.96 × 72.84 × 31.20 | 12.6 MB |
| SM_F01_Folger (= v001) | 63,878 / 7,054 / 1,008 | 85.38 × 46.33 × 14.63 | 6.1 MB |

Interface changes on the Cannon:
- **Bounds grow** by the terrace: the wall stands 3.2 m in front of the building face, and the corner stair runs out a further 4 m.
- **Collision:** 10 UCX hulls (was 5). 5 wing hulls + 3 terrace + 2 stairs.
- **Sockets:**
  - New: `SOCKET_Entrance_Independence_W`.
  - `SOCKET_Entrance_Main_NW_Rotunda` keeps its v001 name and moves up to the door sill (z = 3.2 m).
  - Other sockets unchanged.
- Material slots are unchanged.
- Pivot and axes are as v001: footprint bbox centre at grade, +X east, +Y north. Units are Blender metres; UE 5.8 glTF import gives cm.

## Gates

| Gate | Result |
|---|---|
| GLB reopen QA (`tools/qa_check.py`) | **20/20 PASS** on all three GLBs |
| Shell orientation (`build_report.json` → `inward_wound_shells`) | **0** on all 9 LOD meshes |
| Visible coincident faces (`run_coplanar.sh` → `coplanar_report.txt`) | **PASS** on all 9 LODs: Cannon LOD1 0.0012 m² (one sliver at the SW corner), everything else 0. The gate fails above 0.05 m² per LOD |
| Clean rebuild (delete `out/`, rerun) | **byte-identical**: all 32 output files hash-match a second rebuild into an empty directory |
| Photo comparison | **Cannon: DONE** against ref 03 (matched camera; side-by-side above). **Folger: DONE** in v001 (ref 01). **Annex: NOT_DONE** (ref 04 is 530 px, too small) |
| Moodbook | pp. 10–12 as in v001; the night views (`*_night_*`) are the tungsten-on-charcoal check. v002 changes geometry only |
| Renders I inspected | Cannon: standard clay/textured ×4; review street views; `photo03_nw`, `detail_corner`, `detail_nj` and `detail_colonnade`; night; base-colour/roughness/normal passes; LOD1/LOD2 at `street_ne` and `photo03_nw`. LOD2 notches the recesses so the columns do not jump at the LOD switch |
| Unreal import / readback | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Motion / drive-by tests | **NOT_RUN — needs local Unreal (UE 5.8)** |

## Evidence gaps

1. **Cannon colonnade pairing.** Single is built as PROBABLE. The HABS colonnade close-up would settle it. It is one parameter: `CANNON["n_cols"]`.
2. **Cannon attic.** The setback (7.0 m) and height (roof 25.5 m) are calibrated only so that the attic stays hidden from the ref 03 vantage. An aerial would fix them (Trikosko 1960, LoC 2016646402, or 1964, 2016646401).
3. **Cannon parts not in the photo, all APPROXIMATE:**
   - the First St and C St fronts: single pilasters, ~5 m bays, no terrace;
   - the NE and SW pavilions;
   - the terrace ends: plain return walls at the NE and SW corners;
   - the exact position of the Independence Ave side stair.
4. **The terrace sits on a flat site.** The real site falls toward New Jersey Ave, which probably explains the terrace. DC-B01 should fit it to the terrain.
5. **Frame identification.** Cannon and the twin SOB are near-identical. Ref 03 is identified as the Cannon by its HABS DC-2 gallery, as recorded in `refs/incoming/SOURCES.md`.
6. Still open from v001: the Annex has no readable photo; there is no 1963-dated photo of any of the three; DC-R02 footprints were not consumed; outside archives are still blocked from this sandbox (re-checked 2026-10-03).

## APPROXIMATE / FICTIONALISED

- **APPROXIMATE:** every Cannon dimension not measured from ref 03, namely:
  - recess depth;
  - window widths;
  - pavilion spacing;
  - terrace heights;
  - stair rises.

  The full list is in EVIDENCE.md, under "Photo inspection for v002" and in the Cannon evidence card. The Annex and Folger labels are as in v001.
- **Simplified carving:** the keystones and arch spandrels are plain. Ref 03 shows carved cartouches and spandrel ornament. The 1908 carving is public domain, so this is a budget simplification for EXT1 distance, not a rights stand-in. The other stand-ins are as in v001.
- **Nothing FICTIONALISED.**

## Expected register status changes (for the head agent; I did not edit the sheet)

- DC-F01 `asset_status`: CLAIMED → **DELIVERED (v001 C10 trio; v002 Cannon photo correction)**, `claim_owner` **claude-cloud-agent**
- `delivery_integrity` → **"v002 SHA256SUMS + clean-rebuild QA + coplanar gate; Unreal NOT_RUN"**
- `asset_user_approval`: **stays PENDING**

## Scope still open

- **v003:** U.S. Courthouse, Post Office Department and IRS (Federal Triangle, C2–C4). This needs DC-C20 v005 (approved on Drive), and DC-C18 if it is approved by then.
- **SOB / NSOB:** F02 keeps both (DECISIONS row 4).

## UNIFICATION PROPOSALS

0. **Cannon (F01) and SOB (F02) now agree on single columns.** The F02 v003 SOB and this Cannon could share:
   - the corner-pavilion composition (the antis bay and pedimented windows);
   - the terrace and stair kit (`cannon_terrace`, `cannon_antis_bay`, `cannon_ped_window` in build.py; generator-agnostic frames).

   If the twin has the same corner, F02 can lift these functions. I have not touched F02's files.
1. **DC-C19 runtime-light Doric**, as in v001: ~1.8k tris per column at LOD0. The Cannon now has 40 columns this way. Swap point: `SOCKET_C19_Order_Swap_Colonnade`.
2. **Two geometry gates for all agent deliveries** (per-shell orientation audit + `coplanar_check.py`), as proposed in v001. v002 passed both, first time.
3. **Photo-matched review cameras.** `render_review.py` now supports a rising front (`shift_y`), so a level camera reproduces view-camera photos (HABS/LoC large format) with vertical verticals. Propose this as the standard way to compare against archive photos.

## What Matt should look at

1. **`renders/review/CMP_ref03_vs_photo03_nw.png`**: your HABS photo next to v001 and v002 from the same camera.
2. `SM_F01_Cannon_textured_detail_corner.png` (door, two-flight stair, balcony, antis bay) and `..._detail_nj.png` (single pilastrade, window cornices, terrace parapet).
3. `SM_F01_Cannon_textured_detail_colonnade.png`: **single columns now (PROBABLE)**. Say if you know they are coupled.
4. `SM_F01_Cannon_textured_street_ne.png`: the NE end of the terrace, which is a guess.
5. Photos that would close the rest: the HABS colonnade close-up; any aerial showing the Cannon roof; the large Horydczak JPEG of the Annex (`PHOTO_REQUEST.md`).

## Files

`PASS_PLAN.md` (Pass log 10) · `CONTEXT_ACK.json` · `EVIDENCE.md` · `HANDOFF.md` · `DECISIONS.md` · `PHOTO_FINDINGS.md` · `PHOTO_REQUEST.md` ·
`DEPENDENCY_LOCK.json` · `PCG_INTERFACE.json` · `REUSABLE_COMPONENTS.json` · `NEXT_CHAT_PROMPT.txt` + `DISPATCH_LOG.json` ·
`source/` (build.py, f01lib.py, f01mat.py, render_review.py, render_all.sh, render_cannon_v002.sh, make_delivery.sh, make_previews.py,
coplanar_check.py, run_coplanar.sh) · `coplanar_report.txt` · `build_report.json` · `meshes/*.glb` · `textures/*.png` · `renders/` ·
`references/` (refs 01–02, and `incoming/` refs 03–04 with SOURCES.md) · `drive_previews/` · `research/` · `context/` · `DELIVERY_MANIFEST.json` · `SHA256SUMS.txt`
