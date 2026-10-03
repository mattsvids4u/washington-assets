"""PREVIEW-ONLY set dressing for DC-X14 demo-room renders.

Furniture belongs to DC-I09 (Office furniture set). Its v005 ZIP could not be brought into the
cloud sandbox, so this module drops simple period stand-ins (flat-top pedestal desk, wooden swivel
armchair, 4-drawer steel file, typewriter, desk telephone, desk lamp, pedestal fan, wall clock,
paper stacks and document boxes per the Sept 1953 LRS photo, EVIDENCE.md E19) onto the
SOCKET_I09_* empties so the rooms can be judged dressed and the socket layout checked at scale.

With `--i09 <meshes dir>` the real DC-I09 LOD0 meshes (desk, filing cabinet, typewriter, rotary
phone, desk lamp, wall clock) are used instead of stand-ins; only the chair, pedestal fan, papers
and document boxes remain stand-ins (DC-I09 has no chair or fan).

None of this geometry is exported in any X14 GLB. It exists only inside render_interior.py
(--dress). Replace with the real DC-I09 meshes in Unreal. No brand marks anywhere.

Socket convention (PCG_INTERFACE.json): the user of an item faces local +Y; desk-top sockets sit
on the desk top (z = 0 local). Desk sitter is on local -Y, drawers face local -Y.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as K  # noqa: E402  (kit helpers: box, cylinder, lathe, finish, orient_wood_uvs)


def _mat(name, color, rough=0.5, metal=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emission:
        b.inputs["Emission Color"].default_value = (*emission, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def _kit(name, fallback):
    return bpy.data.materials.get(name) or fallback


def materials():
    oak = _kit("MI_X14_Oak_Door", _mat("PREVIEW_Oak", (0.36, 0.23, 0.14), 0.45))
    return {
        "oak": oak,
        "brass": _kit("MI_X14_Brass", _mat("PREVIEW_Brass", (0.78, 0.62, 0.32), 0.3, 1.0)),
        "dark": _kit("MI_X14_Metal_Painted", _mat("PREVIEW_DarkMetal", (0.12, 0.12, 0.12), 0.45, 0.6)),
        "steel": _mat("PREVIEW_SteelEnamel_LightGray", (0.56, 0.57, 0.53), 0.42, 0.2),
        "chrome": _mat("PREVIEW_Chrome", (0.8, 0.8, 0.8), 0.15, 1.0),
        "black": _mat("PREVIEW_BlackEnamel", (0.025, 0.025, 0.025), 0.3),
        "paper": _mat("PREVIEW_Paper", (0.86, 0.84, 0.77), 0.8),
        "card": _mat("PREVIEW_Cardboard", (0.55, 0.42, 0.27), 0.85),
        "white": _mat("PREVIEW_DialWhite", (0.9, 0.9, 0.86), 0.4),
        "green": _mat("PREVIEW_ShadeGreen", (0.02, 0.16, 0.07), 0.12, 0.0, (0.4, 0.8, 0.45), 0.12),
        "leather": _mat("PREVIEW_Leather", (0.20, 0.10, 0.06), 0.55),
    }


def _xform(bm, verts, rot=None, loc=(0, 0, 0)):
    if rot is not None:
        bmesh.ops.rotate(bm, verts=verts, cent=(0, 0, 0), matrix=rot)
    bmesh.ops.translate(bm, verts=verts, vec=Vector(loc))


# ----------------------------------------------------------------------------- pieces (local frame)
def desk(bm, M):
    o, b = 0, 1
    K.box(bm, -0.76, -0.38, 0.725, 0.76, 0.38, 0.76, o)                    # top, overhangs pedestals
    for x0, x1 in ((-0.73, -0.33), (0.33, 0.73)):
        K.box(bm, x0, -0.355, 0.045, x1, 0.355, 0.73, o)                  # pedestal carcass
        K.box(bm, x0 + 0.02, -0.335, 0.0, x1 - 0.02, 0.335, 0.05, o)      # recessed plinth
        for z0, z1 in ((0.06, 0.255), (0.268, 0.468), (0.481, 0.705)):
            K.box(bm, x0 + 0.012, -0.366, z0, x1 - 0.012, -0.35, z1, o)    # drawer front (embedded 5 mm)
            K.box(bm, (x0 + x1) / 2 - 0.05, -0.38, (z0 + z1) / 2 - 0.008, (x0 + x1) / 2 + 0.05, -0.362, (z0 + z1) / 2 + 0.008, b)
    K.box(bm, -0.318, -0.366, 0.645, 0.318, -0.30, 0.72, o)                 # centre (pencil) drawer
    K.box(bm, -0.05, -0.378, 0.674, 0.05, -0.362, 0.69, b)
    K.box(bm, -0.335, 0.325, 0.16, 0.335, 0.35, 0.73, o)                    # modesty panel at the back


def chair(bm, M):
    w, d, m = 0, 1, 2
    K.cylinder(bm, 0, 0, 0.43, 0.475, 0.235, 28, mat=w)                    # round saddle seat
    for sx in (-1, 1):
        K.box(bm, sx * 0.205 - 0.014, -0.235, 0.47, sx * 0.205 + 0.014, -0.205, 0.86, w)   # back posts
        K.box(bm, sx * 0.235 - 0.014, -0.215, 0.62, sx * 0.235 + 0.014, 0.17, 0.645, w)    # arms
        K.box(bm, sx * 0.235 - 0.011, 0.13, 0.47, sx * 0.235 + 0.011, 0.155, 0.625, w)     # arm stumps
    K.box(bm, -0.22, -0.245, 0.74, 0.22, -0.208, 0.87, w)                  # back rail
    for sx in (-0.11, 0.0, 0.11):
        K.box(bm, sx - 0.018, -0.232, 0.475, sx + 0.018, -0.214, 0.745, w)  # back spindles
    K.cylinder(bm, 0, 0, 0.40, 0.432, 0.11, 20, mat=m)                      # iron spider plate
    K.cylinder(bm, 0, 0, 0.10, 0.405, 0.028, 16, mat=m)                     # swivel column
    for a in range(4):                                                     # 4 splayed feet
        ang = a * math.pi / 2 + math.pi / 4
        g = bmesh.ops.create_cube(bm, size=1.0)
        vs = g["verts"]
        bmesh.ops.scale(bm, vec=(0.30, 0.04, 0.035), verts=vs)
        _xform(bm, vs, None, (0.17, 0, 0.09))
        _xform(bm, vs, Matrix.Rotation(ang, 3, "Z"))
        for f in {f for v in vs for f in v.link_faces}:
            f.material_index = m
        cx, cy = 0.31 * math.cos(ang), 0.31 * math.sin(ang)
        K.cylinder(bm, cx, cy, 0.0, 0.07, 0.03, 12, mat=d)                   # caster


def file_cabinet(bm, M):
    s, c = 0, 1
    K.box(bm, -0.19, -0.355, 0.03, 0.19, 0.355, 1.32, s)                    # carcass
    K.box(bm, -0.17, -0.335, 0.0, 0.17, 0.335, 0.035, s)                    # recessed base
    h = (1.30 - 0.05) / 4
    for i in range(4):
        z0 = 0.05 + i * h + 0.006
        z1 = z0 + h - 0.012
        K.box(bm, -0.178, 0.348, z0, 0.178, 0.364, z1, s)                   # drawer front
        zm = z0 + (z1 - z0) * 0.62
        K.box(bm, -0.06, 0.362, zm - 0.012, 0.06, 0.382, zm + 0.012, c)       # pull
        K.box(bm, -0.04, 0.362, zm + 0.03, 0.04, 0.368, zm + 0.058, c)        # label holder


def typewriter(bm, M):
    k, ch, p = 0, 1, 2
    K.box(bm, -0.22, -0.16, 0.0, 0.22, 0.13, 0.085, k)                       # frame
    K.box(bm, -0.20, -0.215, 0.0, 0.20, -0.155, 0.04, k)                     # keyboard apron
    for r in range(4):
        for i in range(11 - (r % 2)):
            x = -0.17 + i * 0.032 + (r % 2) * 0.016
            y, z = -0.20 + r * 0.025, 0.045 + r * 0.012
            K.cylinder(bm, x, y, z, z + 0.012, 0.0075, 8, mat=ch)           # key tops
    K.box(bm, -0.09, -0.215, 0.035, 0.09, -0.19, 0.05, k)                   # space bar
    K.cylinder(bm, 0.11, 0.11, -0.26, 0.26, 0.024, 16, mat=k, axis="X")     # platen (y=0.11, z=0.11)
    K.box(bm, -0.105, 0.105, 0.11, 0.105, 0.111, 0.36, p)                   # sheet of paper
    K.box(bm, -0.30, 0.09, 0.115, -0.26, 0.12, 0.125, ch)                   # carriage return lever


def telephone(bm, M):
    k, w = 0, 1
    K.box(bm, -0.105, -0.11, 0.0, 0.105, 0.10, 0.065, k)                     # base
    K.box(bm, -0.09, -0.06, 0.06, 0.09, 0.07, 0.085, k)                      # upper housing
    K.cylinder(bm, -0.035, 0.0, 0.06, 0.075, 0.05, 24, mat=k)               # dial ring (front)
    K.box(bm, -0.13, 0.02, 0.10, 0.13, 0.06, 0.122, k)                       # handset bar
    for x in (-0.11, 0.11):
        K.cylinder(bm, x, 0.04, 0.085, 0.125, 0.032, 16, mat=k)             # ear / mouth cups
    for x in (-0.06, 0.06):
        K.box(bm, x - 0.01, 0.03, 0.08, x + 0.01, 0.05, 0.10, k)             # cradle prongs


def telephone_dial(bm, M):
    K.cylinder(bm, -0.035, 0.0, 0.075, 0.079, 0.036, 24, mat=0)             # dial face


def desk_lamp(bm, M):
    b, g = 0, 1
    K.cylinder(bm, 0, 0, 0.0, 0.02, 0.085, 28, mat=b)
    K.cylinder(bm, 0, 0, 0.02, 0.33, 0.009, 12, mat=b)
    K.box(bm, -0.13, -0.012, 0.31, 0.13, 0.012, 0.325, b)                    # yoke
    r0, r1 = K.cylinder(bm, 0.0, 0.355, -0.12, 0.12, 0.048, 32, mat=g, axis="X")   # cased-glass shade
    bmesh.ops.delete(bm, geom=[v for v in r0 + r1 if v.co.z < 0.355 - 1e-4], context="VERTS")  # half-shade, open below


def pedestal_fan(bm, M):
    m, br = 0, 1
    K.cylinder(bm, 0, 0, 0.0, 0.035, 0.17, 32, mat=m)
    K.cylinder(bm, 0, 0, 0.035, 1.12, 0.014, 12, mat=m)
    K.cylinder(bm, 0.0, 1.17, -0.08, 0.06, 0.07, 24, mat=m, axis="Y")       # motor (x=0, z=1.17), along Y
    # guard: two rings + a few ribs, and three brass blades, all facing +Y
    tmp = bmesh.new()
    for r, y in ((0.20, 0.10), (0.20, 0.13)):
        K.lathe(tmp, [(r - 0.008, 0.0), (r, 0.0), (r, 0.006), (r - 0.008, 0.006)], 48, z0=y)
    for i in range(8):
        a = i * math.pi / 4
        g = bmesh.ops.create_cube(tmp, size=1.0)
        bmesh.ops.scale(tmp, vec=(0.004, 0.40, 0.004), verts=g["verts"])
        _xform(tmp, g["verts"], Matrix.Rotation(a, 3, "Z"), (0, 0, 0.13))
    for i in range(3):
        a = i * 2 * math.pi / 3
        g = bmesh.ops.create_cube(tmp, size=1.0)
        bmesh.ops.scale(tmp, vec=(0.06, 0.15, 0.004), verts=g["verts"])
        _xform(tmp, g["verts"], Matrix.Rotation(0.35, 3, "Y"), (0, 0.09, 0.115))
        _xform(tmp, g["verts"], Matrix.Rotation(a, 3, "Z"))
        for f in {f for v in g["verts"] for f in v.link_faces}:
            f.material_index = br
    # rotate guard axis from +Z to +Y and hang on the motor
    bmesh.ops.rotate(tmp, verts=tmp.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(-math.pi / 2, 3, "X"))
    bmesh.ops.translate(tmp, verts=tmp.verts, vec=(0, 0.0, 1.17))
    me = bpy.data.meshes.new("tmp")
    tmp.to_mesh(me)
    tmp.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def wall_clock(bm, M):
    w, f, k = 0, 1, 2
    K.cylinder(bm, 0.0, 0.0, 0.0, 0.07, 0.19, 48, mat=w, axis="Y")         # oak case (x, z) = (0, 0)
    K.cylinder(bm, 0.0, 0.0, 0.07, 0.078, 0.165, 48, mat=f, axis="Y")      # face
    K.box(bm, -0.004, 0.078, -0.005, 0.004, 0.083, 0.12, k)                  # minute hand
    g = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.085, 0.004, 0.01), verts=g["verts"])
    _xform(bm, g["verts"], Matrix.Rotation(math.radians(30), 3, "Y"), (0.035, 0.081, -0.02))
    for fc in {fc for v in g["verts"] for fc in v.link_faces}:
        fc.material_index = k
    for i in range(12):
        a = i * math.pi / 6
        K.box(bm, 0.14 * math.sin(a) - 0.004, 0.078, 0.14 * math.cos(a) - 0.012, 0.14 * math.sin(a) + 0.004, 0.081, 0.14 * math.cos(a) + 0.012, k)


def paper_stack(bm, M, w=0.22, d=0.28, h=0.03):
    K.box(bm, -w / 2, -d / 2, 0.0, w / 2, d / 2, h, 0)


def doc_box(bm, M):
    K.box(bm, -0.13, -0.19, 0.0, 0.13, 0.19, 0.25, 0)
    K.box(bm, -0.135, -0.195, 0.235, 0.135, 0.195, 0.27, 0)                  # lid


# ----------------------------------------------------------------------------- placement
PIECES = {
    "Desk": [(desk, ("oak", "brass"))],
    "Chair": [(chair, ("oak", "black", "dark"))],
    "FileCabinet": [(file_cabinet, ("steel", "chrome"))],
    "Typewriter": [(typewriter, ("black", "white", "paper"))],
    "Telephone": [(telephone, ("black", "white")), (telephone_dial, ("white",))],
    "DeskLamp": [(desk_lamp, ("brass", "green"))],
    "PedestalFan": [(pedestal_fan, ("dark", "brass"))],
    "WallClock": [(wall_clock, ("oak", "white", "black"))],
}
EXTRAS = {   # per-socket extra props (local offsets), from the 1953 photo: paper, wire baskets, boxes
    "Desk": [(paper_stack, ("paper",), (-0.15, -0.05, 0.76)), (paper_stack, ("paper",), (0.45, 0.12, 0.76))],
    "FileCabinet": [(doc_box, ("card",), (0.0, 0.0, 1.32))],
}


def _spawn(fn, mat_keys, M, name, mw, local=(0, 0, 0)):
    bm = bmesh.new()
    fn(bm, M)
    if local != (0, 0, 0):
        bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(local))
    ob = K.finish(bm, name, [M[k] for k in mat_keys])
    K.orient_wood_uvs([ob])
    ob.matrix_world = mw
    return ob


# ----------------------------------------------------------------------------- real DC-I09 meshes
I09_FILES = {
    "Desk": "I09_desk_LOD0.glb",
    "FileCabinet": "I09_filing_cabinet_LOD0.glb",
    "Typewriter": "I09_typewriter_LOD0.glb",
    "Telephone": "I09_rotary_phone_LOD0.glb",
    "DeskLamp": "I09_desk_lamp_LOD0.glb",
    "WallClock": "I09_wall_clock_LOD0.glb",
}
# DC-I09 v004 GLBs store their authored Z-up coordinates without the glTF Y-up conversion, so a
# standard importer lays every piece on its back. Preview-only correction: rotate -90° about X.
# (Reported to the I09 owner in HANDOFF.md; the I09 files themselves are not modified.)
I09_AXIS_FIX = Matrix.Rotation(-math.pi / 2, 4, "X")
# Paper stacks placed clear of the real I09 typewriter / phone / lamp footprints (desk-local).
EXTRAS_I09 = {
    "Desk": [(lambda bm, M: paper_stack(bm, M, 0.21, 0.18, 0.025), ("paper",), (-0.42, -0.27, 0.763)),
             (lambda bm, M: paper_stack(bm, M, 0.20, 0.26, 0.035), ("paper",), (0.62, -0.20, 0.763))],
    "FileCabinet": [(doc_box, ("card",), (0.0, 0.0, 1.334))],
}


def _load_i09(path):
    """Import one I09 GLB; return [(mesh_data, local_matrix)] with the axis fix baked in. The
    imported originals are hidden and kept only as data holders."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    bpy.context.view_layer.update()
    parts = [(o.data, I09_AXIS_FIX @ o.matrix_world.copy()) for o in new if o.type == "MESH"]
    for o in new:
        o.hide_render = True
        o.hide_viewport = True
        o.location.z -= 1000.0 if o.parent is None else 0.0
    return parts


def dress(scene_objects, i09_dir=None):
    """Dress every SOCKET_I09_* empty. With i09_dir, real DC-I09 LOD0 meshes are instanced where
    I09 provides the piece; chair, pedestal fan, papers and boxes stay as stand-ins either way."""
    M = materials()
    out = []
    sockets = [o for o in scene_objects if o.type == "EMPTY" and o.name.startswith("SOCKET_I09_")]
    real = {}
    if i09_dir:
        for kind, fn in I09_FILES.items():
            real[kind] = _load_i09(os.path.join(i09_dir, fn))
    extras = EXTRAS_I09 if i09_dir else EXTRAS
    for e in sockets:
        kind = e.name.split("_")[2]
        mw = e.matrix_world.copy()
        if kind in real:
            for i, (data, local) in enumerate(real[kind]):
                ob = bpy.data.objects.new(f"I09_{kind}_{e.name[-2:]}_{i}", data)
                bpy.context.scene.collection.objects.link(ob)
                ob.matrix_world = mw @ local
                out.append(ob)
        else:
            for i, (fn, keys) in enumerate(PIECES.get(kind, [])):
                out.append(_spawn(fn, keys, M, f"PREVIEW_{kind}_{e.name[-2:]}_{i}", mw))
        for j, (fn, keys, off) in enumerate(extras.get(kind, [])):
            out.append(_spawn(fn, keys, M, f"PREVIEW_{kind}_{e.name[-2:]}_x{j}", mw, off))
    return out
