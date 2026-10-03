"""Review renders for DC-F01: street-level (car height) views, night lit-window view and
moodbook p12 pass views (base colour, roughness, normal) of the actual exported GLBs.

    python jobs/DC-F01/render_review.py <asset.glb> <out_dir> [--views name,...] [--mode textured|clay|night|basecolor|roughness|normal]
                                        [--res 1280] [--samples 48]

Camera presets live in VIEWS below (per asset, metres in the asset's own frame: +X east, +Y north).
Only LOD0 is shown; UCX_ and LOD1/LOD2 are hidden.
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

TUNGSTEN = (0.552, 0.337, 0.125)   # #C49D63 linearised

# (camera location, look-at target, lens mm)
VIEWS = {
    "SM_F01_Folger": {
        "street_ne": ((26.0, 52.0, 1.6), (-4.0, 10.0, 6.0), 28),           # East Capitol St, NE, looking SW
        "street_n": ((0.0, 58.0, 1.6), (0.0, 12.0, 6.5), 32),              # straight on from East Capitol St
        "street_nw": ((-52.0, 40.0, 1.6), (-12.0, 4.0, 6.0), 30),          # 2nd St / East Capitol corner
        "detail_bays": ((6.0, 30.0, 1.7), (0.0, 16.9, 5.5), 35),           # relief + window bays close-up
        "rear_se": ((55.0, -45.0, 1.6), (8.0, -6.0, 6.0), 30),             # alley / 3rd St
        "photo01_ne": ((52.0, 40.0, 1.6), (14.0, 12.0, 6.5), 26),          # vantage of ref 01 (Commons 2025, NE corner)
    },
    "SM_F01_LOCAnnex": {
        "street_sw": ((-80.0, -78.0, 1.6), (-20.0, -10.0, 12.0), 30),      # Independence Ave / 2nd St
        "street_s": ((0.0, -95.0, 1.6), (0.0, -20.0, 13.0), 32),           # Independence Ave, straight on
        "street_w": ((-88.0, 6.0, 1.6), (-40.0, 0.0, 12.0), 30),           # from 2nd St (Jefferson side)
        "detail_entrance_s": ((6.0, -60.0, 1.7), (0.0, -34.0, 7.0), 32),
        "street_ne": ((80.0, 60.0, 1.6), (20.0, 5.0, 12.0), 30),
    },
    "SM_F01_Cannon": {
        "street_nw": ((-105.0, 95.0, 1.6), (-50.0, 40.0, 13.0), 28),       # Independence x New Jersey
        "street_n": ((0.0, 112.0, 1.6), (0.0, 50.0, 13.0), 30),            # from the Capitol side
        "street_ne": ((105.0, 95.0, 1.6), (45.0, 40.0, 13.0), 28),         # Independence x 1st St SE
        "detail_colonnade": ((20.0, 82.0, 1.7), (14.0, 58.0, 14.0), 35),
        "street_se": ((100.0, -95.0, 1.6), (50.0, -40.0, 12.0), 28),       # 1st St / C St
        # vantage of ref 03 (HABS DC-2, 1976, NW corner): level camera on the chamfer normal, rising
        # front (shift) as on the view camera, so verticals stay vertical as in the photo
        "photo03_nw": ((-97.8, 82.1, 1.6), (-60.1, 52.4, 1.6), 26, 0.16),
        "detail_corner": ((-80.0, 68.0, 1.7), (-60.6, 52.8, 7.0), 30),     # NW corner door, stairs, balcony
        "detail_nj": ((-78.0, 30.0, 1.7), (-58.0, 20.0, 9.0), 30),         # New Jersey Ave pilastrade + terrace
    },
}


# Review lighting per asset (azimuth deg clockwise from north the light comes FROM, elevation).
# North facades get no direct sun in November; these are raking review lights so relief depth
# can be judged, NOT a claim about historical sun position.
SUN = {
    "SM_F01_Folger": (20.0, 28.0),
    "SM_F01_LOCAnnex": (235.0, 26.0),
    "SM_F01_Cannon": (20.0, 30.0),
}
EXPOSURE = {"SM_F01_Folger": -0.3, "SM_F01_LOCAnnex": -0.6, "SM_F01_Cannon": -0.45}


def parse_args():
    argv = sys.argv[1:]
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("glb")
    p.add_argument("out_dir")
    p.add_argument("--views", default="")
    p.add_argument("--mode", default="textured",
                   choices=["textured", "clay", "night", "basecolor", "roughness", "normal"])
    p.add_argument("--res", type=int, default=1280)
    p.add_argument("--samples", type=int, default=48)
    p.add_argument("--lod", type=int, default=0, help="which LOD to show (0, 1, 2)")
    return p.parse_args(argv)


def setup_world(scene, mode):
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    if mode == "night":
        bg.inputs["Color"].default_value = (0.006, 0.008, 0.014, 1)
        bg.inputs["Strength"].default_value = 1.0
    elif mode in ("basecolor", "roughness", "normal"):
        bg.inputs["Color"].default_value = (0.5, 0.5, 0.5, 1)
        bg.inputs["Strength"].default_value = 1.0
    else:
        sky = nt.nodes.new("ShaderNodeTexSky")
        try:
            sky.sky_type = 'NISHITA'
            sky.sun_elevation = math.radians(32)
            sky.sun_rotation = math.radians(210)
            sky.air_density = 1.2
            sky.dust_density = 2.0
        except Exception:
            pass
        nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = 0.30
    scene.world = world


def add_sun(scene, mode, azimuth_deg=-150.0, elevation_deg=32.0):
    """azimuth: direction the light travels FROM, degrees clockwise from north (review lighting)."""
    if mode in ("basecolor", "roughness", "normal"):
        return
    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    if mode == "night":
        sun.data.energy = 0.03
        sun.data.color = (0.6, 0.7, 1.0)
        sun.rotation_euler = (math.radians(30), 0, math.radians(40))
    else:
        sun.data.energy = 3.2
        sun.data.angle = math.radians(1.0)
        # light arrives from `azimuth` (clockwise from north) at `elevation`
        az = math.radians(azimuth_deg)
        sun.rotation_euler = (math.radians(90 - elevation_deg), 0, -az + math.pi)
        sun.data.color = (1.0, 0.95, 0.88)
    scene.collection.objects.link(sun)


def ground(scene, size, z, mode):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z - 0.002))
    g = bpy.context.object
    mat = bpy.data.materials.new("GroundAsphalt")
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.045, 0.045, 0.047, 1) if mode != "clay" else (0.18, 0.18, 0.19, 1)
    b.inputs["Roughness"].default_value = 0.85
    g.data.materials.append(mat)
    return g


def material_pass(obj_list, mode):
    """Replace each material's output with a pass visualisation (emission)."""
    for mat in {s.material for o in obj_list for s in o.material_slots if s.material}:
        nt = mat.node_tree
        bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
        if bsdf is None or out is None:
            continue
        em = nt.nodes.new("ShaderNodeEmission")
        if mode == "basecolor":
            src = bsdf.inputs["Base Color"]
        elif mode == "roughness":
            src = bsdf.inputs["Roughness"]
        else:
            src = None
        if mode == "normal":
            geo = nt.nodes.new("ShaderNodeNewGeometry")
            nm_in = bsdf.inputs["Normal"]
            vec_src = nm_in.links[0].from_socket if nm_in.links else geo.outputs["Normal"]
            # world-space normal remapped to colour
            mapn = nt.nodes.new("ShaderNodeVectorMath")
            mapn.operation = 'MULTIPLY_ADD'
            mapn.inputs[1].default_value = (0.5, 0.5, 0.5)
            mapn.inputs[2].default_value = (0.5, 0.5, 0.5)
            nt.links.new(vec_src, mapn.inputs[0])
            nt.links.new(mapn.outputs["Vector"], em.inputs["Color"])
        elif src.links:
            nt.links.new(src.links[0].from_socket, em.inputs["Color"])
        else:
            dv = src.default_value
            em.inputs["Color"].default_value = (dv[0], dv[1], dv[2], 1) if hasattr(dv, "__len__") else (dv, dv, dv, 1)
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])


def night_materials(obj_list):
    for mat in {s.material for o in obj_list for s in o.material_slots if s.material}:
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None:
            continue
        if mat.name.startswith("M_F01_Glass_NightLit") or mat.name.startswith("M_F01_Lamp_Glass"):
            bsdf.inputs["Emission Color"].default_value = (TUNGSTEN[0], TUNGSTEN[1], TUNGSTEN[2], 1)
            bsdf.inputs["Emission Strength"].default_value = 6.0 if "Glass_NightLit" in mat.name else 14.0


def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(args.glb))
    base = os.path.splitext(os.path.basename(args.glb))[0]
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in meshes:
        n = o.name.upper()
        if n.startswith(("UCX_", "UBX_", "USP_")) or not n.endswith(f"_LOD{args.lod}"):
            o.hide_render = True
    vis = [o for o in meshes if not o.hide_render]
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = args.res
    scene.render.resolution_y = int(args.res * 9 / 16)
    vt = [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]
    if args.mode in ("basecolor", "roughness", "normal"):
        scene.view_settings.view_transform = "Standard"
    else:
        scene.view_settings.view_transform = "AgX" if "AgX" in vt else "Filmic"
        scene.view_settings.exposure = (EXPOSURE.get(os.path.splitext(os.path.basename(args.glb))[0], 0.0)
                                        if args.mode != "night" else 1.2)
    if args.mode == "clay":
        clay = bpy.data.materials.new("Clay")
        clay.use_nodes = True
        clay.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.62, 0.62, 0.6, 1)
        clay.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
        for o in vis:
            o.data.materials.clear()
            o.data.materials.append(clay)
    elif args.mode == "night":
        night_materials(vis)
    elif args.mode in ("basecolor", "roughness", "normal"):
        material_pass(vis, args.mode)
    setup_world(scene, args.mode)
    presets0 = VIEWS.get(os.path.splitext(os.path.basename(args.glb))[0], {})
    add_sun(scene, args.mode, *SUN.get(os.path.splitext(os.path.basename(args.glb))[0], (-150.0, 32.0)))
    ground(scene, 2000, 0.0, args.mode)
    if args.mode == "night":
        # two generic street lights (warm) so the facade reads as at night from a car
        for i, loc in enumerate([(0, 1, 0), (1, 0, 0)]):
            pass
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.sensor_width = 36
    scene.collection.objects.link(cam)
    scene.camera = cam
    presets = VIEWS.get(base, {})
    wanted = [v for v in args.views.split(",") if v] or list(presets)
    for vname in wanted:
        loc, tgt, lens = presets[vname][:3]
        cam.location = Vector(loc)
        cam.data.lens = lens
        cam.data.shift_y = presets[vname][3] if len(presets[vname]) > 3 else 0.0
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        if args.mode == "night":
            for o in [o for o in scene.objects if o.name.startswith("StreetLamp")]:
                bpy.data.objects.remove(o)
            # street lamps near the camera, warm sodium/incandescent mix
            for j, off in enumerate((-18.0, 18.0)):
                d = (Vector(tgt) - Vector(loc))
                d.z = 0
                d.normalize()
                side = Vector((-d.y, d.x, 0))
                p = Vector(loc) + side * off + d * 6.0
                p.z = 8.0
                lt = bpy.data.objects.new(f"StreetLamp{j}", bpy.data.lights.new(f"StreetLamp{j}", "POINT"))
                lt.data.energy = 9000
                lt.data.color = (1.0, 0.78, 0.5)
                lt.data.shadow_soft_size = 0.4
                lt.location = p
                scene.collection.objects.link(lt)
        tag = "" if args.lod == 0 else f"_LOD{args.lod}"
        scene.render.filepath = os.path.join(args.out_dir, f"{base}_{args.mode}{tag}_{vname}.png")
        bpy.ops.render.render(write_still=True)
        print("wrote", scene.render.filepath)


if __name__ == "__main__":
    main()
