#!/usr/bin/env bash
# Cannon render set for asset-v002 (the only building changed in v002). Run from the repo root.
set -u
OUT=jobs/DC-F01/renders
g=jobs/DC-F01/out/SM_F01_Cannon.glb
R=jobs/DC-F01/render_review.py
mkdir -p "$OUT/standard" "$OUT/review"
python tools/render_views.py "$g" "$OUT/standard" --mode clay --samples 40 > /dev/null 2>&1 && echo "clay"
python tools/render_views.py "$g" "$OUT/standard" --mode textured --samples 40 > /dev/null 2>&1 && echo "textured"
python $R "$g" "$OUT/review" --mode textured --samples 40 > /dev/null 2>&1 && echo "review views"
python $R "$g" "$OUT/review" --mode clay --views photo03_nw,street_ne,detail_corner --samples 32 > /dev/null 2>&1 && echo "clay review"
python $R "$g" "$OUT/review" --mode night --views street_ne,street_nw,photo03_nw --samples 48 > /dev/null 2>&1 && echo "night"
for m in basecolor roughness normal; do
  python $R "$g" "$OUT/review" --mode $m --views detail_colonnade --samples 16 > /dev/null 2>&1
done
echo "passes"
for L in 1 2; do
  python $R "$g" "$OUT/review" --mode textured --lod $L --views street_ne,photo03_nw --samples 24 > /dev/null 2>&1
done
echo CANNON_V002_RENDERS_DONE
