#!/usr/bin/env bash
# Full Pass-3 render set for DC-F01 v001 (actual exported GLBs). Run from the repo root.
set -u
OUT=jobs/DC-F01/renders
mkdir -p "$OUT/standard" "$OUT/review"
for g in jobs/DC-F01/out/SM_F01_*.glb; do
  python tools/render_views.py "$g" "$OUT/standard" --mode clay --samples 40 > /dev/null 2>&1 && echo "clay $g"
  python tools/render_views.py "$g" "$OUT/standard" --mode textured --samples 40 > /dev/null 2>&1 && echo "textured $g"
  python jobs/DC-F01/render_review.py "$g" "$OUT/review" --mode textured --samples 40 > /dev/null 2>&1 && echo "street $g"
done
python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_Folger.glb "$OUT/review" --mode night --views street_ne,street_nw --samples 48 > /dev/null 2>&1 && echo night-folger
python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_Folger.glb "$OUT/review" --mode textured --views photo01_ne --samples 40 > /dev/null 2>&1 && echo photo01-folger
python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_LOCAnnex.glb "$OUT/review" --mode night --views street_sw,street_w --samples 48 > /dev/null 2>&1 && echo night-annex
python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_Cannon.glb "$OUT/review" --mode night --views street_ne,street_nw --samples 48 > /dev/null 2>&1 && echo night-cannon
for m in basecolor roughness normal; do
  python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_Folger.glb "$OUT/review" --mode $m --views detail_bays --samples 16 > /dev/null 2>&1
  python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_LOCAnnex.glb "$OUT/review" --mode $m --views street_w --samples 16 > /dev/null 2>&1
  python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_Cannon.glb "$OUT/review" --mode $m --views detail_colonnade --samples 16 > /dev/null 2>&1
  echo "pass $m"
done
python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_Folger.glb "$OUT/review" --mode clay --views street_ne --samples 32 > /dev/null 2>&1
python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_LOCAnnex.glb "$OUT/review" --mode clay --views street_sw --samples 32 > /dev/null 2>&1
python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_Cannon.glb "$OUT/review" --mode clay --views street_ne --samples 32 > /dev/null 2>&1
echo "clay-street done"
for L in 1 2; do
  python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_Folger.glb "$OUT/review" --mode textured --lod $L --views street_ne --samples 24 > /dev/null 2>&1
  python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_LOCAnnex.glb "$OUT/review" --mode textured --lod $L --views street_sw --samples 24 > /dev/null 2>&1
  python jobs/DC-F01/render_review.py jobs/DC-F01/out/SM_F01_Cannon.glb "$OUT/review" --mode textured --lod $L --views street_ne --samples 24 > /dev/null 2>&1
  echo "lod $L done"
done
echo ALL_RENDERS_DONE
