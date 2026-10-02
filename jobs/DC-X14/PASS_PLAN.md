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
  LoC Photoduplication Service, loc.gov/item/2009631159 (catalog located; image NOT inspected,
  see Uncertainties).
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

1. Evidence (this run) — EVIDENCE.md, gates, APPROXIMATE/FICTIONALISED labels. **DONE 2026-10-02** (image inspection blocked, see below).
2. Build — `jobs/DC-X14/build.py` rebuilds everything from scratch (geometry, generated PBR textures, GLBs).
3. Verify — `tools/qa_check.py` per GLB, `tools/render_views.py` clay + textured per module, custom interior renders of the demo room, harsh self-review, clean rebuild.
4. Deliver — `deliveries/DC-X14/asset-v001/`, branch `asset/DC-X14-v001`, PR, Drive Incoming Deliveries folder.

## Acceptance checks

- Every GLB passes `tools/qa_check.py` (bounds, ground contact, UVs, materials, normals, LODs, UCX).
- Module seams: 3.000 m wall modules butt with no gap; partition panels 1.200 m; posts fill corners.
- Renders read as a 1890s federal office with 1960s partition overlay, not a box: real window reveal and sash, door panels, mouldings, partition framing, ceiling grid and fixtures.
- Clean rebuild from empty `out/` reproduces the files.

## Dependencies

- DC-I09 Office furniture set v005 (Drive `DC-I09 — asset — v005`, 1MUveU1GrHxPHtkQB6FiVWbJmhCVJTQG3; ZIP 1ajFUC-Ivz_gn2ZFsKyK1X3WM9w9NQTfX, 6,707,841 bytes; register: DELIVERED / VERIFIED / approval PENDING). Locked by ID in DEPENDENCY_LOCK.json; sockets only, no furniture built here.
- DC-X15 may route staff access through these rooms; no gala dressing.

## Uncertainties

- Sandbox egress blocks loc.gov, tile.loc.gov, Wikipedia/Commons, archive.org, HathiTrust: catalog
  records are cited but **no reference image could be opened or saved**. Everything dimensional is
  APPROXIMATE. Matt (or a local run) should open the cited records and compare.
- Exact 1963 room assignment of LRS divisions in the Main Building: PROBABLE (NW/SW curtains and
  pavilions, Great Hall upper level, first-floor east corridor) from a 1967 account; not a 1963 document.
- Partition colour, height and glazing pattern: APPROXIMATE (gray, c. 2.1 m, obscure-glass uppers).
- Ceiling heights, window sizes, cornice profiles: APPROXIMATE (no HABS data pages reachable).
- Sign text uses the 1963 name "Legislative Reference Service" (historical signage rule); room numbers FICTIONALISED.
