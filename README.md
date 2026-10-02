# washington-assets

Workspace for the Claude cloud routine that fulfils AGENTS-lane WASHINGTON asset
requests from Google Drive. Operating rules for the agent are in [CLAUDE.md](CLAUDE.md).

- `tools/setup.sh` — install Blender's Python module (`bpy`) in the sandbox
- `tools/render_views.py` — clay/textured front, profile, rear, ¾ renders (Cycles CPU)
- `tools/qa_check.py` — reopen a GLB and check scale, UVs, normals, materials, LODs, collision
- `tools/package_delivery.py` — DELIVERY_MANIFEST.json + SHA256SUMS.txt
- `jobs/<ID>/` — per-job generator (`build.py`), evidence, renders
- `deliveries/<ID>/asset-v###/` — frozen delivery packages (never overwritten)

Unreal import/readback isn't possible in the cloud; do it locally from the delivered GLB.
