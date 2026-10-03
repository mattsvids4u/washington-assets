#!/usr/bin/env bash
# Exposed coplanar-overlap gate on every LOD of every DC-F01 GLB -> out/coplanar_report.txt
# Usage (repo root): bash jobs/DC-F01/run_coplanar.sh   (exit 1 if any LOD fails the gate)
set -u
J=jobs/DC-F01
R=$J/out/coplanar_report.txt
T=$(mktemp)
: > "$R"
status=0
for g in $J/out/SM_F01_*.glb; do
  for l in 0 1 2; do
    python $J/coplanar_check.py "$g" --lod $l --top 5 > "$T" 2>&1 || status=1
    grep -v "| INFO\|| WARNING" "$T" >> "$R"
  done
done
rm -f "$T"
echo "gate: $([ $status -eq 0 ] && echo PASS || echo FAIL) (fail threshold 0.05 m^2 visible per LOD)" >> "$R"
cat "$R"
exit $status
