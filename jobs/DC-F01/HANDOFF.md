# DC-F01 — Federal background building assemblies — HANDOFF v001

**Status: DELIVERED FOR MATT'S REVIEW. Not approved.** Only Matt approves. This handoff is
not an approval, and neither is a passing QA run.

- Claimant: claude-cloud-agent · Lane: AGENTS / DC-EXT1 · Priority P1 · PCG assembly
- Request revision: WASHINGTON-2026-09-22-v001 + Road Plan 05 integration addendum (doc modified 2026-09-25T10:29Z)
- Brief WASHINGTON-2026-09-22-v001 · Stage standard v001 · Road plans canon v002 (2026-09-30)
- Claim: Drive `EXT1 / Claimed / DC-F01 — claude-cloud-agent` (CLAIM.json 1WLLiZbaP2XxED8WP4e-rD1_0xMeuX42x), 2026-10-02T10:30Z
- Source: `jobs/DC-F01/build.py` (+ `f01lib.py`, `f01mat.py`). `python jobs/DC-F01/build.py` rebuilds everything from scratch in ~50 s.

## What was built (v001 = the C10 hard-locks)

v001 covers the three buildings the Road Plan 05 addendum assigns to F01 in C10, in their
autumn 1963 state, under their 1963-facing names:

| Asset | GLB | LOD0 / LOD1 / LOD2 tris | Size (m) | Identity features modelled |
|---|---|---|---|---|
| **Library of Congress Annex** | `SM_F01_LOCAnnex.glb` | __ANNEX_TRIS__ | __ANNEX_SIZE__ | 400 × 225 ft footprint; corner and central pavilions linked by recessed fenestrated curtains; vertically linked bays (bronze spandrels with honeysuckle ornament) between narrow marble piers; NC pink granite skirt; attic set back 35 ft; three-tier aged copper roof; 3 + 3 bronze door pairs (W/E) and the south pair on the owl-and-lamp stair; figure-per-leaf door stand-ins |
| **Folger Shakespeare Library** | `SM_F01_Folger.glb` | __FOLGER_TRIS__ | __FOLGER_SIZE__ | 226 × 111 × 48 ft on a marble plinth; nine tall windows with cast-aluminium Art Deco grilles between fluted pilasters; nine 6 × 6 ft relief panels (stand-ins); incised frieze; broad attic carrying the verified Jonson and Johnson inscriptions; slight top recession; end entrances with mask medallions; three-bay west front; blank east wall with comedy/tragedy masks; U-plan rear with the 1958–59 one-storey infill; terrace with the 25 × 135 ft lawn bed, front wall and stairs; marble Puck fountain on the west lawn (stand-in figure) |
| **Cannon House Office Building** | `SM_F01_Cannon.glb` | __CANNON_TRIS__ | __CANNON_SIZE__ | hollow trapezoid on Square 690, New Jersey Ave diagonal; rusticated arcaded base (keystoned arched windows, basement windows, granite plinth); **34 fluted Doric columns (17 coupled pairs)** in a deep loggia on Independence Ave; coupled-pilaster pilastrade on the other fronts; Doric entablature with triglyphs and mutules; balustrade; recessed attic (4th + 5th storeys); chamfered NW rotunda-corner main entrance; limestone court fronts; 1955 garage-deck court |

Each GLB contains `<name>_LOD0/1/2`, convex `UCX_<name>_NN` collision hulls, and `SOCKET_*`
empties (entrances, lamps, typed kit swap points, and pending signage). Material slots are stable
`M_F01_*` names, typed by ITS ALIVE family in `PCG_INTERFACE.json`. Portable PBR sources
(BaseColor / ORM / Normal PNG) are in `textures/`.
Units are Blender metres; UE 5.8 glTF import gives cm. Pivot is at the footprint bbox centre at
grade, +X east, +Y north.

## Gates

| Gate | Result |
|---|---|
| GLB reopen QA (`tools/qa_check.py`) | __QA__ |
| Clean rebuild (delete `out/`, rerun) | __REBUILD__ |
| Actual-output renders | clay + textured front/profile/rear/¾ (`renders/standard/`); street-level car-height views, night lit-window views, base-colour/roughness/normal passes, clay street views and LOD1/LOD2 views (`renders/review/`) |
| Unreal import / readback | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Motion / drive-by tests | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Visual comparison against reference photos | **NOT_DONE.** No reference image could be opened in this cloud environment (see Evidence gaps) |
| Visual comparison against the moodbook images | **NOT_DONE.** The moodbook was read as text only; pp. 10–12 directives were applied (see CONTEXT_ACK.json) |

## Evidence gaps (what Matt should know first)

1. **No photos were inspected.** The environment's network allowlist blocks every image
   host (loc.gov, Wikimedia, NARA, NPS, AOC, DC Planning, Flickr, archive.org). The Drive
   connector returns no image data, so the two starter photos in `References/DC-F01` were not viewable either.
   Facts come from search-result text quoting authoritative pages (AOC, LoC, SAH Archipedia,
   DC HPO/NRHP forms, Folger, House Historian); see `EVIDENCE.md` and `research/`.
2. **DC-R02 footprints not consumed.** The approved R02 data package lives on Matt's PC only,
   so footprints use published dimensions. Re-snap them to the R02 evidence cards before placement.
3. Bay counts not stated in text, window sizes, storey heights, moulding profiles and the
   Cannon's facade lengths are **APPROXIMATE**. The Cannon footprint is cross-checked against
   AOC's 70,000 sq ft court: these dimensions give ≈ 69,500 sq ft.

## APPROXIMATE / FICTIONALISED

- **APPROXIMATE (examples, full list in EVIDENCE.md):**
  - Annex: heights, pavilion widths and bay counts; spandrel material (bronze is a PROBABLE inference from SAH wording).
  - Folger: window size; terrace layout; rear wing widths; inscription positions.
  - Cannon: overall dimensions and angle, heights, column size, the chamfered corner form, and the attic's look; coupled columns are PROBABLE.
- **Labelled stand-ins (rights unconfirmed, never likenesses):**
  - Lawrie bronze door figures (Annex).
  - John Gregory reliefs (Folger).
  - Brenda Putnam's Puck (Folger).
  - Comedy/tragedy masks (Folger).
  - Owls and lamp standards (Annex).
- **Inscriptions:**
  - Carved: only the two Folger quotations, whose wording is VERIFIED; their placement over the end bays is APPROXIMATE, and Liberation Serif is a stand-in typeface.
  - Not carved: no other building names, because their positions are unverified. They are marked with `SOCKET_Signage_*_PENDING`.
- **Placeholder:** `M_F01_Turf_Placeholder` on the Folger lawn bed, to be replaced by DC-N03 via `SOCKET_Lawn_N03_Turf`.
- **Nothing FICTIONALISED:** all three identities, names and histories are real.

## Expected register status changes (for the head agent; I did not edit the sheet)

- DC-F01: `asset_status` UNCLAIMED → **CLAIMED** (2026-10-02) → **DELIVERED (v001, partial scope: C10 trio)**
- `claim_owner` → **claude-cloud-agent**
- `delivery_integrity` → **"v001 SHA256SUMS + clean-rebuild QA; Unreal NOT_RUN"**
- `asset_user_approval`: **stays PENDING**
- Housekeeping seen on Drive (register lags):
  - DC-C20 has a "v005 APPROVED" delivery folder, but its row says UNCLAIMED.
  - DC-V01 was claimed by another claude-cloud-agent session on 2026-10-02 (row still shows Lu / ChatGPT).
  - DC-X14 has an active claude-cloud-agent claim.

## Scope still open in DC-F01 (next versions)

- **v002:**
  - U.S. Courthouse, plus Post Office Department and IRS (Federal Triangle, C2–C4).
  - These need DC-C18 (not yet approved) and DC-C20 v005 (approved on Drive).
- **SOB / NSOB ownership conflict:**
  - The DC-F01 request lists the Senate Office Building and New Senate Office Building.
  - DC-F02 and Road Plans canon v002 assign both to F02.
  - **Matt: confirm the owner.** F01 has not built either.

## UNIFICATION PROPOSALS

1. **DC-C19 runtime-light Doric.**
   - C19 v004 is sculpt-review density (Corinthian LOD0 740k tris) and lists a lighter runtime version as open.
   - F01's background Doric (Vignola profile with entasis, 20 two-segment flutes, ~1.8k tris per column at LOD0, 12-sided at LOD1, octagonal at LOD2) could seed that variant.
   - Swap point: `SOCKET_C19_Order_Swap_Colonnade`.
2. **C18 adapter from the Annex bay.**
   - The Annex's vertically linked bay (bronze spandrel, sunk window, narrow marble pier) is a 1930s federal Art Deco bay type.
   - If C18's federal limestone bay gains an "Art Deco vertical-bay" adapter, F01 v002 (Courthouse, Federal Triangle) can consume it instead of bespoke bays.
3. **Shared marble/granite/copper material slots.**
   - Five `M_F01_*` material sets are portable and seeded: Georgia marble ashlar, alternating-course marble, NC pink granite, aged copper roof, glazed brick.
   - Propose registering them as WASHINGTON city material slots (F02, H-series block-outs).
4. **Night glazing slot convention.**
   - F01 uses a two-slot glazing convention: `M_F01_Glass` (day) and `M_F01_Glass_NightLit` (~35 %, stable hash).
   - Propose it as the corridor-wide convention so DC-L01 can drive night states without per-building logic.
5. **No DALLAS parent** (NEW), so there is nothing to propose upstream to DALLAS.

## What Matt should look at

1. `renders/review/*_textured_street_*.png`: the three buildings at car height, compared with your own knowledge or photos of each.
2. **Cannon colonnade pairing** (`SM_F01_Cannon_textured_detail_colonnade.png`): coupled (built) vs evenly spaced single columns. It is one parameter (`CANNON["n_pairs"]`, `pair_cc`).
3. **Annex spandrels** (`SM_F01_LOCAnnex_textured_street_w.png`): bronze (built, PROBABLE) vs marble.
4. **Folger front** (`SM_F01_Folger_textured_street_n.png`, `detail_bays`): grilles, relief stand-ins, attic inscriptions.
5. Night views (`*_night_*.png`) for the moving-car-at-night read.
6. Decisions: the SOB/NSOB owner; whether to keep the Folger inscriptions at APPROXIMATE positions; any of the dimensions above.

## Files

`PASS_PLAN.md` · `CONTEXT_ACK.json` · `EVIDENCE.md` · `HANDOFF.md` · `DEPENDENCY_LOCK.json` · `PCG_INTERFACE.json` ·
`REUSABLE_COMPONENTS.json` · `NEXT_CHAT_PROMPT.txt` + `DISPATCH_LOG.json` (successor note; no claim queued) ·
`source/` (build.py, f01lib.py, f01mat.py, render_review.py, render_all.sh, make_delivery.sh, make_previews.py) ·
`meshes/*.glb` · `textures/*.png` · `renders/` · `research/` · `build_report.json` · `DELIVERY_MANIFEST.json` · `SHA256SUMS.txt`
