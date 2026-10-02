"""DC-V01 — MPD patrol car 1963 — reproducible generator (bpy 4.5).

Run:  python jobs/DC-V01/build.py            (full build + GLB export)
      python jobs/DC-V01/build.py --preview  (body shell only, quick clay check)

Builds a 1963 Ford-pattern full-size four-door sedan (APPROXIMATE identity, see EVIDENCE.md):
lofted body skin from parametric cross-sections -> Catmull-Clark -> solidified shell ->
boolean window apertures / wheel wells / panel gaps -> doors, hood, trunk split into hinged
objects -> glazing, chrome, lamps, grille, bumpers, wheels, interior, MPD livery layer.
Units: Blender metres (authored in cm, converted by V()). Nose points to -Y, driver side +X,
Z up, tyres on Z = 0. glTF export in metres; Unreal imports as centimetres.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TEX = os.path.join(OUT, "textures")
PREVIEW = "--preview" in sys.argv

# ----------------------------------------------------------------------------- key dimensions (cm)
WHEELBASE = 302.0          # 119 in
TREAD_F, TREAD_R = 155.0, 152.0
TYRE_OD, TYRE_W = 71.0, 19.0
TYRE_SAG = 1.0             # loaded-tyre deflection: hub height = OD/2 - SAG, flat contact patch
RIM_D = 35.6               # 14 in
AXLE_F, AXLE_R = -151.0, 151.0
NOSE, TAIL = -240.0, 278.0  # sheet-metal ends (bumpers add ~6 cm each)
SHELL_T = 2.5

# ----------------------------------------------------------------------------- helpers

def V(x, y, z):
    return Vector((x / 100.0, y / 100.0, z / 100.0))


def interp(keys, t):
    """Piecewise-linear interpolation over [(t, value), ...] sorted by t."""
    if t <= keys[0][0]:
        return keys[0][1]
    if t >= keys[-1][0]:
        return keys[-1][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0
            f = f * f * (3 - 2 * f)  # smoothstep between keys
            return v0 + (v1 - v0) * f
    return keys[-1][1]


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def new_obj(name, bm, mats=()):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    return link(bpy.data.objects.new(name, me))


def set_active(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_mod(obj, mod):
    set_active(obj)
    bpy.ops.object.modifier_apply(modifier=mod.name)


def boolean(obj, cutter, op="DIFFERENCE", keep=False):
    mod = obj.modifiers.new("bool", "BOOLEAN")
    mod.operation = op
    mod.solver = "EXACT"
    mod.use_self = False
    mod.use_hole_tolerant = True
    mod.object = cutter
    apply_mod(obj, mod)
    if not keep:
        bpy.data.objects.remove(cutter, do_unlink=True)


def duplicate(obj, name):
    o = obj.copy()
    o.data = obj.data.copy()
    o.name = name
    o.data.name = name
    link(o)
    return o


def cleanup(obj, merge=0.0005):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=merge)
    bmesh.ops.dissolve_degenerate(bm, dist=merge, edges=bm.edges)
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method="BEAUTY", ngon_method="BEAUTY")
    slivers = [f for f in bm.faces if f.calc_area() < 2e-10]   # zero-area triangles (QA threshold 1e-10)
    if slivers:
        bmesh.ops.delete(bm, geom=slivers, context="FACES")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()


def box_uv(obj, scale=1.0):
    """Triplanar box projection, 1 UV unit = 1 m * scale."""
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if ax == 0:
                u, v = co.y, co.z
            elif ax == 1:
                u, v = co.x, co.z
            else:
                u, v = co.x, co.y
            uv[li].uv = (u * scale, v * scale)


def set_origin(obj, pivot):
    """Move the object's origin to `pivot` (world, metres) without moving the geometry."""
    d = Vector(pivot) - obj.matrix_world.translation
    obj.data.transform(Matrix.Translation(-d))
    obj.location = obj.location + d


def smooth(obj, angle=35):
    me = obj.data
    for p in me.polygons:
        p.use_smooth = True
    if hasattr(me, "set_sharp_from_angle"):
        me.set_sharp_from_angle(angle=math.radians(angle))


def mat_index(obj, mat):
    for i, s in enumerate(obj.material_slots):
        if s.material == mat:
            return i
    obj.data.materials.append(mat)
    return len(obj.material_slots) - 1


def assign_all(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.material_index = 0


# ----------------------------------------------------------------------------- bmesh primitives

def bm_box(bm, x0, y0, z0, x1, y1, z1, mat=0):
    vs = [bm.verts.new(V(x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    # index: x*4 + y*2 + z
    idx = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    for q in idx:
        f = bm.faces.new([vs[i] for i in q])
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_prism(bm, poly, axis, a0, a1, mat=0):
    """Extrude a 2D polygon [(u, v), ...] along `axis` ('x', 'y' or 'z') from a0 to a1 (cm)."""
    def p3(u, v, a):
        if axis == "x":
            return V(a, u, v)
        if axis == "y":
            return V(u, a, v)
        return V(u, v, a)
    lo = [bm.verts.new(p3(u, v, a0)) for u, v in poly]
    hi = [bm.verts.new(p3(u, v, a1)) for u, v in poly]
    n = len(poly)
    bm.faces.new(lo)
    bm.faces.new(list(reversed(hi)))
    for i in range(n):
        bm.faces.new([lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]])
    for f in bm.faces:
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_plate(bm, pts3, normal, t0, t1, mat=0):
    """Polygon given by 3D points (metres) thickened from t0 to t1 (metres) along `normal`."""
    n = Vector(normal).normalized()
    lo = [bm.verts.new(Vector(p) + n * t0) for p in pts3]
    hi = [bm.verts.new(Vector(p) + n * t1) for p in pts3]
    k = len(pts3)
    bm.faces.new(lo)
    bm.faces.new(list(reversed(hi)))
    for i in range(k):
        bm.faces.new([lo[i], lo[(i + 1) % k], hi[(i + 1) % k], hi[i]])
    for f in bm.faces:
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_ring_plate(bm, outer3, inner3, normal, t0, t1, mat=0):
    """Flat ring between two same-count 3D polygons, thickened along normal."""
    n = Vector(normal).normalized()
    k = len(outer3)
    ol = [bm.verts.new(Vector(p) + n * t0) for p in outer3]
    il = [bm.verts.new(Vector(p) + n * t0) for p in inner3]
    oh = [bm.verts.new(Vector(p) + n * t1) for p in outer3]
    ih = [bm.verts.new(Vector(p) + n * t1) for p in inner3]
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new([ol[i], ol[j], il[j], il[i]])
        bm.faces.new([oh[j], oh[i], ih[i], ih[j]])
        bm.faces.new([ol[j], ol[i], oh[i], oh[j]])
        bm.faces.new([il[i], il[j], ih[j], ih[i]])
    for f in bm.faces:
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_cylinder(bm, center, axis, r, h0, h1, segs=32, mat=0):
    """Cylinder of radius r (cm) along axis ('x','y','z') from h0 to h1 (cm, relative to center)."""
    c = Vector(center)
    rings = []
    for h in (h0, h1):
        ring = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            u, v = r * math.cos(a), r * math.sin(a)
            if axis == "x":
                p = (c.x + h, c.y + u, c.z + v)
            elif axis == "y":
                p = (c.x + u, c.y + h, c.z + v)
            else:
                p = (c.x + u, c.y + v, c.z + h)
            ring.append(bm.verts.new(V(*p)))
        rings.append(ring)
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[1])
    for i in range(segs):
        j = (i + 1) % segs
        bm.faces.new([rings[0][i], rings[0][j], rings[1][j], rings[1][i]])
    for f in bm.faces:
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_revolve(bm, profile, axis, center, segs=40, mat=0, close=True):
    """Revolve a (radius, height) profile (cm) around `axis` through `center` (cm).
    profile: list of (r, h). Rings connected in order; closed into a torus-like tube if close."""
    c = Vector(center)
    rings = []
    for r, h in profile:
        ring = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            u, v = r * math.cos(a), r * math.sin(a)
            if axis == "x":
                p = (c.x + h, c.y + u, c.z + v)
            elif axis == "y":
                p = (c.x + u, c.y + h, c.z + v)
            else:
                p = (c.x + u, c.y + v, c.z + h)
            ring.append(bm.verts.new(V(*p)))
        rings.append(ring)
    n = len(rings)
    pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if close else [])
    for ra, rb in pairs:
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new([ra[i], ra[j], rb[j], rb[i]])
    if not close:
        # cap ends if the end radius is > 0
        for ring, rev in ((rings[0], True), (rings[-1], False)):
            if profile[0 if rev else -1][0] > 0.01:
                bm.faces.new(list(reversed(ring)) if rev else ring)
    for f in bm.faces:
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_sweep(bm, profile, path, mat=0):
    """Sweep a closed 2D profile [(s, t)] (cm, in the plane normal to the path) along a 3D path
    [(x,y,z) cm]. Profile s = lateral (binormal), t = up (Z-ish)."""
    pts = [Vector(p) for p in path]
    rings = []
    for i, p in enumerate(pts):
        if i == 0:
            d = pts[1] - pts[0]
        elif i == len(pts) - 1:
            d = pts[-1] - pts[-2]
        else:
            d = (pts[i + 1] - pts[i - 1])
        d.normalize()
        up = Vector((0, 0, 1))
        side = d.cross(up).normalized()
        ring = [bm.verts.new(V(*(p + side * s + up * t))) for s, t in profile]
        rings.append(ring)
    n = len(profile)
    for ra, rb in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([ra[i], ra[j], rb[j], rb[i]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    for f in bm.faces:
        f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def rounded_rect(w, h, r, n=4):
    """Closed 2D rounded rectangle centred on origin (cm)."""
    pts = []
    cx, cy = w / 2 - r, h / 2 - r
    for (sx, sy, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((sx * cx + r * math.cos(a), sy * cy + r * math.sin(a)))
    return pts


# ----------------------------------------------------------------------------- materials
M = {}


def material(name, color, roughness=0.5, metallic=0.0, alpha=1.0, transmission=0.0,
             emission=None, emission_strength=0.0, image=None, ior=1.45, specular=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = roughness
    b.inputs["Metallic"].default_value = metallic
    b.inputs["IOR"].default_value = ior
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = specular
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
        m.blend_method = "BLEND"
    if emission:
        b.inputs["Emission Color"].default_value = (*emission, 1)
        b.inputs["Emission Strength"].default_value = emission_strength
    if image:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
        tex.location = (-400, 200)
        nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
        nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
        m.surface_render_method = "BLENDED"
        m.blend_method = "BLEND"
    M[name] = m
    return m


def make_materials(images):
    material("MI_V01_Paint_Body", (0.86, 0.83, 0.70), roughness=0.22, specular=0.6)       # CT: cream
    material("MI_V01_Paint_Neutral", (0.42, 0.45, 0.42), roughness=0.25, specular=0.6)    # CT: base
    material("MI_V01_Chrome", (0.92, 0.92, 0.92), roughness=0.08, metallic=1.0)           # MT
    material("MI_V01_Steel_Painted", (0.06, 0.06, 0.06), roughness=0.5)                   # MT: wheels
    material("MI_V01_Glass", (0.80, 0.86, 0.86), roughness=0.03, alpha=0.22, transmission=0.9, ior=1.5)  # GL
    material("MI_V01_Lens_Red", (0.75, 0.04, 0.03), roughness=0.08, alpha=0.75, transmission=0.4, ior=1.5)
    material("MI_V01_Lens_Clear", (0.95, 0.95, 0.9), roughness=0.08, alpha=0.6, transmission=0.6, ior=1.5)
    material("MI_V01_Headlamp", (0.92, 0.93, 0.90), roughness=0.22, metallic=0.3, specular=1.0, alpha=0.9, transmission=0.25, ior=1.5)
    material("MI_V01_Rubber_Tyre", (0.04, 0.04, 0.04), roughness=0.85)
    material("MI_V01_Whitewall", (0.86, 0.86, 0.82), roughness=0.75)
    material("MI_V01_Interior_Trim", (0.52, 0.47, 0.38), roughness=0.8)                   # headliner/door cards
    material("MI_V01_Interior_Vinyl", (0.36, 0.30, 0.22), roughness=0.6)                  # seats
    material("MI_V01_Interior_Dark", (0.08, 0.08, 0.08), roughness=0.7)                   # dash/column/floor
    material("MI_V01_Undercoat", (0.11, 0.11, 0.105), roughness=0.95)                      # wells, gaps, underside
    material("MI_V01_Grille_Dark", (0.06, 0.06, 0.07), roughness=0.6, metallic=0.3)
    material("MI_V01_Beacon_Red_Unlit", (0.70, 0.05, 0.05), roughness=0.1, alpha=0.8, transmission=0.3, ior=1.5)
    material("MI_V01_Beacon_Red_Lit", (0.9, 0.05, 0.05), roughness=0.1, alpha=0.9,
             emission=(1.0, 0.05, 0.02), emission_strength=12.0)
    material("MI_V01_Decal_RoofID", (1, 1, 1), roughness=0.35, image=images["roof"])
    material("MI_V01_Decal_DoorSeal", (1, 1, 1), roughness=0.35, image=images["seal"])
    material("MI_V01_Decal_Trunk", (1, 1, 1), roughness=0.35, image=images["trunk"])
    material("MI_V01_Plate", (1, 1, 1), roughness=0.4, image=images["plate"])


# ----------------------------------------------------------------------------- textures (PIL)

def make_textures():
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(TEX, exist_ok=True)
    TEAL = (72, 150, 150, 255)
    BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    out = {}

    # Roof identifier: texture U = +X (driver side at U=1), V = car Y (front at V=0 top).
    # Two stacked letter pairs: M (driver) / P (passenger) over the front seat,
    # D / C over the rear seat; letter tops point to the driver side (+X) -> rotate glyphs 90 deg.
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    font = ImageFont.truetype(BOLD, 540)
    def glyph(ch):
        g = Image.new("RGBA", (560, 560), (0, 0, 0, 0))
        d = ImageDraw.Draw(g)
        bb = d.textbbox((0, 0), ch, font=font)
        d.text(((560 - (bb[2] - bb[0])) / 2 - bb[0], (560 - (bb[3] - bb[1])) / 2 - bb[1]), ch, font=font, fill=TEAL)
        return g.rotate(90, expand=False)   # top of the glyph now points to +U (driver side, +X)
    # decal plane spans x -72..72 (U), y -12..96 (V, front at V=0)
    for ch, u_c, v_c in (("M", 0.75, 0.22), ("P", 0.25, 0.22), ("D", 0.75, 0.77), ("C", 0.25, 0.77)):
        g = glyph(ch)
        im.alpha_composite(g, (int(u_c * S - 280), int(v_c * S - 280)))
    p = os.path.join(TEX, "T_V01_Decal_RoofID.png"); im.save(p); out["roof"] = p

    # Door seal: circular seal with generic text (APPROXIMATE, no copied artwork).
    S = 512
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((16, 16, S - 16, S - 16), outline=TEAL, width=18)
    d.ellipse((120, 120, S - 120, S - 120), outline=TEAL, width=10)
    d.ellipse((190, 190, S - 190, S - 190), fill=TEAL)
    fs = ImageFont.truetype(BOLD, 44)
    def arc_text(text, r, a0, a1, flip=False):
        n = len(text)
        if flip:
            a0, a1 = a1, a0          # lower arc: place glyphs right-to-left in angle so the text reads left-to-right
        for i, ch in enumerate(text):
            a = math.radians(a0 + (a1 - a0) * (i + 0.5) / n)
            cx, cy = S / 2 + r * math.cos(a), S / 2 + r * math.sin(a)
            g = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            bb = gd.textbbox((0, 0), ch, font=fs)
            gd.text(((80 - (bb[2] - bb[0])) / 2 - bb[0], (80 - (bb[3] - bb[1])) / 2 - bb[1]), ch, font=fs, fill=TEAL)
            rot = -math.degrees(a) - 90 + (180 if flip else 0)
            g = g.rotate(rot, resample=Image.BICUBIC)
            im.alpha_composite(g, (int(cx - 40), int(cy - 40)))
    arc_text("METROPOLITAN POLICE", 190, 200, 340)
    arc_text("WASHINGTON D.C.", 190, 20, 160, flip=True)
    p = os.path.join(TEX, "T_V01_Decal_DoorSeal.png"); im.save(p); out["seal"] = p

    # Trunk POLICE: U = -X..+X? plane maps U = car X (driver at U=0), V = car Y; read from behind.
    im = Image.new("RGBA", (1024, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f2 = ImageFont.truetype(BOLD, 150)
    bb = d.textbbox((0, 0), "POLICE", font=f2)
    d.text(((1024 - (bb[2] - bb[0])) / 2 - bb[0], (256 - (bb[3] - bb[1])) / 2 - bb[1]), "POLICE", font=f2, fill=TEAL)
    im = im.transpose(Image.FLIP_LEFT_RIGHT)  # viewer behind the car, driver side on their left
    p = os.path.join(TEX, "T_V01_Decal_Trunk.png"); im.save(p); out["trunk"] = p

    # Licence plate (FICTIONALISED): 1963-style DC plate, white on dark.
    im = Image.new("RGBA", (512, 256), (28, 36, 54, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((8, 8, 503, 247), outline=(230, 230, 220, 255), width=6)
    f3 = ImageFont.truetype(BOLD, 112)
    bb = d.textbbox((0, 0), "MP 1963", font=f3)
    d.text(((512 - (bb[2] - bb[0])) / 2 - bb[0], 86 - bb[1]), "MP 1963", font=f3, fill=(235, 235, 225, 255))
    f4 = ImageFont.truetype(BOLD, 34)
    bb = d.textbbox((0, 0), "DISTRICT OF COLUMBIA", font=f4)
    d.text(((512 - (bb[2] - bb[0])) / 2 - bb[0], 22 - bb[1]), "DISTRICT OF COLUMBIA", font=f4, fill=(235, 235, 225, 255))
    p = os.path.join(TEX, "T_V01_Plate.png"); im.save(p); out["plate"] = p
    return out


def load_images(paths):
    imgs = {}
    for k, p in paths.items():
        img = bpy.data.images.load(p)
        img.pack()
        imgs[k] = img
    return imgs


# ----------------------------------------------------------------------------- body cross-sections
# Feature curves along Y (cm). Each returns a value at station y.
K = {
    # centreline top: hood -> windshield -> roof -> rear window -> deck
    "zc":   [(NOSE, 85.0), (-225, 87.0), (-150, 89.0), (-70, 91.5), (-58, 93.5), (-24, 136.5), (35, 140.5),
             (118, 138.5), (122, 136.0), (158, 98.0), (166, 96.0), (240, 93.0), (TAIL, 90.0)],
    # near-centre crown point (hood crease / roof crown)
    "x1":   [(NOSE, 14), (-60, 14), (-24, 30), (118, 30), (158, 20), (TAIL, 20)],
    "dz1":  [(NOSE, -1.8), (-62, -1.8), (-50, -0.6), (-24, -0.4), (118, -0.4), (158, -0.4), (TAIL, -0.8)],
    # outer top panel point (hood edge / roof edge at the drip rail)
    "x3":   [(NOSE, 54), (-150, 60), (-70, 64), (-58, 66), (-34, 70), (-24, 72), (40, 74), (118, 72),
             (124, 70), (158, 70), (166, 72), (240, 68), (TAIL, 60)],
    "z3":   [(NOSE, 84.0), (-225, 86.0), (-150, 88.0), (-70, 90.5), (-58, 92.5), (-24, 134.0), (35, 137.5),
             (118, 135.0), (122, 133.0), (158, 97.0), (166, 95.0), (240, 92.0), (TAIL, 89.0)],
    # fender top inner / belt sill (window base)
    "x4":   [(NOSE, 76), (-225, 82), (-150, 86), (-70, 89), (-58, 90), (-34, 91.5), (-24, 92), (40, 93),
             (130, 93), (158, 92), (166, 91), (240, 88), (TAIL, 80)],
    "z4":   [(NOSE, 84.5), (-225, 86.5), (-150, 88.5), (-70, 91.0), (-58, 93.0), (-34, 95.5), (-24, 96.5), (40, 96.5),
             (158, 96.5), (166, 95.5), (240, 93.0), (TAIL, 90.0)],
    # shoulder crease (max width upper) - sharp horizontal character line
    "x5":   [(NOSE, 88), (-225, 95), (-150, 98.5), (-70, 100.5), (0, 101.5), (120, 101.5), (160, 100.5), (240, 97), (TAIL, 90)],
    "z5":   [(NOSE, 81.5), (-225, 83.5), (-150, 85.5), (-70, 88.0), (0, 90.5), (158, 91.0), (240, 89.5), (TAIL, 86.5)],
    # side mid (slightly convex door skin)
    "x6":   [(NOSE, 87), (-225, 94.5), (-150, 98.5), (-70, 100.8), (0, 102.0), (120, 102.0), (160, 100.8), (240, 96.5), (TAIL, 89)],
    "z6":   [(NOSE, 64), (-70, 64), (0, 64), (TAIL, 64)],
    # lower side
    "x7":   [(NOSE, 84), (-225, 92), (-150, 95.5), (-70, 97.5), (0, 98.5), (120, 98.5), (160, 97.5), (240, 94), (TAIL, 86)],
    "z7":   [(NOSE, 46), (-70, 44), (0, 44), (TAIL, 46)],
    # rocker top / bottom (tucked under)
    "x8":   [(NOSE, 78), (-225, 86), (-150, 90), (-70, 92), (0, 93), (120, 93), (160, 92), (240, 88), (TAIL, 80)],
    "z8":   [(NOSE, 36), (-70, 31), (0, 30), (120, 30), (TAIL, 36)],
    "x9":   [(NOSE, 70), (-225, 78), (-150, 82), (-70, 84), (0, 85), (120, 85), (160, 84), (240, 80), (TAIL, 72)],
    "z9":   [(NOSE, 31), (-70, 25), (0, 24), (120, 24), (TAIL, 30)],
    # floor
    "x10":  [(NOSE, 56), (-100, 66), (0, 70), (120, 70), (TAIL, 58)],
    "z10":  [(NOSE, 30), (-70, 24), (0, 22), (120, 22), (TAIL, 29)],
}


def half_ring(y):
    g = lambda k: interp(K[k], y)
    zc = g("zc")
    pts = [
        (0.0, zc),
        (g("x1"), zc + g("dz1")),
        (g("x3") * 0.55, (zc + g("dz1") + g("z3")) / 2 + 0.4),
        (g("x3"), g("z3")),
        (g("x4"), g("z4")),
        (g("x5"), g("z5")),
        (g("x6"), g("z6")),
        (g("x7"), g("z7")),
        (g("x8"), g("z8")),
        (g("x9"), g("z9")),
        (g("x10"), g("z10")),
        (0.0, g("z10")),
    ]
    return pts


def full_ring(y):
    h = half_ring(y)
    right = [(x, z) for x, z in h]                    # +X side, top -> bottom
    left = [(-x, z) for x, z in reversed(h[1:-1])]    # -X side, bottom -> top
    return right + left


STATIONS = [NOSE, -236, -228, -216, -200, -180, -160, -140, -120, -100, -84, -70, -62, -58, -52, -44,
            -36, -30, -24, -12, 4, 20, 36, 52, 68, 84, 100, 112, 118, 122, 128, 136, 144, 150, 156,
            160, 166, 176, 190, 205, 220, 240, 256, 268, 274, TAIL]


def build_loft():
    """Open body skin: lofted, Catmull-Clark subdivided, fender tips pushed forward/back."""
    bm = bmesh.new()
    rings = []
    for y in STATIONS:
        rings.append([bm.verts.new(V(x, y, z)) for x, z in full_ring(y)])
    n = len(rings[0])
    for ra, rb in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([ra[i], rb[i], rb[j], ra[j]])
    cap_f = bm.faces.new(list(rings[0]))
    cap_r = bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    crease = bm.edges.layers.float.new("crease_edge")
    for e in cap_f.edges:
        e[crease] = 0.8
    for e in cap_r.edges:
        e[crease] = 0.8
    for ra, rb in zip(rings, rings[1:]):
        for idx, w in ((5, 0.85), (n - 5, 0.85), (4, 0.3), (n - 4, 0.3), (9, 0.7), (n - 9, 0.7), (8, 0.3), (n - 8, 0.3)):
            e = bm.edges.get((ra[idx], rb[idx]))
            if e:
                e[crease] = w
    obj = new_obj("BODY", bm, [M["MI_V01_Paint_Body"], M["MI_V01_Interior_Trim"], M["MI_V01_Undercoat"]])
    sub = obj.modifiers.new("sub", "SUBSURF")
    sub.levels = 2
    sub.use_creases = True
    apply_mod(obj, sub)
    # fender tips: push the outer corners of the nose/tail forward of the centre (plan-view V)
    me = obj.data
    for v in me.vertices:
        x, y, z = v.co
        zw = min(1.0, max(0.0, (z - 0.30) / 0.15)); zw = zw * zw * (3 - 2 * zw)   # upper fender only
        if y < -2.10:
            w = min(1.0, (-2.10 - y) / 0.30); w = w * w * (3 - 2 * w)
            v.co.y -= 0.07 * w * zw * (abs(x) / 0.90) ** 2
        if y > 2.45:
            w = min(1.0, (y - 2.45) / 0.33); w = w * w * (3 - 2 * w)
            v.co.y += 0.04 * w * zw * (abs(x) / 0.88) ** 2
    return obj


# ----------------------------------------------------------------------------- bisect-based cutting

def _region_faces(bm, lo, hi):
    """Faces whose bounding box overlaps the box lo..hi (metres)."""
    out = []
    for f in bm.faces:
        xs = [v.co.x for v in f.verts]; ys = [v.co.y for v in f.verts]; zs = [v.co.z for v in f.verts]
        if max(xs) < lo[0] or min(xs) > hi[0] or max(ys) < lo[1] or min(ys) > hi[1] or max(zs) < lo[2] or min(zs) > hi[2]:
            continue
        out.append(f)
    return out


def bisect_cut(bm, planes, lo, hi, inside, delete=True):
    """Slice faces in region lo..hi with each (co, no) plane; then delete (or return) faces whose
    centre satisfies inside(p). Returns the inside faces when delete is False."""
    for co, no in planes:
        faces = _region_faces(bm, lo, hi)
        if not faces:
            continue
        verts = list({v for f in faces for v in f.verts})
        edges = list({e for f in faces for e in f.edges})
        bmesh.ops.bisect_plane(bm, geom=verts + edges + faces, plane_co=Vector(co), plane_no=Vector(no).normalized(),
                               dist=1e-6, use_snap_center=False, clear_outer=False, clear_inner=False)
    inner = [f for f in _region_faces(bm, lo, hi) if inside(f.calc_center_median())]
    if delete:
        bmesh.ops.delete(bm, geom=inner, context="FACES")
        return None
    return inner


def point_in_poly(u, v, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        (u0, v0), (u1, v1) = poly[i], poly[(i + 1) % n]
        if (v0 > v) != (v1 > v):
            x = u0 + (v - v0) * (u1 - u0) / (v1 - v0)
            if u < x:
                inside = not inside
    return inside


def prism_cut_x(bm, poly_cm, side, x0_cm, x1_cm, delete=True):
    """Cut a (y,z) polygon extruded along X on one side of the car."""
    poly = [(y / 100.0, z / 100.0) for y, z in poly_cm]
    planes = []
    for (y0, z0), (y1, z1) in zip(poly, poly[1:] + poly[:1]):
        planes.append(((0, y0, z0), (0, -(z1 - z0), (y1 - y0))))
    xs = sorted((side * x0_cm / 100.0, side * x1_cm / 100.0))
    lo = (xs[0], min(p[0] for p in poly) - 0.001, min(p[1] for p in poly) - 0.001)
    hi = (xs[1], max(p[0] for p in poly) + 0.001, max(p[1] for p in poly) + 0.001)
    def inside(p):
        return xs[0] <= p.x <= xs[1] and point_in_poly(p.y, p.z, poly)
    return bisect_cut(bm, planes, lo, hi, inside, delete)


def prism_cut_z(bm, poly_cm, z0_cm, z1_cm, delete=True):
    """Cut an (x,y) polygon extruded along Z (hood / trunk lids)."""
    poly = [(x / 100.0, y / 100.0) for x, y in poly_cm]
    planes = []
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        planes.append(((x0, y0, 0), (-(y1 - y0), (x1 - x0), 0)))
    zs = (z0_cm / 100.0, z1_cm / 100.0)
    lo = (min(p[0] for p in poly) - 0.001, min(p[1] for p in poly) - 0.001, zs[0])
    hi = (max(p[0] for p in poly) + 0.001, max(p[1] for p in poly) + 0.001, zs[1])
    def inside(p):
        return zs[0] <= p.z <= zs[1] and point_in_poly(p.x, p.y, poly)
    return bisect_cut(bm, planes, lo, hi, inside, delete)


def plane_poly_cut(bm, pts3, normal, slab=0.2, delete=True):
    """Cut a planar 3D polygon (metres) through the skin: planes contain each edge and the normal."""
    n = Vector(normal).normalized()
    c = sum((Vector(p) for p in pts3), Vector()) / len(pts3)
    planes = []
    for p0, p1 in zip(pts3, pts3[1:] + pts3[:1]):
        pn = (Vector(p1) - Vector(p0)).cross(n).normalized()
        if pn.dot(c - Vector(p0)) > 0:
            pn = -pn  # make it point outward
        planes.append((p0, pn))
    lo = Vector((min(p.x for p in pts3), min(p.y for p in pts3), min(p.z for p in pts3))) - Vector((slab,) * 3)
    hi = Vector((max(p.x for p in pts3), max(p.y for p in pts3), max(p.z for p in pts3))) + Vector((slab,) * 3)
    def inside(p):
        if abs(n.dot(p - c)) > slab:
            return False
        return all(pn.dot(p - Vector(p0)) < 0 for p0, pn in planes)
    return bisect_cut(bm, planes, lo, hi, inside, delete)


def circle_cut(bm, center_cm, axis, r_cm, span_cm, segs=20, delete=True):
    """Cut a regular polygon (approximating a circle of radius r) around `axis` through the skin
    within span_cm = (a0, a1) along the axis."""
    c = V(*center_cm); r = r_cm / 100.0
    a0, a1 = sorted(v / 100.0 for v in span_cm)
    planes = []
    rc = r * math.cos(math.pi / segs)
    normals = []
    for i in range(segs):
        a = 2 * math.pi * (i + 0.5) / segs
        if axis == "x":
            nn = Vector((0, math.cos(a), math.sin(a)))
        else:
            nn = Vector((math.cos(a), 0, math.sin(a)))
        normals.append(nn)
        planes.append((c + nn * rc, nn))
    if axis == "x":
        lo = (a0, c.y - r, c.z - r); hi = (a1, c.y + r, c.z + r)
        def inside(p):
            return a0 <= p.x <= a1 and all(nn.dot(p - c) < rc for nn in normals)
    else:
        lo = (c.x - r, a0, c.z - r); hi = (c.x + r, a1, c.z + r)
        def inside(p):
            return a0 <= p.y <= a1 and all(nn.dot(p - c) < rc for nn in normals)
    return bisect_cut(bm, planes, lo, hi, inside, delete)


def extract_faces(bm, faces, name, mats):
    """Copy `faces` into a new object and delete them from bm."""
    nb = bmesh.new()
    vmap = {}
    for f in faces:
        vs = []
        for v in f.verts:
            if v not in vmap:
                vmap[v] = nb.verts.new(v.co)
            vs.append(vmap[v])
        nf = nb.faces.new(vs)
        nf.material_index = f.material_index
    bmesh.ops.delete(bm, geom=faces, context="FACES")
    return new_obj(name, nb, mats)


def shrink_boundary(obj, amount=0.0035):
    """Pull every boundary vertex inward along the surface by `amount` (panel gaps)."""
    bm = bmesh.new(); bm.from_mesh(obj.data)
    moves = {}
    for e in bm.edges:
        if e.is_boundary and e.link_faces:
            f = e.link_faces[0]
            mid = (e.verts[0].co + e.verts[1].co) / 2
            d = e.verts[1].co - e.verts[0].co
            inward = f.calc_center_median() - mid
            inward = inward - d * (inward.dot(d) / max(d.length_squared, 1e-12))
            if inward.length < 1e-9:
                continue
            inward.normalize()
            for v in e.verts:
                moves.setdefault(v, []).append(inward)
    for v, ds in moves.items():
        d = sum(ds, Vector()) / len(ds)
        if d.length > 1e-9:
            v.co += d.normalized() * amount
    bm.to_mesh(obj.data); bm.free()


def tidy(obj, dist=0.00008):
    """Merge near-duplicate verts and dissolve sliver faces left by the plane bisects."""
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges)
    # drop any face thinner than ~0.05 mm across (sliver), which would spike the solidify normals
    slivers = []
    for f in bm.faces:
        if f.calc_area() < 2.5e-9:
            slivers.append(f)
    if slivers:
        bmesh.ops.delete(bm, geom=slivers, context="FACES")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data); bm.free()


def solidify(obj, inner_mat=1, rim_mat=0):
    tidy(obj)
    sol = obj.modifiers.new("sol", "SOLIDIFY")
    sol.thickness = -SHELL_T / 100.0
    sol.offset = -1.0
    sol.use_even_offset = False
    sol.use_quality_normals = True
    sol.use_rim = True
    sol.material_offset = inner_mat
    sol.material_offset_rim = rim_mat
    apply_mod(obj, sol)


def bevel(obj, width=0.004, segs=2, angle=50):
    """Fine edge bevel (angle-limited, overlap-clamped) so hard edges catch light."""
    b = obj.modifiers.new("bev", "BEVEL")
    b.width = width
    b.segments = segs
    b.limit_method = "ANGLE"
    b.angle_limit = math.radians(angle)
    b.use_clamp_overlap = True
    b.miter_outer = "MITER_ARC"
    apply_mod(obj, b)


# ----------------------------------------------------------------------------- apertures
WIN_FRONT = [(-43, 97.5), (-15, 131.0), (45, 131.0), (45, 97.5)]
WIN_REAR = [(58, 97.5), (58, 131.0), (112, 131.0), (120, 97.5)]
def band_x(z):
    """Glass band plane: drip rail (x=72, z=135) to belt (x=92, z=97)."""
    return 72.0 + (135.0 - z) * (20.0 / 38.0)


def side_window_pts(poly, side, inset=0.0):
    cy = sum(p[0] for p in poly) / len(poly)
    cz = sum(p[1] for p in poly) / len(poly)
    out = []
    for y, z in poly:
        dy, dz = y - cy, z - cz
        l = math.hypot(dy, dz)
        y2, z2 = y - dy / l * inset, z - dz / l * inset
        out.append(V(side * band_x(z2), y2, z2))
    return out


def band_normal(side):
    return Vector((side * 38.0, 0, 20.0)).normalized()


WS_TOP, WS_BASE = (-24.0, 135.5), (-57.0, 95.0)
RW_TOP, RW_BASE = (122.0, 135.5), (158.0, 97.0)


def glass_plane_pts(top, base, half_top, half_base, inset=0.0):
    (yt, zt), (yb, zb) = top, base
    d = Vector((0, yt - yb, zt - zb))
    n = d.cross(Vector((1, 0, 0))).normalized()
    ht, hb = half_top - inset, half_base - inset
    k = inset / d.length
    yt2, zt2 = yt - (yt - yb) * k, zt - (zt - zb) * k
    yb2, zb2 = yb + (yt - yb) * k, zb + (zt - zb) * k
    pts = [V(-hb, yb2, zb2), V(hb, yb2, zb2), V(ht, yt2, zt2), V(-ht, yt2, zt2)]
    return pts, n


# panel outlines (y, z) cm
DOOR_F = [(-47, 27), (-47, 97.5), (-21.5, 134.5), (49, 134.5), (49, 27)]
DOOR_R = [(52, 27), (52, 134.5), (115, 134.5), (124.5, 97.5), (124.5, 76), (113, 63), (106.5, 49), (105, 27)]
HOOD_Y0, HOOD_Y1, HOOD_X = -236.0, -62.0, 72.0
TRUNK_Y0, TRUNK_Y1, TRUNK_X = 162.0, 272.0, 78.0
GRILLE = (58.0, 60.0, 79.0)   # half-width, z0, z1
LAMP_X, LAMP_Z = (57.0, 74.0), 70.0
TAIL_X, TAIL_Z = 72.0, 72.0


def cut_and_split(body):
    """All apertures + panel separation on the open skin. Returns (panels dict)."""
    bm = bmesh.new(); bm.from_mesh(body.data)
    # windows
    for side in (1, -1):
        for poly in (WIN_FRONT, WIN_REAR):
            prism_cut_x(bm, poly, side, 58, 125)
    for top, base, ht, hb in ((WS_TOP, WS_BASE, 66, 86), (RW_TOP, RW_BASE, 60, 80)):
        pts, n = glass_plane_pts(top, base, ht, hb)
        plane_poly_cut(bm, pts, n, slab=0.12)
    # wheel wells
    for y in (AXLE_F, AXLE_R):
        for side in (1, -1):
            circle_cut(bm, (0, y, TYRE_OD / 2 + 1.5), "x", 41.0, (side * 58, side * 125), segs=28)
    # grille opening + lamp openings on the nose, tail lamps on the tail
    gh, gz0, gz1 = GRILLE
    planes = [((-gh / 100, 0, 0), (-1, 0, 0)), ((gh / 100, 0, 0), (1, 0, 0)), ((0, 0, gz0 / 100), (0, 0, -1)), ((0, 0, gz1 / 100), (0, 0, 1))]
    bisect_cut(bm, planes, (-gh / 100 - 0.001, NOSE / 100 - 0.12, gz0 / 100 - 0.001), (gh / 100 + 0.001, NOSE / 100 + 0.08, gz1 / 100 + 0.001),
               lambda p: abs(p.x) < gh / 100 and gz0 / 100 < p.z < gz1 / 100 and p.y < NOSE / 100 + 0.08)
    for x in LAMP_X:
        for sgn in (1, -1):
            circle_cut(bm, (sgn * x, NOSE, LAMP_Z), "y", 8.3, (NOSE - 12, NOSE + 8), segs=20)
    for sgn in (1, -1):
        circle_cut(bm, (sgn * TAIL_X, TAIL, TAIL_Z), "y", 8.3, (TAIL - 8, TAIL + 10), segs=20)
    # panels
    mats = [M["MI_V01_Paint_Body"], M["MI_V01_Interior_Trim"], M["MI_V01_Undercoat"]]
    panels = {}
    for side, tag in ((1, "L"), (-1, "R")):
        f = prism_cut_x(bm, DOOR_F, side, 58, 125, delete=False)
        panels[f"DOOR_F{tag}"] = extract_faces(bm, f, f"DOOR_F{tag}", mats)
        f = prism_cut_x(bm, DOOR_R, side, 58, 125, delete=False)
        panels[f"DOOR_R{tag}"] = extract_faces(bm, f, f"DOOR_R{tag}", mats)
    hood = [(-HOOD_X, HOOD_Y0), (HOOD_X, HOOD_Y0), (HOOD_X, HOOD_Y1), (-HOOD_X, HOOD_Y1)]
    f = prism_cut_z(bm, hood, 78, 110, delete=False)
    panels["HOOD"] = extract_faces(bm, f, "HOOD", mats)
    trunk = [(-TRUNK_X, TRUNK_Y0), (TRUNK_X, TRUNK_Y0), (TRUNK_X, TRUNK_Y1), (-TRUNK_X, TRUNK_Y1)]
    f = prism_cut_z(bm, trunk, 82, 110, delete=False)
    panels["TRUNK"] = extract_faces(bm, f, "TRUNK", mats)
    bm.to_mesh(body.data); bm.free()
    # gaps + thickness
    for name, p in panels.items():
        shrink_boundary(p, 0.0035)
        solidify(p, inner_mat=1 if name.startswith("DOOR") else 2, rim_mat=0)
    solidify(body, inner_mat=1, rim_mat=0)
    # v002: rolled panel edges / flanged aperture rims (3.5 mm, 2 segments)
    for p in list(panels.values()) + [body]:
        bevel(p, width=0.0035, segs=2, angle=55)
    # v002: the floor pan / underside reads as dark undercoat, not body colour
    me = body.data
    for poly in me.polygons:
        c = poly.center
        if c.z < 0.40 and poly.normal.z < -0.55:
            poly.material_index = 2
    pivots = {"DOOR_FL": (97, -46, 62), "DOOR_FR": (-97, -46, 62), "DOOR_RL": (99, 53, 62), "DOOR_RR": (-99, 53, 62),
              "HOOD": (0, HOOD_Y1, 91), "TRUNK": (0, TRUNK_Y0, 96)}
    for name, p in panels.items():
        set_origin(p, V(*pivots[name]))
    return panels


def wheel_houses():
    """Inner wheel-house shells (closed solids) so the wells read as real cavities."""
    bm = bmesh.new()
    for y in (AXLE_F, AXLE_R):
        for side in (1, -1):
            r0, r1 = 42.0, 44.5
            segs = 24
            cz = TYRE_OD / 2 + 1.5
            xin, xout = (62, 102) if side > 0 else (-102, -62)
            rings = []
            for x in (xin, xout):
                for r in (r0, r1):
                    ring = []
                    for i in range(segs + 1):
                        a = math.pi * i / segs
                        ring.append(bm.verts.new(V(x, y + r * math.cos(a), cz + r * math.sin(a))))
                    rings.append(ring)
            ri_in, ro_in, ri_out, ro_out = rings
            for i in range(segs):
                j = i + 1
                bm.faces.new([ri_in[i], ri_in[j], ri_out[j], ri_out[i]])
                bm.faces.new([ro_out[i], ro_out[j], ro_in[j], ro_in[i]])
                bm.faces.new([ri_in[j], ri_in[i], ro_in[i], ro_in[j]])
                bm.faces.new([ri_out[i], ri_out[j], ro_out[j], ro_out[i]])
            for a in (0, segs):
                bm.faces.new([ri_in[a], ro_in[a], ro_out[a], ri_out[a]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.material_index = 0
    return new_obj("WHEELHOUSES", bm, [M["MI_V01_Undercoat"]])


# ----------------------------------------------------------------------------- glazing + mouldings

def glazing(panels):
    objs = {}
    for side, tag in ((1, "L"), (-1, "R")):
        n = band_normal(side)
        for poly, pname, gname in ((WIN_FRONT, f"DOOR_F{tag}", f"GLASS_DOOR_F{tag}"),
                                   (WIN_REAR, f"DOOR_R{tag}", f"GLASS_DOOR_R{tag}")):
            bm = bmesh.new()
            pts = side_window_pts(poly, side, inset=0.6)
            bm_plate(bm, pts, n, -0.003, 0.003, mat=0)
            g = new_obj(gname, bm, [M["MI_V01_Glass"]])
            # chrome moulding ring around the aperture
            bm = bmesh.new()
            outer = side_window_pts(poly, side, inset=-1.8)
            inner = side_window_pts(poly, side, inset=0.9)
            bm_ring_plate(bm, outer, inner, n, -0.004, 0.006, mat=0)
            r = new_obj(gname.replace("GLASS", "TRIM_WINDOW"), bm, [M["MI_V01_Chrome"]])
            for o in (g, r):
                o.parent = panels[pname]
                o.matrix_parent_inverse = Matrix.Translation(-panels[pname].location)
            objs[gname] = g
    for top, base, ht, hb, name in ((WS_TOP, WS_BASE, 66, 86, "GLASS_WINDSHIELD"), (RW_TOP, RW_BASE, 60, 80, "GLASS_REAR")):
        pts, n = glass_plane_pts(top, base, ht, hb, inset=0.6)
        bm = bmesh.new(); bm_plate(bm, pts, n, -0.003, 0.003, mat=0)
        objs[name] = new_obj(name, bm, [M["MI_V01_Glass"]])
        outer, _ = glass_plane_pts(top, base, ht, hb, inset=-1.8)
        inner, _ = glass_plane_pts(top, base, ht, hb, inset=0.9)
        bm = bmesh.new(); bm_ring_plate(bm, outer, inner, n, -0.004, 0.006, mat=0)
        new_obj(name.replace("GLASS", "TRIM_WINDOW"), bm, [M["MI_V01_Chrome"]])
    return objs


# ----------------------------------------------------------------------------- exterior details

def bumpers():
    prof = rounded_rect(8.0, 11.0, 3.0, n=3)
    out = []
    for y_face, name, sgn in ((NOSE - 7, "BUMPER_FRONT", -1), (TAIL + 7, "BUMPER_REAR", 1)):
        path = []
        # straight centre section then wrap back along the fenders
        for x in (-104, -96, -88, -70, -40, 0, 40, 70, 88, 96, 104):
            wrap = max(0.0, abs(x) - 88) / 16.0
            path.append((x, y_face - sgn * wrap * wrap * 22.0, 44.0))
        # sweep profile: s lateral along the path normal is wrong for X paths -> build with t up
        bm = bmesh.new()
        pts = [Vector(p) for p in path]
        rings = []
        for i, p in enumerate(pts):
            d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            up = Vector((0, 0, 1)); side = up.cross(d).normalized()
            rings.append([bm.verts.new(V(*(p + side * s + up * t))) for s, t in prof])
        k = len(prof)
        for ra, rb in zip(rings, rings[1:]):
            for i in range(k):
                j = (i + 1) % k
                bm.faces.new([ra[i], ra[j], rb[j], rb[i]])
        bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces: f.material_index = 0
        b = new_obj(name, bm, [M["MI_V01_Chrome"]])
        # bumper guards
        bm = bmesh.new()
        for x in (-34, 34):
            y0, y1 = (y_face - 7, y_face + 1) if sgn < 0 else (y_face - 1, y_face + 7)
            bm_box(bm, x - 3, y0, 38, x + 3, y1, 56)
        new_obj(name + "_GUARDS", bm, [M["MI_V01_Chrome"]])
        out.append(b)
    return out


def front_end():
    gh, gz0, gz1 = GRILLE
    # recessed dark grille box behind the opening, with a chrome surround and horizontal bars
    bm = bmesh.new()
    bm_box(bm, -gh - 1, NOSE + 1.0, gz0 - 1, gh + 1, NOSE + 7.0, gz1 + 1)
    grille = new_obj("GRILLE_BACK", bm, [M["MI_V01_Grille_Dark"]])
    bm = bmesh.new()
    for z in (gz0 + 3.0, gz0 + 6.8, gz0 + 10.6, gz0 + 14.4, gz0 + 18.2):
        bm_box(bm, -gh, NOSE - 1.5, z - 0.6, gh, NOSE + 1.0, z + 0.6)
    for x in (-19, 19):
        bm_box(bm, x - 0.7, NOSE - 1.5, gz0, x + 0.7, NOSE + 1.0, gz1)
    # surround (frame) proud of the skin
    bm_box(bm, -gh - 2.0, NOSE - 2.5, gz0 - 2.0, gh + 2.0, NOSE + 0.5, gz0)
    bm_box(bm, -gh - 2.0, NOSE - 2.5, gz1, gh + 2.0, NOSE + 0.5, gz1 + 2.0)
    bm_box(bm, -gh - 2.0, NOSE - 2.5, gz0, -gh, NOSE + 0.5, gz1)
    bm_box(bm, gh, NOSE - 2.5, gz0, gh + 2.0, NOSE + 0.5, gz1)
    bars = new_obj("GRILLE_BARS", bm, [M["MI_V01_Chrome"]])
    # headlamps: bezel ring + sealed-beam lens, set into the lamp openings
    bm = bmesh.new(); bm2 = bmesh.new()
    for x in LAMP_X:
        for sgn in (1, -1):
            cx = sgn * x
            yf = NOSE - 7.0 * (x / 90.0) ** 2   # follow the fender-tip projection
            bm_revolve(bm, [(9.6, -2.0), (9.6, 1.0), (7.4, 1.0), (7.4, -2.0)], "y", (cx, yf, LAMP_Z), segs=28)
            bm_revolve(bm2, [(0.0, -1.2), (5.0, -1.6), (7.4, -0.4), (7.4, 3.0), (0.0, 3.0)], "y", (cx, yf, LAMP_Z), segs=28, close=False)
    bezels = new_obj("HEADLAMP_BEZELS", bm, [M["MI_V01_Chrome"]])
    lenses = new_obj("HEADLAMP_LENSES", bm2, [M["MI_V01_Headlamp"]])
    # hood lip trim (generic, no brand)
    bm = bmesh.new(); bm_box(bm, -10, NOSE - 1.0, 84.5, 10, NOSE + 3, 86.5)
    new_obj("TRIM_HOOD_FRONT", bm, [M["MI_V01_Chrome"]])
    return [grille, bars, bezels, lenses]


def rear_end():
    bm = bmesh.new(); bm2 = bmesh.new(); bm3 = bmesh.new()
    for sgn in (1, -1):
        cx = sgn * TAIL_X
        yr = TAIL + 4.0 * (TAIL_X / 88.0) ** 2
        bm_revolve(bm, [(9.6, 2.0), (9.6, -1.0), (7.4, -1.0), (7.4, 2.0)], "y", (cx, yr, TAIL_Z), segs=28)
        bm_revolve(bm2, [(0.0, 1.5), (5.0, 2.0), (7.4, 0.8), (7.4, -3.0), (0.0, -3.0)], "y", (cx, yr, TAIL_Z), segs=28, close=False)
        bm_cylinder(bm3, (cx, yr, TAIL_Z - 12.5), "y", 4.0, -0.5, 1.2, segs=20)
    new_obj("TAILLAMP_BEZELS", bm, [M["MI_V01_Chrome"]])
    new_obj("TAILLAMP_LENSES", bm2, [M["MI_V01_Lens_Red"]])
    new_obj("BACKUP_LENSES", bm3, [M["MI_V01_Lens_Clear"]])
    bm = bmesh.new(); bm_box(bm, -58, TAIL - 0.5, 83, 58, TAIL + 1.2, 85)
    new_obj("TRIM_REAR_PANEL", bm, [M["MI_V01_Chrome"]])


def side_details(panels):
    out = []
    # door handles (push-button type) and lower-body chrome strips
    bm = bmesh.new()
    for side in (1, -1):
        for y in (20, 88):
            x = side * (band_x(88) + 7.5)
            bm_box(bm, x - 1.2, y - 7, 84, x + 1.2, y + 7, 86.5)
            bm_cylinder(bm, (x, y + 9, 85.2), "x", 1.1, -1.2, 1.8, segs=12)
    out.append(new_obj("DOOR_HANDLES", bm, [M["MI_V01_Chrome"]]))
    # rocker / lower body strip, following the body with a shrinkwrap
    # shrink-wrap target = body skin + door skins (doors are separate objects), merged with bmesh
    tbm = bmesh.new()
    tbm.from_mesh(bpy.data.objects["BODY"].data)
    for n_, p_ in panels.items():
        if n_.startswith("DOOR"):
            n0 = len(tbm.verts)
            tbm.from_mesh(p_.data)
            tbm.verts.ensure_lookup_table()
            bmesh.ops.transform(tbm, matrix=Matrix.Translation(p_.location), verts=tbm.verts[n0:])   # matrix_world is stale before a depsgraph update
    body = new_obj("tmp_target", tbm, [M["MI_V01_Paint_Body"]])
    for side, tag in ((1, "L"), (-1, "R")):
        bm = bmesh.new()
        n = 40
        y0, y1 = -104, 104                               # rocker moulding between the wheel arches
        vs = [[bm.verts.new(V(side * 110, y0 + (y1 - y0) * i / n, z)) for i in range(n + 1)] for z in (35.5, 39.5)]
        for i in range(n):
            bm.faces.new([vs[0][i], vs[0][i + 1], vs[1][i + 1], vs[1][i]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        strip = new_obj(f"TRIM_ROCKER_{tag}", bm, [M["MI_V01_Chrome"]])
        sw = strip.modifiers.new("sw", "SHRINKWRAP")
        sw.wrap_method = "PROJECT"; sw.use_project_x = True
        sw.use_negative_direction = side > 0; sw.use_positive_direction = side < 0
        sw.target = body; sw.offset = 0.004
        apply_mod(strip, sw)
        sol = strip.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.006; sol.offset = 1.0
        apply_mod(strip, sol)
        # keep the strip's outward face pointing +/-X
        bmq = bmesh.new(); bmq.from_mesh(strip.data); bmq.normal_update()
        if sum(f.normal.x * side for f in bmq.faces) < 0:
            for f in bmq.faces: f.normal_flip()
        bmq.to_mesh(strip.data); bmq.free()
        out.append(strip)
    bpy.data.objects.remove(body, do_unlink=True)
    # driver-side round mirror
    bm = bmesh.new()
    bm_cylinder(bm, (band_x(100) + 4, -25, 100), "x", 0.8, 0, 9, segs=10)
    bm_revolve(bm, [(0.5, 0.0), (5.5, 0.0), (5.5, 1.6), (0.5, 1.6)], "y", (band_x(100) + 14, -25, 100), segs=24)
    out.append(new_obj("MIRROR_DRIVER", bm, [M["MI_V01_Chrome"]]))
    # wipers
    bm = bmesh.new()
    for x, a in ((-40, 20), (18, 20)):
        bm_box(bm, x, -62, 93.5, x + 42, -60.8, 94.3)
    out.append(new_obj("WIPERS", bm, [M["MI_V01_Steel_Painted"]]))
    return out


# ----------------------------------------------------------------------------- wheels

def wheel(name, side, pivot):
    bm = bmesh.new()
    R, w = TYRE_OD / 2, TYRE_W / 2
    rr = RIM_D / 2
    # tyre: tread -> shoulder -> sidewall -> bead, both sides, closed torus
    tread = [(R, -w + 2)]
    for o in (-5.2, 0.0, 5.2):                      # three circumferential tread grooves
        tread += [(R, o - 0.55), (R - 0.7, o - 0.3), (R - 0.7, o + 0.3), (R, o + 0.55)]
    tread.append((R, w - 2))
    prof = tread + [(R - 1.5, w), (rr + 6, w - 0.8), (rr + 1, w - 3), (rr, w - 3),
                    (rr, -w + 3), (rr + 1, -w + 3), (rr + 6, -w + 0.8), (R - 1.5, -w)]
    bm_revolve(bm, prof, "x", (0, 0, 0), segs=64, mat=0)
    tyre_faces = list(bm.faces)
    # whitewall band on the outboard sidewall
    ww = bmesh.new()
    s = 1 if side > 0 else -1
    ww_prof = [(rr + 2.5, s * (w - 2.4)), (rr + 9.5, s * (w - 1.2)), (rr + 9.5, s * (w - 0.9)), (rr + 2.5, s * (w - 2.1))]
    bm_revolve(ww, ww_prof, "x", (0, 0, 0), segs=48, mat=1)
    ww.to_mesh(bpy.data.meshes.new("tmp"));
    tmp = bpy.data.meshes.new("tmp2"); ww.to_mesh(tmp); ww.free()
    bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    for f in bm.faces:
        if f not in tyre_faces:
            f.material_index = 1
    # steel wheel: rim barrel + dish, outboard dog-dish hubcap
    rim = [(rr, -w + 3.5), (rr, w - 3.5), (rr - 1.2, w - 3.5), (rr - 1.2, s * 2.0), (6.0, s * 4.0), (6.0, -s * 1.0), (rr - 1.2, -s * 2.5), (rr - 1.2, -w + 3.5)]
    rb = bmesh.new(); bm_revolve(rb, rim, "x", (0, 0, 0), segs=36, mat=2)
    tmp = bpy.data.meshes.new("tmp3"); rb.to_mesh(tmp); rb.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    cap = [(0.0, s * 7.0), (6.0, s * 6.6), (10.5, s * 5.0), (13.0, s * 4.0), (13.0, s * 3.0), (0.0, s * 3.0)]
    cb = bmesh.new(); bm_revolve(cb, cap, "x", (0, 0, 0), segs=36, mat=3, close=False)
    tmp = bpy.data.meshes.new("tmp4"); cb.to_mesh(tmp); cb.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    # fix material indices by mesh order: faces appended keep their index from each sub-bmesh
    # contact patch: the loaded tyre flattens against the ground (hub sits TYRE_SAG below R)
    for v in bm.verts:
        zl = v.co.z * 100.0
        if zl < -(R - TYRE_SAG):
            depth = (-(R - TYRE_SAG) - zl) / TYRE_SAG
            v.co.z = -(R - TYRE_SAG) / 100.0
            v.co.y *= 1.0 + 0.012 * depth           # sidewall bulge at the patch
    obj = new_obj(name, bm, [M["MI_V01_Rubber_Tyre"], M["MI_V01_Whitewall"], M["MI_V01_Steel_Painted"], M["MI_V01_Chrome"]])
    obj.location = V(*pivot)
    return obj


def wheels():
    out = {}
    for y, tread in ((AXLE_F, TREAD_F), (AXLE_R, TREAD_R)):
        for side, tag in ((1, "L"), (-1, "R")):
            name = f"WHEEL_{'F' if y < 0 else 'R'}{tag}"
            out[name] = wheel(name, side, (side * tread / 2, y, TYRE_OD / 2 - TYRE_SAG))
    return out


# ----------------------------------------------------------------------------- interior

def interior():
    objs = []
    bm = bmesh.new()
    # floor pan + transmission tunnel + rear parcel shelf + firewall + trunk floor
    bm_box(bm, -92, -60, 22, 92, 160, 26)
    bm_box(bm, -12, -60, 22, 12, 60, 34)
    bm_box(bm, -80, 130, 22, 80, 162, 60)       # rear seat riser / rear floor
    bm_box(bm, -88, 140, 92, 88, 160, 95)       # parcel shelf
    bm_box(bm, -90, -62, 22, 90, -58, 92)       # firewall
    floor = new_obj("INT_FLOOR", bm, [M["MI_V01_Interior_Dark"]])
    objs.append(floor)
    # dash: padded top + instrument hood + lower panel
    bm = bmesh.new()
    bm_box(bm, -88, -58, 80, 88, -40, 93)
    bm_box(bm, -86, -40, 68, 86, -36, 82)
    bm_box(bm, 24, -42, 93, 58, -32, 99)         # instrument hood (driver side +X)
    bm_box(bm, -30, -40, 86, 10, -34, 92)        # radio / glove area
    dash = new_obj("INT_DASH", bm, [M["MI_V01_Interior_Dark"]])
    objs.append(dash)
    # police radio set under the dash + microphone hook
    bm = bmesh.new()
    bm_box(bm, -16, -40, 62, 16, -24, 70)
    bm_box(bm, 18, -36, 70, 24, -30, 78)
    objs.append(new_obj("POLICE_RADIO", bm, [M["MI_V01_Interior_Dark"]]))
    # steering column + 17 in wheel (driver side +X, LHD): column from the dash up toward the driver
    cx = 41.0
    p0, p1 = Vector((cx, -40.0, 80.0)), Vector((cx, -12.0, 92.0))
    bm = bmesh.new()
    d = (p1 - p0).normalized()
    up = Vector((0, 0, 1)); side = d.cross(up).normalized(); up2 = side.cross(d).normalized()
    rings = []
    for q in (p0, p1):
        rings.append([bm.verts.new(V(*(q + side * 2.2 * math.cos(a) + up2 * 2.2 * math.sin(a)))) for a in [2 * math.pi * i / 14 for i in range(14)]])
    for i in range(14):
        j = (i + 1) % 14
        bm.faces.new([rings[0][i], rings[0][j], rings[1][j], rings[1][i]])
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    objs.append(new_obj("INT_COLUMN", bm, [M["MI_V01_Interior_Dark"]]))
    bm = bmesh.new()
    rw = 21.5
    # rim: torus in the plane normal to d, centred at p1
    for prof in ([(rw - 1.6, -1.6), (rw + 1.6, -1.6), (rw + 1.6, 1.6), (rw - 1.6, 1.6)],):
        rings = []
        for r, h in prof:
            rings.append([bm.verts.new(V(*(p1 + d * h + side * r * math.cos(a) + up2 * r * math.sin(a)))) for a in [2 * math.pi * i / 36 for i in range(36)]])
        for ra, rb in zip(rings, rings[1:] + rings[:1]):
            for i in range(36):
                j = (i + 1) % 36
                bm.faces.new([ra[i], ra[j], rb[j], rb[i]])
    # three spokes + hub
    for ang in (90, 210, 330):
        a = math.radians(ang)
        rad = side * math.cos(a) + up2 * math.sin(a)
        tng = d.cross(rad).normalized()
        c0, c1 = p1 + rad * 2.5, p1 + rad * (rw - 1.0)
        corners = []
        for q in (c0, c1):
            corners.append([bm.verts.new(V(*(q + tng * sx * 1.2 + d * sz * 0.9))) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
        bm.faces.new(list(reversed(corners[0]))); bm.faces.new(corners[1])
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new([corners[0][i], corners[0][j], corners[1][j], corners[1][i]])
    hub = [bm.verts.new(V(*(p1 + d * h + side * 3.5 * math.cos(a) + up2 * 3.5 * math.sin(a)))) for h in (-1.0, 2.0) for a in [2 * math.pi * i / 16 for i in range(16)]]
    bm.faces.new(list(reversed(hub[:16]))); bm.faces.new(hub[16:])
    for i in range(16):
        j = (i + 1) % 16
        bm.faces.new([hub[i], hub[j], hub[16 + j], hub[16 + i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    objs.append(new_obj("INT_STEERING_WHEEL", bm, [M["MI_V01_Interior_Dark"]]))
    # bench seats (cushion + backrest, soft rounded)
    for y0, name in ((-2, "INT_SEAT_FRONT"), (94, "INT_SEAT_REAR")):
        bm = bmesh.new()
        bm_box(bm, -78, y0, 32, 78, y0 + 52, 46)              # cushion
        bm_box(bm, -78, y0 + 44, 46, 78, y0 + 58, 96)         # backrest
        bm_box(bm, -78, y0 + 40, 30, 78, y0 + 58, 46)
        s = new_obj(name, bm, [M["MI_V01_Interior_Vinyl"]])
        bev = s.modifiers.new("bev", "BEVEL"); bev.width = 0.05; bev.segments = 4; bev.limit_method = "NONE"
        apply_mod(s, bev)
        objs.append(s)
    # engine-bay placeholder (APPROXIMATE dressing so an open hood is not an empty shell)
    bm = bmesh.new()
    bm_box(bm, -34, -200, 36, 34, -120, 72)             # block
    bm_box(bm, -40, -150, 72, 40, -118, 80)             # valve covers / intake
    bm_revolve(bm, [(0.0, 80.0), (17.0, 80.0), (17.0, 88.0), (0.0, 88.0)], "z", (0, -140, 0), segs=28, close=False)  # air cleaner
    bm_box(bm, -44, -232, 40, 44, -226, 78)             # radiator core
    bm_box(bm, -70, -225, 32, 70, -200, 36)             # front cross-member
    bm_box(bm, -78, -236, 26, 78, -60, 30)              # engine-bay floor / splash pan
    objs.append(new_obj("INT_ENGINE_BAY", bm, [M["MI_V01_Interior_Dark"]]))
    bm = bmesh.new()
    bm_box(bm, -60, -234, 26, 60, -228, 79)             # radiator support (stays below the hood lip, z 84)
    bm_box(bm, -74, -228, 26, -70, -64, 80)             # inner fender walls
    bm_box(bm, 70, -228, 26, 74, -64, 80)
    objs.append(new_obj("INT_ENGINE_BAY_WALLS", bm, [M["MI_V01_Undercoat"]]))
    # sun visors + mirror
    bm = bmesh.new()
    for x0 in (-66, 14):
        bm_box(bm, x0, -34, 128, x0 + 52, -20, 129.5)
    bm_box(bm, -11, -30, 118, 11, -29, 124)
    objs.append(new_obj("INT_VISORS", bm, [M["MI_V01_Interior_Trim"]]))
    # driver placeholder socket marker is an empty (added in sockets())
    return objs


# ----------------------------------------------------------------------------- underbody (v002)

def underbody():
    """Exhaust, muffler, driveshaft, rear axle + differential, leaf springs, fuel tank — so the car
    reads grounded from kerb level and under the open hood/trunk. APPROXIMATE layout."""
    objs = []
    bm = bmesh.new()
    px = -30.0                                           # exhaust runs on the passenger side
    bm_cylinder(bm, (px, 0, 17.5), "y", 2.2, -118, 58, segs=14)      # head pipe
    bm_revolve(bm, [(0.0, 60.0), (5.0, 61.0), (8.5, 66.0), (8.5, 124.0), (5.0, 129.0), (0.0, 130.0)], "y", (px, 0, 17.0), segs=20, close=False)  # muffler
    bm_cylinder(bm, (px, 0, 17.5), "y", 2.2, 130, 262, segs=14)      # tailpipe
    bm_cylinder(bm, (px, 262, 17.5), "y", 2.4, 0, 14, segs=14)       # tailpipe tip
    bm_cylinder(bm, (0, 0, 28.0), "y", 3.5, -62, 138, segs=14)       # driveshaft
    objs.append(new_obj("UNDER_EXHAUST_DRIVELINE", bm, [M["MI_V01_Steel_Painted"]]))
    bm = bmesh.new()
    bm_cylinder(bm, (0, AXLE_R, TYRE_OD / 2 - TYRE_SAG), "x", 4.2, -70, 70, segs=16)   # axle tubes
    bm_revolve(bm, [(0.0, -14.0), (13.0, -12.0), (14.5, 0.0), (13.0, 12.0), (0.0, 14.0)], "y", (0, AXLE_R, TYRE_OD / 2 - TYRE_SAG), segs=20, close=False)  # differential
    for sx in (-56, 56):
        bm_box(bm, sx - 3, AXLE_R - 58, 27, sx + 3, AXLE_R + 58, 30.5)   # leaf springs
        bm_box(bm, sx - 3.5, AXLE_R - 6, 26, sx + 3.5, AXLE_R + 6, 40)   # spring seats / U-bolts
    bm_box(bm, -44, 196, 12, 44, 252, 22)                                 # fuel tank (behind the axle)
    bm_box(bm, -90, NOSE - 8, 21, 90, NOSE + 16, 38)                      # front valance / gravel pan
    bm_box(bm, -86, TAIL - 16, 21, 86, TAIL + 8, 38)                      # rear valance
    bm_box(bm, -66, AXLE_F - 8, 28, 66, AXLE_F + 8, 36)                   # front cross-member
    for sx in (-60, 60):
        bm_box(bm, sx - 10, AXLE_F - 20, 24, sx + 10, AXLE_F + 20, 32)    # lower control arms (block-in)
    objs.append(new_obj("UNDER_AXLES_TANK", bm, [M["MI_V01_Undercoat"]]))
    return objs


def armrests(panels):
    """Door armrests, parented to each door so they swing with it."""
    objs = []
    for name, p in panels.items():
        if not name.startswith("DOOR"):
            continue
        side = 1 if name.endswith("L") else -1
        y0, y1 = (-20, 24) if "_F" in name else (62, 104)
        xin = side * (band_x(97.5) - SHELL_T - 1.5)
        bm = bmesh.new()
        bm_box(bm, min(xin, xin - side * 7), y0, 62, max(xin, xin - side * 7), y1, 68)
        o = new_obj(f"INT_ARMREST_{name[-2:]}", bm, [M["MI_V01_Interior_Vinyl"]])
        o.parent = p
        o.matrix_parent_inverse = Matrix.Translation(-p.location)
        objs.append(o)
    return objs


# ----------------------------------------------------------------------------- MPD layer

def decal_plane(name, x0, y0, x1, y1, z, mat, target, direction=(0, 0, -1), subdiv=24, offset=0.004):
    bm = bmesh.new()
    nx, ny = subdiv, subdiv
    grid = [[bm.verts.new(V(x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, z)) for j in range(ny + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(ny):
            bm.faces.new([grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]])
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for l in f.loops:
            co = l.vert.co
            u = (co.x * 100 - x0) / (x1 - x0)
            v = 1.0 - (co.y * 100 - y0) / (y1 - y0)
            l[uv].uv = (u, v)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    for f in bm.faces:            # decal faces always point up (+Z) on top surfaces
        if f.normal.z < 0:
            f.normal_flip()
    obj = new_obj(name, bm, [mat])
    sw = obj.modifiers.new("sw", "SHRINKWRAP")
    sw.wrap_method = "PROJECT"
    sw.use_project_z = True
    sw.use_negative_direction = direction[2] < 0
    sw.use_positive_direction = direction[2] > 0
    sw.target = target
    sw.offset = offset
    apply_mod(obj, sw)
    return obj


def side_decal(name, y0, z0, y1, z1, side, mat, target, subdiv=20, offset=0.004):
    bm = bmesh.new()
    x = side * 110
    grid = [[bm.verts.new(V(x, y0 + (y1 - y0) * i / subdiv, z0 + (z1 - z0) * j / subdiv)) for j in range(subdiv + 1)] for i in range(subdiv + 1)]
    for i in range(subdiv):
        for j in range(subdiv):
            bm.faces.new([grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]])
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for l in f.loops:
            co = l.vert.co
            u = (co.y * 100 - y0) / (y1 - y0)   # driver side (+X): reader's right is +Y (rear)
            if side < 0:
                u = 1 - u
            v = (co.z * 100 - z0) / (z1 - z0)
            l[uv].uv = (u, v)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = new_obj(name, bm, [mat])
    # make normals face outward (+X for the driver side)
    for p in obj.data.polygons:
        pass
    sw = obj.modifiers.new("sw", "SHRINKWRAP")
    sw.wrap_method = "PROJECT"
    sw.use_project_x = True
    sw.use_negative_direction = side > 0
    sw.use_positive_direction = side < 0
    sw.target = target
    sw.offset = offset
    apply_mod(obj, sw)
    cleanup(obj)
    # ensure outward normals
    bm = bmesh.new(); bm.from_mesh(obj.data)
    for f in bm.faces:
        if (f.normal.x * side) < 0:
            f.normal_flip()
    bm.to_mesh(obj.data); bm.free()
    return obj


def police_layer(body, panels):
    objs = []
    # roof identifier decal (MP / DC)
    objs.append(decal_plane("POLICE_DECAL_ROOF_ID", -72, -14, 72, 116, 150, M["MI_V01_Decal_RoofID"], body))
    # trunk POLICE decal
    objs.append(decal_plane("POLICE_DECAL_TRUNK", -46, 246, 46, 268, 110, M["MI_V01_Decal_Trunk"], panels["TRUNK"]))
    # door seals (front doors, both sides)
    for side, tag in ((1, "L"), (-1, "R")):
        objs.append(side_decal(f"POLICE_DECAL_SEAL_F{tag}", -18, 46, 22, 86, side, M["MI_V01_Decal_DoorSeal"], panels[f"DOOR_F{tag}"]))
    # beacon: chrome base + red dome (Beacon Ray 17 class, APPROXIMATE), on the roof centreline
    by = 32.0
    bz = interp(K["zc"], by)
    bm = bmesh.new()
    bm_revolve(bm, [(0.0, 0.0), (9.0, 0.0), (9.0, 2.5), (7.5, 4.5), (0.0, 4.5)], "z", (0, by, bz - 0.5), segs=36, close=False)
    base = new_obj("POLICE_BEACON_BASE", bm, [M["MI_V01_Chrome"]])
    bm = bmesh.new()
    dome = [(0.0, 4.5), (7.0, 4.5), (7.0, 9.0), (6.4, 13.0), (4.8, 16.5), (2.2, 19.0), (0.0, 19.8)]
    bm_revolve(bm, dome, "z", (0, by, bz - 0.5), segs=36, close=False)
    dome_o = new_obj("POLICE_BEACON_DOME", bm, [M["MI_V01_Beacon_Red_Unlit"]])
    objs += [base, dome_o]
    # roof antenna (APPROXIMATE): base + whip
    bm = bmesh.new()
    ay = 68.0; az = interp(K["zc"], ay)
    bm_cylinder(bm, (0, ay, az - 0.5), "z", 2.0, 0, 2.5, segs=16)
    bm_cylinder(bm, (0, ay, az + 1.5), "z", 0.35, 0, 48, segs=8)   # quarter-wave VHF whip, APPROXIMATE
    objs.append(new_obj("POLICE_ANTENNA", bm, [M["MI_V01_Chrome"]]))
    # licence plates (FICTIONALISED) front + rear
    for y, nm, flip in ((NOSE - 12.5, "PLATE_FRONT", False), (TAIL + 12.5, "PLATE_REAR", True)):
        bm = bmesh.new(); bm_box(bm, -15.25, y - 0.3, 36, 15.25, y + 0.3, 51.2)
        uv = bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            for l in f.loops:
                co = l.vert.co
                u = (co.x * 100 + 15.25) / 30.5
                if flip:
                    u = 1 - u
                l[uv].uv = (u, (co.z * 100 - 36) / 15.2)
        objs.append(new_obj(nm, bm, [M["MI_V01_Plate"]]))
    return objs


# ----------------------------------------------------------------------------- sockets / LODs / collision

def empty(name, loc, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.1
    e.location = V(*loc)
    link(e)
    if parent:
        e.parent = parent
    return e


def make_lods(objs, ratios=(0.45, 0.18), min_faces=(300, 1500)):
    out = []
    for o in objs:
        nf = len(o.data.polygons)
        for lvl, (ratio, mn) in enumerate(zip(ratios, min_faces), start=1):
            if nf < mn:
                continue
            d = duplicate(o, f"{o.name}_LOD{lvl}")
            d.parent = o.parent
            d.matrix_parent_inverse = o.matrix_parent_inverse.copy()
            tri = d.modifiers.new("tri", "TRIANGULATE"); apply_mod(d, tri)
            dec = d.modifiers.new("dec", "DECIMATE"); dec.ratio = ratio; apply_mod(d, dec)
            out.append(d)
    return out


def collision():
    bm = bmesh.new(); bm_box(bm, -100, NOSE, 25, 100, TAIL, 96); a = new_obj("UCX_BODY_01", bm, [M["MI_V01_Undercoat"]])
    bm = bmesh.new()
    # cabin: tapered prism (side view) from belt to roof
    poly = [(-57, 96), (-24, 139), (118, 139), (158, 96)]
    bm_prism(bm, poly, "x", -92, 92); b = new_obj("UCX_BODY_02", bm, [M["MI_V01_Undercoat"]])
    bm = bmesh.new(); bm_box(bm, -104, NOSE - 10, 36, 104, NOSE + 2, 56); c = new_obj("UCX_BODY_03", bm, [M["MI_V01_Undercoat"]])
    bm = bmesh.new(); bm_box(bm, -104, TAIL - 2, 36, 104, TAIL + 10, 56); d = new_obj("UCX_BODY_04", bm, [M["MI_V01_Undercoat"]])
    return [a, b, c, d]


# ----------------------------------------------------------------------------- export

def orient_sheet(obj, direction):
    """Open decal sheets: make all faces point along `direction` (recalc may have flipped them)."""
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bm.normal_update()
    d = Vector(direction)
    if sum(f.normal.dot(d) for f in bm.faces) < 0:
        for f in bm.faces:
            f.normal_flip()
    bm.to_mesh(obj.data); bm.free()


def finalize(objs):
    for o in objs:
        if o.type != "MESH":
            continue
        cleanup(o)
        if "DECAL" in o.name:
            if "SEAL" in o.name:
                orient_sheet(o, (1 if o.matrix_world.translation.x + o.data.vertices[0].co.x > 0 else -1, 0, 0))
            else:
                orient_sheet(o, (0, 0, 1))
        if not o.data.uv_layers:
            box_uv(o)
        smooth(o)


def export(path, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_apply=True,
        export_yup=True, export_normals=True, export_texcoords=True, export_materials="EXPORT",
        export_image_format="AUTO", export_extras=False, export_cameras=False, export_lights=False,
        export_animations=False, export_skins=False, export_morph=False,
    )
    print("wrote", path, os.path.getsize(path), "bytes")


def all_descendants(root):
    out = [root]
    for c in root.children:
        out += all_descendants(c)
    return out


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(OUT, exist_ok=True)
    tex = make_textures()
    make_materials(load_images(tex))

    body = build_loft()
    panels = cut_and_split(body)
    if PREVIEW:
        objs = [body] + list(panels.values())
        for o in objs:
            cleanup(o); box_uv(o); smooth(o)
        ws = wheels()
        export(os.path.join(OUT, "PREVIEW_shell.glb"), objs + list(ws.values()))
        return
    houses = wheel_houses()
    glass = glazing(panels)
    front_end()
    rear_end()
    chrome = bumpers() + side_details(panels)
    ws = wheels()
    inte = interior() + underbody() + armrests(panels)
    pol = police_layer(body, panels)
    # v002 fine bevels on hard-surface props (edges that catch light)
    for nm in ("GRILLE_BARS", "BUMPER_FRONT_GUARDS", "BUMPER_REAR_GUARDS", "DOOR_HANDLES", "INT_DASH", "INT_FLOOR",
               "TRIM_REAR_PANEL", "TRIM_HOOD_FRONT", "INT_ENGINE_BAY", "INT_ENGINE_BAY_WALLS",
               "POLICE_RADIO", "INT_VISORS", "UNDER_AXLES_TANK", "WIPERS", "INT_SEAT_FRONT", "INT_SEAT_REAR"):
        o = bpy.data.objects.get(nm)
        if o is not None:
            bevel(o, width=0.004, segs=2, angle=40)
    for o in bpy.context.scene.objects:
        if o.name.startswith("INT_ARMREST"):
            bevel(o, width=0.008, segs=3, angle=40)

    root = empty("SM_V01_PatrolSedan_MPDC", (0, 0, 0))
    for o in list(bpy.context.scene.objects):
        if o.type == "MESH" and o.parent is None and not o.name.startswith("WHEEL_"):
            o.parent = root
    for tag, side in (("L", 1), ("R", -1)):
        st = empty(f"STEER_F{tag}", (side * TREAD_F / 2, AXLE_F, TYRE_OD / 2 - TYRE_SAG), root)
        w = ws[f"WHEEL_F{tag}"]
        w.parent = st
        w.location = (0, 0, 0)
        ws[f"WHEEL_R{tag}"].parent = root
    empty("SOCKET_DRIVER", (41, 20, 60), root)
    empty("SOCKET_STEERING", (41, -12, 92), root)
    empty("SOCKET_BEACON", (0, 32, interp(K["zc"], 32)), root)
    empty("SOCKET_ANTENNA", (0, 68, interp(K["zc"], 68)), root)
    empty("SOCKET_ROOF_SIGN", (0, 48, interp(K["zc"], 48)), root)
    empty("SOCKET_PLATE_F", (0, NOSE - 12.5, 43.6), root)
    empty("SOCKET_PLATE_R", (0, TAIL + 12.5, 43.6), root)
    empty("SOCKET_SPOTLIGHT_L", (band_x(104), -40, 104), root)
    empty("SOCKET_SIREN", (band_x(88) - 6, -200, 88), root)
    for name, p in panels.items():
        empty(f"HINGE_{name}", (0, 0, 0), p)

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    finalize(meshes)
    lods = make_lods([o for o in meshes if not o.name.startswith("UCX_")])
    col = collision()
    for c in col:
        c.parent = root
    finalize(col)

    everything = all_descendants(root)
    export(os.path.join(OUT, "SM_V01_PatrolSedan_MPDC.glb"), everything)

    # city-neutral base: no POLICE_* parts, neutral paint
    for o in list(everything):
        if o.name.startswith("POLICE_"):
            bpy.data.objects.remove(o, do_unlink=True)
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            for s in o.material_slots:
                if s.material == M["MI_V01_Paint_Body"]:
                    s.material = M["MI_V01_Paint_Neutral"]
    root.name = "SM_V01_Sedan_Base_Neutral"
    export(os.path.join(OUT, "SM_V01_Sedan_Base_Neutral.glb"), all_descendants(root))


if __name__ == "__main__":
    main()
