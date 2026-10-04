"""Writes HIERARCHY.txt and MESH_STATS.txt for a delivered GLB (read back through the glTF importer).
Usage: python jobs/DC-V01/report.py <asset.glb> <out_dir>"""
import os
import sys

import bpy
from mathutils import Vector

glb, out = sys.argv[1], sys.argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb))
root = next(o for o in bpy.context.scene.objects if o.parent is None and o.name.startswith("SM_V01"))
hier, stats, mats = [], [], set()


def walk(o, depth):
    for c in sorted(o.children, key=lambda c: c.name):
        t = c.matrix_world.translation * 100.0
        line = f"{'  ' * depth}{c.name} [{'MESH' if c.type == 'MESH' else 'NODE'}] @({t.x:.1f},{t.y:.1f},{t.z:.1f}) cm"
        if c.type == "MESH":
            n = len(c.data.polygons)
            line += f" faces={n}"
            ws = [c.matrix_world @ v.co for v in c.data.vertices]
            lo = Vector((min(p.x for p in ws), min(p.y for p in ws), min(p.z for p in ws)))
            hi = Vector((max(p.x for p in ws), max(p.y for p in ws), max(p.z for p in ws)))
            stats.append(f"{c.name:<28} faces={n:>6} min=({lo.x:7.2f},{lo.y:7.2f},{lo.z:7.2f}) "
                         f"max=({hi.x:7.2f},{hi.y:7.2f},{hi.z:7.2f})")
            mats.update(m.name for m in c.data.materials if m)
        hier.append(line)
        walk(c, depth + 1)


walk(root, 1)
hier.append(f"materials: {sorted(mats)}")
with open(os.path.join(out, "HIERARCHY.txt"), "w") as f:
    f.write("\n".join(hier) + "\n")
with open(os.path.join(out, "MESH_STATS.txt"), "w") as f:
    f.write("\n".join(stats) + "\n")
