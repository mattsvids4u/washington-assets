#!/usr/bin/env bash
# Installs Blender-as-a-Python-module (bpy) and helpers in the cloud sandbox.
# bpy wheels are pinned to one Python minor version, so find a matching interpreter.
set -euo pipefail

if python -c "import bpy" 2>/dev/null; then
  python -c "import bpy, sys; print('bpy', bpy.app.version_string, 'python', sys.version.split()[0])"
  exit 0
fi

# bpy 4.2–4.5 → Python 3.11; bpy 5.x → Python 3.13 (check PyPI if this changes).
PY=""
for candidate in python3.11 python3.13 python3; do
  if command -v "$candidate" >/dev/null; then PY="$candidate"; break; fi
done
echo "Using $PY ($($PY --version))"

case "$($PY -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')" in
  3.11) SPEC="bpy>=4.2,<5" ;;
  3.13) SPEC="bpy>=5" ;;
  *)
    echo "No Python 3.11/3.13 found; trying uv to fetch 3.11"
    pip install -q uv
    uv venv -p 3.11 .venv
    PY=".venv/bin/python"
    SPEC="bpy>=4.2,<5"
    ;;
esac

$PY -m pip install -q "$SPEC" numpy pillow trimesh pygltflib shapely   # shapely: WASHINGTON tabletop PCG
# Headless Blender needs a few X/GL libs even with no display.
if command -v apt-get >/dev/null; then
  (sudo apt-get install -y -q libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libxkbcommon0 libsm6 2>/dev/null \
    || apt-get install -y -q libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libxkbcommon0 libsm6 2>/dev/null) || true
fi

$PY -c "import bpy, sys; print('bpy', bpy.app.version_string, 'python', sys.version.split()[0])"
echo "If you used a venv, run scripts with: $PY"
