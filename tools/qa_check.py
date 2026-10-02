"""Reopen an exported GLB and check the things the stage standard asks for.

Usage: python tools/qa_check.py <asset.glb> [--expect-size-cm X Y Z] [--tolerance 0.15]
Exits non-zero if any check FAILs.
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector


def parse_args():
    argv = sys.argv[1:]
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("glb")
    p.add_argument("--expect-size-cm", type=float, nargs=3, metavar=("X", "Y", "Z"))
    p.add_argument("--tolerance", type=float, default=0.15)
    return p.parse_args(argv)


results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))


def main():
    args = parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(args.glb))
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    check("has meshes", bool(objs), f"{len(objs)} mesh objects")
    if not objs:
        sys.exit(1)

    render = [o for o in objs if not o.name.upper().startswith(("UCX_", "UBX_", "USP_"))]
    collision = [o for o in objs if o.name.upper().startswith(("UCX_", "UBX_", "USP_"))]
    lods = {o.name for o in render if "_LOD" in o.name.upper()}
    check("simple collision present (UCX_/UBX_/USP_)", bool(collision), f"{len(collision)} collision meshes")
    check("LODs present", any("_LOD1" in n.upper() for n in lods), ", ".join(sorted(lods)) or "none")

    lo = Vector((math.inf,) * 3)
    hi = Vector((-math.inf,) * 3)
    for o in render:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    size_cm = (hi - lo) * 100
    check("bounds sane (1 cm - 200 m)", 1 <= max(size_cm) <= 20000,
          f"{size_cm.x:.1f} x {size_cm.y:.1f} x {size_cm.z:.1f} cm")
    check("sits on ground (min Z ~ 0)", abs(lo.z * 100) < 2, f"min Z {lo.z*100:.2f} cm")
    if args.expect_size_cm:
        exp = Vector(args.expect_size_cm)
        dims = sorted(size_cm)
        want = sorted(exp)
        ok = all(abs(a - b) <= b * args.tolerance for a, b in zip(dims, want))
        check("matches expected size", ok, f"got {tuple(round(v,1) for v in size_cm)} want {tuple(exp)}")

    for o in render:
        me = o.data
        check(f"{o.name}: has UVs", len(me.uv_layers) > 0)
        check(f"{o.name}: has material", any(s.material for s in o.material_slots),
              ", ".join(s.material.name for s in o.material_slots if s.material))
        zero = sum(1 for p in me.polygons if p.area < 1e-10)
        check(f"{o.name}: no degenerate faces", zero == 0, f"{zero} zero-area faces")
        # Flipped normals: on a closed mesh, the signed volume should be positive.
        vol = 0.0
        for p in me.polygons:
            vs = [me.vertices[i].co for i in p.vertices]
            for i in range(1, len(vs) - 1):
                vol += vs[0].dot(vs[i].cross(vs[i + 1])) / 6
        check(f"{o.name}: normals face outward", vol >= 0, f"signed volume {vol:.4f}")
        check(f"{o.name}: transforms applied", o.scale == Vector((1, 1, 1)) or all(abs(s - 1) < 1e-4 for s in o.scale),
              f"scale {tuple(round(s, 4) for s in o.scale)}")

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
