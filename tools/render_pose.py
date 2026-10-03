"""Render a GLB with its hinged parts posed (doors / hood / trunk open, front wheels steered) to
show that the exported hierarchy articulates. Usage: python tools/render_pose.py <glb> <out.png>"""
import math, os, sys
import bpy
from mathutils import Vector, Euler
glb, out = sys.argv[1], sys.argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb))
objs = {o.name: o for o in bpy.context.scene.objects}
for o in objs.values():
    n = o.name.upper()
    if o.type == "MESH" and (n.startswith(("UCX_", "UBX_", "USP_")) or "_LOD1" in n or "_LOD2" in n):
        o.hide_render = True
pose = {"DOOR_FL": (0, 0, math.radians(-50)), "DOOR_RR": (0, 0, math.radians(40)),
        "HOOD": (math.radians(-38), 0, 0), "TRUNK": (math.radians(45), 0, 0),
        "STEER_FL": (0, 0, math.radians(22)), "STEER_FR": (0, 0, math.radians(22))}
for name, rot in pose.items():
    if name in objs:
        o = objs[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler(rot, "XYZ")
    else:
        print("missing node", name)
bpy.context.view_layer.update()
vis = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.hide_render]
lo = Vector((math.inf,) * 3); hi = Vector((-math.inf,) * 3)
for o in vis:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c); lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
center = (lo + hi) / 2; size = (hi - lo).length
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 48
sc.render.resolution_x = 1200; sc.render.resolution_y = 800
world = bpy.data.worlds.new("W"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.78, 0.82, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
sc.world = world
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35)); sc.collection.objects.link(sun)
bpy.ops.mesh.primitive_plane_add(size=size * 6, location=(center.x, center.y, 0))
g = bpy.data.materials.new("G"); g.use_nodes = True
g.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.18, 0.18, 0.19, 1)
bpy.context.object.data.materials.append(g)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); cam.data.lens = 45
sc.collection.objects.link(cam); sc.camera = cam
d = Vector((0.85, -0.75, 0.5)).normalized()
cam.location = center + d * size * 1.05
cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = os.path.abspath(out)
bpy.ops.render.render(write_still=True)
print("wrote", out)
