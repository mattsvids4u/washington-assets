# DC-X14 asset-v006 — PCG dressing payload (REVIEW / PREVIEW ONLY)

Output of `source/dress_pcg.py` for both demo rooms. Not X14 kit geometry.

- `tabletop/<SurfaceID>.glb|.json`: WASHINGTON Tabletop PCG v003 (support-aware) result for each
  `SURFACE_X14_Tabletop_*` record in the room GLBs. The geometry is DC-I18's (APPROVED) bank; the system
  is a WORKING prototype. The JSON is the persisted record: seeds, controls, resolved placements and the
  support-solver QA.
- `books/<ShelfID>.glb|.json`: DC-I05 v015 shelf personality cropped to each `SOCKET_X14_Books_*`.
  The geometry and canonical bindings are DC-I05's (CLAIMED, approval PENDING). The JSON records the
  BookSeed, personality, run shift, and kept and cropped books.
- `DRESS_PCG_MANIFEST.json`: per-surface counts, the I18 bank variant list, and the 4 SUBSTITUTE states.

Every GLB is in its surface or socket local frame (glTF Y-up): parent it to the matching empty in the
room. Approval status of the source assets is unchanged by this payload.
