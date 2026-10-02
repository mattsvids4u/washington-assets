"""DC-X14 — Staff offices and Legislative Reference Service room — reproducible generator.

Run:  python jobs/DC-X14/build.py
Rebuilds every texture and GLB in jobs/DC-X14/out/ from scratch (deterministic, seeded).

Units: Blender metres (glTF is metres by spec; UE 5.8's glTF importer converts to cm).
Kit layers:
  ARCH_  — 1897 Main Building office shell (painted plaster, oak trim, arched deep-reveal
           windows, panelled oak doors with glazed transoms, cast-iron radiators, plaster
           ceiling, oak strip / linoleum floor).
  PART_  — 1950s–60s temporary overlay (gray steel partitions with glazed uppers, partition
           doors, posts, suspended acoustic-tile ceiling, 2-tube fluorescent fixtures, door sign).
  DEMO_  — one assembled LRS division room built only from the kit, with DC-I09 furniture sockets.
Every module: pivot at its own base (z = 0), +X along the module run, interior face on y = 0
with the room on +Y. LOD0–LOD2, UCX_ convex collision, box-mapped UVs (1 UV unit = 1 m),
stable material slot names (MI_X14_*). All dimensions APPROXIMATE unless EVIDENCE.md says otherwise.
"""
import json
import math
import os
import shutil

import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")
TEX = os.path.join(OUT, "textures")
SEED = 1963

# ----------------------------------------------------------------------------- dimensions (m)
ROOM_H = 4.60          # APPROXIMATE first-floor office height in the curtains
WALL_T = 0.30          # interior partition walls of the 1897 building (brick, plastered)
EXT_WALL_T = 0.60      # exterior granite wall, shown as a deep window reveal
MOD_W = 3.00           # wall module run
BASE_H, BASE_D = 0.22, 0.025
RAIL_Z, RAIL_H, RAIL_D = 3.20, 0.06, 0.03   # picture rail
CORN_H, CORN_D = 0.26, 0.22                 # plaster cove cornice
WIN_W, WIN_SILL, WIN_RECT_H = 1.50, 0.90, 2.45   # arch radius = WIN_W/2 on top of rect
DOOR_W, DOOR_H, TRANS_H = 1.10, 2.60, 0.40
PART_H, PART_W, PART_T = 2.13, 1.20, 0.05  # 7 ft steel partitions
PART_BASE_H, POST_W = 0.10, 0.05
DROP_Z = 2.75          # underside of the temporary dropped ceiling (placement height)
TILE = 0.60

# ----------------------------------------------------------------------------- palette (moodbook)
CHARCOAL = (0x13 / 255, 0x1D / 255, 0x1B / 255)
OLIVE = (0x66 / 255, 0x73 / 255, 0x63 / 255)
WALNUT = (0x6B / 255, 0x47 / 255, 0x34 / 255)
TUNGSTEN = (0xC4 / 255, 0x9D / 255, 0x63 / 255)
COLD_PAPER = (0xDF / 255, 0xDF / 255, 0xD4 / 255)


# =============================================================================== textures
def _noise(size, octaves=5, persistence=0.55, rng=None, base=4):
    """Value-noise fBm in [0,1] from upsampled random grids (deterministic via rng)."""
    acc = np.zeros((size, size), dtype=np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        n = base * (2 ** o)
        grid = rng.random((n, n)).astype(np.float32)
        img = Image.fromarray((grid * 255).astype(np.uint8)).resize((size, size), Image.BICUBIC)
        acc += amp * (np.asarray(img, dtype=np.float32) / 255.0)
        total += amp
        amp *= persistence
    acc /= total
    return (acc - acc.min()) / max(acc.max() - acc.min(), 1e-6)


def _save_rgb(path, arr):
    arr = np.clip(arr, 0, 1)
    Image.fromarray((arr * 255).astype(np.uint8), "RGB").save(path)


def _save_l(path, arr):
    arr = np.clip(arr, 0, 1)
    Image.fromarray((arr * 255).astype(np.uint8), "L").save(path)


def _normal_from_height(path, h, strength=2.0):
    gy, gx = np.gradient(h.astype(np.float32))
    nx, ny, nz = -gx * strength, -gy * strength, np.ones_like(h)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    n = np.stack([nx / l, ny / l, nz / l], axis=-1) * 0.5 + 0.5
    _save_rgb(path, n)


def _tint(base, n, lo, hi):
    """Blend a grey-level noise field onto a base colour between lo..hi multipliers."""
    m = lo + (hi - lo) * n[..., None]
    return np.array(base, dtype=np.float32)[None, None, :] * m


def build_textures():
    os.makedirs(TEX, exist_ok=True)
    S = 1024
    rng = np.random.default_rng(SEED)

    # Plaster, painted buff (institutional, lifted neutral close to COLD PAPER, warmed).
    n = _noise(S, 6, 0.6, rng, 8)
    fine = _noise(S, 3, 0.5, rng, 128)
    _save_rgb(f"{TEX}/T_X14_Plaster_BC.png", _tint((0.80, 0.77, 0.69), n * 0.6 + fine * 0.4, 0.90, 1.04))
    _save_l(f"{TEX}/T_X14_Plaster_R.png", 0.72 + 0.18 * fine)
    _normal_from_height(f"{TEX}/T_X14_Plaster_N.png", n * 0.4 + fine * 0.6, 1.2)

    # Plaster ceiling, whiter.
    _save_rgb(f"{TEX}/T_X14_PlasterCeiling_BC.png", _tint((0.86, 0.85, 0.80), n * 0.5 + fine * 0.5, 0.94, 1.02))

    # Oak: streaky grain along U, quarter-sawn flecks.
    u = np.linspace(0, 1, S, dtype=np.float32)[None, :].repeat(S, 0)
    grain = _noise(S, 4, 0.5, rng, 2)
    streak = 0.5 + 0.5 * np.sin((u * 60 + grain * 6) * math.pi)
    streak = streak ** 1.6
    fleck = (_noise(S, 2, 0.5, rng, 256) > 0.74).astype(np.float32) * 0.35
    oak = _tint((0.62, 0.45, 0.28), streak * 0.8 + fleck, 0.72, 1.08)
    _save_rgb(f"{TEX}/T_X14_Oak_BC.png", oak)
    _save_l(f"{TEX}/T_X14_Oak_R.png", 0.42 + 0.2 * streak)
    _normal_from_height(f"{TEX}/T_X14_Oak_N.png", streak * 0.5 + grain * 0.5, 0.8)

    # Walnut-stained oak for doors (closer to WALNUT swatch).
    _save_rgb(f"{TEX}/T_X14_OakDoor_BC.png", _tint((0.42, 0.28, 0.19), streak * 0.8 + fleck * 0.5, 0.70, 1.10))

    # Oak strip flooring: 75 mm strips with staggered end joints and a dark joint line.
    strip_w = 1 / 13.33           # 75 mm strips per 1 m tile
    v = np.linspace(0, 1, S, dtype=np.float32)[:, None].repeat(S, 1)
    strip_idx = np.floor(v / strip_w)
    joint = ((v % strip_w) < 0.006).astype(np.float32)
    per_strip = rng.random(64)[strip_idx.astype(int) % 64]
    ends = (((u + per_strip[:, :]) % 0.5) < 0.004).astype(np.float32)
    g2 = 0.5 + 0.5 * np.sin((u * 80 + grain * 8 + per_strip * 20) * math.pi)
    floor = _tint((0.55, 0.38, 0.22), g2 ** 1.4 * 0.9 + (per_strip - 0.5) * 0.5, 0.70, 1.05)
    floor *= (1 - 0.5 * np.maximum(joint, ends))[..., None]
    _save_rgb(f"{TEX}/T_X14_OakFloor_BC.png", floor)
    _save_l(f"{TEX}/T_X14_OakFloor_R.png", 0.35 + 0.15 * g2 + 0.3 * np.maximum(joint, ends))
    _normal_from_height(f"{TEX}/T_X14_OakFloor_N.png", -0.8 * np.maximum(joint, ends) + 0.15 * g2, 2.5)

    # Linoleum (1950s battleship / marbled olive-gray).
    m = _noise(S, 5, 0.65, rng, 6)
    speck = _noise(S, 2, 0.5, rng, 256)
    lino = _tint((0.42, 0.45, 0.38), m * 0.7 + speck * 0.3, 0.80, 1.10)
    _save_rgb(f"{TEX}/T_X14_Linoleum_BC.png", lino)
    _save_l(f"{TEX}/T_X14_Linoleum_R.png", 0.45 + 0.1 * speck)

    # Partition paint: gray (E4) and faux-mahogany (E5) variants, brushed-enamel micro noise.
    pm = _noise(S, 3, 0.5, rng, 64)
    _save_rgb(f"{TEX}/T_X14_PartitionGray_BC.png", _tint((0.52, 0.53, 0.52), pm, 0.94, 1.04))
    _save_rgb(f"{TEX}/T_X14_PartitionMahogany_BC.png", _tint((0.38, 0.20, 0.14), streak * 0.6 + pm * 0.4, 0.80, 1.10))
    _save_l(f"{TEX}/T_X14_Partition_R.png", 0.38 + 0.12 * pm)

    # Acoustic tile: 12-inch fissured tiles, 2 per 0.6 m module tile.
    tx = (u * 2) % 1
    ty = (v * 2) % 1
    edge = ((tx < 0.012) | (ty < 0.012)).astype(np.float32)
    fiss = (_noise(S, 3, 0.5, rng, 96) > 0.62).astype(np.float32)
    tile = _tint((0.88, 0.87, 0.82), 1 - fiss * 0.35, 0.92, 1.0)
    tile *= (1 - 0.35 * edge)[..., None]
    _save_rgb(f"{TEX}/T_X14_AcousticTile_BC.png", tile)
    _save_l(f"{TEX}/T_X14_AcousticTile_R.png", np.full((S, S), 0.9, np.float32))
    _normal_from_height(f"{TEX}/T_X14_AcousticTile_N.png", -fiss * 0.5 - edge * 0.8, 2.0)

    # Painted dark metal (radiators, fixtures) and marble sill.
    _save_rgb(f"{TEX}/T_X14_MetalPaint_BC.png", _tint((0.16, 0.17, 0.16), pm, 0.9, 1.1))
    _save_l(f"{TEX}/T_X14_MetalPaint_R.png", 0.45 + 0.1 * pm)
    vein = np.abs(np.sin((_noise(S, 4, 0.6, rng, 3) * 9 + u * 2) * math.pi)) ** 8
    _save_rgb(f"{TEX}/T_X14_Marble_BC.png", _tint((0.84, 0.82, 0.78), 1 - vein * 0.5, 0.9, 1.0))
    _save_l(f"{TEX}/T_X14_Marble_R.png", np.full((S, S), 0.22, np.float32))


# =============================================================================== materials
_MATS = {}


def _img(name):
    path = f"{TEX}/{name}"
    img = bpy.data.images.get(name)
    if img is None:
        img = bpy.data.images.load(path)
        img.name = name
    return img


def material(name, bc=None, rough=None, normal=None, color=(0.8, 0.8, 0.8, 1), roughness=0.5,
             metallic=0.0, uv_scale=1.0, alpha=None, emission=None, emission_strength=0.0):
    """Principled material with optional image maps. Non-colour maps flagged correctly."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if alpha is not None:
        bsdf.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
        m.surface_render_method = "BLENDED" if hasattr(m, "surface_render_method") else None
    mapping = None
    if bc or rough or normal:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (uv_scale, uv_scale, uv_scale)
        nt.links.new(tc.outputs["UV"], mapping.inputs["Vector"])
    if bc:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _img(bc)
        nt.links.new(mapping.outputs["Vector"], t.inputs["Vector"])
        nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    if rough:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _img(rough)
        t.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mapping.outputs["Vector"], t.inputs["Vector"])
        nt.links.new(t.outputs["Color"], bsdf.inputs["Roughness"])
    if normal:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = _img(normal)
        t.image.colorspace_settings.name = "Non-Color"
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(mapping.outputs["Vector"], t.inputs["Vector"])
        nt.links.new(t.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    _MATS[name] = m
    return m


def materials():
    M = {}
    M["plaster"] = material("MI_X14_Plaster_Wall", "T_X14_Plaster_BC.png", "T_X14_Plaster_R.png", "T_X14_Plaster_N.png", uv_scale=0.5)
    M["ceiling"] = material("MI_X14_Plaster_Ceiling", "T_X14_PlasterCeiling_BC.png", "T_X14_Plaster_R.png", "T_X14_Plaster_N.png", uv_scale=0.5)
    M["oak"] = material("MI_X14_Oak_Trim", "T_X14_Oak_BC.png", "T_X14_Oak_R.png", "T_X14_Oak_N.png", uv_scale=1.0)
    M["door"] = material("MI_X14_Oak_Door", "T_X14_OakDoor_BC.png", "T_X14_Oak_R.png", "T_X14_Oak_N.png", uv_scale=1.0)
    M["floor"] = material("MI_X14_Oak_Floor", "T_X14_OakFloor_BC.png", "T_X14_OakFloor_R.png", "T_X14_OakFloor_N.png", uv_scale=1.0)
    M["lino"] = material("MI_X14_Linoleum", "T_X14_Linoleum_BC.png", "T_X14_Linoleum_R.png", uv_scale=0.5)
    M["marble"] = material("MI_X14_Marble_Sill", "T_X14_Marble_BC.png", "T_X14_Marble_R.png", uv_scale=1.0)
    M["glass"] = material("MI_X14_Glass_Clear", color=(0.85, 0.9, 0.9, 1), roughness=0.05, alpha=0.18)
    M["part"] = material("MI_X14_Paint_Partition_Gray", "T_X14_PartitionGray_BC.png", "T_X14_Partition_R.png", uv_scale=1.0)
    M["metal"] = material("MI_X14_Metal_Painted", "T_X14_MetalPaint_BC.png", "T_X14_MetalPaint_R.png", uv_scale=1.0)
    M["brass"] = material("MI_X14_Brass", color=(0.78, 0.62, 0.32, 1), roughness=0.3, metallic=1.0)
    M["tile"] = material("MI_X14_Acoustic_Tile", "T_X14_AcousticTile_BC.png", "T_X14_AcousticTile_R.png", "T_X14_AcousticTile_N.png", uv_scale=1.6667)
    M["fluor"] = material("MI_X14_FluorTube_Lit", color=(0.95, 0.97, 1.0, 1), roughness=0.3, emission=(0.9, 0.95, 1.0, 1), emission_strength=6.0)
    M["opal"] = material("MI_X14_Opal_Glass", color=(0.95, 0.93, 0.86, 1), roughness=0.35, alpha=0.9, emission=(1.0, 0.85, 0.6, 1), emission_strength=1.5)
    M["signtext"] = material("MI_X14_Sign_Text", color=(0.05, 0.05, 0.05, 1), roughness=0.4)
    return M


# =============================================================================== bmesh helpers
def new_bm():
    return bmesh.new()


def box(bm, x0, y0, z0, x1, y1, z1, mat=0):
    """Axis-aligned closed box with outward normals."""
    v = [bm.verts.new(c) for c in [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                   (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    for f in faces:
        face = bm.faces.new([v[i] for i in f])
        face.material_index = mat
    return v


def cylinder(bm, cx, cy, z0, z1, r, segs=16, mat=0, axis="Z"):
    """Closed cylinder along Z (or X/Y) with outward normals."""
    ring0, ring1 = [], []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        if axis == "Z":
            ring0.append(bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z0)))
            ring1.append(bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z1)))
        elif axis == "X":   # cx is y, cy is z, z0..z1 along x
            ring0.append(bm.verts.new((z0, cx + r * math.cos(a), cy + r * math.sin(a))))
            ring1.append(bm.verts.new((z1, cx + r * math.cos(a), cy + r * math.sin(a))))
        else:               # Y: cx is x, cy is z, z0..z1 along y
            ring0.append(bm.verts.new((cx + r * math.cos(a), z0, cy + r * math.sin(a))))
            ring1.append(bm.verts.new((cx + r * math.cos(a), z1, cy + r * math.sin(a))))
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new([ring0[i], ring0[j], ring1[j], ring1[i]])
        f.material_index = mat
    f0 = bm.faces.new(list(reversed(ring0)))
    f1 = bm.faces.new(ring1)
    f0.material_index = f1.material_index = mat
    return ring0, ring1


def sweep(bm, profile, path, normal=(0, 1, 0), mat=0, cap=True):
    """Sweep a closed 2-D profile [(lateral, depth)] along a polyline with mitred corners.

    lateral = along cross(tangent, normal); depth = along `normal` (out of the wall face).
    """
    n = Vector(normal).normalized()
    pts = [Vector(p) for p in path]
    rings = []
    for i, p in enumerate(pts):
        d_in = (pts[i] - pts[i - 1]).normalized() if i > 0 else None
        d_out = (pts[i + 1] - pts[i]).normalized() if i < len(pts) - 1 else None
        if d_in is None:
            t, k = d_out, 1.0
        elif d_out is None:
            t, k = d_in, 1.0
        else:
            t = (d_in + d_out).normalized()
            k = 1.0 / max(d_in.dot(t), 0.2)
        lat = t.cross(n).normalized()
        rings.append([bm.verts.new(p + lat * (w * k) + n * d) for (w, d) in profile])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(len(profile)):
            j = (i + 1) % len(profile)
            f = bm.faces.new([a[i], a[j], b[j], b[i]])
            f.material_index = mat
    if cap:
        f0 = bm.faces.new(list(reversed(rings[0])))
        f1 = bm.faces.new(rings[-1])
        f0.material_index = f1.material_index = mat
    return rings


def box_uv(bm, scale=1.0):
    """World-space box projection: 1 UV unit = `1/scale` metres, by dominant normal axis."""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        nrm = f.normal
        ax = max(range(3), key=lambda i: abs(nrm[i]))
        for l in f.loops:
            c = l.vert.co
            if ax == 0:
                l[uv].uv = (c.y * scale, c.z * scale)
            elif ax == 1:
                l[uv].uv = (c.x * scale, c.z * scale)
            else:
                l[uv].uv = (c.x * scale, c.y * scale)


def clean(bm):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_area() < 1e-10], context="FACES_ONLY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()


def finish(bm, name, mats, cleanup=True):
    """bmesh → object with materials, cleaned, UV'd, normals recalculated, linked to scene."""
    if cleanup:
        clean(bm)
    else:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
    box_uv(bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def empty(name, loc, rot=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.25
    e.location = loc
    e.rotation_euler = rot
    if parent:
        e.parent = parent
    bpy.context.scene.collection.objects.link(e)
    return e


def boolean_cut(target, cutter):
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier="cut")
    bpy.data.objects.remove(cutter, do_unlink=True)
    # Re-run cleanup + box UVs on the cut result.
    bm = bmesh.new()
    bm.from_mesh(target.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    box_uv(bm)
    bm.to_mesh(target.data)
    bm.free()


def arch_cutter(name, x0, y0, y1, z_sill, w, rect_h, segs=24):
    """Rect + semicircle opening profile in XZ, extruded through y0..y1."""
    bm = new_bm()
    r = w / 2
    cx = x0 + r
    prof = [(x0, z_sill), (x0 + w, z_sill), (x0 + w, z_sill + rect_h)]
    for i in range(1, segs):
        a = math.pi * i / segs
        prof.append((cx + r * math.cos(a), z_sill + rect_h + r * math.sin(a)))
    prof.append((x0, z_sill + rect_h))
    back = [bm.verts.new((x, y0, z)) for x, z in prof]
    front = [bm.verts.new((x, y1, z)) for x, z in prof]
    bm.faces.new(list(reversed(back)))
    bm.faces.new(front)
    for i in range(len(prof)):
        j = (i + 1) % len(prof)
        bm.faces.new([back[i], back[j], front[j], front[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def rect_cutter(name, x0, x1, y0, y1, z0, z1):
    bm = new_bm()
    box(bm, x0, y0, z0, x1, y1, z1)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# =============================================================================== profiles
# Profiles are closed polygons [(lateral, depth)], lateral = up (for a run along +X with the
# room on +Y), depth = out into the room from the wall face (y = 0).
def baseboard_profile():
    return [(0, 0), (0, BASE_D), (0.17, BASE_D), (0.19, BASE_D - 0.006), (0.205, BASE_D - 0.004),
            (0.22, BASE_D - 0.012), (BASE_H, 0.0)]


def rail_profile():
    z = RAIL_Z
    return [(z, 0), (z, 0.012), (z + 0.015, RAIL_D), (z + 0.045, RAIL_D), (z + RAIL_H, 0.01), (z + RAIL_H, 0)]


def cornice_profile(h=ROOM_H):
    # Plaster cove: quarter-round from the wall up into the ceiling line, 8 segments.
    z0 = h - CORN_H
    pts = [(z0, 0), (z0, 0.02), (z0 + 0.02, 0.02)]
    for i in range(0, 9):
        a = math.pi / 2 * i / 8
        pts.append((z0 + 0.03 + (CORN_H - 0.03) * math.sin(a), 0.02 + (CORN_D - 0.02) * (1 - math.cos(a))))
    pts.append((h, 0))
    return pts


def architrave_profile():
    # Oak door architrave, 110 mm wide, stepped and bevelled; lateral = away from opening.
    return [(0, 0), (0, 0.018), (0.02, 0.018), (0.025, 0.028), (0.06, 0.028), (0.07, 0.022), (0.10, 0.022), (0.11, 0.0)]


# =============================================================================== module builders
def runs(length, gaps):
    """Split 0..length into runs that avoid the (x0, x1) gaps."""
    out, x = [], 0.0
    for g0, g1 in sorted(gaps):
        if g0 > x + 1e-6:
            out.append((x, g0))
        x = max(x, g1)
    if x < length - 1e-6:
        out.append((x, length))
    return out


def wall_trims(bm, lod, length=MOD_W, h=ROOM_H, base_gaps=(), rail_gaps=(), mat_plaster=0, mat_oak=1):
    """Oak baseboard, picture rail and plaster cove cornice along +X, interrupted at openings."""
    if lod <= 1:
        for a, b in runs(length, base_gaps):
            sweep(bm, baseboard_profile(), [(a, 0, 0), (b, 0, 0)], mat=mat_oak)
        sweep(bm, cornice_profile(h), [(0, 0, 0), (length, 0, 0)], mat=mat_plaster)
    if lod == 0:
        for a, b in runs(length, rail_gaps):
            sweep(bm, rail_profile(), [(a, 0, 0), (b, 0, 0)], mat=mat_oak)


def wall_slab(name, mats, thick=WALL_T, length=MOD_W, h=ROOM_H):
    """Bare plaster wall box as an object (booleans are applied to this single closed shell)."""
    bm = new_bm()
    box(bm, 0, -thick, 0, length, 0, h, 0)
    return finish(bm, name, mats)


def wall_core(bm, lod, thick=WALL_T, length=MOD_W, h=ROOM_H, mat_plaster=0, mat_oak=1):
    """Plaster wall slab + trims (no openings)."""
    box(bm, 0, -thick, 0, length, 0, h, mat_plaster)
    wall_trims(bm, lod, length, h, mat_plaster=mat_plaster, mat_oak=mat_oak)


def ucx_boxes(name, boxes, M):
    """Create UCX_ convex collision boxes (dark material; material only to satisfy tools)."""
    objs = []
    for i, (x0, y0, z0, x1, y1, z1) in enumerate(boxes, 1):
        bm = new_bm()
        box(bm, x0, y0, z0, x1, y1, z1)
        ob = finish(bm, f"UCX_{name}_{i:02d}", [M["metal"]])
        objs.append(ob)
    return objs


def build_wall_plain(M):
    name = "X14_ARCH_Wall_Plain_300"
    objs = []
    for lod in range(3):
        bm = new_bm()
        wall_core(bm, lod)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["plaster"], M["oak"]]))
    objs += ucx_boxes(name, [(0, -WALL_T, 0, MOD_W, 0, ROOM_H)], M)
    objs.append(empty("SOCKET_X14_WallNext", (MOD_W, 0, 0)))
    objs.append(empty("SOCKET_X14_WallPrev", (0, 0, 0)))
    return name, objs


def build_wall_window(M):
    """Exterior wall bay: round-arched deep reveal, marble sill, two-light double-hung sash with
    arched fixed transom, cast-iron column radiator. Window centred in the 3 m bay."""
    name = "X14_ARCH_Wall_Window_300"
    x0 = (MOD_W - WIN_W) / 2
    objs = []
    thick = EXT_WALL_T
    for lod in range(3):
        ob = wall_slab(f"{name}_LOD{lod}", [M["plaster"], M["oak"], M["marble"], M["door"], M["metal"]], thick=thick)
        cut = arch_cutter("cut", x0, -thick - 0.1, 0.3, WIN_SILL, WIN_W, WIN_RECT_H, segs=24 if lod == 0 else 10)
        boolean_cut(ob, cut)
        # Trims (rail stops at the reveal), then sill, sash and radiator as more shells in the same mesh.
        bm = new_bm()
        bm.from_mesh(ob.data)
        wall_trims(bm, lod, rail_gaps=[(x0 - 0.001, x0 + WIN_W + 0.001)])
        # Marble sill: through the reveal, 50 mm proud into the room, 40 mm thick.
        box(bm, x0 - 0.04, -thick + 0.01, WIN_SILL - 0.04, x0 + WIN_W + 0.04, 0.05, WIN_SILL + 0.006, 2)
        # Window frame set 0.42 m back from the room face in the reveal.
        fy = -0.42
        fd = 0.06  # frame depth (y)
        fw = 0.06  # frame member width
        jamb_h = WIN_RECT_H
        # jambs
        box(bm, x0, fy, WIN_SILL, x0 + fw, fy + fd, WIN_SILL + jamb_h, 3)
        box(bm, x0 + WIN_W - fw, fy, WIN_SILL, x0 + WIN_W, fy + fd, WIN_SILL + jamb_h, 3)
        # transom bar between sash and arched light
        box(bm, x0 + fw, fy, WIN_SILL + jamb_h - 0.05, x0 + WIN_W - fw, fy + fd + 0.02, WIN_SILL + jamb_h + 0.03, 3)
        if lod <= 1:
            # Double-hung: lower sash (inner plane) and upper sash (outer plane), each 2 lights.
            sash_h = (jamb_h - 0.05) / 2
            for k, yy in enumerate([fy + 0.005, fy + fd - 0.03]):
                zb = WIN_SILL + k * sash_h
                sw = 0.045
                box(bm, x0 + fw, yy, zb, x0 + fw + sw, yy + 0.028, zb + sash_h, 3)
                box(bm, x0 + WIN_W - fw - sw, yy, zb, x0 + WIN_W - fw, yy + 0.028, zb + sash_h, 3)
                box(bm, x0 + fw + sw, yy, zb, x0 + WIN_W - fw - sw, yy + 0.028, zb + sw, 3)
                box(bm, x0 + fw + sw, yy, zb + sash_h - sw, x0 + WIN_W - fw - sw, yy + 0.028, zb + sash_h, 3)
                if lod == 0:  # single vertical muntin per sash (two lights)
                    cx = x0 + WIN_W / 2
                    box(bm, cx - 0.012, yy, zb + sw, cx + 0.012, yy + 0.028, zb + sash_h - sw, 3)
            # Arched transom: fixed frame ring following the arch (polyline sweep) + radial muntins.
            r = WIN_W / 2
            cx = x0 + r
            zc = WIN_SILL + jamb_h
            segs = 16 if lod == 0 else 8
            path = []
            for i in range(segs + 1):
                a = math.pi * i / segs
                path.append((cx + (r - 0.03) * math.cos(a), fy + fd / 2, zc + (r - 0.03) * math.sin(a)))
            path = list(reversed(path))
            sweep(bm, [(0, -0.03), (0, 0.03), (-0.06, 0.03), (-0.06, -0.03)], path, normal=(0, 1, 0), mat=3)
            if lod == 0:
                for a in (math.pi / 3, 2 * math.pi / 3):
                    ex, ez = cx + (r - 0.06) * math.cos(a), zc + (r - 0.06) * math.sin(a)
                    sweep(bm, [(0, -0.012), (0, 0.012), (-0.02, 0.012), (-0.02, -0.012)],
                          [(cx, fy + fd / 2, zc + 0.02), (ex, fy + fd / 2, ez)], normal=(0, 1, 0), mat=3)
        # Radiator: cast-iron column radiator under the sill, 3 columns deep.
        if lod <= 1:
            n_sec = 12 if lod == 0 else 6
            rw = 0.06 if lod == 0 else 0.12
            rx0 = x0 + (WIN_W - n_sec * rw) / 2
            for s in range(n_sec):
                for c in range(3):
                    cylinder(bm, rx0 + rw * (s + 0.5), 0.09 + c * 0.055, 0.12, 0.72, 0.024 if lod == 0 else 0.03, 10 if lod == 0 else 6, mat=4)
            box(bm, rx0, 0.05, 0.70, rx0 + n_sec * rw, 0.24, 0.76, 4)
            box(bm, rx0, 0.05, 0.10, rx0 + n_sec * rw, 0.24, 0.14, 4)
            for lx in (rx0 + 0.08, rx0 + n_sec * rw - 0.08):
                cylinder(bm, lx, 0.145, 0.0, 0.12, 0.018, 8, mat=4)
        else:
            box(bm, x0 + 0.1, 0.05, 0.0, x0 + WIN_W - 0.1, 0.24, 0.76, 4)
        clean(bm)
        box_uv(bm)
        bm.to_mesh(ob.data)
        bm.free()
        objs.append(ob)
        # Glazing as its own object (so glass is a separate, inspectable, swappable material).
        bm = new_bm()
        zc = WIN_SILL + WIN_RECT_H
        if lod <= 1:
            sash_h = (WIN_RECT_H - 0.05) / 2
            box(bm, x0 + 0.06, fy + 0.014, WIN_SILL + 0.045, x0 + WIN_W - 0.06, fy + 0.018, WIN_SILL + sash_h, 0)
            box(bm, x0 + 0.06, fy + fd - 0.02, WIN_SILL + sash_h, x0 + WIN_W - 0.06, fy + fd - 0.016, zc - 0.05, 0)
        else:
            box(bm, x0 + 0.06, fy + 0.02, WIN_SILL, x0 + WIN_W - 0.06, fy + 0.024, zc, 0)
        # Arched transom pane: a flat half-disc, thickened.
        r = WIN_W / 2 - 0.04
        cx = x0 + WIN_W / 2
        segs = 16 if lod == 0 else 8
        back, front = [], []
        for i in range(segs + 1):
            a = math.pi * i / segs
            back.append(bm.verts.new((cx + r * math.cos(a), fy + 0.028, zc + r * math.sin(a))))
            front.append(bm.verts.new((cx + r * math.cos(a), fy + 0.032, zc + r * math.sin(a))))
        bm.faces.new(list(reversed(back)))
        bm.faces.new(front)
        for i in range(segs):
            bm.faces.new([back[i], back[i + 1], front[i + 1], front[i]])
        bm.faces.new([back[-1], back[0], front[0], front[-1]])
        objs.append(finish(bm, f"{name}_Glass_LOD{lod}", [M["glass"]]))
    objs += ucx_boxes(name, [
        (0, -thick, 0, x0, 0, ROOM_H), (x0 + WIN_W, -thick, 0, MOD_W, 0, ROOM_H),
        (x0, -thick, 0, x0 + WIN_W, 0, WIN_SILL), (x0, -thick, WIN_SILL + WIN_RECT_H + WIN_W / 2, x0 + WIN_W, 0, ROOM_H),
        (x0, -0.45, WIN_SILL, x0 + WIN_W, -0.36, WIN_SILL + WIN_RECT_H + WIN_W / 2),
    ], M)
    objs.append(empty("SOCKET_X14_WallNext", (MOD_W, 0, 0)))
    objs.append(empty("SOCKET_X14_WallPrev", (0, 0, 0)))
    objs.append(empty("SOCKET_X14_WindowCentre", (MOD_W / 2, 0, WIN_SILL)))
    return name, objs


def door_leaf(bm, w, h, t, mat_door, mat_brass, lod, hinge_left=True):
    """Four-panel oak door built at origin: hinge edge on x=0, leaf spans x 0..w, y 0..t."""
    st = 0.12   # stile width
    rl = 0.20   # bottom rail
    rt = 0.11   # top rail
    mid = 0.10  # lock rail
    if lod >= 2:
        box(bm, 0, 0, 0, w, t, h, mat_door)
        return
    # stiles and rails as a frame
    box(bm, 0, 0, 0, st, t, h, mat_door)
    box(bm, w - st, 0, 0, w, t, h, mat_door)
    box(bm, st, 0, 0, w - st, t, rl, mat_door)
    box(bm, st, 0, h - rt, w - st, t, h, mat_door)
    zl = rl + (h - rl - rt) * 0.42
    box(bm, st, 0, zl, w - st, t, zl + mid, mat_door)
    # centre muntin and recessed panels (panels 12 mm in from each face)
    mu = 0.09
    cx = w / 2
    box(bm, cx - mu / 2, 0, rl, cx + mu / 2, t, zl, mat_door)
    box(bm, cx - mu / 2, 0, zl + mid, cx + mu / 2, t, h - rt, mat_door)
    inset = 0.012
    for (xa, xb) in ((st, cx - mu / 2), (cx + mu / 2, w - st)):
        for (za, zb) in ((rl, zl), (zl + mid, h - rt)):
            box(bm, xa, inset, za, xb, t - inset, zb, mat_door)
            if lod == 0:  # raised field on the room side
                box(bm, xa + 0.035, t - inset - 0.004, za + 0.035, xb - 0.035, t - inset + 0.004, zb - 0.035, mat_door)
    if lod == 0:
        # knob + rose on the room side, lock side
        kx = w - st / 2 if hinge_left else st / 2
        cylinder(bm, kx, 0.0, t, t + 0.012, 0.03, 12, mat=mat_brass, axis="Y") if False else None
        cylinder(bm, kx, 1.0, t, t + 0.012, 0.03, 12, mat=mat_brass, axis="Y")
        cylinder(bm, kx, 1.0, t + 0.012, t + 0.06, 0.009, 8, mat=mat_brass, axis="Y")
        # sphere-ish knob: short fat cylinder
        cylinder(bm, kx, 1.0, t + 0.06, t + 0.09, 0.028, 12, mat=mat_brass, axis="Y")
        # hinges (3) on the hinge edge, room face
        for hz in (0.25, h / 2, h - 0.25):
            box(bm, -0.002, t - 0.004, hz - 0.05, 0.03, t + 0.004, hz + 0.05, mat_brass)


def build_wall_door(M):
    """Interior wall with panelled oak door, glazed transom, oak architrave; door pivot node."""
    name = "X14_ARCH_Wall_Door_300"
    x0 = (MOD_W - DOOR_W) / 2
    objs = []
    frame_t = 0.045
    for lod in range(3):
        ob = wall_slab(f"{name}_LOD{lod}", [M["plaster"], M["oak"], M["door"], M["brass"]])
        cut = rect_cutter("cut", x0, x0 + DOOR_W, -WALL_T - 0.1, 0.1, -0.1, DOOR_H + TRANS_H)
        boolean_cut(ob, cut)
        bm = new_bm()
        bm.from_mesh(ob.data)
        wall_trims(bm, lod, base_gaps=[(x0 - 0.12, x0 + DOOR_W + 0.12)])
        # Door frame (jamb lining) through the wall thickness.
        box(bm, x0, -WALL_T, 0, x0 + frame_t, 0, DOOR_H + TRANS_H, 1)
        box(bm, x0 + DOOR_W - frame_t, -WALL_T, 0, x0 + DOOR_W, 0, DOOR_H + TRANS_H, 1)
        box(bm, x0 + frame_t, -WALL_T, DOOR_H + TRANS_H - frame_t, x0 + DOOR_W - frame_t, 0, DOOR_H + TRANS_H, 1)
        # Transom bar
        box(bm, x0 + frame_t, -WALL_T, DOOR_H, x0 + DOOR_W - frame_t, 0, DOOR_H + 0.05, 1)
        if lod <= 1:
            # Architrave both faces (room side and back side), mitred around the opening.
            seg = [(x0 - 0.002, 0, 0), (x0 - 0.002, 0, DOOR_H + TRANS_H + 0.002),
                   (x0 + DOOR_W + 0.002, 0, DOOR_H + TRANS_H + 0.002), (x0 + DOOR_W + 0.002, 0, 0)]
            sweep(bm, architrave_profile(), seg, normal=(0, 1, 0), mat=1)
            segb = [(x, -WALL_T, z) for x, y, z in seg]
            sweep(bm, architrave_profile(), segb, normal=(0, -1, 0), mat=1)
            # Transom sash (fixed) with 2 lights
            box(bm, x0 + frame_t, -0.16, DOOR_H + 0.05, x0 + frame_t + 0.04, -0.12, DOOR_H + TRANS_H - frame_t, 2)
            box(bm, x0 + DOOR_W - frame_t - 0.04, -0.16, DOOR_H + 0.05, x0 + DOOR_W - frame_t, -0.12, DOOR_H + TRANS_H - frame_t, 2)
            box(bm, x0 + frame_t + 0.04, -0.16, DOOR_H + 0.05, x0 + DOOR_W - frame_t - 0.04, -0.12, DOOR_H + 0.09, 2)
            box(bm, x0 + frame_t + 0.04, -0.16, DOOR_H + TRANS_H - frame_t - 0.04, x0 + DOOR_W - frame_t - 0.04, -0.12, DOOR_H + TRANS_H - frame_t, 2)
            if lod == 0:
                box(bm, MOD_W / 2 - 0.012, -0.16, DOOR_H + 0.09, MOD_W / 2 + 0.012, -0.12, DOOR_H + TRANS_H - frame_t - 0.04, 2)
        clean(bm)
        box_uv(bm)
        bm.to_mesh(ob.data)
        bm.free()
        objs.append(ob)
        # Transom glass
        bm = new_bm()
        box(bm, x0 + frame_t + 0.03, -0.142, DOOR_H + 0.08, x0 + DOOR_W - frame_t - 0.03, -0.138, DOOR_H + TRANS_H - frame_t - 0.03, 0)
        objs.append(finish(bm, f"{name}_Glass_LOD{lod}", [M["glass"]]))
    # Door leaf as a child of a hinge pivot, closed position inside the frame on the back plane.
    leaf_w = DOOR_W - 2 * frame_t - 0.006
    leaf_t = 0.045
    pivot = empty("PIVOT_X14_DoorHinge", (x0 + frame_t + 0.003, -0.16, 0.01))
    objs.append(pivot)
    for lod in range(3):
        bm = new_bm()
        door_leaf(bm, leaf_w, DOOR_H - 0.02, leaf_t, 0, 1, lod)
        leaf = finish(bm, f"{name}_Leaf_LOD{lod}", [M["door"], M["brass"]])
        leaf.parent = pivot
        objs.append(leaf)
    objs += ucx_boxes(name, [
        (0, -WALL_T, 0, x0, 0, ROOM_H), (x0 + DOOR_W, -WALL_T, 0, MOD_W, 0, ROOM_H),
        (x0, -WALL_T, DOOR_H + TRANS_H, x0 + DOOR_W, 0, ROOM_H),
    ], M)
    # Door leaf collision (convex box) — exported in the leaf's closed pose.
    bm = new_bm()
    box(bm, x0 + frame_t, -0.16, 0, x0 + DOOR_W - frame_t, -0.115, DOOR_H)
    objs.append(finish(bm, f"UCX_{name}_Leaf_01", [M["metal"]]))
    objs.append(empty("SOCKET_X14_WallNext", (MOD_W, 0, 0)))
    objs.append(empty("SOCKET_X14_WallPrev", (0, 0, 0)))
    objs.append(empty("SOCKET_X14_DoorSign", (x0 + DOOR_W + 0.25, 0.0, 1.55)))
    return name, objs


def build_corner(M):
    """Outside notch filler for an inside corner where two wall runs meet: 0.3 × 0.3 plan, full
    height, plaster. The visible inside-corner mitre is formed automatically by the union of the
    two walls' baseboard / rail / cornice extrusions, which end exactly on the corner planes."""
    name = "X14_ARCH_Corner"
    objs = []
    for lod in range(3):
        bm = new_bm()
        box(bm, -WALL_T, -WALL_T, 0, 0, 0, ROOM_H, 0)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["plaster"]]))
    objs += ucx_boxes(name, [(-WALL_T, -WALL_T, 0, 0, 0, ROOM_H)], M)
    return name, objs


def build_floor(M, lino=False):
    name = "X14_ARCH_Floor_300" + ("_Linoleum" if lino else "")
    objs = []
    for lod in range(3):
        bm = new_bm()
        box(bm, 0, 0, -0.05, MOD_W, MOD_W, 0.0, 0)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["lino"] if lino else M["floor"]]))
    objs += ucx_boxes(name, [(0, 0, -0.05, MOD_W, MOD_W, 0)], M)
    for o in objs:
        o.location.z += 0.05   # pivot on the walking surface would put geometry below z=0; keep base at 0
    return name, objs


def build_ceiling(M):
    """Plaster ceiling slab, pivot at its underside (placed at z = ROOM_H by the PCG). Pendant socket."""
    name = "X14_ARCH_Ceiling_300"
    objs = []
    for lod in range(3):
        bm = new_bm()
        box(bm, 0, 0, 0, MOD_W, MOD_W, 0.06, 0)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["ceiling"]]))
    objs += ucx_boxes(name, [(0, 0, 0, MOD_W, MOD_W, 0.06)], M)
    objs.append(empty("SOCKET_X14_Pendant", (MOD_W / 2, MOD_W / 2, 0), rot=(math.pi, 0, 0)))
    return name, objs


def build_pendant(M):
    """Period opal-glass bowl pendant on a chain. Pivot at the ceiling canopy; hangs down (-Z).
    Exported with geometry above z=0 (bowl at the base) so the module 'sits' on z=0; the socket
    on the ceiling module is rotated 180° about X so -Z becomes down."""
    name = "X14_ARCH_Pendant_Lamp"
    objs = []
    drop = 1.10
    for lod in range(3):
        bm = new_bm()
        # canopy at top (z = drop), chain, bowl at bottom (z ~ 0..0.18)
        cylinder(bm, 0, 0, drop - 0.03, drop, 0.06, 16 if lod == 0 else 8, mat=0)
        cylinder(bm, 0, 0, 0.19, drop - 0.02, 0.006, 6, mat=0)
        if lod == 0:
            for i in range(10):
                z = 0.25 + i * 0.08
                cylinder(bm, 0, 0, z, z + 0.03, 0.012, 8, mat=0)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["brass"]]))
        bm = new_bm()
        # bowl: stacked frusta
        segs = 20 if lod == 0 else 10
        rings = []
        prof = [(0.0, 0.0), (0.09, 0.0), (0.16, 0.05), (0.19, 0.12), (0.17, 0.18), (0.035, 0.20), (0.0, 0.20)]
        for (r, z) in prof:
            if r == 0:
                rings.append([bm.verts.new((0, 0, z))] * segs)
            else:
                rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / segs), r * math.sin(2 * math.pi * i / segs), z)) for i in range(segs)])
        for a, b in zip(rings[:-1], rings[1:]):
            for i in range(segs):
                j = (i + 1) % segs
                quad = [a[i], a[j], b[j], b[i]]
                uniq = []
                for v in quad:
                    if v not in uniq:
                        uniq.append(v)
                if len(uniq) >= 3:
                    bm.faces.new(uniq)
        objs.append(finish(bm, f"{name}_Glass_LOD{lod}", [M["opal"]]))
    objs += ucx_boxes(name, [(-0.19, -0.19, 0, 0.19, 0.19, 0.2)], M)
    return name, objs


def partition_frame(bm, w, lod, mat_paint, glazed=False, door=False):
    """Steel partition: full-height end posts; base channel and top cap run BETWEEN the posts
    (no coincident end faces); infill panel solid or solid + glazed."""
    t = PART_T
    box(bm, 0, -t / 2, 0, POST_W, t / 2, PART_H, mat_paint)
    box(bm, w - POST_W, -t / 2, 0, w, t / 2, PART_H, mat_paint)
    if door:
        return
    box(bm, POST_W, -t / 2 - 0.015, 0, w - POST_W, t / 2 + 0.015, PART_BASE_H, mat_paint)       # base channel
    box(bm, POST_W, -t / 2 - 0.01, PART_H - 0.04, w - POST_W, t / 2 + 0.01, PART_H, mat_paint)  # top cap
    if glazed:
        split = 1.20
        box(bm, POST_W, -t / 2 + 0.01, PART_BASE_H, w - POST_W, t / 2 - 0.01, split, mat_paint)
        box(bm, POST_W, -t / 2 - 0.005, split, w - POST_W, t / 2 + 0.005, split + 0.05, mat_paint)  # glazing rail
        box(bm, POST_W, -t / 2 - 0.005, PART_H - 0.09, w - POST_W, t / 2 + 0.005, PART_H - 0.04, mat_paint)
        if lod == 0:  # glazing beads
            for yy in (-t / 2 - 0.004, t / 2 - 0.006):
                box(bm, POST_W, yy, split + 0.05, POST_W + 0.012, yy + 0.01, PART_H - 0.09, mat_paint)
                box(bm, w - POST_W - 0.012, yy, split + 0.05, w - POST_W, yy + 0.01, PART_H - 0.09, mat_paint)
    else:
        box(bm, POST_W, -t / 2 + 0.01, PART_BASE_H, w - POST_W, t / 2 - 0.01, PART_H - 0.04, mat_paint)
        if lod == 0:  # horizontal seam strip where two steel sheets meet (7 ft panels came in two)
            box(bm, POST_W, -t / 2 - 0.004, 1.19, w - POST_W, t / 2 + 0.004, 1.21, mat_paint)


def build_part_panel(M, glazed, width=PART_W):
    name = ("X14_PART_Panel_Glazed_" if glazed else "X14_PART_Panel_Solid_") + f"{int(round(width * 100)):03d}"
    objs = []
    for lod in range(3):
        bm = new_bm()
        partition_frame(bm, width, lod, 0, glazed=glazed)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["part"]]))
        if glazed:
            bm = new_bm()
            box(bm, POST_W + 0.01, -0.002, 1.26, width - POST_W - 0.01, 0.002, PART_H - 0.10, 0)
            objs.append(finish(bm, f"{name}_Glass_LOD{lod}", [M["glass"]]))
    objs += ucx_boxes(name, [(0, -PART_T / 2 - 0.015, 0, width, PART_T / 2 + 0.015, PART_H)], M)
    objs.append(empty("SOCKET_X14_PartNext", (width, 0, 0)))
    objs.append(empty("SOCKET_X14_PartPrev", (0, 0, 0)))
    return name, objs


def build_part_door(M):
    """0.9 m partition door unit: frame + flush steel door leaf on a hinge pivot, knob."""
    name = "X14_PART_Door_090"
    w = 0.90
    objs = []
    for lod in range(3):
        bm = new_bm()
        partition_frame(bm, w, lod, 0, door=True)
        # head panel above the door (door 2.0 m high) and a top cap between the posts
        box(bm, POST_W, -PART_T / 2 + 0.01, 2.0, w - POST_W, PART_T / 2 - 0.01, PART_H - 0.04, 0)
        box(bm, POST_W, -PART_T / 2 - 0.01, PART_H - 0.04, w - POST_W, PART_T / 2 + 0.01, PART_H, 0)
        # threshold strip
        box(bm, POST_W, -PART_T / 2 - 0.015, 0, w - POST_W, PART_T / 2 + 0.015, 0.012, 0)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["part"], M["brass"]]))
    pivot = empty("PIVOT_X14_PartDoorHinge", (POST_W + 0.002, 0.0, 0.012))
    objs.append(pivot)
    for lod in range(3):
        bm = new_bm()
        lw, lh, lt = w - 2 * POST_W - 0.006, 1.98, 0.04
        box(bm, 0, -lt / 2, 0, lw, lt / 2, lh, 0)
        if lod == 0:
            cylinder(bm, lw - 0.07, 1.0, lt / 2, lt / 2 + 0.07, 0.009, 8, mat=1, axis="Y")
            cylinder(bm, lw - 0.07, 1.0, lt / 2 + 0.07, lt / 2 + 0.10, 0.026, 12, mat=1, axis="Y")
            cylinder(bm, lw - 0.07, 1.0, -lt / 2 - 0.07, -lt / 2, 0.009, 8, mat=1, axis="Y")
            cylinder(bm, lw - 0.07, 1.0, -lt / 2 - 0.10, -lt / 2 - 0.07, 0.026, 12, mat=1, axis="Y")
        leaf = finish(bm, f"{name}_Leaf_LOD{lod}", [M["part"], M["brass"]])
        leaf.parent = pivot
        objs.append(leaf)
    objs += ucx_boxes(name, [
        (0, -PART_T / 2 - 0.015, 0, POST_W, PART_T / 2 + 0.015, PART_H),
        (w - POST_W, -PART_T / 2 - 0.015, 0, w, PART_T / 2 + 0.015, PART_H),
        (POST_W, -PART_T / 2 - 0.015, 2.0, w - POST_W, PART_T / 2 + 0.015, PART_H),
    ], M)
    bm = new_bm()
    box(bm, POST_W, -0.02, 0, w - POST_W, 0.02, 2.0)
    objs.append(finish(bm, f"UCX_{name}_Leaf_01", [M["metal"]]))
    objs.append(empty("SOCKET_X14_PartNext", (w, 0, 0)))
    objs.append(empty("SOCKET_X14_PartPrev", (0, 0, 0)))
    objs.append(empty("SOCKET_X14_DoorSign", (w / 2, PART_T / 2 + 0.002, 1.75)))
    return name, objs


def build_part_post(M):
    """Free-standing connector post with foot, used at panel corners / tees / run ends."""
    name = "X14_PART_Post"
    objs = []
    for lod in range(3):
        bm = new_bm()
        pw = POST_W + 0.01   # 60 mm cover post: wraps the 50 mm panel end posts, no shared planes
        box(bm, -pw / 2, -pw / 2, 0.004, pw / 2, pw / 2, PART_H, 0)
        box(bm, -0.09, -0.09, 0, 0.09, 0.09, 0.012, 0)
        box(bm, -pw / 2 - 0.004, -pw / 2 - 0.004, PART_H - 0.04, pw / 2 + 0.004, pw / 2 + 0.004, PART_H + 0.004, 0)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["part"]]))
    objs += ucx_boxes(name, [(-0.09, -0.09, 0, 0.09, 0.09, PART_H + 0.004)], M)
    return name, objs


def build_drop_ceiling(M):
    """1.2 × 1.2 suspended acoustic-tile ceiling: exposed T-grid, four 0.6 m fissured tiles recessed
    10 mm. Pivot on the grid underside (place at z = DROP_Z)."""
    name = "X14_PART_DropCeiling_120"
    objs = []
    gw, gd = 0.025, 0.035
    for lod in range(3):
        bm = new_bm()
        W = 2 * TILE
        # T-grid: perimeter + cross
        for x in (0, TILE, W):
            box(bm, x - gw / 2, -gw / 2, 0, x + gw / 2, W + gw / 2, gd, 1)
        for y in (0, TILE, W):
            for xa, xb in ((gw / 2, TILE - gw / 2), (TILE + gw / 2, W - gw / 2)):
                box(bm, xa, y - gw / 2, 0, xb, y + gw / 2, gd, 1)
        # tiles
        for i in range(2):
            for j in range(2):
                box(bm, i * TILE + gw / 2, j * TILE + gw / 2, 0.010, (i + 1) * TILE - gw / 2, (j + 1) * TILE - gw / 2, 0.025, 0)
        if lod == 0:
            # hanger wires to a plenum anchor 0.5 m up (reads through gaps and in section)
            for (x, y) in ((TILE, 0), (TILE, W), (0, TILE), (W, TILE)):
                cylinder(bm, x, y, gd, gd + 0.5, 0.002, 4, mat=1)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["tile"], M["metal"]]))
    objs += ucx_boxes(name, [(0, 0, 0, 2 * TILE, 2 * TILE, 0.03)], M)
    objs.append(empty("SOCKET_X14_Fixture", (TILE, TILE, 0), rot=(math.pi, 0, 0)))
    return name, objs


def build_fluorescent(M):
    """Two-tube 4-ft industrial strip fixture on chains. Pivot at the fixture's underside plane."""
    name = "X14_PART_Fluorescent_120"
    objs = []
    L = 1.22
    for lod in range(3):
        bm = new_bm()
        # channel body sits above z=0.06 (tubes hang below the reflector), reflector flares
        box(bm, 0, -0.07, 0.10, L, 0.07, 0.16, 0)
        # reflector: swept trapezoid profile along X
        prof = [(0.0, -0.07), (0.0, 0.07), (-0.06, 0.16), (-0.065, 0.16), (-0.065, -0.16), (-0.06, -0.16)]
        # sweep expects (lateral, depth) with lateral along cross(t, n); use n = +Z, t = +X -> lateral = -Y
        sweep(bm, [(d, z) for (z, d) in prof], [(0, 0, 0.10), (L, 0, 0.10)], normal=(0, 0, 1), mat=0)
        if lod == 0:
            # end plates with sockets
            for x in (0, L):
                box(bm, x - 0.004, -0.09, 0.0, x + 0.004, 0.09, 0.10, 0)
            # chains to an anchor 0.45 m up
            for x in (0.15, L - 0.15):
                cylinder(bm, x, 0, 0.16, 0.61, 0.004, 6, mat=0)
        objs.append(finish(bm, f"{name}_LOD{lod}", [M["metal"]]))
        bm = new_bm()
        for y in (-0.045, 0.045):
            cylinder(bm, y, 0.065, 0.02, L - 0.02, 0.019, 12 if lod == 0 else 6, mat=0, axis="X")
        objs.append(finish(bm, f"{name}_Tubes_LOD{lod}", [M["fluor"]]))
    objs += ucx_boxes(name, [(0, -0.16, 0.0, L, 0.16, 0.16)], M)
    return name, objs


def build_sign(M):
    """Door sign: brass plate with raised black letters, 1963 wording. Room number FICTIONALISED."""
    name = "X14_PART_Sign_Door"
    objs = []
    pw, ph, pt = 0.42, 0.14, 0.004
    for lod in range(3):
        bm = new_bm()
        box(bm, -pw / 2, 0, 0, pw / 2, pt, ph, 0)
        if lod == 0:
            for (x, y) in ((-pw / 2 + 0.012, 0.012), (pw / 2 - 0.012, 0.012), (-pw / 2 + 0.012, ph - 0.012), (pw / 2 - 0.012, ph - 0.012)):
                cylinder(bm, x, y, pt, pt + 0.002, 0.004, 8, mat=0)
        plate = finish(bm, f"{name}_LOD{lod}", [M["brass"], M["signtext"]])
        objs.append(plate)
        if lod == 0:
            for text, z, size in (("LEGISLATIVE REFERENCE SERVICE", 0.085, 0.022),
                                  ("HISTORY AND GOVERNMENT DIVISION", 0.052, 0.016),
                                  ("ROOM 128", 0.020, 0.018)):
                cu = bpy.data.curves.new("txt", "FONT")
                cu.body = text
                cu.size = size
                cu.resolution_u = 3
                cu.align_x = "CENTER"
                cu.extrude = 0.0015
                to = bpy.data.objects.new("txt", cu)
                bpy.context.scene.collection.objects.link(to)
                to.location = (0, pt + 0.0015, z)
                to.rotation_euler = (math.pi / 2, 0, math.pi)
                bpy.ops.object.select_all(action="DESELECT")
                to.select_set(True)
                bpy.context.view_layer.objects.active = to
                bpy.ops.object.convert(target="MESH")
                to = bpy.context.view_layer.objects.active
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                tb = bmesh.new()
                tb.from_mesh(to.data)
                bmesh.ops.remove_doubles(tb, verts=tb.verts, dist=1e-5)
                bmesh.ops.dissolve_degenerate(tb, dist=1e-6, edges=tb.edges)
                bmesh.ops.triangulate(tb, faces=tb.faces)
                bmesh.ops.delete(tb, geom=[f for f in tb.faces if f.calc_area() < 1e-9], context="FACES_ONLY")
                bmesh.ops.recalc_face_normals(tb, faces=tb.faces)
                for f in tb.faces:
                    f.material_index = 1
                box_uv(tb)
                tb.to_mesh(to.data)
                tb.free()
                # merge letters into the plate mesh
                pb = bmesh.new()
                pb.from_mesh(plate.data)
                pb.from_mesh(to.data)
                pb.to_mesh(plate.data)
                pb.free()
                bpy.data.objects.remove(to, do_unlink=True)
    objs += ucx_boxes(name, [(-pw / 2, 0, 0, pw / 2, pt + 0.002, ph)], M)
    return name, objs


# =============================================================================== export
def export_glb(name, objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
        for c in o.children_recursive:
            c.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_apply=True,
        export_yup=True, export_texcoords=True, export_normals=True, export_materials="EXPORT",
        export_image_format="AUTO", export_extras=True, export_lights=False, export_cameras=False,
        export_animations=False, export_skins=False, export_morph=False,
    )


MODULES = [
    ("X14_ARCH_Wall_Plain_300", build_wall_plain),
    ("X14_ARCH_Wall_Window_300", build_wall_window),
    ("X14_ARCH_Wall_Door_300", build_wall_door),
    ("X14_ARCH_Corner", build_corner),
    ("X14_ARCH_Floor_300", lambda M: build_floor(M, False)),
    ("X14_ARCH_Floor_300_Linoleum", lambda M: build_floor(M, True)),
    ("X14_ARCH_Ceiling_300", build_ceiling),
    ("X14_ARCH_Pendant_Lamp", build_pendant),
    ("X14_PART_Panel_Solid_120", lambda M: build_part_panel(M, False)),
    ("X14_PART_Panel_Glazed_120", lambda M: build_part_panel(M, True)),
    ("X14_PART_Panel_Solid_060", lambda M: build_part_panel(M, False, 0.60)),
    ("X14_PART_Door_090", build_part_door),
    ("X14_PART_Post", build_part_post),
    ("X14_PART_DropCeiling_120", build_drop_ceiling),
    ("X14_PART_Fluorescent_120", build_fluorescent),
    ("X14_PART_Sign_Door", build_sign),
]


def place(objs, loc, rot_z=0.0, tag=""):
    """Instance a module's objects (shared mesh data) at a transform; returns new objects."""
    out = []
    mat = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rot_z, 4, "Z")
    mapping = {}
    for o in objs:
        n = o.data.copy() if False else o.data  # shared data
        c = bpy.data.objects.new(o.name + tag, n)
        c.empty_display_type = o.empty_display_type if o.type == "EMPTY" else "PLAIN_AXES"
        bpy.context.scene.collection.objects.link(c)
        mapping[o] = c
        out.append(c)
    for o in objs:
        c = mapping[o]
        if o.parent in mapping:
            c.parent = mapping[o.parent]
            c.matrix_local = o.matrix_local
        else:
            c.matrix_world = mat @ o.matrix_world
    return out


def build_demo(M, built):
    """9 × 6 m LRS division room: east wall with 3 arched windows, door in the west wall, gray
    partitions dividing the room into 3 cubicles + corridor, dropped ceiling and fluorescents over
    the cubicle zone, pendants over the open zone, I09 furniture sockets. FICTIONALISED layout."""
    B = {n: o for n, o in built}
    objs = []
    W, D = 9.0, 6.0
    # floor 3×2 modules, ceiling
    for i in range(3):
        for j in range(2):
            objs += place(B["X14_ARCH_Floor_300"], (i * 3, j * 3, 0), tag=f".f{i}{j}")
            objs += place(B["X14_ARCH_Ceiling_300"], (i * 3, j * 3, ROOM_H), tag=f".c{i}{j}")
    # south wall (y=0, room on +Y): plain, door, plain
    objs += place(B["X14_ARCH_Wall_Plain_300"], (0, 0, 0), 0, ".s0")
    objs += place(B["X14_ARCH_Wall_Door_300"], (3, 0, 0), 0, ".s1")
    objs += place(B["X14_ARCH_Wall_Plain_300"], (6, 0, 0), 0, ".s2")
    # east wall (x=9): three window bays, run along +Y with room on -X → rotate +90° (run +Y, face -X)
    for j in range(2):
        objs += place(B["X14_ARCH_Wall_Window_300"], (W, j * 3, 0), math.pi / 2, f".e{j}")
    # north wall (y=6): run along -X, room on -Y → rotate 180°
    for i in range(3):
        objs += place(B["X14_ARCH_Wall_Plain_300"], (W - i * 3, D, 0), math.pi, f".n{i}")
    # west wall (x=0): run along -Y, room on +X → rotate -90°
    for j in range(2):
        objs += place(B["X14_ARCH_Wall_Window_300" if j == 1 else "X14_ARCH_Wall_Plain_300"], (0, D - j * 3, 0), -math.pi / 2, f".w{j}")
    # corners
    objs += place(B["X14_ARCH_Corner"], (0, 0, 0), 0, ".k0")
    objs += place(B["X14_ARCH_Corner"], (W, 0, 0), math.pi / 2, ".k1")
    objs += place(B["X14_ARCH_Corner"], (W, D, 0), math.pi, ".k2")
    objs += place(B["X14_ARCH_Corner"], (0, D, 0), -math.pi / 2, ".k3")
    # door sign beside the door
    objs += place(B["X14_PART_Sign_Door"], (3 + (MOD_W - DOOR_W) / 2 + DOOR_W + 0.25, 0.0, 1.55), 0, ".sign")
    # Partition run along y = 1.8 (corridor 1.8 m wide along the south wall), three cubicles.
    # Each cubicle front = glazed 1.2 + door 0.9 + solid filler 0.6 = 2.7 m; 3 × 2.7 = 8.1 m, from x = 0.45.
    y_run = 1.8
    x = 0.45
    objs += place(B["X14_PART_Post"], (x, y_run, 0), 0, ".p0")
    seq = ["G", "D", "S6"] * 3
    for k, s_ in enumerate(seq):
        mod = {"G": "X14_PART_Panel_Glazed_120", "D": "X14_PART_Door_090", "S6": "X14_PART_Panel_Solid_060"}[s_]
        wid = {"G": 1.2, "D": 0.9, "S6": 0.6}[s_]
        objs += place(B[mod], (x, y_run, 0), 0, f".pr{k}")
        x += wid
        objs += place(B["X14_PART_Post"], (x, y_run, 0), 0, f".pq{k}")
    # cubicle dividers running +Y from the corridor line to the north wall: 3 × 1.2 + 0.6 = 4.2 m
    for xd in (0.45 + 2.7, 0.45 + 5.4):
        yy = y_run
        for k, (mod, wid) in enumerate([("X14_PART_Panel_Solid_120", 1.2), ("X14_PART_Panel_Glazed_120", 1.2),
                                        ("X14_PART_Panel_Glazed_120", 1.2), ("X14_PART_Panel_Solid_060", 0.6)]):
            objs += place(B[mod], (xd, yy, 0), math.pi / 2, f".pdv{int(xd*100)}_{k}")
            yy += wid
            if yy < D - 0.01:
                objs += place(B["X14_PART_Post"], (xd, yy, 0), 0, f".pdq{int(xd*100)}_{k}")
    # dropped ceiling over the cubicle zone (y 1.8..6.0, x 0.3..8.7), fixtures every other cell
    nx, ny = 7, 3
    for i in range(nx):
        for j in range(ny):
            objs += place(B["X14_PART_DropCeiling_120"], (0.3 + i * 1.2, y_run + j * 1.2 + 0.6, DROP_Z), 0, f".dc{i}{j}")
            if (i + j) % 2 == 0:
                objs += place(B["X14_PART_Fluorescent_120"], (0.3 + i * 1.2 - 0.01, y_run + j * 1.2 + 1.2, DROP_Z - 0.62), 0, f".fl{i}{j}")
    # pendants over the corridor zone
    for i in range(3):
        objs += place(B["X14_ARCH_Pendant_Lamp"], (1.5 + i * 3, 0.9, ROOM_H - 1.10), 0, f".pl{i}")
    # I09 furniture sockets (desk faces -Y toward the corridor; chair behind; file cabinet on divider)
    cub_x = [1.8, 4.5, 7.2]
    for c, cx in enumerate(cub_x):
        objs.append(empty(f"SOCKET_I09_Desk_{c+1:02d}", (cx, 3.6, 0), (0, 0, math.pi)))
        objs.append(empty(f"SOCKET_I09_Chair_{c+1:02d}", (cx, 4.4, 0), (0, 0, math.pi)))
        objs.append(empty(f"SOCKET_I09_FileCabinet_{c+1:02d}", (cx - 1.0, 5.6, 0), (0, 0, 0)))
        objs.append(empty(f"SOCKET_I09_Typewriter_{c+1:02d}", (cx + 0.4, 3.5, 0.75), (0, 0, math.pi)))
        objs.append(empty(f"SOCKET_I09_DeskLamp_{c+1:02d}", (cx - 0.5, 3.75, 0.75), (0, 0, math.pi)))
        objs.append(empty(f"SOCKET_I09_Telephone_{c+1:02d}", (cx + 0.6, 3.75, 0.75), (0, 0, math.pi)))
    objs.append(empty("SOCKET_I09_WallClock_01", (4.5, 0.03, 2.4), (0, 0, 0)))
    objs.append(empty("SOCKET_X15_StaffAccess_Door", (4.5, 0.0, 0), (0, 0, math.pi / 2)))
    return "X14_DEMO_LRS_Room", objs


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    build_textures()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    M = materials()
    built = []
    manifest = {"units": "metres (glTF spec); UE 5.8 glTF import → cm", "seed": SEED, "modules": {}}
    for name, fn in MODULES:
        n, objs = fn(M)
        built.append((n, objs))
        path = os.path.join(OUT, f"{n}.glb")
        export_glb(n, objs, path)
        tris = sum(len(o.data.polygons) for o in objs if o.type == "MESH" and o.name.endswith("_LOD0"))
        manifest["modules"][n] = {
            "file": os.path.basename(path),
            "objects": [o.name for o in objs],
            "lod0_faces": tris,
            "materials": sorted({s.material.name for o in objs if o.type == "MESH" for s in o.material_slots if s.material}),
        }
        print("exported", path)
    n, objs = build_demo(M, built)
    path = os.path.join(OUT, f"{n}.glb")
    export_glb(n, objs, path)
    manifest["modules"][n] = {"file": os.path.basename(path), "objects": len(objs), "note": "assembly of kit instances + I09 sockets"}
    print("exported", path)
    with open(os.path.join(OUT, "BUILD_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "DC-X14_kit.blend"))


if __name__ == "__main__":
    main()
