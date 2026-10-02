"""Street-level and detail renders for DC-F02 (Cycles CPU).

Usage: python jobs/DC-F02/render_street.py <asset.glb> <out_dir> [--res 1280] [--samples 48] [--only name,...]
Camera positions are in the asset frame (metres, +X east, +Y north); Constitution Ave grade = 7.3 m.
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

ZC = 7.3
VIEWS = {
    # name: (camera xyz, target xyz, lens mm, night)
    "street_rotunda_corner": ((-32.0, -30.0, ZC + 1.4), (8.0, 6.0, ZC + 11.0), 24, False),
    "street_constitution_east": ((-10.0, -26.0, ZC + 1.4), (90.0, 2.0, ZC + 10.0), 28, False),
    "detail_colonnade_bay": ((70.0, -11.0, ZC + 1.6), (70.0, 2.0, ZC + 12.5), 30, False),
    "street_cst_slope_nw": ((-28.0, 135.0, 1.7), (20.0, 95.0, 9.0), 24, False),
    "street_constitution_night": ((-10.0, -26.0, ZC + 1.4), (90.0, 2.0, ZC + 10.0), 28, True),
    "aerial_sw_corner": ((-25.0, -25.0, 55.0), (20.0, 20.0, 25.0), 35, False),
    # matched to the E11 (c.1909) / E15 (modern) photographs: across the Delaware x Constitution
    # intersection, looking NE at the rotunda corner
    "photo_match_E11_corner": ((-52.0, -50.0, ZC + 1.6), (14.0, 12.0, ZC + 10.0), 32, False),
    "detail_corner_pavilion": ((-20.0, -20.0, ZC + 1.6), (7.0, 7.0, ZC + 12.0), 28, False),
}


def parse_args():
    argv = sys.argv[1:]
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("glb")
    p.add_argument("out_dir")
    p.add_argument("--res", type=int, default=1280)
    p.add_argument("--samples", type=int, default=48)
    p.add_argument("--only", default="")
    return p.parse_args(argv)


def main():
    a = parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(a.glb))
    for o in bpy.context.scene.objects:
        n = o.name.upper()
        if o.type == "MESH" and (n.startswith("UCX_") or "_LOD1" in n or "_LOD2" in n):
            o.hide_render = True
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = a.samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x = a.res
    sc.render.resolution_y = int(a.res * 0.5625)
    sc.view_settings.view_transform = "AgX"
    world = bpy.data.worlds.new("W")
    world.use_nodes = True
    sc.world = world
    nt = world.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sc.collection.objects.link(sun)
    # street surface following the same N-S grade as the site apron (render context only, not the asset)
    def gz(y):
        if y < -9:
            return ZC - 0.17
        if y > 119:
            return 0.28
        return ZC - 7.0 * min(max(y / 110.0, 0), 1) - 0.02
    xs = [-400, 600]
    ys = [-400, -9.01, -9] + [i * 5.0 for i in range(0, 23)] + [119, 119.01, 600]
    verts = [(x, y, gz(y)) for y in ys for x in xs]
    faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(ys) - 1)]
    me = bpy.data.meshes.new("Street")
    me.from_pydata(verts, [], faces)
    street = bpy.data.objects.new("Street", me)
    sc.collection.objects.link(street)
    gm = bpy.data.materials.new("Street")
    gm.use_nodes = True
    gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.07, 0.07, 0.07, 1)
    gm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.85
    me.materials.append(gm)
    # placeholder warm street lamps for the night view only (placement is DC-R03 / lighting DC-L01)
    lamps = []
    for i in range(7):
        l = bpy.data.objects.new(f"Lamp{i}", bpy.data.lights.new(f"Lamp{i}", "POINT"))
        l.location = (-20 + i * 30, -12.5, ZC + 7.5)
        l.data.energy = 9000
        l.data.color = (1.0, 0.72, 0.42)
        l.data.shadow_soft_size = 0.3
        sc.collection.objects.link(l)
        lamps.append(l)
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    only = set(filter(None, a.only.split(",")))
    base = os.path.splitext(os.path.basename(a.glb))[0]
    for name, (loc, tgt, lens, night) in VIEWS.items():
        if only and name not in only:
            continue
        for l in lamps:
            l.hide_render = not night
        if night:
            sky.sun_elevation = math.radians(-8)
            bg.inputs["Strength"].default_value = 0.0
            bg.inputs["Color"].default_value = (0.02, 0.025, 0.04, 1)
            sun.data.energy = 0.03
            sun.data.color = (0.6, 0.7, 1.0)
            sun.rotation_euler = (math.radians(30), 0, math.radians(200))
            sc.view_settings.exposure = 0.5
        else:  # late-autumn afternoon, sun from the south-west
            sky.sun_elevation = math.radians(28)
            sky.sun_rotation = math.radians(220)
            bg.inputs["Strength"].default_value = 0.35
            sun.data.energy = 3.2
            sun.data.color = (1.0, 0.93, 0.82)
            sun.rotation_euler = (math.radians(62), 0, math.radians(220 - 180 + 90))
            sc.view_settings.exposure = -0.4
        cam.location = loc
        cam.data.lens = lens
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(a.out_dir, f"{base}_{name}.png")
        bpy.ops.render.render(write_still=True)
        print("wrote", sc.render.filepath)


if __name__ == "__main__":
    main()
