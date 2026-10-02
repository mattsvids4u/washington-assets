"""Orthographic top / underside view of a GLB (for roof-livery and underbody checks).
Usage: python tools/render_top.py <asset.glb> <out.png> [--bottom]"""
import math, os, sys
import bpy
from mathutils import Vector
glb, out = sys.argv[1], sys.argv[2]
bottom = "--bottom" in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb))
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in meshes:
    n = o.name.upper()
    if n.startswith(("UCX_", "UBX_", "USP_")) or "_LOD1" in n or "_LOD2" in n:
        o.hide_render = True
vis = [o for o in meshes if not o.hide_render]
lo = Vector((math.inf,) * 3); hi = Vector((-math.inf,) * 3)
for o in vis:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
center = (lo + hi) / 2
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 32
sc.render.resolution_x = 1000; sc.render.resolution_y = 1000
world = bpy.data.worlds.new("W"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.6 if bottom else 0.8
sc.world = world
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(150 if bottom else 30), 0, math.radians(20)); sc.collection.objects.link(sun)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); cam.data.type = "ORTHO"
cam.data.ortho_scale = max(hi - lo) * 1.1
sc.collection.objects.link(cam); sc.camera = cam
if bottom:
    cam.location = (center.x, center.y, lo.z - 5); cam.rotation_euler = (math.radians(180), 0, 0)
else:
    cam.location = (center.x, center.y, hi.z + 5); cam.rotation_euler = (0, 0, 0)
sc.render.filepath = os.path.abspath(out)
bpy.ops.render.render(write_still=True)
print("wrote", out)
