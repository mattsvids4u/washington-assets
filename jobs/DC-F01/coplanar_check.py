"""Detect same-direction coplanar overlapping faces (z-fighting / path-tracer self-shadow
'black band' artifacts) in the LOD meshes of an exported GLB.

    python jobs/DC-F01/coplanar_check.py <asset.glb> [--lod 0] [--min-area 0.0004] [--top 15]

Faces are grouped by oriented plane (normal direction, then offset clustered at 1 mm).
Within a plane, candidate pairs come from an in-plane bbox sweep; overlap area is computed by
convex clipping. Opposite-facing coincident faces are NOT reported (they are internal and
harmless).

Most same-direction overlaps in a generator built from overlapping closed shells are buried
inside another solid and can never be seen. Each overlap polygon is therefore fanned from its
centroid and sampled at interior points of every fan triangle (barycentric 0.6/0.2/0.2, so no
sample sits on the polygon boundary); every sample is lifted 1 mm off the face along its normal
and a fan of rays is cast from it over the outward hemisphere against all non-glass triangles
plus a ground plane at z = 0 (the asset stands on terrain). Samples that see the sky give the
overlap's VISIBLE area (area-weighted); the overlap counts as EXPOSED when that is >= 20 % of it
or >= 25 cm^2. (Boundary-only exposure is a hairline along a convex corner edge, not a visible
patch.) Glass is treated as transparent, so defects behind windows are still found. Only exposed
overlaps count toward the exit status: exit 1 if their visible area totals > --fail-area.
"""
import argparse
import math
import os
import sys
from collections import defaultdict

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

TRANSPARENT = ("Glass", "Lamp_Glass")


def parse():
    argv = sys.argv[1:]
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    p = argparse.ArgumentParser()
    p.add_argument("glb")
    p.add_argument("--lod", type=int, default=0)
    p.add_argument("--min-area", type=float, default=4e-4)     # 2 x 2 cm
    p.add_argument("--fail-area", type=float, default=0.05)    # m^2 total
    p.add_argument("--top", type=int, default=15)
    p.add_argument("--lift", type=float, default=0.001)       # sample offset off the face, m
    p.add_argument("--all", action="store_true", help="also list buried (hidden) overlaps")
    p.add_argument("--explain", action="store_true", help="print the sky-seeing samples of listed findings")
    return p.parse_args(argv)


def ray_fan(n):
    """Unit directions over the hemisphere around n: n itself plus rings at 40 and 75 degrees."""
    n = n.normalized()
    t = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = n.cross(t).normalized()
    v = n.cross(u)
    dirs = [n]
    for tilt, k in ((math.radians(40), 8), (math.radians(75), 12)):
        for i in range(k):
            a = 2 * math.pi * (i + 0.5) / k
            d = n * math.cos(tilt) + (u * math.cos(a) + v * math.sin(a)) * math.sin(tilt)
            dirs.append(d.normalized())
    return dirs


def sees_sky(bvh, q, fan):
    for d in fan:
        if bvh.ray_cast(q, d)[0] is None:
            return d
    return None


def visible_area(bvh, samples, n, lift):
    """samples: [(point3, weight_area)]. Returns (visible area, [(lifted point, sky dir)])."""
    fan = ray_fan(n)
    vis, hits = 0.0, []
    for p, w in samples:
        q = p + n * lift
        d = sees_sky(bvh, q, fan)
        if d is not None:
            vis += w
            hits.append((q, d))
    return vis, hits


def clip(subject, clipper):
    """Sutherland-Hodgman: intersection of convex polygons (lists of (x, y), CCW)."""
    out = subject
    n = len(clipper)
    for i in range(n):
        a, b = clipper[i], clipper[(i + 1) % n]
        inp, out = out, []
        if not inp:
            break

        def inside(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-12

        def inter(p, q):
            x1, y1, x2, y2 = a[0], a[1], b[0], b[1]
            x3, y3, x4, y4 = p[0], p[1], q[0], q[1]
            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(den) < 1e-18:
                return q
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        s = inp[-1]
        for e in inp:
            if inside(e):
                if not inside(s):
                    out.append(inter(s, e))
                out.append(e)
            elif inside(s):
                out.append(inter(s, e))
            s = e
    return out


def area(poly):
    s = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        s += x0 * y1 - x1 * y0
    return s / 2


def main():
    a = parse()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(a.glb))
    tag = f"_LOD{a.lod}"
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.endswith(tag)]
    total = 0.0
    hidden_total = 0.0
    findings = []
    hidden = []
    for o in objs:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.transform(o.matrix_world)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])   # glTF import is already triangles
        mats = [s.material.name if s.material else "?" for s in o.material_slots]
        opaque = [f for f in bm.faces
                  if not any(t in mats[f.material_index] for t in TRANSPARENT)]
        verts = [v.co.copy() for v in bm.verts]
        polys = [[v.index for v in f.verts] for f in opaque]
        g = len(verts)
        verts += [Vector((-1e4, -1e4, 0.0)), Vector((1e4, -1e4, 0.0)), Vector((1e4, 1e4, 0.0)),
                  Vector((-1e4, 1e4, 0.0))]
        polys.append([g, g + 1, g + 2, g + 3])          # terrain
        bvh = BVHTree.FromPolygons(verts, polys, epsilon=0.0)
        by_normal = defaultdict(list)
        for f in bm.faces:
            n = f.normal
            if n.length < 0.5 or f.calc_area() < 1e-10:
                continue
            by_normal[(round(n.x, 3), round(n.y, 3), round(n.z, 3))].append((n.dot(f.verts[0].co), f))
        for nkey, items in by_normal.items():
            if len(items) < 2:
                continue
            items.sort(key=lambda r: r[0])
            clusters, cur = [], [items[0]]
            for it in items[1:]:
                if it[0] - cur[-1][0] <= 1e-3:
                    cur.append(it)
                else:
                    clusters.append(cur)
                    cur = [it]
            clusters.append(cur)
            for cl in clusters:
                if len(cl) < 2:
                    continue
                # exact plane of this cluster: mean face normal, local origin on the first face
                # (the rounded key normal would misplace samples by cm on oblique planes far
                # from the world origin)
                n = Vector((0.0, 0.0, 0.0))
                for _, f in cl:
                    n += f.normal * f.calc_area()
                n.normalize()
                org = cl[0][1].verts[0].co.copy()
                dmean = sum((f.verts[0].co - org).dot(n) for _, f in cl) / len(cl)
                if n.z < -0.99 and abs(org.z) < 0.01:
                    continue        # ground-contact bottoms at grade: never visible
                t = Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))
                u = n.cross(t).normalized()
                v = n.cross(u)
                polys = []
                for _, f in cl:
                    pts = [((vv.co - org).dot(u), (vv.co - org).dot(v)) for vv in f.verts]
                    if area(pts) < 0:
                        pts = pts[::-1]
                    xs = [q[0] for q in pts]
                    ys = [q[1] for q in pts]
                    polys.append((min(xs), max(xs), min(ys), max(ys), pts, f))
                polys.sort(key=lambda r: r[0])
                active = []
                for r in polys:
                    active = [s_ for s_ in active if s_[1] > r[0] + 1e-4]
                    for s_ in active:
                        if s_[3] <= r[2] + 1e-4 or r[3] <= s_[2] + 1e-4:
                            continue
                        inter = clip(r[4], s_[4])
                        if len(inter) < 3:
                            continue
                        ar = abs(area(inter))
                        if ar <= a.min_area:
                            continue
                        cx = sum(q[0] for q in inter) / len(inter)
                        cy = sum(q[1] for q in inter) / len(inter)
                        samples = []
                        for k in range(len(inter)):
                            p1, p2 = inter[k], inter[(k + 1) % len(inter)]
                            wt = abs(area([(cx, cy), p1, p2])) / 3.0
                            if wt <= 0.0:
                                continue
                            for (w0, w1, w2) in ((0.6, 0.2, 0.2), (0.2, 0.6, 0.2), (0.2, 0.2, 0.6)):
                                x = w0 * cx + w1 * p1[0] + w2 * p2[0]
                                y = w0 * cy + w1 * p1[1] + w2 * p2[1]
                                samples.append((org + u * x + v * y + n * dmean, wt))
                        vis, hits = visible_area(bvh, samples, n, a.lift)
                        c = org + u * cx + v * cy + n * dmean
                        rec = (vis, o.name, mats[r[5].material_index], mats[s_[5].material_index],
                               tuple(round(x, 2) for x in c), nkey, hits[:3], ar)
                        if vis >= 0.2 * ar or vis >= 25e-4:
                            total += vis
                            findings.append(rec)
                        else:
                            hidden_total += ar
                            hidden.append(rec)
                    active.append(r)
        bm.free()
    findings.sort(reverse=True)
    hidden.sort(reverse=True)
    print(f"{os.path.basename(a.glb)} LOD{a.lod}: {len(findings)} EXPOSED coplanar same-direction "
          f"overlaps, visible area {total:.4f} m^2 ({len(hidden)} buried overlaps, {hidden_total:.1f} m^2, ignored)")
    for f in findings[:a.top]:
        print(f"  {f[0]:.4f} m^2 visible of {f[7]:.4f}  {f[2]} / {f[3]}  at {f[4]}  normal {f[5]}")
        if a.explain:
            for q, d in f[6]:
                print(f"      sky from {tuple(round(x, 3) for x in q)} along {tuple(round(x, 3) for x in d)}")
    pairs = defaultdict(lambda: [0, 0.0])
    for f in findings:
        k = tuple(sorted((f[2], f[3]))) + (f[5],)
        pairs[k][0] += 1
        pairs[k][1] += f[0]
    print("  by material pair / normal:")
    for k, (cnt, ar) in sorted(pairs.items(), key=lambda kv: -kv[1][1])[:a.top]:
        print(f"    {ar:8.4f} m^2  x{cnt:<4d} {k[0]} / {k[1]}  normal {k[2]}")
    if a.all:
        print("  -- buried --")
        for f in hidden[:a.top]:
            print(f"  {f[0]:.4f} m^2  {f[2]} / {f[3]}  at {f[4]}  normal {f[5]}")
    sys.exit(1 if total > a.fail_area else 0)


if __name__ == "__main__":
    main()
