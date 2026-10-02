#!/usr/bin/env bash
# Re-render the Cannon standard + street views after the corner-flag fix (2026-10-02).
set -u
OUT=jobs/DC-F01/renders
g=jobs/DC-F01/out/SM_F01_Cannon.glb
python tools/render_views.py "$g" "$OUT/standard" --mode clay --samples 40 > /dev/null 2>&1 && echo "clay redo"
python tools/render_views.py "$g" "$OUT/standard" --mode textured --samples 40 > /dev/null 2>&1 && echo "textured redo"
python jobs/DC-F01/render_review.py "$g" "$OUT/review" --mode textured --samples 40 > /dev/null 2>&1 && echo "street redo"
echo CANNON_REDO_DONE
