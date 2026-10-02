"""Render front / profile / rear / three-quarter views of a GLB with Cycles on CPU.

Usage: python tools/render_views.py <asset.glb> <out_dir> [--mode clay|textured] [--res 1280]
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

VIEWS = {
    "front": (0, -1, 0.25),
    "profile": (1, 0, 0.2),
    "rear": (0, 1, 0.25),
    "three_quarter": (0.8, -0.8, 0.45),
}


def parse_args():
    argv = sys.argv[1:]
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("glb")
    p.add_argument("out_dir")
    p.add_argument("--mode", choices=["clay", "textured"], default="clay")
    p.add_argument("--res", type=int, default=1280)
    p.add_argument("--samples", type=int, default=64)
    return p.parse_args(argv)


def scene_bounds(objs):
    lo = Vector((math.inf,) * 3)
    hi = Vector((-math.inf,) * 3)
    for o in objs:
        for corner in o.bound_box:
            w = o.matrix_world @ Vector(corner)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(args.glb))

    # Skip collision and LOD helpers so renders show the LOD0 asset only.
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in meshes:
        n = o.name.upper()
        if n.startswith(("UCX_", "UBX_", "USP_")) or "_LOD1" in n or "_LOD2" in n or "_LOD3" in n:
            o.hide_render = True
    visible = [o for o in meshes if not o.hide_render]
    if not visible:
        sys.exit("No visible meshes in " + args.glb)

    if args.mode == "clay":
        clay = bpy.data.materials.new("Clay")
        clay.use_nodes = True
        bsdf = clay.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.62, 0.62, 0.6, 1)
        bsdf.inputs["Roughness"].default_value = 0.6
        for o in visible:
            o.data.materials.clear()
            o.data.materials.append(clay)

    lo, hi = scene_bounds(visible)
    center = (lo + hi) / 2
    size = max((hi - lo).length, 0.01)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = args.samples
    scene.render.resolution_x = args.res
    scene.render.resolution_y = int(args.res * 0.66)
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.78, 0.82, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    scene.world = world

    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    scene.collection.objects.link(sun)

    # Darker ground plane for contact shadows and contrast against the clay.
    bpy.ops.mesh.primitive_plane_add(size=size * 6, location=(center.x, center.y, lo.z))
    ground = bpy.data.materials.new("Ground")
    ground.use_nodes = True
    ground.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.18, 0.18, 0.19, 1)
    bpy.context.object.data.materials.append(ground)

    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.lens = 50
    cam.data.sensor_fit = "HORIZONTAL"
    scene.collection.objects.link(cam)
    scene.camera = cam

    # Fit the bounding sphere inside the narrower (vertical) field of view, with margin.
    aspect = scene.render.resolution_y / scene.render.resolution_x
    vfov = 2 * math.atan(math.tan(cam.data.angle_x / 2) * aspect)
    distance = (size / 2) / math.sin(vfov / 2) * 1.05

    base = os.path.splitext(os.path.basename(args.glb))[0]
    for name, d in VIEWS.items():
        direction = Vector(d).normalized()
        cam.location = center + direction * distance
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(args.out_dir, f"{base}_{args.mode}_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("wrote", scene.render.filepath)


if __name__ == "__main__":
    main()
