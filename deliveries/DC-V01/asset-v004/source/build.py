"""DC-V01 — MPD patrol car 1963 — reproducible generator (bpy 4.5).

Run:  python jobs/DC-V01/build.py            (full build + GLB export)
      python jobs/DC-V01/build.py --preview  (body shell only, quick clay check)

Builds a 1963 Ford-pattern full-size four-door sedan (APPROXIMATE identity, see EVIDENCE.md):
structured body grid (stations x rows around a filleted section outline, C1 key curves) ->
wheel openings, pillar plane cuts, grille/lamp openings -> windows, mouldings, doors, hood and
trunk selected on the grid -> glass taken from the skin -> solidified shell with panel gaps ->
hinged panels, chrome, lamps, grille, bumpers, wheels, interior, underbody, MPD livery layer.
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
SHELL_T = 1.2              # v003: sheet + inner panel read thinner at every opening

# ----------------------------------------------------------------------------- helpers

def V(x, y, z):
    return Vector((x / 100.0, y / 100.0, z / 100.0))


_PCHIP = {}


def _pchip_slopes(keys):
    """Fritsch-Carlson monotone cubic slopes: C1-continuous, no overshoot between keys."""
    ts = [k[0] for k in keys]; vs = [k[1] for k in keys]
    n = len(keys)
    d = [(vs[i + 1] - vs[i]) / (ts[i + 1] - ts[i]) for i in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            h0, h1 = ts[i] - ts[i - 1], ts[i + 1] - ts[i]
            w0, w1 = 2 * h1 + h0, h1 + 2 * h0
            m[i] = (w0 + w1) / (w0 / d[i - 1] + w1 / d[i])
    return m


def interp(keys, t):
    """Smooth (C1, monotone-preserving) interpolation over [(t, value), ...] sorted by t.
    v003: replaces the v001/v002 per-segment smoothstep, whose zero slope at every key put
    flat spots and ripples into the hood, fenders and roof."""
    if t <= keys[0][0]:
        return keys[0][1]
    if t >= keys[-1][0]:
        return keys[-1][1]
    key = id(keys)
    if key not in _PCHIP:
        _PCHIP[key] = _pchip_slopes(keys)
    m = _PCHIP[key]
    for i, ((t0, v0), (t1, v1)) in enumerate(zip(keys, keys[1:])):
        if t0 <= t <= t1:
            h = t1 - t0
            s = (t - t0) / h
            h00 = 2 * s ** 3 - 3 * s ** 2 + 1; h10 = s ** 3 - 2 * s ** 2 + s
            h01 = -2 * s ** 3 + 3 * s ** 2; h11 = s ** 3 - s ** 2
            return h00 * v0 + h10 * h * m[i] + h01 * v1 + h11 * h * m[i + 1]
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
    SANS = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"   # Helvetica-class caps (closest to E1)
    if not os.path.exists(SANS):
        SANS = BOLD
    out = {}

    # Roof identifier (E1): from above with the nose to the right, the roof reads "D M" over "C P":
    # M (driver side) / P (passenger) over the front seat, D / C over the rear seat, letter tops toward
    # the driver side (+X). Decal UVs: U = +X, image row 0 = front of the plane (y = -14), so the
    # rendered roof is this image flipped top-to-bottom -> glyphs are turned clockwise, then flipped.
    S = 1024
    X0, X1, Y0, Y1 = -72.0, 72.0, -14.0, 116.0          # decal plane extent (cm), see police_layer()
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    font = ImageFont.truetype(SANS, 420)
    def glyph(ch, along_cm, across_cm):
        g = Image.new("L", (520, 520), 0)
        d = ImageDraw.Draw(g)
        d.text((40, 20), ch, font=font, fill=255)
        g = g.crop(g.getbbox())
        w = int(round(along_cm / (Y1 - Y0) * S)); h = int(round(across_cm / (X1 - X0) * S))
        g = g.resize((w, h), Image.LANCZOS)            # upright: width = along the car, height = across
        g = g.transpose(Image.ROTATE_270)              # tops now point to +U (driver side)
        g = g.transpose(Image.FLIP_TOP_BOTTOM)         # undo the plane's front-at-top row order
        tile = Image.new("RGBA", g.size, TEAL[:3] + (0,))
        tile.putalpha(g)
        return tile
    # (letter, centre x cm, centre y cm, width along car cm, cap height across car cm) — sizes from E1
    for ch, xc, yc, wl, hc in (("M", 38, 16, 47, 39), ("P", -38, 16, 40, 39),
                               ("D", 38, 82, 43, 39), ("C", -38, 82, 43, 39)):
        g = glyph(ch, wl, hc)
        u = (xc - X0) / (X1 - X0) * S; row = (yc - Y0) / (Y1 - Y0) * S
        im.alpha_composite(g, (int(round(u - g.size[0] / 2)), int(round(row - g.size[1] / 2))))
    p = os.path.join(TEX, "T_V01_Decal_RoofID.png"); im.save(p); out["roof"] = p

    # Door seal (APPROXIMATE, generic — no copied artwork): rings, a star, and evenly spaced ring text
    # (upper arc reads left-to-right with tops outward, lower arc left-to-right with tops inward).
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    d.ellipse((24, 24, S - 24, S - 24), outline=TEAL, width=30)
    d.ellipse((250, 250, S - 250, S - 250), outline=TEAL, width=16)
    star = []
    for i in range(10):
        r = 190 if i % 2 == 0 else 78
        a = math.radians(-90 + 36 * i)
        star.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(star, fill=TEAL)
    fs = ImageFont.truetype(SANS, 92)
    def arc_text(text, r, upper):
        track = 6.0
        adv = [fs.getlength(ch) + track for ch in text]
        total = sum(adv) - track
        ang = total / r                                   # radians spanned
        acc = 0.0
        for ch, w in zip(text, adv):
            mid = acc + (w - track) / 2
            acc += w
            if upper:
                psi = math.pi / 2 + ang / 2 - mid / r     # left -> right across the top
                rot = math.degrees(psi) - 90
            else:
                psi = -math.pi / 2 - ang / 2 + mid / r    # left -> right across the bottom
                rot = math.degrees(psi) + 90
            gx, gy = c + r * math.cos(psi), c - r * math.sin(psi)
            g = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            gd.text((80, 80), ch, font=fs, fill=TEAL, anchor="mm")
            g = g.rotate(rot, resample=Image.BICUBIC)
            im.alpha_composite(g, (int(round(gx - 80)), int(round(gy - 80))))
    arc_text("METROPOLITAN POLICE", 372, True)
    arc_text("WASHINGTON, D.C.", 372, False)
    p = os.path.join(TEX, "T_V01_Decal_DoorSeal.png"); im.save(p); out["seal"] = p

    # Trunk POLICE: U = -X..+X? plane maps U = car X (driver at U=0), V = car Y; read from behind.
    im = Image.new("RGBA", (1024, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f2 = ImageFont.truetype(SANS, 150)
    bb = d.textbbox((0, 0), "POLICE", font=f2)
    d.text(((1024 - (bb[2] - bb[0])) / 2 - bb[0], (256 - (bb[3] - bb[1])) / 2 - bb[1]), "POLICE", font=f2, fill=TEAL)
    im = im.transpose(Image.FLIP_LEFT_RIGHT)  # viewer behind the car, driver side on their left
    p = os.path.join(TEX, "T_V01_Decal_Trunk.png"); im.save(p); out["trunk"] = p

    # Licence plate (FICTIONALISED): 1963-style DC plate, white on dark.
    im = Image.new("RGBA", (512, 256), (28, 36, 54, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((8, 8, 503, 247), outline=(230, 230, 220, 255), width=6)
    f3 = ImageFont.truetype(SANS, 100)
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


# ----------------------------------------------------------------------------- body surface (v003)
# The skin is a structured grid: STATIONS along Y x section ROWS around a filleted control polygon.
# Every panel line, window opening and moulding is selected along grid rows/stations (plus a few
# straight plane cuts for slanted pillar edges), so apertures are clean and pillars keep their width.
# Control polygon per half-section (+X), top centre -> bottom centre:
#   0 centre top | 1 crown | 2 roof/hood mid | 3 drip rail (greenhouse) / hood+deck panel edge |
#   4 belt (window sill) / fender top | 5 shoulder crease | 6 upper side | 7 lower side |
#   8 rocker top | 9 rocker bottom | 10 floor edge | 11 floor centre
K = {
    # centreline top: hood -> windshield -> roof -> rear window -> deck
    "zc":  [(NOSE, 86.0), (-225, 87.5), (-150, 89.5), (-70, 91.5), (-58, 93.0), (-40, 116.5), (-24, 136.5),
            (35, 140.8), (118, 138.6), (122, 136.6), (140, 117.5), (158, 98.5), (166, 96.6), (240, 94.6), (TAIL, 91.5)],
    # v004: narrow crown + steeper fall on the hood -> E1's central longitudinal hood crease
    "x1":  [(NOSE, 12), (-66, 12), (-50, 18), (-24, 30), (118, 30), (158, 22), (TAIL, 22)],
    "dz1": [(NOSE, -0.75), (-66, -0.75), (-50, -0.6), (-24, -0.8), (118, -0.8), (158, -0.5), (TAIL, -0.5)],
    "dz2": [(NOSE, -1.2), (-62, -1.2), (-24, -2.4), (118, -2.4), (158, -1.2), (TAIL, -1.2)],
    # drip rail (greenhouse) / hood & deck-lid edge
    "x3":  [(NOSE, 66), (-150, 69), (-70, 71), (-58, 75.5), (-24, 71.5), (35, 73.5), (118, 71.5), (122, 71.5),
            (158, 77.0), (166, 75), (240, 73), (TAIL, 69)],
    "z3":  [(NOSE, 84.8), (-225, 86.3), (-150, 88.2), (-70, 90.0), (-58, 92.2), (-40, 113.5), (-24, 133.8),
            (35, 137.6), (118, 135.6), (122, 133.6), (140, 115.0), (158, 97.2), (166, 95.4), (240, 93.4), (TAIL, 90.3)],
    # belt (window sill) / fender top
    # v004: '63 Ford is slab-sided in plan; ends barely pull in (v003 tapered ~8 cm/side and read boat-like)
    "x4":  [(NOSE, 88), (-225, 89.5), (-150, 90.5), (-70, 91.5), (-58, 92.5), (-24, 93.0), (120, 93.0),
            (158, 92.5), (166, 92.0), (240, 90.5), (TAIL, 89)],
    "z4":  [(NOSE, 84.2), (-225, 85.8), (-150, 87.6), (-70, 89.6), (-58, 92.0), (-40, 95.6), (-24, 96.5),
            (120, 96.5), (158, 96.3), (166, 95.0), (240, 92.8), (TAIL, 89.6)],
    # shoulder crease: the sharp full-length character line
    "x5":  [(NOSE, 96.5), (-225, 98.6), (-150, 100.0), (-70, 101.0), (0, 101.6), (120, 101.6), (160, 101.2),
            (240, 99.8), (TAIL, 97.5)],
    "z5":  [(NOSE, 82.0), (-225, 83.6), (-150, 85.4), (-70, 87.8), (0, 89.8), (158, 90.6), (240, 89.4), (TAIL, 87.0)],
    "x6":  [(NOSE, 96.0), (-225, 98.2), (-150, 99.8), (-70, 101.0), (0, 101.8), (120, 101.8), (160, 101.4),
            (240, 99.5), (TAIL, 97.0)],
    "z6":  [(NOSE, 66), (TAIL, 66)],
    "x7":  [(NOSE, 93.5), (-225, 96.0), (-150, 97.6), (-70, 99.0), (0, 99.6), (120, 99.6), (160, 99.2),
            (240, 97.3), (TAIL, 94.5)],
    "z7":  [(NOSE, 44), (-70, 42), (0, 42), (TAIL, 44)],
    "x8":  [(NOSE, 90), (-225, 92.5), (-150, 93.5), (-70, 95), (0, 95.5), (120, 95.5), (160, 95.0), (240, 93.8), (TAIL, 92)],
    "z8":  [(NOSE, 33), (-70, 30), (0, 29.5), (120, 29.5), (TAIL, 33)],
    "x9":  [(NOSE, 84), (-225, 86.5), (-150, 87.5), (-70, 88.5), (0, 89), (120, 89), (160, 88.4), (240, 87.5), (TAIL, 86)],
    "z9":  [(NOSE, 27), (-70, 24), (0, 23.5), (120, 23.5), (TAIL, 27)],
    "x10": [(NOSE, 66), (-100, 72), (0, 74), (120, 74), (TAIL, 66)],
    "z10": [(NOSE, 27), (-70, 22.5), (0, 22), (120, 22), (TAIL, 26)],
    # fillet radii (cm) at control points 1..10; small = crisp edge, large = soft curve
    "r1":  [(NOSE, 80), (TAIL, 80)],
    "r2":  [(NOSE, 80), (TAIL, 80)],
    "r3":  [(NOSE, 14), (-70, 14), (-58, 2.0), (158, 2.0), (166, 14), (TAIL, 14)],
    "r4":  [(NOSE, 8), (-70, 8), (-58, 1.4), (158, 1.4), (166, 8), (TAIL, 8)],
    "r5":  [(NOSE, 0.9), (TAIL, 0.9)],
    "r6":  [(NOSE, 120), (TAIL, 120)],
    "r7":  [(NOSE, 50), (TAIL, 50)],
    "r8":  [(NOSE, 6), (TAIL, 6)],
    "r9":  [(NOSE, 3), (TAIL, 3)],
    "r10": [(NOSE, 4), (TAIL, 4)],
}

# rows per span between control points i -> i+1, as cumulative fractions of the span length
SPAN_FRACS = [
    [0, 0.34, 0.67, 1.0],                                   # 0-1 centre -> crown
    [0, 0.25, 0.5, 0.75, 1.0],                              # 1-2
    [0, 0.30, 0.55, 0.75, 0.88, 0.95, 1.0],                 # 2-3 (dense toward the drip / panel edge)
    [0, 0.04, 0.10] + [0.10 + 0.87 * i / 9 for i in range(1, 10)] + [1.0],   # 3-4 window band
    [0, 0.25, 0.55, 0.85, 1.0],                             # 4-5 shoulder top
    [0, 0.12, 0.3, 0.5, 0.7, 0.88, 1.0],                    # 5-6
    [0, 0.2, 0.4, 0.6, 0.8, 1.0],                           # 6-7
    [0, 0.3, 0.6, 0.85, 1.0],                               # 7-8
    [0, 0.33, 0.67, 1.0],                                   # 8-9 rocker
    [0, 0.5, 1.0],                                          # 9-10
    [0, 0.3, 0.65, 1.0],                                    # 10-11 floor
]
CP_ROW = [0]
for _f in SPAN_FRACS:
    CP_ROW.append(CP_ROW[-1] + len(_f) - 1)
HALF_ROWS = CP_ROW[-1]                                      # faces per half-ring


def control_polygon(y):
    g = lambda k: interp(K[k], y)
    zc = g("zc"); x3, z3 = g("x3"), g("z3")
    pts = [(0.0, zc), (g("x1"), zc + g("dz1")), (0.6 * x3, zc + g("dz2")), (x3, z3), (g("x4"), g("z4")),
           (g("x5"), g("z5")), (g("x6"), g("z6")), (g("x7"), g("z7")), (g("x8"), g("z8")), (g("x9"), g("z9")),
           (g("x10"), g("z10")), (0.0, g("z10"))]
    radii = [0.0] + [g(f"r{i}") for i in range(1, 11)] + [0.0]
    return pts, radii


def _fillet(p_prev, p, p_next, r):
    """Tangent points + arc samples for a fillet of radius r at polygon corner p (2D tuples)."""
    a = Vector((p_prev[0] - p[0], p_prev[1] - p[1])); b = Vector((p_next[0] - p[0], p_next[1] - p[1]))
    la, lb = a.length, b.length
    if la < 1e-6 or lb < 1e-6 or r <= 0:
        return [p]
    a.normalize(); b.normalize()
    cosphi = max(-1.0, min(1.0, a.dot(b)))
    phi = math.acos(cosphi)                      # interior angle
    if phi > math.radians(179.5):
        return [p]
    d = r / math.tan(phi / 2)
    dmax = 0.45 * min(la, lb)
    if d > dmax:
        d = dmax; r = d * math.tan(phi / 2)
    t0 = Vector(p) + a * d; t1 = Vector(p) + b * d
    bis = (a + b).normalized()
    c = Vector(p) + bis * (r / math.sin(phi / 2))
    v0, v1 = t0 - c, t1 - c
    ang0, ang1 = math.atan2(v0.y, v0.x), math.atan2(v1.y, v1.x)
    da = ang1 - ang0
    while da > math.pi: da -= 2 * math.pi
    while da < -math.pi: da += 2 * math.pi
    n = 8
    return [(c.x + r * math.cos(ang0 + da * i / n), c.y + r * math.sin(ang0 + da * i / n)) for i in range(n + 1)]


def half_section(y):
    """Resampled half section at station y: list of HALF_ROWS + 1 (x, z) points, top -> bottom."""
    pts, radii = control_polygon(y)
    # build a dense polyline with fillets; remember where each control point's arc midpoint lies
    poly, marks = [], []
    for i, p in enumerate(pts):
        if 0 < i < len(pts) - 1:
            arc = _fillet(pts[i - 1], p, pts[i + 1], radii[i])
        else:
            arc = [p]
        marks.append(len(poly) + len(arc) // 2)
        poly.extend(arc)
    # cumulative arc length
    s = [0.0]
    for (x0, z0), (x1, z1) in zip(poly, poly[1:]):
        s.append(s[-1] + math.hypot(x1 - x0, z1 - z0))
    def at(sv):
        for k in range(len(s) - 1):
            if s[k] <= sv <= s[k + 1]:
                f = (sv - s[k]) / (s[k + 1] - s[k]) if s[k + 1] > s[k] else 0.0
                return (poly[k][0] + (poly[k + 1][0] - poly[k][0]) * f, poly[k][1] + (poly[k + 1][1] - poly[k][1]) * f)
        return poly[-1]
    out = []
    for i, fr in enumerate(SPAN_FRACS):
        s0, s1 = s[marks[i]], s[marks[i + 1]]
        for f in fr[:-1]:
            out.append(at(s0 + (s1 - s0) * f))
    out.append(poly[-1])
    out[0] = (0.0, out[0][1]); out[-1] = (0.0, out[-1][1])
    return out


def side_x(y, z):
    """Outer body x (cm, +X side) at station y and height z, searched between the drip rail and rocker."""
    h = half_section(y)
    for (x0, z0), (x1, z1) in zip(h[CP_ROW[3]:CP_ROW[9]], h[CP_ROW[3] + 1:CP_ROW[9] + 1]):
        if min(z0, z1) <= z <= max(z0, z1) and abs(z1 - z0) > 1e-6:
            return x0 + (x1 - x0) * (z - z0) / (z1 - z0)
    return interp(K["x5"], y)


ROLL_R = 2.5                      # radius of the rolled edge around the flat front and rear faces
# exact stations where panel lines / openings fall (cm)
HOOD_Y0, HOOD_Y1 = NOSE + ROLL_R, -62.0
TRUNK_Y0, TRUNK_Y1 = 162.0, TAIL - ROLL_R
WS_Y = (-55.0, -26.5)             # windshield opening (between cowl and header)
BL_Y = (125.0, 155.5)             # backlight opening
DOOR_F_Y = (-47.0, 50.0)          # front door, below the belt
DOOR_R_Y = (51.0, 106.0)          # rear door, below the belt (ahead of the rear wheel arch)
WIN_F_Y1, WIN_R_Y0 = 45.0, 57.0   # B-pillar between the side windows
TRIM_W = 2.0                      # bright window-surround moulding width
WS_TRIM_Y = (WS_Y[0] - 1.5, WS_Y[1] + 1.5)
BL_TRIM_Y = (BL_Y[0] - 1.5, BL_Y[1] + 1.5)
EXACT_Y = [HOOD_Y0, HOOD_Y1, *WS_Y, *BL_Y, *DOOR_F_Y, *DOOR_R_Y, WIN_F_Y1, WIN_R_Y0, TRUNK_Y0, TRUNK_Y1,
           -24.0, -58.0, 122.0, 158.0, *WS_TRIM_Y, *BL_TRIM_Y, WIN_F_Y1 + TRIM_W, WIN_R_Y0 - TRIM_W]
# slanted edges in side view (y, z) pairs: A-pillar side and C-pillar side
L_DOOR_F = ((-47.0, 96.5), (-18.4, 131.0))      # front-door frame front edge (parallel to the A-pillar)
L_WIN_F = ((-41.0, 97.5), (-13.2, 131.0))       # front side-window front edge
L_WIN_R = ((112.0, 131.0), (120.0, 97.5))       # rear side-window rear edge (C-pillar)
L_DOOR_R = ((115.5, 131.0), (123.5, 97.5))      # rear-door frame rear edge
L_TRIM_F = tuple((y - TRIM_W, z) for y, z in L_WIN_F)   # outer edge of the front-window moulding
L_TRIM_R = tuple((y + TRIM_W, z) for y, z in L_WIN_R)   # outer edge of the rear-window moulding
# v004: the door's window-band edge IS the chrome frame's outer edge. v003 kept a 1.5-3 cm painted
# door-frame strip between L_DOOR_* and L_TRIM_*; panel-gap shrink + bevel turned it into a torn,
# zig-zag sliver along the A- and C-pillars.
L_DOOR_F = L_TRIM_F
L_DOOR_R = L_TRIM_R


def body_stations():
    ys = []
    # front roll: quarter circle from the hood/fender top down onto the flat front face
    rolls_f = [(NOSE + ROLL_R * (1 - math.sin(t)), ROLL_R * (1 - math.cos(t)))
               for t in [math.radians(a) for a in (90, 70, 50, 30, 15, 0)]]
    rolls_r = [(TAIL - ROLL_R * (1 - math.sin(t)), ROLL_R * (1 - math.cos(t)))
               for t in [math.radians(a) for a in (0, 15, 30, 50, 70, 90)]]
    y0, y1 = NOSE + ROLL_R, TAIL - ROLL_R
    n = int(round((y1 - y0) / 3.0))
    mids = [y0 + (y1 - y0) * i / n for i in range(n + 1)]
    mids = [y for y in mids if all(abs(y - e) > 0.9 for e in EXACT_Y) or y in (y0, y1)]
    mids = sorted(set([round(y, 4) for y in mids + EXACT_Y if y0 <= y <= y1]))
    st = [(y, ins) for y, ins in rolls_f[:-1]] + [(y, 0.0) for y in mids] + [(y, ins) for y, ins in rolls_r[1:]]
    return st


def _inset_ring(ring, d):
    """Offset a closed 2D ring (list of (x, z)) inward by d along per-vertex normals."""
    if d <= 0:
        return ring
    n = len(ring)
    cx = sum(p[0] for p in ring) / n; cz = sum(p[1] for p in ring) / n
    out = []
    for i in range(n):
        p0, p1, p2 = ring[i - 1], ring[i], ring[(i + 1) % n]
        t = Vector((p2[0] - p0[0], p2[1] - p0[1]))
        if t.length < 1e-9:
            out.append(p1); continue
        t.normalize()
        nrm = Vector((t.y, -t.x))
        if nrm.dot(Vector((cx - p1[0], cz - p1[1]))) < 0:
            nrm = -nrm
        out.append((p1[0] + nrm.x * d, p1[1] + nrm.y * d))
    return out


def full_ring(y):
    h = half_section(y)
    return [(x, z) for x, z in h] + [(-x, z) for x, z in reversed(h[1:-1])]


def build_body():
    """Closed body skin with per-face grid indices (layers: st = station, row = half-ring row,
    side = +1/-1, 0 for the end caps)."""
    bm = bmesh.new()
    st_l = bm.faces.layers.int.new("st"); row_l = bm.faces.layers.int.new("row"); side_l = bm.faces.layers.int.new("side")
    stations = body_stations()
    STATION_Y[:] = [y for y, _ in stations]
    rings = []
    for y, ins in stations:
        ring = _inset_ring(full_ring(min(max(y, NOSE), TAIL)), ins)
        rings.append([bm.verts.new(V(x, y, z)) for x, z in ring])
    n = len(rings[0])
    for si, (ra, rb) in enumerate(zip(rings, rings[1:])):
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new([ra[i], rb[i], rb[j], ra[j]])
            f[st_l] = si
            if i < HALF_ROWS:
                f[row_l], f[side_l] = i, 1
            else:
                f[row_l], f[side_l] = n - 1 - i, -1
    for ring in (rings[0], rings[-1]):
        f = bm.faces.new(list(ring)); f[st_l] = -1; f[row_l] = -1; f[side_l] = 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.material_index = 0
        if f[row_l] >= CP_ROW[9]:
            f.material_index = 2                     # underside reads as undercoat
    obj = new_obj("BODY", bm, [M["MI_V01_Paint_Body"], M["MI_V01_Interior_Trim"], M["MI_V01_Undercoat"], M["MI_V01_Chrome"]])
    return obj


STATION_Y = []


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


# ----------------------------------------------------------------------------- apertures + panels (v003)
GRILLE = (84.0, 53.0, 80.0)        # half-width, z0, z1: full-width '63-pattern grille, lamps inside it
LAMP_X, LAMP_Z = (53.0, 72.0), 67.0
TAIL_X, TAIL_Z = 71.0, 70.0
PLATE_Y_F, PLATE_Y_R = NOSE - 3.5 - 7.1 - 0.9, TAIL + 3.5 + 7.1 + 0.9   # v004: plates just proud of the blade bumpers
SPOT_Y, SPOT_Z = -44.0, 104.0      # spotlight pivot on the driver A-pillar base (ahead of the mirror)
TAIL_R = 10.2                      # v004: big round '63 tail lamp (v003 8.3 cm read as a marker light)
R_BAND0, R_BAND1 = CP_ROW[3], CP_ROW[4]          # window band rows [R_BAND0, R_BAND1)
GLASS_ROWS = (R_BAND0 + 2, R_BAND1 - 1)          # side glass rows (frame row above, sill reveal row below)
DOOR_ROWS = (R_BAND0 + 1, CP_ROW[8])             # doors: from the frame row down to the rocker top
PILLAR_ROWS = 2                                  # top-region rows kept as pillar beside windshield/backlight


def _line_side(p, line):
    """>0 when (y, z) point p is behind (toward +Y) the side-view line ((y0, z0), (y1, z1))."""
    (y0, z0), (y1, z1) = line
    dy, dz = y1 - y0, z1 - z0
    nrm = Vector((dz, -dy)).normalized()     # rotate direction -> normal
    if nrm.x < 0:
        nrm = -nrm                           # point toward +Y
    return nrm.dot(Vector((p[0] - y0, p[1] - z0)))


def _bisect_line(bm, line, faces):
    (y0, z0), (y1, z1) = line
    no = Vector((0.0, z1 - z0, -(y1 - y0))).normalized()
    co = Vector((0.0, y0 / 100.0, z0 / 100.0))
    geom = list({v for f in faces for v in f.verts}) + list({e for f in faces for e in f.edges}) + list(faces)
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, dist=1e-6,
                           use_snap_center=False, clear_outer=False, clear_inner=False)


def _yz(f):
    c = f.calc_center_median()
    return c.y * 100.0, c.z * 100.0


def cut_and_split(body):
    """Openings, mouldings and opening panels selected on the body grid. Returns (panels, glass, trims)."""
    bm = bmesh.new(); bm.from_mesh(body.data)
    st_l = bm.faces.layers.int["st"]; row_l = bm.faces.layers.int["row"]; side_l = bm.faces.layers.int["side"]
    # wheel openings: round over the top, straight down below the hub line (no hanging tabs)
    for y in (AXLE_F, AXLE_R):
        for side in (1, -1):
            arch_cut(bm, y, TYRE_OD / 2 + 1.5, 41.0, (side * 58, side * 125))
    # slanted pillar edges: plane cuts limited to the window-band rows
    band = lambda: [f for f in bm.faces if f[side_l] != 0 and R_BAND0 <= f[row_l] < CP_ROW[4]]
    for line in (L_DOOR_F, L_TRIM_F, L_WIN_F, L_WIN_R, L_TRIM_R, L_DOOR_R):
        _bisect_line(bm, line, band())
    # grille, headlamp and tail-lamp openings in the flat end faces
    gh, gz0, gz1 = GRILLE
    planes = [((-gh / 100, 0, 0), (-1, 0, 0)), ((gh / 100, 0, 0), (1, 0, 0)), ((0, 0, gz0 / 100), (0, 0, -1)), ((0, 0, gz1 / 100), (0, 0, 1))]
    bisect_cut(bm, planes, (-gh / 100 - 0.001, NOSE / 100 - 0.01, gz0 / 100 - 0.001), (gh / 100 + 0.001, NOSE / 100 + 0.01, gz1 / 100 + 0.001),
               lambda p: abs(p.x) < gh / 100 and gz0 / 100 < p.z < gz1 / 100 and p.y < NOSE / 100 + 0.005)
    for sgn in (1, -1):
        circle_cut(bm, (sgn * TAIL_X, TAIL, TAIL_Z), "y", TAIL_R, (TAIL - 1, TAIL + 1), segs=28)

    # ---- classify faces
    sets = {k: [] for k in ("WINDSHIELD", "REAR", "DOOR_FL", "DOOR_FR", "DOOR_RL", "DOOR_RR", "HOOD", "TRUNK")}
    for k in ("GDOOR_FL", "GDOOR_FR", "GDOOR_RL", "GDOOR_RR"):
        sets[k] = []
    drip = []
    trims = {k: [] for k in ("WINDSHIELD", "REAR", "GDOOR_FL", "GDOOR_FR", "GDOOR_RL", "GDOOR_RR")}
    for f in bm.faces:
        sd, r = f[side_l], f[row_l]
        if sd == 0 or r < 0:
            continue
        y, z = _yz(f)
        tag = "L" if sd > 0 else "R"
        if r < R_BAND0 - PILLAR_ROWS:
            if WS_Y[0] < y < WS_Y[1]:
                sets["WINDSHIELD"].append(f); continue
            if BL_Y[0] < y < BL_Y[1]:
                sets["REAR"].append(f); continue
        if r < R_BAND0 - 1:
            if WS_TRIM_Y[0] < y < WS_TRIM_Y[1]:
                trims["WINDSHIELD"].append(f); continue
            if BL_TRIM_Y[0] < y < BL_TRIM_Y[1]:
                trims["REAR"].append(f); continue
        if r < R_BAND0:
            if HOOD_Y0 < y < HOOD_Y1:
                sets["HOOD"].append(f); continue
            if TRUNK_Y0 < y < TRUNK_Y1:
                sets["TRUNK"].append(f); continue
            if -24 < y < 122 and r >= R_BAND0 - 1:
                drip.append(f)                                   # bright drip-rail moulding
            continue
        if r == R_BAND0 and -24 < y < 122:
            drip.append(f)
            continue
        in_band = r < R_BAND1
        # side glass
        if GLASS_ROWS[0] <= r < GLASS_ROWS[1]:
            if _line_side((y, z), L_WIN_F) > 0 and y < WIN_F_Y1:
                sets[f"GDOOR_F{tag}"].append(f); continue
            if y > WIN_R_Y0 and _line_side((y, z), L_WIN_R) < 0:
                sets[f"GDOOR_R{tag}"].append(f); continue
        # doors
        if DOOR_ROWS[0] <= r < DOOR_ROWS[1]:
            if in_band:
                if _line_side((y, z), L_DOOR_F) > 0 and y < DOOR_F_Y[1]:
                    if _line_side((y, z), L_TRIM_F) > 0 and y < WIN_F_Y1 + TRIM_W:
                        trims[f"GDOOR_F{tag}"].append(f)      # frame top, pillar edges and sill reveal
                    else:
                        sets[f"DOOR_F{tag}"].append(f)
                    continue
                if DOOR_R_Y[0] < y and _line_side((y, z), L_DOOR_R) < 0:
                    if y > WIN_R_Y0 - TRIM_W and _line_side((y, z), L_TRIM_R) < 0:
                        trims[f"GDOOR_R{tag}"].append(f)
                    else:
                        sets[f"DOOR_R{tag}"].append(f)
                    continue
            else:
                if DOOR_F_Y[0] < y < DOOR_F_Y[1]:
                    sets[f"DOOR_F{tag}"].append(f); continue
                if DOOR_R_Y[0] < y < DOOR_R_Y[1]:
                    sets[f"DOOR_R{tag}"].append(f); continue
    for f in drip:
        f.material_index = 3                                     # bright drip-rail moulding (stays on the body)
    glass_keys = ("WINDSHIELD", "REAR", "GDOOR_FL", "GDOOR_FR", "GDOOR_RL", "GDOOR_RR")

    mats = [M["MI_V01_Paint_Body"], M["MI_V01_Interior_Trim"], M["MI_V01_Undercoat"], M["MI_V01_Chrome"]]
    glass, trim_objs, panels = {}, {}, {}
    gname = {"WINDSHIELD": "GLASS_WINDSHIELD", "REAR": "GLASS_REAR"}
    for gk in glass_keys:
        nm = gname.get(gk, "GLASS_" + gk[1:])
        glass[nm] = extract_faces(bm, sets[gk], nm, [M["MI_V01_Glass"]])
        trim_objs[nm] = extract_faces(bm, trims[gk], nm.replace("GLASS", "TRIM_WINDOW"), [M["MI_V01_Chrome"]])
    for k in ("DOOR_FL", "DOOR_FR", "DOOR_RL", "DOOR_RR", "HOOD", "TRUNK"):
        panels[k] = extract_faces(bm, sets[k], k, mats)
    bm.to_mesh(body.data); bm.free()

    # panel gaps + sheet thickness + rolled edges
    for name, p in panels.items():
        shrink_boundary(p, 0.0035)
        solidify(p, inner_mat=1 if name.startswith("DOOR") else 2, rim_mat=0)
    solidify(body, inner_mat=1, rim_mat=0)
    for p in list(panels.values()) + [body]:
        bevel(p, width=0.0025, segs=2, angle=55)
    # glass sits just inside the frame; mouldings stand slightly proud
    for nm, g in glass.items():
        _offset_along_normals(g, -0.009)
        assign_all(g, M["MI_V01_Glass"])
        sol = g.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.005; sol.offset = -1.0
        apply_mod(g, sol)
    for nm, t in trim_objs.items():
        assign_all(t, M["MI_V01_Chrome"])
        _offset_along_normals(t, 0.0015)
        sol = t.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.005; sol.offset = -1.0; sol.use_even_offset = True
        apply_mod(t, sol)
        bevel(t, width=0.0015, segs=1, angle=40)
    pivots = {"DOOR_FL": (side_x(-46, 62), -46, 62), "DOOR_FR": (-side_x(-46, 62), -46, 62),
              "DOOR_RL": (side_x(52, 62), 52, 62), "DOOR_RR": (-side_x(52, 62), 52, 62),
              "HOOD": (0, HOOD_Y1, interp(K["zc"], HOOD_Y1)), "TRUNK": (0, TRUNK_Y0, interp(K["zc"], TRUNK_Y0))}
    for name, p in panels.items():
        set_origin(p, V(*pivots[name]))
    # door glass + surround mouldings ride with their door
    for nm in list(glass):
        if "DOOR" in nm:
            door = panels[nm.replace("GLASS_", "")]
            for o in (glass[nm], trim_objs[nm]):
                o.parent = door
                o.matrix_parent_inverse = Matrix.Translation(-door.location)
    return panels, glass


def arch_cut(bm, yc_cm, zc_cm, r_cm, span_cm, segs=48):
    """Wheel opening through the side skin: upper half-circle + vertical sides down past the sill."""
    yc, zc, r = yc_cm / 100.0, zc_cm / 100.0, r_cm / 100.0
    a0, a1 = sorted(v / 100.0 for v in span_cm)
    rc = r * math.cos(math.pi / segs)
    planes, normals = [], []
    for i in range(segs // 2):                                    # upper half only
        a = math.pi * (i + 0.5) / (segs // 2)
        nn = Vector((0, math.cos(a), math.sin(a)))
        normals.append(nn)
        planes.append((Vector((0, yc, zc)) + nn * rc, nn))
    planes += [((0, yc - rc, 0), (0, -1, 0)), ((0, yc + rc, 0), (0, 1, 0)), ((0, 0, zc), (0, 0, 1))]
    lo, hi = (a0, yc - r - 0.01, -0.1), (a1, yc + r + 0.01, zc + r + 0.01)
    def inside(p):
        if not (a0 <= p.x <= a1 and abs(p.y - yc) < rc):
            return False
        if p.z <= zc:
            return True
        return all(nn.dot(Vector((0, p.y - yc, p.z - zc))) < rc for nn in normals)
    bisect_cut(bm, planes, lo, hi, inside, True)


def _offset_along_normals(obj, d):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * d
    bm.to_mesh(obj.data); bm.free()


def wheel_houses():
    """Inner wheel-house liners (closed, 1 cm thick): half-round over the tyre and straight walls down
    to the sill line, matching the U-shaped wheel openings."""
    bm = bmesh.new()
    cz = TYRE_OD / 2 + 1.5
    for y in (AXLE_F, AXLE_R):
        for side in (1, -1):
            xin, xout = (62, 93) if side > 0 else (-93, -62)       # stays inside the skin down to the rocker
            for r in ((42.0, 43.0),):
                r0, r1 = r
                # profile in (y, z): down the front wall, over the arch, down the rear wall
                zf, zr = interp(K["z8"], y - r0) + 1.0, interp(K["z8"], y + r0) + 1.0   # walls end at the rocker top
                prof = lambda rr: ([(y - rr, zf)] +
                                   [(y - rr * math.cos(math.pi * i / 32), cz + rr * math.sin(math.pi * i / 32)) for i in range(33)] +
                                   [(y + rr, zr)])
                rings = [[bm.verts.new(V(x, py, pz)) for py, pz in prof(rr)] for x in (xin, xout) for rr in (r0, r1)]
                ri_in, ro_in, ri_out, ro_out = rings
                n = len(ri_in)
                for i in range(n - 1):
                    j = i + 1
                    bm.faces.new([ri_in[i], ri_in[j], ri_out[j], ri_out[i]])
                    bm.faces.new([ro_out[i], ro_out[j], ro_in[j], ro_in[i]])
                    bm.faces.new([ri_in[j], ri_in[i], ro_in[i], ro_in[j]])
                    bm.faces.new([ri_out[i], ri_out[j], ro_out[j], ro_out[i]])
                for k in (0, n - 1):
                    bm.faces.new([ri_in[k], ro_in[k], ro_out[k], ri_out[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.material_index = 0
    return new_obj("WHEELHOUSES", bm, [M["MI_V01_Undercoat"]])


# ----------------------------------------------------------------------------- exterior details

BUMPER_PROF = [(-3.0, -7.0), (1.5, -7.6), (4.6, -6.2), (6.6, -2.8), (7.1, 0.8), (6.2, 4.4), (3.8, 6.9),
               (0.2, 7.8), (-3.0, 7.0)]          # v004 blade section (s outward, t up), cm: 15 cm face, rolled top
BUMPER_FACE = 7.1                               # forward-most s of the section
BUMPER_SET = 3.5                                # blade centreline ahead of the sheet-metal end (back face 0.5 cm proud)


def bumpers():
    """v004: '63-pattern blade bumpers (v003 was an 11 cm round tube that read as a pipe from behind),
    wrapping round the fender corners; rounded vertical guards."""
    out = []
    for y_face, name, sgn in ((NOSE - BUMPER_SET, "BUMPER_FRONT", -1), (TAIL + BUMPER_SET, "BUMPER_REAR", 1)):
        path = []
        xs = (-105, -101, -97, -92, -88, -70, -40, 0, 40, 70, 88, 92, 97, 101, 105)
        for x in xs:
            wrap = max(0.0, abs(x) - 88) / 17.0
            path.append((x, y_face - sgn * wrap * wrap * 26.0, 44.0))
        bm = bmesh.new()
        pts = [Vector(p) for p in path]
        rings = []
        for i, p in enumerate(pts):
            d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
            up = Vector((0, 0, 1)); side = up.cross(d).normalized()       # +Y on the straight span
            k_end = min(i, len(pts) - 1 - i)
            sc = (0.55, 0.82, 0.95)[k_end] if k_end < 3 else 1.0          # blade thins into the wrap tips
            rings.append([bm.verts.new(V(*(p + side * (sgn * s * sc) + up * (t * (0.5 + 0.5 * sc)))))
                          for s, t in BUMPER_PROF[:-1]])
        k = len(BUMPER_PROF) - 1
        for ra, rb in zip(rings, rings[1:]):
            for i in range(k):
                j = (i + 1) % k
                bm.faces.new([ra[i], ra[j], rb[j], rb[i]])
        bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces: f.material_index = 0
        b = new_obj(name, bm, [M["MI_V01_Chrome"]])
        # rounded vertical bumper guards standing proud of the blade
        bm = bmesh.new()
        face = y_face + sgn * BUMPER_FACE
        for x in (-34, 34):
            prof = [(x + u, face + sgn * (v + 0.2)) for u, v in rounded_rect(6.0, 6.4, 2.6, n=3)]
            bm_prism(bm, prof, "z", 34.0, 57.0)
        new_obj(name + "_GUARDS", bm, [M["MI_V01_Chrome"]])
        out.append(b)
    return out


def front_end():
    gh, gz0, gz1 = GRILLE
    # recessed dark grille back behind the full-width opening
    bm = bmesh.new()
    bm_box(bm, -gh - 1, NOSE + 2.5, gz0 - 1, gh + 1, NOSE + 8.0, gz1 + 1)
    grille = new_obj("GRILLE_BACK", bm, [M["MI_V01_Grille_Dark"]])
    bm = bmesh.new()
    nb = 10
    for i in range(nb):                                   # fine horizontal bars between the lamp pairs
        z = gz0 + 2.0 + (gz1 - gz0 - 4.0) * i / (nb - 1)
        bm_box(bm, -42.5, NOSE + 0.8, z - 0.45, 42.5, NOSE + 2.4, z + 0.45)
    for x in (-42.5, -21, 0, 21, 42.5):                  # vertical dividers
        bm_box(bm, x - 0.6, NOSE + 0.5, gz0, x + 0.6, NOSE + 2.4, gz1)
    t = 1.6                                               # chrome surround, proud of the face
    bm_box(bm, -gh - t, NOSE - 1.2, gz0 - t, gh + t, NOSE + 0.6, gz0)
    bm_box(bm, -gh - t, NOSE - 1.2, gz1, gh + t, NOSE + 0.6, gz1 + t)
    bm_box(bm, -gh - t, NOSE - 1.2, gz0, -gh, NOSE + 0.6, gz1)
    bm_box(bm, gh, NOSE - 1.2, gz0, gh + t, NOSE + 0.6, gz1)
    bars = new_obj("GRILLE_BARS", bm, [M["MI_V01_Chrome"]])
    # quad 5.75-in sealed beams: chrome bezel + lens, mounted in the grille opening
    bm = bmesh.new(); bm2 = bmesh.new()
    for x in LAMP_X:
        for sgn in (1, -1):
            cx, yf = sgn * x, NOSE + 0.6
            bm_revolve(bm, [(9.6, -2.2), (9.6, 0.8), (7.4, 0.8), (7.4, -2.2)], "y", (cx, yf, LAMP_Z), segs=32)
            bm_revolve(bm2, [(0.0, -1.6), (5.0, -1.9), (7.4, -0.6), (7.4, 2.0), (0.0, 2.0)], "y", (cx, yf, LAMP_Z), segs=32, close=False)
            bm_cylinder(bm, (cx, yf, LAMP_Z), "y", 10.4, 0.8, 4.5, segs=32)    # lamp bucket
    bezels = new_obj("HEADLAMP_BEZELS", bm, [M["MI_V01_Chrome"]])
    lenses = new_obj("HEADLAMP_LENSES", bm2, [M["MI_V01_Headlamp"]])
    return [grille, bars, bezels, lenses]


def rear_end():
    """v004: big round '63 tail lamps with a deep chrome bezel and the back-up lamp as the lower
    half-moon of the same lens (EVIDENCE: round tail lamps with half-moon lower lenses)."""
    R = TAIL_R
    bm = bmesh.new(); lens = bmesh.new()
    for sgn in (1, -1):
        cx, yr = sgn * TAIL_X, TAIL + 0.4
        bm_revolve(bm, [(R + 1.8, 2.6), (R + 1.8, -0.8), (R - 0.6, -0.8), (R - 0.6, 1.4), (R + 0.6, 2.6)], "y",
                   (cx, yr, TAIL_Z), segs=40)
        bm_revolve(bm, [(2.2, 1.0), (2.2, 2.4), (0.0, 2.6)], "y", (cx, yr, TAIL_Z), segs=20, close=False)   # centre boss
        bm_revolve(lens, [(0.0, 1.0), (4.0, 1.4), (R - 2.0, 1.2), (R - 0.6, 0.5), (R - 0.6, -3.0), (0.0, -3.0)], "y",
                   (cx, yr, TAIL_Z), segs=40, close=False)
    new_obj("TAILLAMP_BEZELS", bm, [M["MI_V01_Chrome"]])
    # split the lens: lower half-moon = clear back-up lamp
    zcut = (TAIL_Z - 0.42 * R) / 100.0
    geom = list(lens.verts) + list(lens.edges) + list(lens.faces)
    bmesh.ops.bisect_plane(lens, geom=geom, plane_co=(0, 0, zcut), plane_no=(0, 0, 1), dist=1e-6)
    low = lens.copy()
    bmesh.ops.delete(lens, geom=[f for f in lens.faces if f.calc_center_median().z < zcut], context="FACES")
    bmesh.ops.delete(low, geom=[f for f in low.faces if f.calc_center_median().z > zcut], context="FACES")
    for b_ in (lens, low):
        bmesh.ops.holes_fill(b_, edges=[e for e in b_.edges if e.is_boundary], sides=0)
        bmesh.ops.recalc_face_normals(b_, faces=b_.faces)
    new_obj("TAILLAMP_LENSES", lens, [M["MI_V01_Lens_Red"]])
    new_obj("BACKUP_LENSES", low, [M["MI_V01_Lens_Clear"]])
    bm = bmesh.new()
    bm_box(bm, -55, TAIL - 0.5, 84.0, 55, TAIL + 1.0, 85.4)                      # bright moulding under the deck lip
    bm_cylinder(bm, (0, TAIL - 0.5, 77.0), "y", 2.6, 0.0, 1.4, segs=24)       # trunk lock escutcheon (generic)
    new_obj("TRIM_REAR_PANEL", bm, [M["MI_V01_Chrome"]])


def hood_emblem(panels):
    """Small generic chrome crest at the hood front centre (E1: small front-centre emblem; no brand
    artwork). Parented to the hood so it opens with it."""
    hood = panels["HOOD"]
    y0 = HOOD_Y0 + 9.0
    z = interp(K["zc"], y0)
    bm = bmesh.new()
    poly = [(4.5 * math.cos(2 * math.pi * i / 20), y0 + 2.8 * math.sin(2 * math.pi * i / 20)) for i in range(20)]
    bm_prism(bm, poly, "z", z - 0.6, z + 0.9)
    o = new_obj("TRIM_HOOD_EMBLEM", bm, [M["MI_V01_Chrome"]])
    o.parent = hood
    o.matrix_parent_inverse = Matrix.Translation(-hood.location)
    return o


def side_details(panels):
    out = []
    # door handles (push-button type) and lower-body chrome strips
    bm = bmesh.new()
    for side in (1, -1):
        for y in (20, 88):
            x = side * (side_x(y, 85.5) + 1.0)
            bm_box(bm, x - 1.2, y - 7, 84.5, x + 1.2, y + 7, 87.0)
            bm_cylinder(bm, (x, y + 9, 85.7), "x", 1.1, -1.2, 1.8, segs=12)
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
        # vertices whose ray fell through a panel gap stay unprojected: interpolate them from neighbours
        me = strip.data
        rows = {}
        for v in me.vertices:
            rows.setdefault(round(v.co.z, 3), []).append(v)
        for row in rows.values():
            row.sort(key=lambda v: v.co.y)
            good = [v for v in row if abs(v.co.x) < 1.08]
            for v in row:
                if abs(v.co.x) >= 1.08 and good:
                    before = [g for g in good if g.co.y < v.co.y]
                    after = [g for g in good if g.co.y > v.co.y]
                    if before and after:
                        a, b = before[-1], after[0]
                        t = (v.co.y - a.co.y) / (b.co.y - a.co.y)
                        v.co.x = a.co.x + (b.co.x - a.co.x) * t
                    else:
                        v.co.x = (before or after)[-1 if before else 0].co.x
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
    mx = side_x(-34, 95.5)
    bm_cylinder(bm, (mx - 1.0, -34, 97.5), "x", 0.8, 0, 10, segs=10)
    bm_revolve(bm, [(0.5, 0.0), (5.5, 0.0), (5.5, 1.6), (0.5, 1.6)], "y", (mx + 9.5, -35, 99.5), segs=24)
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
    # v003: rounded shoulder + bulging sidewall (bias-ply 7.50-14 section)
    side_out = [(R - 0.4, w - 0.7), (R - 1.6, w), (R - 4.0, w + 0.35), (R - 8.0, w + 0.45), (rr + 7.0, w + 0.1),
                (rr + 3.5, w - 1.0), (rr + 1.0, w - 3.0)]
    prof = tread + side_out + [(rr, w - 3), (rr, -w + 3)] + [(r_, -z_) for r_, z_ in reversed(side_out)]
    bm_revolve(bm, prof, "x", (0, 0, 0), segs=64, mat=0)
    tyre_faces = list(bm.faces)
    # whitewall band on the outboard sidewall
    ww = bmesh.new()
    s = 1 if side > 0 else -1
    ww_prof = [(rr + 4.5, s * (w - 0.55)), (rr + 10.5, s * (w + 0.55)), (rr + 10.5, s * (w + 0.75)), (rr + 4.5, s * (w - 0.25))]
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
    bm_box(bm, -90, -60, 22, 90, 106, 26)       # cabin floor (stops ahead of the rear wheel houses)
    bm_box(bm, -60, 106, 22, 60, 160, 26)       # rear floor between the wheel houses
    bm_box(bm, -12, -60, 22, 12, 60, 34)
    bm_box(bm, -60, 130, 22, 60, 162, 60)       # rear seat riser, between the wheel houses
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
    for y0, name, hw in ((-2, "INT_SEAT_FRONT", 78), (94, "INT_SEAT_REAR", 60)):   # rear bench sits between the wheel houses
        bm = bmesh.new()
        bm_box(bm, -hw, y0, 32, hw, y0 + 52, 46)              # cushion
        bm_box(bm, -hw, y0 + 44, 46, hw, y0 + 58, 96)         # backrest
        bm_box(bm, -hw, y0 + 40, 30, hw, y0 + 58, 46)
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
    bm_box(bm, -60, -236, 26, 60, -60, 30)              # engine-bay splash pan (inboard of the wheel houses)
    objs.append(new_obj("INT_ENGINE_BAY", bm, [M["MI_V01_Interior_Dark"]]))
    bm = bmesh.new()
    bm_box(bm, -60, -234, 26, 60, -228, 79)             # radiator support (stays below the hood lip, z 84)
    bm_box(bm, -61, -228, 26, -58, -64, 80)             # inner fender walls (inboard of the tyres)
    bm_box(bm, 58, -228, 26, 61, -64, 80)
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
    bm_box(bm, -66, AXLE_F - 8, 28, 66, AXLE_F + 8, 36)                   # front cross-member
    for sx in (-52, 52):
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
        xin = side * (side_x((y0 + y1) / 2, 66) - SHELL_T - 1.0)
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
    by = 14.0                       # E1: between M and P, forward of the roof centre
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
    ay = 55.0; az = interp(K["zc"], ay)   # E1: dark dot near the roof centre
    bm_cylinder(bm, (0, ay, az - 0.5), "z", 2.0, 0, 2.5, segs=16)
    bm_cylinder(bm, (0, ay, az + 1.5), "z", 0.35, 0, 48, segs=8)   # quarter-wave VHF whip, APPROXIMATE
    objs.append(new_obj("POLICE_ANTENNA", bm, [M["MI_V01_Chrome"]]))
    # v004: driver-side A-pillar spotlight (Unity-type, period-typical for US patrol cars; APPROXIMATE —
    # not visible in E1). Pillar bracket + swivel arm + 6.5-in lamp head aimed forward.
    sy, sz = SPOT_Y, SPOT_Z
    sx = side_x(sy, sz)
    bm = bmesh.new()
    bm_cylinder(bm, (sx - 0.5, sy, sz), "x", 2.2, 0.0, 2.2, segs=16)            # pillar boss
    bm_cylinder(bm, (sx, sy, sz), "x", 0.9, 0.0, 8.5, segs=12)                  # swivel arm
    hx = sx + 8.5
    bm_revolve(bm, [(0.0, 9.5), (3.0, 9.2), (5.4, 8.0), (7.0, 5.8), (7.8, 3.0), (8.0, 0.0), (0.0, 0.0)], "y",
               (hx, sy - 2.0, sz), segs=32, close=False)                           # lamp shell (rounded rear bowl)
    bm_revolve(bm, [(8.3, 0.2), (8.3, -1.5), (7.0, -1.5), (7.0, 0.2)], "y", (hx, sy - 2.0, sz), segs=32)  # bezel
    objs.append(new_obj("POLICE_SPOTLIGHT", bm, [M["MI_V01_Chrome"]]))
    bm = bmesh.new()
    bm_revolve(bm, [(0.0, -2.2), (4.0, -2.0), (7.0, -1.2), (7.0, -0.2), (0.0, -0.2)], "y", (hx, sy - 2.0, sz),
               segs=32, close=False)
    objs.append(new_obj("POLICE_SPOTLIGHT_LENS", bm, [M["MI_V01_Headlamp"]]))
    # licence plates (FICTIONALISED) front + rear
    for y, nm, flip in ((PLATE_Y_F, "PLATE_FRONT", False), (PLATE_Y_R, "PLATE_REAR", True)):
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
    bm = bmesh.new(); bm_box(bm, -108, NOSE - 14, 34, 108, NOSE + 2, 57); c = new_obj("UCX_BODY_03", bm, [M["MI_V01_Undercoat"]])
    bm = bmesh.new(); bm_box(bm, -108, TAIL - 2, 34, 108, TAIL + 14, 57); d = new_obj("UCX_BODY_04", bm, [M["MI_V01_Undercoat"]])
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

    body = build_body()
    panels, glass = cut_and_split(body)
    if PREVIEW:
        objs = [body] + list(panels.values()) + list(glass.values())
        for o in objs:
            cleanup(o); box_uv(o); smooth(o)
        ws = wheels()
        export(os.path.join(OUT, "PREVIEW_shell.glb"), objs + list(ws.values()))
        return
    houses = wheel_houses()
    front_end()
    rear_end()
    chrome = bumpers() + side_details(panels) + [hood_emblem(panels)]
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
    empty("SOCKET_BEACON", (0, 14, interp(K["zc"], 14)), root)
    empty("SOCKET_ANTENNA", (0, 55, interp(K["zc"], 55)), root)
    empty("SOCKET_ROOF_SIGN", (0, 48, interp(K["zc"], 48)), root)
    empty("SOCKET_PLATE_F", (0, PLATE_Y_F, 43.6), root)
    empty("SOCKET_PLATE_R", (0, PLATE_Y_R, 43.6), root)
    empty("SOCKET_SPOTLIGHT_L", (side_x(SPOT_Y, SPOT_Z), SPOT_Y, SPOT_Z), root)
    empty("SOCKET_SIREN", (side_x(-200, 80) - 6, -200, 80), root)
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
