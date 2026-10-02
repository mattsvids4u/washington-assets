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
| **Library of Congress Annex** | `SM_F01_LOCAnnex.glb` | 103,476 / 41,836 / 5,556 | 126.96 × 72.84 × 31.20 (12.6 MB) | 400 × 225 ft footprint; corner and central pavilions linked by recessed fenestrated curtains; vertically linked bays (bronze spandrels with honeysuckle ornament) between narrow marble piers; NC pink granite skirt; attic set back 35 ft; three-tier aged copper roof; 3 + 3 bronze door pairs (W/E) and the south pair on the owl-and-lamp stair; figure-per-leaf door stand-ins |
| **Folger Shakespeare Library** | `SM_F01_Folger.glb` | 63,878 / 7,054 / 1,008 | 85.38 × 46.33 × 14.63 incl. terrace and fountain (6.1 MB) | 226 × 111 × 48 ft on a marble plinth; **checked against photo ref 01:** nine tall windows in sunk fields up to the frieze, rectilinear cast-aluminium fret grilles, wide 8-flute pilasters; nine 6 × 6 ft relief panels (stand-ins); incised frieze on the window heads; broad attic with the Johnson (east half) and Jonson (west half) inscriptions over the window row; slight top recession; end entrances in tall sunk panels under projecting canopies with lanterns and mask cartouches; three-bay west front; blank east wall with comedy/tragedy masks; U-plan rear with the 1958–59 one-storey infill; terrace with the 25 × 135 ft lawn bed, front wall and stairs; marble Puck fountain on the west lawn (stand-in figure) |
| **Cannon House Office Building** | `SM_F01_Cannon.glb` | 225,852 / 65,540 / 6,444 | 132.77 × 117.06 × 28.40 incl. plinth and stairs (22.7 MB) | hollow trapezoid on Square 690, New Jersey Ave diagonal; rusticated arcaded base (keystoned arched windows, basement windows, granite plinth); **34 fluted Doric columns (17 coupled pairs)** in a deep loggia on Independence Ave; coupled-pilaster pilastrade on the other fronts; Doric entablature with triglyphs and mutules; balustrade; recessed attic (4th + 5th storeys); chamfered NW rotunda-corner main entrance; limestone court fronts; 1955 garage-deck court |

Each GLB contains `<name>_LOD0/1/2`, convex `UCX_<name>_NN` collision hulls, and `SOCKET_*`
empties (entrances, lamps, typed kit swap points, and pending signage). Material slots are stable
`M_F01_*` names, typed by ITS ALIVE family in `PCG_INTERFACE.json`. Portable PBR sources
(BaseColor / ORM / Normal PNG) are in `textures/`.
Units are Blender metres; UE 5.8 glTF import gives cm. Pivot is at the footprint bbox centre at
grade, +X east, +Y north.

## Gates

| Gate | Result |
|---|---|
| GLB reopen QA (`tools/qa_check.py`) | **20/20 PASS** on all three GLBs |
| Shell orientation (build.py `orientation_audit`) | **0 inward-wound shells** on all 9 LOD meshes (`build_report.json` → `inward_wound_shells`) |
| Visible coincident faces (`source/coplanar_check.py`, `run_coplanar.sh`) | **PASS** on all 9 LOD meshes (`coplanar_report.txt`): 0.004 m² visible in total, two same-material slivers at the Cannon SW corner; gate fails above 0.05 m² per LOD |
| Materials | single-sided (glTF `doubleSided: false`); every shell is closed and outward-wound |
| Clean rebuild (delete `out/`, rerun) | **byte-identical**: all 32 output files (3 GLBs, 27 textures, build report, PCG interface) hash-match a rebuild into an empty directory |
| Actual-output renders | clay + textured front/profile/rear/¾ (`renders/standard/`); street-level car-height views, night lit-window views, base-colour/roughness/normal passes, clay street views and LOD1/LOD2 views (`renders/review/`) |
| Unreal import / readback | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Motion / drive-by tests | **NOT_RUN — needs local Unreal (UE 5.8)** |
| Visual comparison against reference photos | **Folger: DONE** against Drive ref 01 (2025, NE corner). Matched camera `photo01_ne`; the side-by-side is `renders/review/CMP_ref01_vs_photo01_ne.png`; five corrections were made (see PASS_PLAN log 8). **Annex / Cannon: NOT_DONE**: there are no geometry photos on Drive, and the outside archives are still blocked |
| Visual comparison against the moodbook images | **DONE (second run):** pp. 10–12 page images inspected. The target is warm tungsten (#C49D63) against charcoal and olive, with cold-paper neutrals; the night lit-window views are the check for that. Day views are neutral review lighting, not a grade |

## Evidence gaps (what Matt should know first)

1. **Only the two Drive starter photos were inspected**, in the second run: the Folger NE view
   (2025) and an Adams stair close-up (2017, material only). The outside archives (loc.gov,
   Wikimedia, NARA, NPS, AOC, Flickr, archive.org) are still blocked, so **no 1963-dated photo
   has been inspected**, and the Annex and Cannon geometry is still unchecked against any photo.
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
  - Folger: bay width, terrace layout, rear wing widths, entrance lantern. Window and frieze heights, pilaster width and entrance canopy are now PROBABLE (photo-measured). Inscription positions are VERIFIED by the photo.
  - Folger east end: the 2025 photo shows a door with steps. It is **not modelled**, because SAH calls the east end a blank wall and the door may date from 2019–24. Needs a pre-2019 photo.
  - Cannon: overall dimensions and angle, heights, column size, the chamfered corner form, and the attic's look; coupled columns are PROBABLE.
- **Labelled stand-ins (rights unconfirmed, never likenesses):**
  - Lawrie bronze door figures (Annex).
  - John Gregory reliefs (Folger).
  - Brenda Putnam's Puck (Folger).
  - Comedy/tragedy masks (Folger).
  - Owls and lamp standards (Annex).
- **Inscriptions:**
  - Carved: only the two Folger quotations, whose wording is VERIFIED; their placement in the attic over the window row is VERIFIED by photo ref 01, and Liberation Serif is a stand-in typeface.
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
  - Another claude-cloud-agent session has since claimed DC-F02 (2026-10-02T11:14Z). It delivered the Senate Office Building as `DC-F02 — asset — v001` and proposes the New SOB as its v002.
  - **Recommendation:** F02 keeps both, and F01 drops them from its scope. **Matt: confirm.** F01 has built neither.

## UNIFICATION PROPOSALS

0. **Cannon (F01) and Senate Office Building (F02) are twins, so make them agree.**
   - AOC calls the two Carrère & Hastings buildings "almost identical"; each has 34 fluted Doric columns facing the Capitol and a pilastrade on the diagonal avenue.
   - The two agent deliveries currently disagree on the colonnade:
     - F01 v001 builds the Cannon's 34 columns as 17 coupled pairs (PROBABLE, from SAH's "doubled fluted columns … doubled pilasters" and the Colonnade du Louvre analogy).
     - F02 v001 builds the SOB's 34 as evenly spaced free-standing columns (3.30 m c/c).
   - At most one reading is right for both. After a photo check, align both generators: F01 is one parameter (`CANNON["n_pairs"]`, `pair_cc`).
   - The column, entablature, balustrade and rusticated-base vocabulary could then be shared between the two jobs.
   - I have not touched F02's files.

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
5. **Two geometry gates for every agent delivery.**
   - `tools/qa_check.py` checks signed volume per LOD as a whole, so inverted parts can hide inside a positive total. That is how F01's inside-out facade boxes went unnoticed until Pass 3 (see PASS_PLAN log 7).
   - Propose adding a per-shell orientation audit and the exposed-coplanar check (`source/coplanar_check.py`, generator-agnostic, works on any GLB) to `tools/`. Every agent delivery would then be gated on "no inside-out shells, no visible z-fighting".
   - F01 has not edited the shared `tools/`.
6. **No DALLAS parent** (NEW), so there is nothing to propose upstream to DALLAS.

## What Matt should look at

1. `renders/review/*_textured_street_*.png`: the three buildings at car height, compared with your own knowledge or photos of each.
2. **Cannon colonnade pairing** (`SM_F01_Cannon_textured_detail_colonnade.png`): coupled (built) vs evenly spaced single columns. It is one parameter (`CANNON["n_pairs"]`, `pair_cc`). F02's twin SOB uses single columns; see UNIFICATION PROPOSAL 0.
3. **Annex spandrels** (`SM_F01_LOCAnnex_textured_street_w.png`): bronze (built, PROBABLE) vs marble.
4. **Folger front:** `CMP_ref01_vs_photo01_ne.png` (photo vs model at a matched vantage), `SM_F01_Folger_textured_street_n.png` and `detail_bays`. Check the grilles, entrance canopies, relief stand-ins and inscriptions. Also tell me whether the east-end door in the 2025 photo existed in 1963.
5. Night views (`*_night_*.png`) for the moving-car-at-night read.
6. **On UE import:** materials arrive one-sided. A missing face seen from outside would mean a winding bug; the audit reports none, so please flag any you find.
7. Decisions: the SOB/NSOB owner; the Folger east-end door; any of the dimensions above.

## Files

`PASS_PLAN.md` · `CONTEXT_ACK.json` · `EVIDENCE.md` · `HANDOFF.md` · `DEPENDENCY_LOCK.json` · `PCG_INTERFACE.json` ·
`REUSABLE_COMPONENTS.json` · `NEXT_CHAT_PROMPT.txt` + `DISPATCH_LOG.json` (successor note; no claim queued) ·
`source/` (build.py, f01lib.py, f01mat.py, render_review.py, render_all.sh, make_delivery.sh, make_previews.py, coplanar_check.py, run_coplanar.sh) · `coplanar_report.txt` ·
`meshes/*.glb` · `textures/*.png` · `renders/` · `research/` · `build_report.json` · `DELIVERY_MANIFEST.json` · `SHA256SUMS.txt`
