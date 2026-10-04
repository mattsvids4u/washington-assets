"""Close-up detail renders (edge bevels, panel gaps, wheel/arch grounding).
Usage: python tools/render_detail.py <glb> <out_dir>"""
import math, os, sys
import bpy
from mathutils import Vector
glb, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb))
for o in bpy.context.scene.objects:
    n = o.name.upper()
    if o.type == "MESH" and (n.startswith(("UCX_", "UBX_", "USP_")) or "_LOD1" in n or "_LOD2" in n):
        o.hide_render = True
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 64
sc.render.resolution_x = 1100; sc.render.resolution_y = 730
world = bpy.data.worlds.new("W"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.78, 0.82, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
sc.world = world
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35)); sc.collection.objects.link(sun)
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
g = bpy.data.materials.new("G"); g.use_nodes = True
g.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.18, 0.18, 0.19, 1)
bpy.context.object.data.materials.append(g)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); cam.data.lens = 50
sc.collection.objects.link(cam); sc.camera = cam
# (name, camera position, look-at) in metres
shots = {
    "detail_front_fender": ((2.6, -3.4, 1.0), (0.7, -2.0, 0.7)),
    "detail_door_belt": ((3.0, -0.4, 1.25), (1.0, 0.1, 0.85)),
    "detail_rear_wheel_kerb": ((3.2, 2.9, 0.35), (0.9, 1.5, 0.4)),
    "detail_grille_low": ((1.6, -4.6, 0.55), (0.0, -2.4, 0.6)),
    "detail_spotlight": ((2.3, -1.6, 1.35), (1.0, -0.45, 1.02)),
    "detail_tail_lamp": ((1.9, 4.6, 0.95), (0.55, 2.75, 0.62)),
}
base = os.path.splitext(os.path.basename(glb))[0]
for name, (pos, look) in shots.items():
    cam.location = Vector(pos)
    cam.rotation_euler = (Vector(look) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, f"{base}_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("wrote", sc.render.filepath)
