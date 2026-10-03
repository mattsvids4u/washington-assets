#!/usr/bin/env bash
# Assemble deliveries/DC-F01/asset-v### from the job folder (never overwrites an existing version).
# Usage (repo root): bash jobs/DC-F01/make_delivery.sh v001
set -euo pipefail
V="${1:?version like v001}"
J=jobs/DC-F01
D=deliveries/DC-F01/asset-$V
if [ -e "$D" ]; then echo "refusing to overwrite $D"; exit 1; fi
mkdir -p "$D"/{source,meshes,textures,renders,research,context,drive_previews}
cp $J/PASS_PLAN.md $J/CONTEXT_ACK.json $J/EVIDENCE.md $J/HANDOFF.md $J/DEPENDENCY_LOCK.json \
   $J/REUSABLE_COMPONENTS.json $J/NEXT_CHAT_PROMPT.txt $J/DISPATCH_LOG.json \
   $J/DECISIONS.md $J/PHOTO_FINDINGS.md $J/PHOTO_REQUEST.md "$D"/
cp $J/out/PCG_INTERFACE.json $J/out/build_report.json "$D"/
cp $J/build.py $J/f01lib.py $J/f01mat.py $J/render_review.py $J/render_all.sh $J/render_cannon_v002.sh $J/make_delivery.sh \
   $J/make_previews.py $J/coplanar_check.py $J/run_coplanar.sh "$D"/source/
cp $J/out/coplanar_report.txt "$D"/
cp $J/out/*.glb "$D"/meshes/
cp $J/out/textures/*.png "$D"/textures/
cp -r $J/renders/standard $J/renders/review "$D"/renders/
cp $J/research/*.md "$D"/research/
cp $J/context/*.txt "$D"/context/
mkdir -p "$D"/references && cp -r $J/refs/* "$D"/references/
cp $J/renders/previews/*.png "$D"/drive_previews/ 2>/dev/null || true
echo "assembled $D"
du -sh "$D"
