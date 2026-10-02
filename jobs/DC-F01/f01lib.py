"""Geometry, material, texture and export helpers for DC-F01 building assemblies.

Everything here is deterministic: no wall-clock time or unseeded randomness, so a clean
rebuild reproduces the same meshes and textures.

Conventions
- Blender metres, Z up. glTF export converts to Y up; UE 5.8 imports glTF metres as cm.
- Map-aligned buildings: +X east, +Y north. Pivot at footprint centre, grade level (Z = 0).
- Every primitive emits CLOSED shells with outward normals so the stage-A QA checks
  (signed volume >= 0, no zero-area faces) hold by construction.
- A facade frame is (origin, u, n): origin = left end of the facade at grade when seen from
  outside, u = unit vector to the viewer's right along the facade, n = outward normal.
  Local coordinates (a, b, c): a along u, b along n (b = 0 is the facade plane, b < 0 is into
  the building), c = height.  For a CCW footprint, edge i gives u = edge direction and
  n = (u.y, -u.x).
"""
import math
import os

import numpy as np

import bpy
import bmesh
from mathutils import Vector

EPS = 1e-6


# ----------------------------------------------------------------------------- frames

class Frame:
    """Horizontal facade frame. a along u, b along outward n, c = world Z."""

    def __init__(self, origin, u):
        ux, uy = u
        ln = math.hypot(ux, uy)
        self.o = (origin[0], origin[1])
        self.u = (ux / ln, uy / ln)
        self.n = (self.u[1], -self.u[0])

    def p(self, a, b, c):
        return (self.o[0] + self.u[0] * a + self.n[0] * b,
                self.o[1] + self.u[1] * a + self.n[1] * b,
                c)

    @staticmethod
    def from_edge(p0, p1):
        f = Frame(p0, (p1[0] - p0[0], p1[1] - p0[1]))
        f.length = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        return f


WORLD = Frame((0.0, 0.0), (1.0, 0.0))   # a = x, b = -y, c = z  (n points -Y)


# ----------------------------------------------------------------------------- mesh accumulator

class Mesh:
    """Accumulates closed shells: vertices, faces, per-face material and UV mode."""

    def __init__(self, name):
        self.name = name
        self.verts = []
        self.faces = []      # (vertex index tuple, material name, uv spec)

    # -- raw shell
    def shell(self, verts, faces, mat, uv=None):
        base = len(self.verts)
        self.verts.extend(tuple(float(c) for c in v) for v in verts)
        for f in faces:
            self.faces.append((tuple(base + i for i in f), mat, uv))

    def extend(self, other):
        base = len(self.verts)
        self.verts.extend(other.verts)
        for f, m, uv in other.faces:
            self.faces.append((tuple(base + i for i in f), m, uv))

    @property
    def tri_count(self):
        return sum(len(f) - 2 for f, _, _ in self.faces)

    # -- primitives ---------------------------------------------------------
    def lbox(self, fr, a0, a1, b0, b1, c0, c1, mat, uv=None):
        """Box in facade-local coordinates (a, b, c). Skips empty boxes."""
        if a1 - a0 < EPS or b1 - b0 < EPS or c1 - c0 < EPS:
            return
        P = fr.p
        v = [P(a0, b0, c0), P(a1, b0, c0), P(a1, b1, c0), P(a0, b1, c0),
             P(a0, b0, c1), P(a1, b0, c1), P(a1, b1, c1), P(a0, b1, c1)]
        # Frame (u, n, z) is left-handed when n = (u.y, -u.x) ... check orientation:
        # u x n = (ux, uy, 0) x (uy, -ux, 0) = (0, 0, -ux^2 - uy^2) = -z, so (u, n, z) is
        # left-handed and face winding must be mirrored relative to an (x, y, z) box.
        faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        faces = [tuple(reversed(f)) for f in faces]
        self.shell(v, faces, mat, uv)

    def box(self, x0, x1, y0, y1, z0, z1, mat, uv=None):
        if x1 - x0 < EPS or y1 - y0 < EPS or z1 - z0 < EPS:
            return
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        self.shell(v, faces, mat, uv)

    def prism(self, poly, z0, z1, mat, mat_top=None, mat_bottom=None, uv=None):
        """Extrude a CCW XY polygon from z0 to z1 (n-gon caps)."""
        poly = _clean_poly(poly)
        if polygon_area(poly) < 0:
            poly = poly[::-1]
        n = len(poly)
        v = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
        base = len(self.verts)
        self.verts.extend(v)
        self.faces.append((tuple(base + i for i in reversed(range(n))), mat_bottom or mat, uv))
        self.faces.append((tuple(base + n + i for i in range(n)), mat_top or mat, uv))
        for i in range(n):
            j = (i + 1) % n
            self.faces.append(((base + i, base + j, base + n + j, base + n + i), mat, uv))

    def lprism(self, fr, poly_ac, b0, b1, mat, uv=None):
        """Extrude a polygon drawn in the facade (a, c) plane from b0 to b1 along n."""
        poly = _clean_poly(poly_ac)
        if polygon_area(poly) < 0:
            poly = poly[::-1]
        n = len(poly)
        front = [fr.p(a, b1, c) for a, c in poly]
        back = [fr.p(a, b0, c) for a, c in poly]
        base = len(self.verts)
        self.verts.extend(front + back)
        # (a, c) CCW seen from +n (outside) -> front cap winding as listed faces +n.
        # Frame handedness: looking from +n, +a is to the right and +c up, so CCW in (a, c)
        # is CCW as seen by the viewer -> outward normal +n. Correct.
        self.faces.append((tuple(base + i for i in range(n)), mat, uv))
        self.faces.append((tuple(base + n + i for i in reversed(range(n))), mat, uv))
        for i in range(n):
            j = (i + 1) % n
            self.faces.append(((base + j, base + i, base + n + i, base + n + j), mat, uv))

    def sweep(self, path, profile, mat, closed=True, z=0.0, uv=None):
        """Sweep a closed cross-section along a horizontal path.

        path: list of XY points; for closed=True it must be CCW (outward = right side).
        profile: CCW list of (out, up) points in the section plane (out along the path's
        outward normal, up = +Z, relative to z)."""
        path = _clean_poly(path) if closed else list(path)
        if closed and polygon_area(path) < 0:
            path = path[::-1]
        prof = list(profile)
        if polygon_area(prof) < 0:
            prof = prof[::-1]
        npth, npr = len(path), len(prof)
        rings = []
        for i in range(npth):
            if closed:
                p_prev, p, p_next = path[i - 1], path[i], path[(i + 1) % npth]
            else:
                p = path[i]
                p_prev = path[i - 1] if i > 0 else None
                p_next = path[i + 1] if i < npth - 1 else None
            normals = []
            if p_prev is not None:
                normals.append(_seg_normal(p_prev, p))
            if p_next is not None:
                normals.append(_seg_normal(p, p_next))
            nx = sum(n[0] for n in normals)
            ny = sum(n[1] for n in normals)
            ln = math.hypot(nx, ny)
            nx, ny = nx / ln, ny / ln
            cosh = nx * normals[0][0] + ny * normals[0][1]
            scale = 1.0 / max(cosh, 0.2)
            ring = [(p[0] + nx * o * scale, p[1] + ny * o * scale, z + up) for o, up in prof]
            rings.append(ring)
        base = len(self.verts)
        for r in rings:
            self.verts.extend(r)
        nseg = npth if closed else npth - 1
        for i in range(nseg):
            j = (i + 1) % npth
            for k in range(npr):
                k2 = (k + 1) % npr
                a0, a1 = base + i * npr + k, base + i * npr + k2
                b0, b1 = base + j * npr + k, base + j * npr + k2
                # profile CCW in (out, up) when looking along +path direction from behind;
                # winding chosen so faces point away from the section interior.
                self.faces.append(((a0, b0, b1, a1), mat, uv))
        if not closed:
            self.faces.append((tuple(base + k for k in range(npr)), mat, uv))
            last = base + (npth - 1) * npr
            self.faces.append((tuple(last + k for k in reversed(range(npr))), mat, uv))

    def lathe(self, cx, cy, profile, segments, mat, flutes=0, flute_depth=0.0,
              flute_zone=None, uv='cyl', z_off=0.0, angle0=0.0):
        """Solid of revolution about the vertical axis through (cx, cy).

        profile: list of (r, z) from bottom to top. Ends with r > 0 are capped.
        flutes: number of concave flutes applied to rings whose z lies in flute_zone."""
        segs = segments
        base = len(self.verts)
        uvs = ('cyl', cx, cy)
        for r, zz in profile:
            fluted = flutes and flute_zone and flute_zone[0] - EPS <= zz <= flute_zone[1] + EPS
            for s in range(segs):
                t = angle0 + 2 * math.pi * s / segs
                rr = r
                if fluted:
                    ph = (s / segs) * flutes
                    frac = ph - math.floor(ph)
                    rr = r - flute_depth * max(0.0, math.sin(math.pi * frac)) ** 1.0
                self.verts.append((cx + rr * math.cos(t), cy + rr * math.sin(t), z_off + zz))
        npf = len(profile)
        for i in range(npf - 1):
            for s in range(segs):
                s2 = (s + 1) % segs
                a0, a1 = base + i * segs + s, base + i * segs + s2
                b0, b1 = base + (i + 1) * segs + s, base + (i + 1) * segs + s2
                if profile[i][0] < EPS and profile[i + 1][0] < EPS:
                    continue
                if profile[i][0] < EPS:
                    self.faces.append(((a0, b1, b0), mat, uvs))
                elif profile[i + 1][0] < EPS:
                    self.faces.append(((a0, a1, b0), mat, uvs))
                else:
                    self.faces.append(((a0, a1, b1, b0), mat, uvs))
        if profile[0][0] > EPS:
            self.faces.append((tuple(base + s for s in reversed(range(segs))), mat, uvs))
        if profile[-1][0] > EPS:
            top = base + (npf - 1) * segs
            self.faces.append((tuple(top + s for s in range(segs)), mat, uvs))


def _seg_normal(p0, p1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy)
    return (dy / ln, -dx / ln)


def _clean_poly(poly):
    out = []
    for p in poly:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-7:
            out.append((float(p[0]), float(p[1])))
    if len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < 1e-7:
        out.pop()
    return out


def polygon_area(poly):
    s = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return s / 2


def offset_polygon(poly, d):
    """Offset a CCW polygon outward by d (negative = inward), mitered."""
    poly = _clean_poly(poly)
    if polygon_area(poly) < 0:
        poly = poly[::-1]
    n = len(poly)
    out = []
    for i in range(n):
        p_prev, p, p_next = poly[i - 1], poly[i], poly[(i + 1) % n]
        n0 = _seg_normal(p_prev, p)
        n1 = _seg_normal(p, p_next)
        nx, ny = n0[0] + n1[0], n0[1] + n1[1]
        ln = math.hypot(nx, ny)
        nx, ny = nx / ln, ny / ln
        cosh = nx * n0[0] + ny * n0[1]
        out.append((p[0] + nx * d / cosh, p[1] + ny * d / cosh))
    return out


def arc_points(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


# ----------------------------------------------------------------------------- facade walls

def wall_with_openings(m, fr, a0, a1, c0, c1, depth, openings, mat, uv=None):
    """Solid wall slab (b in [-depth, 0]) over a in [a0, a1], c in [c0, c1] with
    rectangular through-openings [(oa0, oa1, oc0, oc1), ...]. The slab is decomposed into
    maximal solid rectangles (closed boxes), so every reveal is real geometry."""
    ab = {a0, a1}
    cb = {c0, c1}
    ops = []
    for (oa0, oa1, oc0, oc1) in openings:
        oa0, oa1 = max(oa0, a0), min(oa1, a1)
        oc0, oc1 = max(oc0, c0), min(oc1, c1)
        if oa1 - oa0 > EPS and oc1 - oc0 > EPS:
            ops.append((oa0, oa1, oc0, oc1))
            ab.update((oa0, oa1))
            cb.update((oc0, oc1))
    A = sorted(_uniq(ab))
    C = sorted(_uniq(cb))
    na, nc = len(A) - 1, len(C) - 1
    solid = np.ones((na, nc), dtype=bool)
    for (oa0, oa1, oc0, oc1) in ops:
        for i in range(na):
            am = (A[i] + A[i + 1]) / 2
            if not (oa0 < am < oa1):
                continue
            for k in range(nc):
                cm = (C[k] + C[k + 1]) / 2
                if oc0 < cm < oc1:
                    solid[i, k] = False
    # greedy merge: vertical runs first, then extend horizontally while identical
    used = np.zeros_like(solid)
    for i in range(na):
        for k in range(nc):
            if not solid[i, k] or used[i, k]:
                continue
            k2 = k
            while k2 + 1 < nc and solid[i, k2 + 1] and not used[i, k2 + 1]:
                k2 += 1
            i2 = i
            while i2 + 1 < na and all(solid[i2 + 1, kk] and not used[i2 + 1, kk] for kk in range(k, k2 + 1)):
                i2 += 1
            used[i:i2 + 1, k:k2 + 1] = True
            m.lbox(fr, A[i], A[i2 + 1], -depth, 0.0, C[k], C[k2 + 1], mat, uv)


def _uniq(vals, tol=1e-5):
    out = []
    for v in sorted(vals):
        if not out or abs(v - out[-1]) > tol:
            out.append(v)
    return out


def arch_fillers(m, fr, a0, a1, c_spring, depth, mat, segs=12, uv=None):
    """Fill the two corners between a semicircular arch and its bounding rectangle.
    The opening itself must be cut as (a0, a1, c_lo, c_spring + r)."""
    r = (a1 - a0) / 2
    am = (a0 + a1) / 2
    top = c_spring + r
    # left corner: from (a0, c_spring) up to (a0, top), across to (am, top), down the arc
    pts_l = [(a0, c_spring), (a0, top), (am, top)]
    for i in range(1, segs):
        t = math.pi / 2 + (math.pi / 2) * i / segs   # from 90deg (top) to 180deg (left)
        pts_l.append((am + r * math.cos(t), c_spring + r * math.sin(t)))
    m.lprism(fr, pts_l, -depth, 0.0, mat, uv)
    # right corner: from (a1, c_spring) up the arc to (am, top), then to (a1, top)
    pts_r = [(a1, c_spring)]
    for i in range(1, segs):
        t = (math.pi / 2) * i / segs                   # from 0deg (right) to 90deg (top)
        pts_r.append((am + r * math.cos(t), c_spring + r * math.sin(t)))
    pts_r += [(am, top), (a1, top)]
    m.lprism(fr, pts_r, -depth, 0.0, mat, uv)


# ----------------------------------------------------------------------------- windows

def window_unit(m, fr, a0, a1, c0, c1, depth, lod, mats, cols=2, rows=2, frame_w=0.07,
                glass_set_back=0.06, mullion_w=0.05, transom_at=None, glass_slot=0):
    """Frame + glazing set into an opening whose reveal runs from b = 0 to b = -depth.

    mats: dict with 'frame' and 'glass' (list of glass material names, picked by glass_slot)."""
    fmat = mats['frame']
    gmat = mats['glass'][glass_slot % len(mats['glass'])]
    bf1 = -depth + glass_set_back + 0.05   # frame front face
    bf0 = -depth + 0.005                   # frame back (just proud of the core face)
    bg = -depth + glass_set_back           # glass plane
    w = a1 - a0
    h = c1 - c0
    if lod >= 2:
        m.lbox(fr, a0, a1, bg - 0.01, bg, c0, c1, gmat)
        return
    fw = min(frame_w, w * 0.2, h * 0.2)
    # outer frame
    m.lbox(fr, a0, a1, bf0, bf1, c0, c0 + fw, fmat)
    m.lbox(fr, a0, a1, bf0, bf1, c1 - fw, c1, fmat)
    m.lbox(fr, a0, a0 + fw, bf0, bf1, c0 + fw, c1 - fw, fmat)
    m.lbox(fr, a1 - fw, a1, bf0, bf1, c0 + fw, c1 - fw, fmat)
    # glass (thin closed slab)
    m.lbox(fr, a0 + fw, a1 - fw, bg - 0.012, bg, c0 + fw, c1 - fw, gmat)
    if lod >= 1:
        return
    mw = min(mullion_w, w * 0.08)
    iw0, iw1 = a0 + fw, a1 - fw
    ih0, ih1 = c0 + fw, c1 - fw
    for i in range(1, cols):
        x = iw0 + (iw1 - iw0) * i / cols
        m.lbox(fr, x - mw / 2, x + mw / 2, bg, bg + 0.035, ih0, ih1, fmat)
    rows_z = []
    if transom_at is not None:
        rows_z.append(ih0 + (ih1 - ih0) * transom_at)
    else:
        rows_z = [ih0 + (ih1 - ih0) * k / rows for k in range(1, rows)]
    for z in rows_z:
        m.lbox(fr, iw0, iw1, bg, bg + 0.045, z - mw / 2, z + mw / 2, fmat)


# ----------------------------------------------------------------------------- columns

def doric_profile(height, d_lower, base=True, entasis=0.17):
    """(r, z) profile of a Roman/Renaissance Doric column of total height `height`.
    Proportions follow Vignola-style rules (module = lower radius); `entasis` is the
    upper-diameter reduction as a fraction."""
    R = d_lower / 2
    M = R  # module
    pts = []
    z = 0.0
    if base:
        pl = 1.0 * M          # plinth height (square plinth added separately)
        torus = 0.75 * M
        pts += [(R * 1.32, 0.0), (R * 1.32, torus * 0.15), (R * 1.36, torus * 0.5), (R * 1.30, torus * 0.85),
                (R * 1.10, torus * 0.95), (R * 1.06, torus)]
        z = torus
    shaft_h = height - z - 1.0 * M      # capital ~ 1 module
    top_r = R * (1 - entasis)
    nseg = 8
    for i in range(nseg + 1):
        t = i / nseg
        # entasis: straight lower third, curved taper above
        k = 0.0 if t < 1 / 3 else ((t - 1 / 3) / (2 / 3)) ** 1.6
        pts.append((R - (R - top_r) * k, z + shaft_h * t))
    zc = z + shaft_h
    # astragal, necking, echinus, abacus (abacus emitted as a separate box by caller)
    pts += [(top_r * 1.08, zc + 0.02 * M), (top_r * 1.08, zc + 0.10 * M), (top_r * 1.0, zc + 0.14 * M),
            (top_r * 1.0, zc + 0.40 * M), (top_r * 1.06, zc + 0.44 * M), (top_r * 1.30, zc + 0.62 * M),
            (top_r * 1.34, zc + 0.68 * M), (top_r * 1.34, zc + 0.70 * M)]
    return pts, z, zc, top_r


# ----------------------------------------------------------------------------- object creation

def to_object(mesh, collection, mat_lookup, uv_tiles):
    """Create a Blender object from a Mesh, with material slots in a stable order and
    world-space box/cylindrical UVs scaled per material (uv_tiles[mat] = metres per UV unit)."""
    me = bpy.data.meshes.new(mesh.name)
    bm = bmesh.new()
    bverts = [bm.verts.new(v) for v in mesh.verts]
    bm.verts.ensure_lookup_table()
    mats_used = []
    for _, mname, _ in mesh.faces:
        if mname not in mats_used:
            mats_used.append(mname)
    mats_used.sort()
    mindex = {n: i for i, n in enumerate(mats_used)}
    uvl = bm.loops.layers.uv.new("UVMap")
    face_specs = []
    for idx, mname, uvspec in mesh.faces:
        try:
            f = bm.faces.new([bverts[i] for i in idx])
        except ValueError:
            # duplicate face (identical vertex set) - skip; can only happen for exactly
            # coincident shells, which the generators avoid
            continue
        f.material_index = mindex[mname]
        face_specs.append((f, mname, uvspec))
    bm.normal_update()
    for f, mname, uvspec in face_specs:
        tile = uv_tiles.get(mname, 2.0)
        _uv_face(f, uvl, tile, uvspec)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(mesh.name, me)
    for n in mats_used:
        obj.data.materials.append(mat_lookup[n])
    collection.objects.link(obj)
    return obj


def _uv_face(f, uvl, tile, uvspec):
    n = f.normal
    if isinstance(uvspec, tuple) and uvspec and uvspec[0] == 'cyl':
        _, cx, cy = uvspec
        if abs(n.z) > 0.7:
            for l in f.loops:
                co = l.vert.co
                l[uvl].uv = ((co.x - cx) / tile, (co.y - cy) / tile)
            return
        # angle-continuous around the face centre to avoid wrap seams inside one face
        c = f.calc_center_median()
        ac = math.atan2(c.y - cy, c.x - cx)
        rr = max(math.hypot(c.x - cx, c.y - cy), 0.05)
        for l in f.loops:
            co = l.vert.co
            ang = math.atan2(co.y - cy, co.x - cx)
            d = (ang - ac + math.pi) % (2 * math.pi) - math.pi
            l[uvl].uv = ((ac + d) * rr / tile, co.z / tile)
        return
    if abs(n.z) >= 0.70710678:
        for l in f.loops:
            co = l.vert.co
            l[uvl].uv = (co.x / tile, co.y / tile)
        return
    # wall-like: u along the horizontal tangent, v = z
    tx, ty = -n.y, n.x
    ln = math.hypot(tx, ty)
    tx, ty = tx / ln, ty / ln
    for l in f.loops:
        co = l.vert.co
        l[uvl].uv = ((co.x * tx + co.y * ty) / tile, co.z / tile)


def convex_hull_object(name, points, collection, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uvl = bm.loops.layers.uv.new("UVMap")
    bm.normal_update()
    for f in bm.faces:
        _uv_face(f, uvl, 4.0, None)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj


def socket(name, location, collection, rotation_z=0.0, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'ARROWS'
    e.empty_display_size = 0.5
    e.location = location
    e.rotation_euler = (0.0, 0.0, rotation_z)
    collection.objects.link(e)
    if parent is not None:
        e.parent = parent
    return e


def mesh_stats(obj):
    me = obj.data
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    lo = [min(v.co[i] for v in me.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in me.vertices) for i in range(3)]
    zero = sum(1 for p in me.polygons if p.area < 1e-10)
    return {"tris": tris, "verts": len(me.vertices), "bbox_min": lo, "bbox_max": hi,
            "size_m": [hi[i] - lo[i] for i in range(3)], "zero_area_faces": zero}


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


# ----------------------------------------------------------------------------- architectural helpers

def stairs(m, fr, a0, a1, b_wall, n_steps, rise, tread, z_top, mat, cheek=None):
    """Straight flight descending outward from a landing at b_wall (top step nosing) to grade.
    Step k (0 = top) occupies b in [b_wall + k*tread, b_wall + (k+1)*tread], top at z_top - k*rise.
    cheek: optional (width, height_above_nosing, mat) for side cheek walls."""
    for k in range(n_steps):
        top = z_top - k * rise
        if top <= EPS:
            break
        m.lbox(fr, a0, a1, b_wall + k * tread, b_wall + (k + 1) * tread, 0.0, top, mat)
    if cheek:
        w, h, cmat = cheek
        b1 = b_wall + n_steps * tread
        for (x0, x1) in ((a0 - w, a0), (a1, a1 + w)):
            m.lbox(fr, x0, x1, b_wall - 0.01, b1, 0.0, z_top + h, cmat)


def balustrade(m, fr, a0, a1, b0, b1, z0, height, spacing, lod, mat, pedestal_at=(), ped_w=0.6):
    """Plinth + balusters + handrail along a facade run. pedestal_at: a-positions of solid dies."""
    plinth_h = 0.16 * height
    rail_h = 0.14 * height
    m.lbox(fr, a0, a1, b0, b1, z0, z0 + plinth_h, mat)
    m.lbox(fr, a0 - 0.02, a1 + 0.02, b0 - 0.02, b1 + 0.02, z0 + height - rail_h, z0 + height, mat)
    peds = sorted(pedestal_at)
    for p in peds:
        m.lbox(fr, p - ped_w / 2, p + ped_w / 2, b0 - 0.03, b1 + 0.03, z0 + plinth_h, z0 + height - rail_h, mat)
    bh = height - plinth_h - rail_h
    if lod >= 2:
        # solid parapet reading at distance
        m.lbox(fr, a0, a1, b0 + 0.05, b1 - 0.05, z0 + plinth_h, z0 + height - rail_h, mat)
        return
    bw = (b1 - b0) * 0.7
    bc = (b0 + b1) / 2
    n = int((a1 - a0) / spacing)
    for i in range(n):
        a = a0 + (i + 0.5) * (a1 - a0) / n
        if any(abs(a - p) < ped_w / 2 + spacing * 0.4 for p in peds):
            continue
        if lod == 1:
            m.lbox(fr, a - bw * 0.3, a + bw * 0.3, bc - bw * 0.3, bc + bw * 0.3, z0 + plinth_h, z0 + plinth_h + bh, mat)
            continue
        x, y, _ = fr.p(a, bc, 0)
        r = bw / 2
        prof = [(r * 0.62, 0.0), (r * 0.62, 0.08 * bh), (r * 0.42, 0.14 * bh), (r * 0.95, 0.38 * bh),
                (r * 0.55, 0.62 * bh), (r * 0.34, 0.74 * bh), (r * 0.5, 0.84 * bh), (r * 0.62, 0.9 * bh), (r * 0.62, bh)]
        m.lathe(x, y, prof, 8, mat, z_off=z0 + plinth_h, angle0=math.pi / 8)


def fluted_pilaster(m, fr, ac, width, c0, c1, b_back, proj, flutes, lod, mat, cap_h=0.0, base_h=0.0):
    """Flat pilaster centred at a = ac standing proud of the wall plane b_back by `proj`.
    LOD0 carves `flutes` channels as separate fillets (real relief), LOD1+ plain."""
    a0, a1 = ac - width / 2, ac + width / 2
    fl_depth = min(0.03, proj * 0.4)
    body_front = b_back + proj - (fl_depth if (lod == 0 and flutes) else 0.0)
    m.lbox(fr, a0, a1, b_back - 0.02, body_front, c0 + base_h, c1 - cap_h, mat)
    if lod == 0 and flutes:
        nf = flutes
        fil = width * 0.14 / (nf + 1) * 2.0
        fil = min(fil, width / (2 * nf + 1))
        gap = (width - (nf + 1) * fil) / nf
        x = a0
        for i in range(nf + 1):
            m.lbox(fr, x, x + fil, body_front, b_back + proj, c0 + base_h + 0.1, c1 - cap_h - 0.1, mat)
            x += fil + gap
        # solid top/bottom stops of the flutes
        m.lbox(fr, a0, a1, body_front, b_back + proj, c0 + base_h, c0 + base_h + 0.1, mat)
        m.lbox(fr, a0, a1, body_front, b_back + proj, c1 - cap_h - 0.1, c1 - cap_h, mat)
    if base_h > 0:
        m.lbox(fr, a0 - 0.04, a1 + 0.04, b_back - 0.02, b_back + proj + 0.04, c0, c0 + base_h, mat)
    if cap_h > 0:
        m.lbox(fr, a0 - 0.05, a1 + 0.05, b_back - 0.02, b_back + proj + 0.05, c1 - cap_h, c1, mat)


def incised_band(m, fr, a0, a1, c0, c1, b_face, depth, grooves, mat):
    """Shallow incised ornament: a thin slab proud of b_face with groove openings that
    expose the surface behind (grooves = list of (a0, a1, c0, c1))."""
    wall_with_openings(Mesh_proxy(m, fr, b_face + depth), WORLD_PROXY, a0, a1, c0, c1, depth, grooves, mat)


class Mesh_proxy:
    """Shift a facade frame outward so wall_with_openings can build a slab at another plane."""

    def __init__(self, m, fr, b_shift):
        self.m, self.fr, self.b_shift = m, fr, b_shift

    def lbox(self, _fr, a0, a1, b0, b1, c0, c1, mat, uv=None):
        self.m.lbox(self.fr, a0, a1, b0 + self.b_shift, b1 + self.b_shift, c0, c1, mat, uv)


WORLD_PROXY = None


def relief_standin(m, fr, a0, a1, c0, c1, b_back, seed, mat, frame_mat=None, lod=0):
    """Labelled simplified stand-in for figural relief (rights unconfirmed): a sunk panel with
    2-3 abstract figure masses in low relief. Never a likeness."""
    import random
    rnd = random.Random(seed)
    w, h = a1 - a0, c1 - c0
    fm = frame_mat or mat
    # frame moulding around the sunk field
    fw = 0.08
    m.lbox(fr, a0 - fw, a1 + fw, b_back, b_back + 0.06, c0 - fw, c0, fm)
    m.lbox(fr, a0 - fw, a1 + fw, b_back, b_back + 0.06, c1, c1 + fw, fm)
    m.lbox(fr, a0 - fw, a0, b_back, b_back + 0.06, c0, c1, fm)
    m.lbox(fr, a1, a1 + fw, b_back, b_back + 0.06, c0, c1, fm)
    if lod >= 1:
        return
    nfig = rnd.choice((2, 3, 3))
    for i in range(nfig):
        cx = a0 + w * (i + 0.5) / nfig + rnd.uniform(-0.08, 0.08) * w
        fh = h * rnd.uniform(0.62, 0.86)
        fw2 = w * rnd.uniform(0.11, 0.16)
        z = c0 + 0.06
        pr = rnd.uniform(0.025, 0.05)
        # legs / robe
        m.lbox(fr, cx - fw2 * 0.5, cx + fw2 * 0.5, b_back, b_back + pr, z, z + fh * 0.48, mat)
        # torso
        lean = rnd.uniform(-0.04, 0.04) * w
        m.lbox(fr, cx - fw2 * 0.62 + lean, cx + fw2 * 0.62 + lean, b_back, b_back + pr * 1.2,
               z + fh * 0.48, z + fh * 0.82, mat)
        # head
        m.lbox(fr, cx - fw2 * 0.26 + lean * 1.4, cx + fw2 * 0.26 + lean * 1.4, b_back, b_back + pr * 1.3,
               z + fh * 0.85, z + fh * 0.98, mat)
        # one raised arm
        if rnd.random() < 0.6:
            s = rnd.choice((-1, 1))
            m.lbox(fr, cx + s * fw2 * 0.6 + lean, cx + s * fw2 * 1.1 + lean, b_back, b_back + pr,
                   z + fh * 0.62, z + fh * 0.9, mat)


def text_inscription(m, fr, lines, ac, c_top, cap_h, line_gap, b_face, mat, font_path, depth=0.004,
                     max_width=None):
    """Carved inscription stand-in: letters as thin solids (darker 'incised' material) on the
    face plane. Text is verified wording; typeface is a stand-in (Liberation Serif caps)."""
    font = bpy.data.fonts.load(font_path, check_existing=True)
    c = c_top
    for line in lines:
        cu = bpy.data.curves.new("insc", 'FONT')
        cu.body = line
        cu.font = font
        cu.size = cap_h / 0.66
        cu.extrude = depth / 2
        cu.align_x = 'CENTER'
        cu.resolution_u = 2
        cu.fill_mode = 'BOTH'
        ob = bpy.data.objects.new("insc", cu)
        bpy.context.scene.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get()
        me = ob.evaluated_get(dg).to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        # drop slivers that would fail the zero-area check
        bad = [f for f in bm.faces if f.calc_area() < 1e-9]
        if bad:
            bmesh.ops.delete(bm, geom=bad, context='FACES')
        xs = [v.co.x for v in bm.verts]
        width = (max(xs) - min(xs)) if xs else 0.0
        scale = 1.0
        if max_width and width > max_width:
            scale = max_width / width
        verts = []
        for v in bm.verts:
            x, y, z = v.co
            verts.append(fr.p(ac + x * scale, b_face + depth / 2 + z, c - cap_h + y * scale))
        bm.verts.index_update()
        faces = [tuple(v.index for v in f.verts) for f in bm.faces]
        m.shell(verts, faces, mat)
        bm.free()
        ob.evaluated_get(dg).to_mesh_clear()
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)
        c -= cap_h * scale + line_gap


def lamp_standard(m, x, y, z0, height, mat_metal, mat_glass, lod=0):
    """Generic period lamp standard stand-in (post + lantern) for entrance stairs."""
    segs = 10 if lod == 0 else 6
    prof = [(0.14, 0.0), (0.14, 0.12), (0.08, 0.2), (0.06, height * 0.82), (0.1, height * 0.84), (0.1, height * 0.86)]
    m.lathe(x, y, prof, segs, mat_metal, z_off=z0)
    gl = [(0.05, 0.0), (0.2, 0.08), (0.22, 0.3), (0.16, 0.42), (0.03, 0.46)]
    m.lathe(x, y, gl, segs, mat_glass, z_off=z0 + height * 0.86)


def relief_blob(m, fr, ac, cc, ra, rc, rb, b_back, mat, angle=0.0, segs=16, rings=5):
    """Smooth domed low-relief form (half-ellipsoid) on a facade: centre (ac, cc), in-plane
    radii ra (along a) / rc (along c), protrusion rb beyond b_back, rotated by `angle` in the
    (a, c) plane. Closed: flat back disc + dome."""
    ca, sa = math.cos(angle), math.sin(angle)
    verts = []
    # rings from the rim (k = 0) to near the apex; apex vertex last
    for k in range(rings):
        t = k / rings
        r = math.cos(t * math.pi / 2)          # 1 at rim -> 0 at apex
        h = math.sin(t * math.pi / 2)
        for s in range(segs):
            ph = 2 * math.pi * s / segs
            x, y = ra * r * math.cos(ph), rc * r * math.sin(ph)
            a, c = ac + x * ca - y * sa, cc + x * sa + y * ca
            verts.append(fr.p(a, b_back + rb * h, c))
    verts.append(fr.p(ac, b_back + rb, cc))                       # apex
    apex = len(verts) - 1
    faces = []
    for k in range(rings - 1):
        for s in range(segs):
            s2 = (s + 1) % segs
            faces.append((k * segs + s, k * segs + s2, (k + 1) * segs + s2, (k + 1) * segs + s))
    top = (rings - 1) * segs
    for s in range(segs):
        faces.append((top + s, top + (s + 1) % segs, apex))
    # ring 0 lies on the back plane (h = 0): close the solid with it, reversed (faces -n)
    faces.append(tuple(reversed(range(segs))))
    m.shell(verts, faces, mat)


def relief_standin_smooth(m, fr, a0, a1, c0, c1, b_back, seed, mat, lod=0):
    """Labelled simplified stand-in for a figural relief (rights unconfirmed): 2-3 standing
    figure masses built from smooth domed forms, so the panel reads as carved relief at street
    distance without asserting a likeness."""
    import random
    rnd = random.Random(seed)
    w, h = a1 - a0, c1 - c0
    fw = 0.08
    m.lbox(fr, a0 - fw, a1 + fw, b_back, b_back + 0.06, c0 - fw, c0, mat)
    m.lbox(fr, a0 - fw, a1 + fw, b_back, b_back + 0.06, c1, c1 + fw, mat)
    m.lbox(fr, a0 - fw, a0, b_back, b_back + 0.06, c0, c1, mat)
    m.lbox(fr, a1, a1 + fw, b_back, b_back + 0.06, c0, c1, mat)
    if lod >= 1:
        return
    segs = 14
    nfig = rnd.choice((2, 3, 3))
    gz = c0 + 0.08                                  # ground line of the scene
    m.lbox(fr, a0, a1, b_back, b_back + 0.02, c0, gz, mat)
    for i in range(nfig):
        cx = a0 + w * (i + 0.5) / nfig + rnd.uniform(-0.06, 0.06) * w
        fh = h * rnd.uniform(0.66, 0.84)
        lean = rnd.uniform(-0.12, 0.12)
        dep = rnd.uniform(0.035, 0.055)
        # robe / legs
        relief_blob(m, fr, cx, gz + fh * 0.27, w * 0.085, fh * 0.29, dep * 0.8, b_back, mat, angle=lean * 0.3, segs=segs)
        # torso
        tx = cx + math.sin(lean) * fh * 0.25
        relief_blob(m, fr, tx, gz + fh * 0.62, w * 0.07, fh * 0.17, dep, b_back, mat, angle=lean, segs=segs)
        # head
        hx = cx + math.sin(lean) * fh * 0.42
        relief_blob(m, fr, hx, gz + fh * 0.88, w * 0.04, fh * 0.065, dep * 1.05, b_back, mat, segs=segs)
        # arms: one hanging, one gesturing
        s = rnd.choice((-1, 1))
        relief_blob(m, fr, tx + s * w * 0.075, gz + fh * 0.58, w * 0.022, fh * 0.15, dep * 0.7, b_back, mat,
                    angle=s * 0.25, segs=10)
        if rnd.random() < 0.7:
            ang = -s * rnd.uniform(0.6, 1.2)
            relief_blob(m, fr, tx - s * w * 0.1, gz + fh * 0.68, w * 0.022, fh * 0.14, dep * 0.75, b_back, mat,
                        angle=ang, segs=10)


# ----------------------------------------------------------------------------- rings / offsets

def offset_polygon_per_edge(poly, dists):
    """Offset each edge of a CCW polygon inward by its own distance (dists[i] for edge
    i -> i+1); vertices are intersections of consecutive offset lines."""
    poly = _clean_poly(poly)
    if polygon_area(poly) < 0:
        raise ValueError("polygon must be CCW")
    n = len(poly)
    lines = []
    for i in range(n):
        p0, p1 = poly[i], poly[(i + 1) % n]
        nx, ny = _seg_normal(p0, p1)          # outward
        d = dists[i]
        lines.append(((p0[0] - nx * d, p0[1] - ny * d), (p1[0] - p0[0], p1[1] - p0[1])))
    out = []
    for i in range(n):
        (a, da), (b, db) = lines[i - 1], lines[i]
        den = da[0] * db[1] - da[1] * db[0]
        if abs(den) < 1e-12:
            out.append(b)
            continue
        t = ((b[0] - a[0]) * db[1] - (b[1] - a[1]) * db[0]) / den
        out.append((a[0] + da[0] * t, a[1] + da[1] * t))
    return out


def ring_prism(m, outer, inner, z0, z1, mat_out, mat_in, mat_top, mat_bottom=None):
    """Closed prism of an outer CCW polygon with one inner hole (court). Caps tessellated
    with holes; outer walls face out, inner walls face into the hole."""
    from mathutils.geometry import tessellate_polygon
    outer = _clean_poly(outer)
    inner = _clean_poly(inner)
    if polygon_area(outer) < 0:
        outer = outer[::-1]
    if polygon_area(inner) < 0:
        inner = inner[::-1]
    pts = outer + inner
    tris = tessellate_polygon([[(x, y, 0.0) for x, y in outer], [(x, y, 0.0) for x, y in inner]])
    base = len(m.verts)
    m.verts.extend([(x, y, z0) for x, y in pts])
    m.verts.extend([(x, y, z1) for x, y in pts])
    npt = len(pts)
    for t in tris:
        a, b, c = t
        (x0, y0), (x1, y1), (x2, y2) = pts[a], pts[b], pts[c]
        cross = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
        if abs(cross) < 1e-9:
            continue
        if cross < 0:
            a, b = b, a
        m.faces.append(((base + npt + a, base + npt + b, base + npt + c), mat_top, None))
        m.faces.append(((base + c, base + b, base + a), mat_bottom or mat_top, None))
    no = len(outer)
    for i in range(no):
        j = (i + 1) % no
        m.faces.append(((base + i, base + j, base + npt + j, base + npt + i), mat_out, None))
    ni = len(inner)
    for i in range(ni):
        j = (i + 1) % ni
        a, b = no + i, no + j
        # inner loop is CCW too; walls must face into the hole -> reversed winding
        m.faces.append(((base + b, base + a, base + npt + a, base + npt + b), mat_in, None))
