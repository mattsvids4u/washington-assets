"""Interior views of the assembled DC-X14 demo room (the tools/render_views.py orbit shoots a room
from outside, which only shows wall backs). Cycles CPU, textured or clay.

Usage: python jobs/DC-X14/render_interior.py jobs/DC-X14/out/X14_DEMO_LRS_Room.glb jobs/DC-X14/renders [--mode textured|clay] [--res 1280] [--samples 96]
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

# (camera position, look-at) in room metres; eye height ~1.6 m. Room: x 0..9, y 0..6, windows on x = 9.
VIEWS = {
    "int_corridor_east": ((0.6, 0.7, 1.65), (8.5, 2.4, 1.7)),
    "int_corridor_west": ((8.6, 0.9, 1.6), (0.3, 1.6, 1.9)),
    "int_cubicle_window": ((5.95, 2.1, 1.55), (9.0, 4.6, 1.4)),
    "int_door_and_sign": ((2.4, 1.5, 1.6), (4.6, 0.0, 1.6)),
    "int_high_overview": ((0.5, 0.5, 4.2), (6.5, 4.5, 1.2)),
    "int_cubicle_ceiling": ((4.5, 2.2, 1.0), (4.5, 5.5, 2.9)),
}


def parse_args():
    argv = sys.argv[1:]
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("glb")
    p.add_argument("out_dir")
    p.add_argument("--mode", choices=["clay", "textured"], default="textured")
    p.add_argument("--res", type=int, default=1280)
    p.add_argument("--samples", type=int, default=96)
    p.add_argument("--views", default="")
    return p.parse_args(argv)


def main():
    a = parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(a.glb))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in meshes:
        n = o.name.upper()
        if n.startswith(("UCX_", "UBX_", "USP_")) or "_LOD1" in n or "_LOD2" in n:
            o.hide_render = True
    visible = [o for o in meshes if not o.hide_render]
    if a.mode == "clay":
        clay = bpy.data.materials.new("Clay")
        clay.use_nodes = True
        b = clay.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.62, 0.62, 0.6, 1)
        b.inputs["Roughness"].default_value = 0.6
        for o in visible:
            if "GLASS" in o.name.upper():
                o.hide_render = True   # clay pass shows the apertures, not the panes
                continue
            o.data.materials.clear()
            o.data.materials.append(clay)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = a.samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = a.res
    scene.render.resolution_y = int(a.res * 0.66)
    vt = [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]
    scene.view_settings.view_transform = "AgX" if "AgX" in vt else "Filmic"
    scene.view_settings.exposure = 0.3

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.65, 0.72, 0.85, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.2
    scene.world = world

    # Autumn afternoon sun through the east windows (sun from +X, low), plus a soft fill.
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 6.0
    sun.data.angle = math.radians(1.5)
    sun.rotation_euler = (math.radians(62), 0, math.radians(-115))
    scene.collection.objects.link(sun)
    for (x, y) in ((2.0, 3.5), (7.0, 3.5), (4.5, 0.9)):
        fill = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", "AREA"))
        fill.data.energy = 120
        fill.data.size = 2.5
        fill.data.color = (1.0, 0.92, 0.8)
        fill.location = (x, y, 4.3)
        fill.rotation_euler = (0, 0, 0)
        scene.collection.objects.link(fill)

    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.lens = 24
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.clip_start = 0.05
    scene.collection.objects.link(cam)
    scene.camera = cam
    base = os.path.splitext(os.path.basename(a.glb))[0]
    wanted = [v for v in a.views.split(",") if v] or list(VIEWS)
    for name in wanted:
        pos, look = VIEWS[name]
        cam.location = Vector(pos)
        cam.rotation_euler = (Vector(look) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(a.out_dir, f"{base}_{a.mode}_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("wrote", scene.render.filepath)


if __name__ == "__main__":
    main()
