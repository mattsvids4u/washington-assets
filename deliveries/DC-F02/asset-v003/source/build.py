"""DC-F02 v001 - Senate Office Building (1909 / 1933 First St wing), Washington DC, autumn 1963.

Reproducible generator: `python jobs/DC-F02/build.py` rebuilds out/ from scratch.

Frame: Blender metres, +X east, +Y north, +Z up. Exported GLB is metres (UE imports to cm).
Origin = SW footprint corner (Delaware Ave x Constitution Ave building corner) at the site datum,
which sits 0.30 m below C St grade (the lowest grade). Constitution Ave grade = PARAMS["z_const"].
All dimensions are APPROXIMATE until reconciled with the DC-R02 SOB evidence card (see EVIDENCE.md).
"""
import math
import os
import random
import shutil
import sys

import bpy
import bmesh  # noqa: F401  (kept for local edits)
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
TEX = os.path.join(OUT, "textures")
ASSET = "SM_F02_SenateOfficeBuilding"

PARAMS = {
    # Footprint (APPROXIMATE - replace with DC-R02 SOB card)
    "W": 143.0,          # Delaware Ave -> First St NE (x)
    "D": 110.0,          # Constitution Ave -> C St NE (y)
    "chamfer": 14.0,     # SW rotunda corner chamfer legs
    "wing": 20.0,        # wing depth outer face -> court face
    # Grade (storey counts VERIFIED E02; metres APPROXIMATE)
    "grade_cst": 0.30,   # C St grade above datum
    "drop": 7.0,         # Constitution grade minus C St grade
    # Elevation, relative to Constitution grade
    "plinth": 1.2, "base_top": 7.0, "band_top": 7.6, "order_top": 19.0,
    "architrave": 0.8, "frieze": 1.1, "cornice": 1.0, "balustrade": 1.5,
    # Colonnade (34 columns VERIFIED E01; spacing APPROXIMATE)
    "n_columns": 34, "col_d": 1.40, "loggia_depth": 2.8,
    "corner_bay": 7.0,   # recessed central bay of the SW chamfer (photo-estimated, E11/E15)
    "return_w": 12.0,    # corner-pavilion return on each street front (E11/E15/E16: pier|recess|pier)
    "return_recess": 5.6,
    "attic_raise": 0.5,  # corner attic block above the parapet line (subtle in E16)
    "base_win_w": 1.2,   # arched ground-storey windows: tall and narrow in E11 (about 1.2 x 4.1 m)
    "pav_w_east": 10.0, "pav_proj": 0.8,
    "bay": 3.30, "wall_t": 0.9,
    "seed": 1963,
}
P = PARAMS
P["z_const"] = P["grade_cst"] + P["drop"]


def zc(rel):
    return P["z_const"] + rel


def grade_at_y(y):
    t = min(max(y / P["D"], 0.0), 1.0)
    return P["z_const"] - P["drop"] * t


# ---------------------------------------------------------------------------
# Mesh builder
# ---------------------------------------------------------------------------
MATS = [
    "M_F02_SOB_MarbleVermont", "M_F02_SOB_MarbleGeorgia", "M_F02_SOB_GraniteNH",
    "M_F02_SOB_LimestoneIndiana", "M_F02_SOB_WindowFramePaint", "M_F02_SOB_GlassInterior",
    "M_F02_SOB_BronzeDoor", "M_F02_SOB_RoofMembrane", "M_F02_SOB_SitePaving",
]
MI = {m: i for i, m in enumerate(MATS)}
UV_TILE = {  # metres per UV unit
    "M_F02_SOB_MarbleVermont": 4.0, "M_F02_SOB_MarbleGeorgia": 4.0, "M_F02_SOB_GraniteNH": 3.0,
    "M_F02_SOB_LimestoneIndiana": 4.0, "M_F02_SOB_WindowFramePaint": 1.0, "M_F02_SOB_GlassInterior": 1.0,
    "M_F02_SOB_BronzeDoor": 2.0, "M_F02_SOB_RoofMembrane": 6.0, "M_F02_SOB_SitePaving": 4.0,
}


class MB:
    def __init__(self):
        self.v = []
        self.f = []
        self.m = []
        self.uvo = {}  # face index -> list of uv tuples

    def _add(self, pts, faces, mat, uv_over=None):
        base = len(self.v)
        self.v.extend(pts)
        f0 = len(self.f)
        for fc in faces:
            self.f.append(tuple(base + i for i in fc))
            self.m.append(MI[mat])
        if uv_over:
            for k, uvs in uv_over.items():
                self.uvo[f0 + k] = uvs

    def hexa(self, p, mat, uv_front=None):
        """8 corner points: 0-3 front ring, 4-7 back ring (same order). Orientation auto-fixed."""
        faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (3, 2, 6, 7), (0, 3, 7, 4), (1, 5, 6, 2)]
        vol = signed_volume(p, faces)
        if abs(vol) < 1e-9:
            return
        if vol < 0:
            faces = [tuple(reversed(fc)) for fc in faces]
            uv_map = {0: list(reversed(uv_front))} if uv_front else None
        else:
            uv_map = {0: uv_front} if uv_front else None
        self._add(p, faces, mat, uv_map)

    def box(self, lo, hi, mat):
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        if x1 - x0 < 1e-4 or y1 - y0 < 1e-4 or z1 - z0 < 1e-4:
            return
        p = [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1),
             (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]
        self.hexa(p, mat)

    def lathe(self, cx, cy, profile, seg, mat, flutes=0, flute_depth=0.0, rings_fluted=()):
        """profile: list of (r, z) bottom->top. Closed with caps."""
        pts = []
        n = seg
        for ri, (r, z) in enumerate(profile):
            for k in range(n):
                a = 2 * math.pi * k / n
                rr = r
                if flutes and ri in rings_fluted:
                    # concave flute: depth peaks mid-flute
                    ph = (k % (n // flutes)) / (n // flutes)
                    rr = r - flute_depth * math.sin(math.pi * ph)
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a), z))
        faces = []
        R = len(profile)
        for ri in range(R - 1):
            for k in range(n):
                a0 = ri * n + k
                a1 = ri * n + (k + 1) % n
                b0 = (ri + 1) * n + k
                b1 = (ri + 1) * n + (k + 1) % n
                faces.append((a0, a1, b1, b0))
        faces.append(tuple(reversed(range(n))))
        faces.append(tuple((R - 1) * n + k for k in range(n)))
        self._add(pts, faces, mat)


def signed_volume(p, faces):
    vol = 0.0
    for fc in faces:
        a = Vector(p[fc[0]])
        for i in range(1, len(fc) - 1):
            b = Vector(p[fc[i]])
            c = Vector(p[fc[i + 1]])
            vol += a.dot(b.cross(c)) / 6.0
    return vol


class Frame:
    """Facade frame: u along facade (viewer's right when outside), d inward, z up."""

    def __init__(self, ox, oy, ux, uy, length, name, dz=0.0):
        self.o = (ox, oy)
        self.dz = dz  # mm-scale offset so overlapping corner pieces are never coplanar
        self.u = (ux, uy)
        self.n = (-uy, ux)  # inward = left of u when seen from above
        self.L = length
        self.name = name

    def w(self, u, d, z):
        return (self.o[0] + self.u[0] * u + self.n[0] * d,
                self.o[1] + self.u[1] * u + self.n[1] * d, z + self.dz)

    def box(self, mb, u0, u1, d0, d1, z0, z1, mat, uv_front=None):
        if u1 - u0 < 1e-4 or d1 - d0 < 1e-4 or z1 - z0 < 1e-4:
            return
        p = [self.w(u0, d0, z0), self.w(u1, d0, z0), self.w(u1, d0, z1), self.w(u0, d0, z1),
             self.w(u0, d1, z0), self.w(u1, d1, z0), self.w(u1, d1, z1), self.w(u0, d1, z1)]
        mb.hexa(p, mat, uv_front)

    def prism(self, mb, pts, d0, d1, mat):
        """Extrude a simple (u, z) polygon between depths d0 and d1 (orientation auto-fixed)."""
        n = len(pts)
        p = [self.w(u, d0, z) for u, z in pts] + [self.w(u, d1, z) for u, z in pts]
        faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
        faces += [(i, n + i, n + (i + 1) % n, (i + 1) % n) for i in range(n)]
        if signed_volume(p, faces) < 0:
            faces = [tuple(reversed(f)) for f in faces]
        mb._add(p, faces, mat)

    def grade(self, u):
        x, y, _ = self.w(u, 0, 0)
        return grade_at_y(y)


# ---------------------------------------------------------------------------
# Facade elements
# ---------------------------------------------------------------------------
RNG = random.Random(P["seed"])
CUR_LOD = [0]
ATLAS_DARK = []  # glazing-atlas cells holding the plain dark state (filled by glass_atlas)


def atlas_uv(state):
    cx, cy = state % 4, state // 4
    e = 0.004
    u0, v0 = cx / 4 + e, cy / 4 + e
    u1, v1 = (cx + 1) / 4 - e, (cy + 1) / 4 - e
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def wall_with_openings(mb, F, u0, u1, z0, z1, d0, d1, openings, mat):
    """Fill rect minus openings [(ou0,ou1,oz0,oz1)] with merged boxes. LOD2 keeps walls solid."""
    if CUR_LOD[0] >= 2:
        openings = []
    zs = sorted({z0, z1} | {o[2] for o in openings if z0 < o[2] < z1} | {o[3] for o in openings if z0 < o[3] < z1})
    for za, zb in zip(zs, zs[1:]):
        zm = (za + zb) / 2
        holes = sorted((o[0], o[1]) for o in openings if o[2] <= zm <= o[3])
        cur = u0
        for ha, hb in holes:
            if ha > cur:
                F.box(mb, cur, min(ha, u1), d0, d1, za, zb, mat)
            cur = max(cur, hb)
        if cur < u1:
            F.box(mb, cur, u1, d0, d1, za, zb, mat)


def rusticated(mb, F, u0, u1, z0, z1, d0, d1, openings, mat, course, lod):
    if lod > 0:
        wall_with_openings(mb, F, u0, u1, z0, z1, d0, d1, openings, mat)
        return
    n = max(1, round((z1 - z0) / course))
    h = (z1 - z0) / n
    j = 0.045  # channel half-height
    for k in range(n):
        a = z0 + k * h
        b = a + h
        ca = a + (j if k > 0 else 0)
        cb = b - (j if k < n - 1 else 0)
        wall_with_openings(mb, F, u0, u1, ca, cb, d0, d1, openings, mat)
        if k < n - 1:  # recessed channel joint
            wall_with_openings(mb, F, u0, u1, b - j, b + j, d0 + 0.07, d1, openings, mat)


def window(mb, F, u0, u1, z0, z1, d_face, depth, lod, kind="sash", hood=False, surround=False,
           sill_mat="M_F02_SOB_MarbleVermont", tag=0, state=None, pediment=False):
    """Opening already cut by caller. Adds frame, glazing, sash bars, sill, trim.
    kind: sash (6/6), two (2/2), tall (small-pane grid, E11 corner windows), door (glazing only).
    state forces a glazing-atlas cell (tall corner windows use a dark cell, not blinds)."""
    fm = "M_F02_SOB_WindowFramePaint"
    gd = d_face + depth  # glass plane
    if lod >= 2:  # solid wall at LOD2: glazing card just proud of the face
        rs = RNG.randrange(16)
        state = rs if state is None else state
        F.box(mb, u0, u1, d_face - 0.03, d_face - 0.01, z0, z1, "M_F02_SOB_GlassInterior", atlas_uv(state))
        return
    fw = 0.09 if lod == 0 else 0.12
    # frame ring
    F.box(mb, u0, u1, gd - 0.06, gd + 0.06, z0, z0 + fw, fm)
    F.box(mb, u0, u1, gd - 0.06, gd + 0.06, z1 - fw, z1, fm)
    F.box(mb, u0, u0 + fw, gd - 0.06, gd + 0.06, z0 + fw, z1 - fw, fm)
    F.box(mb, u1 - fw, u1, gd - 0.06, gd + 0.06, z0 + fw, z1 - fw, fm)
    rs = RNG.randrange(16)
    state = rs if state is None else state
    F.box(mb, u0 + fw, u1 - fw, gd, gd + 0.015, z0 + fw, z1 - fw, "M_F02_SOB_GlassInterior", atlas_uv(state))
    if kind == "door":
        return
    zm = (z0 + z1) / 2
    F.box(mb, u0 + fw, u1 - fw, gd - 0.05, gd, zm - 0.035, zm + 0.035, fm)  # meeting rail
    if lod == 0:
        bw = 0.022
        if kind == "sash":  # 6-over-6
            for t in (1 / 3, 2 / 3):
                uc = u0 + (u1 - u0) * t
                F.box(mb, uc - bw, uc + bw, gd - 0.03, gd, z0 + fw, z1 - fw, fm)
            for zz in ((z0 + zm) / 2, (zm + z1) / 2):
                F.box(mb, u0 + fw, u1 - fw, gd - 0.03, gd, zz - bw, zz + bw, fm)
        elif kind == "tall":  # small-pane grid: 4 lights wide, ~0.75 m rows (E11 corner window)
            for t in (0.25, 0.5, 0.75):
                uc = u0 + (u1 - u0) * t
                F.box(mb, uc - bw, uc + bw, gd - 0.03, gd, z0 + fw, z1 - fw, fm)
            nr = max(2, round((z1 - z0) / 0.75))
            for k in range(1, nr):
                zz = z0 + (z1 - z0) * k / nr
                if abs(zz - zm) > 0.1:
                    F.box(mb, u0 + fw, u1 - fw, gd - 0.03, gd, zz - bw, zz + bw, fm)
        elif kind == "two":  # 2-over-2
            uc = (u0 + u1) / 2
            F.box(mb, uc - bw, uc + bw, gd - 0.03, gd, z0 + fw, z1 - fw, fm)
        # sill
        F.box(mb, u0 - 0.10, u1 + 0.10, d_face - 0.09, gd - 0.06, z0 - 0.12, z0, sill_mat)
        if surround:
            t = 0.20
            F.box(mb, u0 - t, u0, d_face - 0.07, d_face, z0, z1 + t, sill_mat)
            F.box(mb, u1, u1 + t, d_face - 0.07, d_face, z0, z1 + t, sill_mat)
            F.box(mb, u0, u1, d_face - 0.07, d_face, z1, z1 + t, sill_mat)
        if hood:
            F.box(mb, u0 - 0.28, u1 + 0.28, d_face - 0.10, d_face, z1 + 0.22, z1 + 0.62, sill_mat)  # frieze
            F.box(mb, u0 - 0.42, u1 + 0.42, d_face - 0.30, d_face, z1 + 0.62, z1 + 0.84, sill_mat)  # cornice
            for uu in (u0 - 0.36, u1 + 0.18):  # consoles
                F.box(mb, uu, uu + 0.18, d_face - 0.26, d_face, z1 + 0.05, z1 + 0.62, sill_mat)
            if pediment:  # low triangular pediment over the hood (framed corner windows, E15/E16)
                uc = (u0 + u1) / 2
                F.prism(mb, [(u0 - 0.42, z1 + 0.84), (u1 + 0.42, z1 + 0.84), (uc, z1 + 1.40)],
                        d_face - 0.26, d_face, sill_mat)


def arch_spandrels(mb, F, u0, u1, zs, d0, d1, mat, lod):
    """Stone filling the two upper corners of a rectangular opening so it reads as a semicircular
    arch springing at zs (radius = half the opening width)."""
    r = (u1 - u0) / 2
    uc = u0 + r
    seg = 10 if lod == 0 else 4
    arc_l = [(uc + r * math.cos(a), zs + r * math.sin(a))
             for a in np.linspace(math.pi / 2, math.pi, seg + 1)[1:-1]]
    arc_r = [(uc + r * math.cos(a), zs + r * math.sin(a))
             for a in np.linspace(0.0, math.pi / 2, seg + 1)[1:-1]]
    F.prism(mb, [(u0, zs), (u0, zs + r), (uc, zs + r)] + arc_l, d0, d1, mat)
    F.prism(mb, [(uc, zs + r), (u1, zs + r), (u1, zs)] + arc_r, d0, d1, mat)


def arched_window(mb, F, u0, u1, z0, ztop, d_face, depth, lod, kind="two", mat="M_F02_SOB_MarbleVermont",
                  keystone=True, state=None):
    """Round-arched window in an opening already cut (rect u0..u1, z0..ztop): sash below the springing,
    glazed fanlight above, stone spandrels, keystone (E11 / E15 photos: arched base windows)."""
    r = (u1 - u0) / 2
    zs = ztop - r
    fm = "M_F02_SOB_WindowFramePaint"
    gd = d_face + depth
    window(mb, F, u0, u1, z0, zs, d_face, depth, lod, kind=kind, sill_mat=mat, state=state)
    rs = RNG.randrange(16)
    state = rs if state is None else state
    if lod >= 2:
        return
    arch_spandrels(mb, F, u0, u1, zs, d_face, gd - 0.07, mat, lod)
    F.box(mb, u0 + 0.06, u1 - 0.06, gd, gd + 0.015, zs, ztop - 0.02, "M_F02_SOB_GlassInterior", atlas_uv(state))
    if lod == 0:
        uc = (u0 + u1) / 2
        F.box(mb, uc - 0.025, uc + 0.025, gd - 0.03, gd, zs, ztop - 0.05, fm)  # fanlight bar
        if kind == "tall":  # radiating fanlight bars
            r = (u1 - u0) / 2
            for ang in (math.radians(45), math.radians(135)):
                cu, cz = uc + 0.5 * r * math.cos(ang), zs + 0.5 * r * math.sin(ang)
                F.box(mb, cu - 0.025, cu + 0.025, gd - 0.03, gd, cz - 0.3, cz + 0.3, fm)
        if keystone:
            F.box(mb, uc - 0.24, uc + 0.24, d_face - 0.09, d_face, ztop - 0.12, ztop + 0.52, mat)


def cartouche(mb, F, uc, d, z0, mat, lod):
    """Carved oval shield over the corner-pier windows (E11 / E15), as stepped stone courses."""
    if lod >= 2:
        return
    seg = 20 if lod == 0 else 10

    def oval(rx, rz, zc_):
        return [(uc + rx * math.cos(2 * math.pi * k / seg), zc_ + rz * math.sin(2 * math.pi * k / seg))
                for k in range(seg)]
    zm = z0 + 0.8
    F.prism(mb, oval(0.62, 0.85, zm), d - 0.16, d, mat)          # shield
    if lod == 0:
        F.prism(mb, oval(0.36, 0.55, zm), d - 0.27, d - 0.15, mat)  # raised boss
        F.box(mb, uc - 0.8, uc + 0.8, d - 0.12, d, zm + 0.80, zm + 1.0, mat)  # scroll top


def column(mb, cx, cy, z0, z1, lod, mat):
    """Beaux-Arts (Roman) Doric column with base, fluted tapered shaft, capital. z0 = plinth bottom."""
    Dm = P["col_d"]
    r = Dm / 2
    H = z1 - z0
    hb, hc = 0.55, 0.85
    hs = H - hb - hc
    if lod >= 2:
        mb.lathe(cx, cy, [(r, z0), (r * 0.86, z1 - hc), (r * 1.2, z1)], 6, mat)
        return
    seg = 80 if lod == 0 else 12
    # square plinth
    mb.box((cx - r * 1.22, cy - r * 1.22, z0), (cx + r * 1.22, cy + r * 1.22, z0 + 0.22), mat)
    mb.lathe(cx, cy, [(r * 1.12, z0 + 0.22), (r * 1.14, z0 + 0.36), (r * 1.06, z0 + 0.48), (r, z0 + hb)],
             32 if lod == 0 else 12, mat)
    zs0 = z0 + hb
    prof = [(r, zs0), (r * 0.985, zs0 + hs * 0.33), (r * 0.93, zs0 + hs * 0.7), (r * 0.86, zs0 + hs)]
    if lod == 0:
        mb.lathe(cx, cy, prof, seg, mat, flutes=20, flute_depth=0.045, rings_fluted=(0, 1, 2, 3))
    else:
        mb.lathe(cx, cy, prof, seg, mat)
    zc0 = zs0 + hs
    cap = [(r * 0.88, zc0), (r * 0.88, zc0 + 0.12), (r * 0.92, zc0 + 0.18), (r * 0.92, zc0 + 0.30),
           (r * 1.18, zc0 + 0.55)]
    mb.lathe(cx, cy, cap, 32 if lod == 0 else 12, mat)
    a = r * 1.25
    mb.box((cx - a, cy - a, zc0 + 0.55), (cx + a, cy + a, z1), mat)


def baluster(mb, F, u, d, z0, z1, lod, mat):
    if lod >= 1:
        F.box(mb, u - 0.07, u + 0.07, d - 0.07, d + 0.07, z0, z1, mat)
        return
    x, y, _ = F.w(u, d, 0)
    h = z1 - z0
    prof = [(0.10, z0), (0.10, z0 + 0.06), (0.07, z0 + 0.10), (0.11, z0 + h * 0.32), (0.09, z0 + h * 0.45),
            (0.055, z0 + h * 0.72), (0.075, z0 + h * 0.82), (0.10, z1 - 0.04), (0.10, z1)]
    mb.lathe(x, y, prof, 8, mat)


def balustrade(mb, F, u0, u1, dface, z0, posts, lod, mat, solid=False):
    """dface = outer face of parapet. posts = list of u for pedestals."""
    hb = P["balustrade"]
    dt = 0.55
    if lod >= 2 or solid:
        F.box(mb, u0, u1, dface, dface + dt, z0, z0 + hb, mat)
        if solid and lod < 2:  # recessed panels on a solid attic
            F.box(mb, u0, u1, dface - 0.06, dface, z0, z0 + 0.25, mat)
            F.box(mb, u0, u1, dface - 0.10, dface, z0 + hb - 0.2, z0 + hb, mat)
        return
    F.box(mb, u0, u1, dface - 0.04, dface + dt, z0, z0 + 0.28, mat)          # plinth
    F.box(mb, u0, u1, dface - 0.06, dface + dt, z0 + hb - 0.20, z0 + hb, mat)  # rail
    posts = sorted(posts)
    pw = 0.65
    for p in posts:
        F.box(mb, p - pw, p + pw, dface - 0.08, dface + dt, z0 + 0.28, z0 + hb - 0.20, mat)
    spacing = 0.30 if lod == 0 else 0.45
    edges = [u0 - pw] + posts + [u1 + pw]
    for a, b in zip(edges, edges[1:]):
        a2, b2 = a + pw + 0.12, b - pw - 0.12
        if b2 - a2 < 0.2:
            continue
        n = max(1, int((b2 - a2) / spacing))
        for i in range(n + 1):
            uu = a2 + (b2 - a2) * i / n
            baluster(mb, F, uu, dface + dt / 2, z0 + 0.28, z0 + hb - 0.20, lod, mat)


def entablature(mb, F, u0, u1, dface, dback, posts, lod, mat, zoff=0.0):
    z = zc(P["order_top"]) + zoff
    za, zf, zco = z + P["architrave"], z + P["architrave"] + P["frieze"], z + P["architrave"] + P["frieze"] + P["cornice"]
    if lod >= 2:
        F.box(mb, u0, u1, dface, dback, z, zf, mat)
        F.box(mb, u0 - 0.6, u1 + 0.6, dface - 0.9, dback, zf, zco, mat)
        return zco
    F.box(mb, u0, u1, dface, dback, z, za - 0.25, mat)                 # architrave fascia 1
    F.box(mb, u0, u1, dface - 0.06, dback, za - 0.25, za, mat)         # fascia 2 + taenia
    F.box(mb, u0, u1, dface, dback, za, zf, mat)                       # frieze
    if lod == 0:  # triglyphs over posts and mid-intervals
        tg = sorted(set([round(p, 3) for p in posts] + [round((a + b) / 2, 3) for a, b in zip(posts, posts[1:])]))
        for t in tg:
            for k in (-1, 0, 1):
                uu = t + k * 0.24
                F.box(mb, uu - 0.09, uu + 0.09, dface - 0.07, dface, za + 0.05, zf - 0.05, mat)
            F.box(mb, t - 0.36, t + 0.36, dface - 0.07, dface, zf - 0.12, zf - 0.02, mat)  # capital band
    F.box(mb, u0 - 0.2, u1 + 0.2, dface - 0.35, dback, zf, zf + 0.25, mat)            # bed mould
    F.box(mb, u0 - 0.9, u1 + 0.9, dface - 1.10, dback, zf + 0.25, zf + 0.75, mat)     # corona
    F.box(mb, u0 - 0.8, u1 + 0.8, dface - 1.00, dback, zf + 0.75, zco, mat)           # cymatium
    if lod == 0:  # mutule blocks under corona
        for t in posts:
            F.box(mb, t - 0.36, t + 0.36, dface - 1.0, dface - 0.35, zf + 0.15, zf + 0.25, mat)
    return zco - zoff


def bays(u0, u1, bay):
    n = max(1, round((u1 - u0) / bay))
    s = (u1 - u0) / n
    return n, s


def base_and_basement(mb, F, u0, u1, dv, centers, ww, lod, mat_base, mat_up, back, doors=()):
    """Granite plinth/basement from datum to plinth top, rusticated marble storey above."""
    zp = zc(P["plinth"])
    zb = zc(P["base_top"])
    # basement windows where exposed by the slope (two storeys below Constitution grade)
    open_low = []
    for c in centers:
        g = F.grade(c)
        for (a, b) in ((zc(-6.3), zc(-4.3)), (zc(-2.9), zc(-0.9))):
            if a > g + 0.35:
                open_low.append((c - ww * 0.45, c + ww * 0.45, a, b))
    rusticated(mb, F, u0, u1, 0.0, zp, dv, dv + back, open_low, mat_base, 0.9, lod)
    for (a0, a1, b0, b1) in open_low:
        window(mb, F, a0, a1, b0, b1, dv, 0.30, lod, kind="two", sill_mat=mat_base)
    bw = P["base_win_w"] / 2
    open_b = [(c - bw, c + bw, zc(1.9), zc(6.0)) for c in centers]
    open_b += list(doors)
    rusticated(mb, F, u0, u1, zp, zb, dv, dv + back, open_b, mat_up, 0.58, lod)
    for o in open_b[:len(centers)]:  # round-arched base windows (E11 / E15)
        arched_window(mb, F, o[0], o[1], o[2], o[3], dv, 0.34, lod, kind="two", mat=mat_up)
    # band / stylobate
    F.box(mb, u0, u1, dv - 0.15, dv + back, zb, zc(P["band_top"]), mat_up)


def order_windows(mb, F, centers, dwall, lod, mat, ww=1.45):
    ops = []
    for c in centers:
        ops.append((c - ww / 2, c + ww / 2, zc(8.6), zc(12.9), "pn"))
        ops.append((c - ww / 2, c + ww / 2, zc(14.6), zc(17.6), "up"))
    for (a, b, z0, z1, t) in ops:
        window(mb, F, a, b, z0, z1, dwall, 0.36, lod, kind="sash", hood=(t == "pn"), surround=(t == "up"),
               sill_mat=mat)
    return [o[:4] for o in ops]


def pilaster(mb, F, u, d, lod, mat, w=1.1):
    z0, z1 = zc(P["band_top"]), zc(P["order_top"])
    if lod >= 2:
        F.box(mb, u - w / 2, u + w / 2, d - 0.3, d, z0, z1, mat)
        return
    F.box(mb, u - w / 2 - 0.1, u + w / 2 + 0.1, d - 0.42, d, z0, z0 + 0.5, mat)
    F.box(mb, u - w / 2, u + w / 2, d - 0.32, d, z0 + 0.5, z1 - 0.6, mat)
    if lod == 0:  # flutes as shallow fillets
        for k in range(5):
            uu = u - w / 2 + w * (k + 0.5) / 5
            F.box(mb, uu - 0.05, uu + 0.05, d - 0.36, d - 0.32, z0 + 0.9, z1 - 1.0, mat)
    F.box(mb, u - w / 2 - 0.05, u + w / 2 + 0.05, d - 0.37, d, z1 - 0.6, z1 - 0.3, mat)
    F.box(mb, u - w / 2 - 0.15, u + w / 2 + 0.15, d - 0.47, d, z1 - 0.3, z1, mat)


def pilastrade_facade(mb, F, lod, mat_up, mat_base, pav_bays=5, u_end=None, recess_pavilion=False):
    """Secondary fronts: flush wall, pilasters per bay, central projecting pavilion.
    u_end stops the pilastrade short of a corner-pavilion return (Delaware Ave)."""
    T = P["wall_t"]
    n, s = bays(0, F.L if u_end is None else u_end, P["bay"])
    mid = n // 2
    pav = set(range(mid - pav_bays // 2, mid + pav_bays // 2 + 1)) if n > pav_bays + 4 else set()
    pv = -P["pav_proj"]
    # group bays into runs (normal / pavilion)
    runs = []
    for i in range(n):
        dv = pv if i in pav else 0.0
        if runs and runs[-1][2] == dv:
            runs[-1][1] = i + 1
        else:
            runs.append([i, i + 1, dv])
    zb, zt = zc(P["band_top"]), zc(P["order_top"])
    for (i0, i1, dv) in runs:
        u0, u1 = i0 * s, i1 * s
        if dv and recess_pavilion:  # Delaware centre pavilion: pier | columns in antis | pier (E11, low-res)
            corner_return(mb, F, u0, u1, lod)
            continue
        centers = [(i + 0.5) * s for i in range(i0, i1)]
        base_and_basement(mb, F, u0, u1, dv, centers, 1.65, lod, mat_base, mat_up, T)
        ops = [(c - 0.725, c + 0.725, z0, z1) for c in centers
               for (z0, z1) in ((zc(8.6), zc(12.9)), (zc(14.6), zc(17.6)))]
        wall_with_openings(mb, F, u0, u1, zb, zt, dv, dv + T, ops, mat_up)
        order_windows(mb, F, centers, dv, lod, mat_up)
        posts = [i * s for i in range(i0, i1 + 1)]
        for p in posts:
            pilaster(mb, F, p, dv, lod, mat_up, w=1.1 if dv == 0 else 1.25)
        zco = entablature(mb, F, u0, u1, dv - 0.35, dv + T, posts, lod, mat_up, zoff=0.015 if dv else 0.0)
        balustrade(mb, F, u0, u1, dv - 0.35, zco, posts, lod, mat_up, solid=(dv != 0))
    return n, s


def constitution_facade(mb, F, lod):
    """South front: west pavilion, 34-column loggia, east pavilion. F spans u in [chamfer, W]."""
    mat, matb = "M_F02_SOB_MarbleVermont", "M_F02_SOB_GraniteNH"
    T = P["wall_t"]
    u_start = P["chamfer"]
    uwp = u_start + P["return_w"]
    uep = F.L - P["pav_w_east"]
    pv = -P["pav_proj"]
    zb, zt = zc(P["band_top"]), zc(P["order_top"])
    corner_return(mb, F, u_start, uwp, lod)
    # --- east end pavilion
    for (a, b) in ((uep, F.L),):
        c = (a + b) / 2
        base_and_basement(mb, F, a, b, pv, [c], 1.6, lod, matb, mat, T + 0.8)
        ops = [(c - 0.9, c + 0.9, zc(8.6), zc(12.9)), (c - 0.9, c + 0.9, zc(14.6), zc(17.6))]
        wall_with_openings(mb, F, a, b, zb, zt, pv, pv + T, ops, mat)
        window(mb, F, c - 0.9, c + 0.9, zc(8.6), zc(12.9), pv, 0.36, lod, hood=True, sill_mat=mat)
        window(mb, F, c - 0.9, c + 0.9, zc(14.6), zc(17.6), pv, 0.36, lod, surround=True, sill_mat=mat)
        posts = [a + 0.75, a + 2.1, b - 2.1, b - 0.75]
        for p in posts:
            pilaster(mb, F, p, pv, lod, mat, w=1.15)
        zco = entablature(mb, F, a, b, pv - 0.35, pv + T, posts, lod, mat, zoff=0.015)
        balustrade(mb, F, a, b, pv - 0.35, zco, [a + 1.4, b - 1.4], lod, mat, solid=True)
    # --- loggia section
    a, b = uwp, uep
    nc = P["n_columns"]
    r = P["col_d"] / 2
    cols = [a + 1.0 + (b - a - 2.0) * i / (nc - 1) for i in range(nc)]
    centers = [(p + q) / 2 for p, q in zip(cols, cols[1:])]
    base_and_basement(mb, F, a, b, 0.0, centers, 1.65, lod, matb, mat, T)
    dl = P["loggia_depth"]
    # loggia floor (top of band) carried back to the recessed wall
    F.box(mb, a, b, 0.0, dl + T, zc(P["base_top"]), zb, mat)
    ops = [(c - 0.725, c + 0.725, z0, z1) for c in centers for (z0, z1) in ((zc(8.6), zc(12.9)), (zc(14.6), zc(17.6)))]
    wall_with_openings(mb, F, a, b, zb, zt, dl, dl + T, ops, mat)
    order_windows(mb, F, centers, dl, lod, mat)
    if lod == 0:  # loggia-wall pilasters (responds) behind each column
        for p in cols:
            F.box(mb, p - 0.45, p + 0.45, dl - 0.12, dl, zb, zt, mat)
    dcol = 1.0
    for p in cols:
        x, y, _ = F.w(p, dcol, 0)
        column(mb, x, y, zb, zt, lod, mat)
    dface = dcol - r * 0.86 - 0.05  # architrave flush with the column top
    zco = entablature(mb, F, a, b, dface, dl + T, cols, lod, mat)
    if lod <= 1:  # coffered loggia soffit beams between columns
        for p in cols:
            F.box(mb, p - 0.35, p + 0.35, dface, dl, zt - 0.45, zt, mat)
    balustrade(mb, F, a, b, dface, zco, cols, lod, mat)
    return cols


def recessed_bay(mb, F, p0, p1, pv, lod, mat, win_w, dr=2.0):
    """Recessed bay between two solid piers: two free-standing Doric columns in antis standing in the
    pier plane, a tall round-arched window in the back wall with a balustraded balconette (E11/E15/E16).
    Returns the column positions (u)."""
    T = P["wall_t"]
    zb, zt, zbt = zc(P["base_top"]), zc(P["order_top"]), zc(P["band_top"])
    c = (p0 + p1) / 2
    r = P["col_d"] / 2
    F.box(mb, p0 - 0.6, p0, pv + T, pv + dr + T, zbt, zt, mat)    # recess returns
    F.box(mb, p1, p1 + 0.6, pv + T, pv + dr + T, zbt, zt, mat)
    F.box(mb, p0, p1, pv, pv + dr + T, zb, zbt, mat)               # recess floor
    tw = (c - win_w / 2, c + win_w / 2, zc(8.6), zc(17.9))
    wall_with_openings(mb, F, p0, p1, zbt, zt, pv + dr, pv + dr + T, [tw], mat)
    arched_window(mb, F, tw[0], tw[1], tw[2], tw[3], pv + dr, 0.36, lod, kind="tall", mat=mat,
                  state=ATLAS_DARK[0])
    if lod <= 1:  # balconette at the window sill
        hw = win_w / 2 + 0.2
        F.box(mb, c - hw, c + hw, pv + dr - 0.45, pv + dr, zbt, zbt + 0.18, mat)
        F.box(mb, c - hw, c + hw, pv + dr - 0.45, pv + dr, zbt + 0.85, zbt + 1.0, mat)
        nb = max(3, int(win_w / 0.33)) if lod == 0 else 4
        for k in range(nb + 1):
            uu = c - hw + 0.2 + (2 * hw - 0.4) * k / nb
            baluster(mb, F, uu, pv + dr - 0.22, zbt + 0.18, zbt + 0.85, lod, mat)
        F.box(mb, c - 0.3, c + 0.3, pv + dr - 0.12, pv + dr, tw[3] - 0.15, tw[3] + 0.55, mat)  # keystone
    cols = [p0 + r + 0.25, p1 - r - 0.25]
    for p in cols:
        x, y, _ = F.w(p, pv + r + 0.05, 0)  # front of shaft in the pier plane
        column(mb, x, y, zbt, zt, lod, mat)
    return cols


def framed_pier(mb, F, a, b, pv, lod, mat):
    """Solid pier with a framed piano-nobile window (hood, consoles, surround) and a carved cartouche
    above it: the return bays of the corner pavilion (E11 ornament; E15/E16 framed windows)."""
    T = P["wall_t"]
    zt, zbt = zc(P["order_top"]), zc(P["band_top"])
    cc = (a + b) / 2
    ops = [(cc - 0.7, cc + 0.7, zc(8.6), zc(12.6))]
    wall_with_openings(mb, F, a, b, zbt, zt, pv, pv + T, ops, mat)
    window(mb, F, cc - 0.7, cc + 0.7, zc(8.6), zc(12.6), pv, 0.36, lod, hood=True, surround=True, sill_mat=mat,
           pediment=True)
    cartouche(mb, F, cc, pv, zc(14.6), mat, lod)


def pavilion_base(mb, F, u0, u1, pv, arches, lod, extra_openings=()):
    """Granite plinth, rusticated marble storey with tall round-arched windows, band course."""
    mat, matb = "M_F02_SOB_MarbleVermont", "M_F02_SOB_GraniteNH"
    T = P["wall_t"]
    zp, zb, zbt = zc(P["plinth"]), zc(P["base_top"]), zc(P["band_top"])
    bw = P["base_win_w"] / 2
    ops = [(cc - bw, cc + bw, zc(1.9), zc(6.0)) for cc in arches]
    low = []  # basement windows where the north slope exposes them (as base_and_basement)
    for cc in arches:
        for (za, zz) in ((zc(-6.3), zc(-4.3)), (zc(-2.9), zc(-0.9))):
            if za > F.grade(cc) + 0.35:
                low.append((cc - 0.74, cc + 0.74, za, zz))
    rusticated(mb, F, u0, u1, 0.0, zp, pv, pv + T, low, matb, 0.9, lod)
    for (a0, a1, b0, b1) in low:
        window(mb, F, a0, a1, b0, b1, pv, 0.30, lod, kind="two", sill_mat=matb)
    rusticated(mb, F, u0, u1, zp, zb, pv, pv + T, ops + list(extra_openings), mat, 0.58, lod)
    for o in ops:
        arched_window(mb, F, o[0], o[1], o[2], o[3], pv, 0.34, lod, kind="two", mat=mat)
    F.box(mb, u0, u1, pv - 0.15, pv + T, zb, zbt, mat)


def corner_return(mb, F, u0, u1, lod):
    """Return of the SW corner pavilion onto a street front, repeating the chamfer motif at smaller
    scale (E11, E15, E16): framed-window pier | recessed bay with 2 columns and a tall arched window |
    framed-window pier, over three arched base windows; entablature and solid attic."""
    mat = "M_F02_SOB_MarbleVermont"
    T = P["wall_t"]
    pv = -0.4
    rw = (u1 - u0 - P["return_recess"]) / 2
    p0, p1 = u0 + rw, u1 - rw
    pavilion_base(mb, F, u0, u1, pv, [u0 + rw / 2, (p0 + p1) / 2, u1 - rw / 2], lod)
    framed_pier(mb, F, u0, p0, pv, lod, mat)
    framed_pier(mb, F, p1, u1, pv, lod, mat)
    cols = recessed_bay(mb, F, p0, p1, pv, lod, mat, win_w=2.2)
    zco = entablature(mb, F, u0, u1, pv, pv + 2.0 + T, [u0 + 0.5] + cols + [u1 - 0.5], lod, mat, zoff=0.008)
    balustrade(mb, F, u0, u1, pv, zco, [], lod, mat, solid=True)


def corner_rotunda(mb, F, lod):
    """SW chamfered rotunda pavilion, matched to E11 (c.1909) and E15/E16 (modern) photographs:
    two PLAIN solid piers; a recessed central bay with two free-standing Doric columns in antis before
    one tall round-arched window with a balconette carried on console brackets over the doorway; one
    round-arched bronze doorway between wide granite podium blocks with a projecting stair; plain
    rusticated base; entablature and solid attic with a low raised tablet block (flag socket above)."""
    mat, matb, bd = "M_F02_SOB_MarbleVermont", "M_F02_SOB_GraniteNH", "M_F02_SOB_BronzeDoor"
    T = P["wall_t"]
    L = F.L
    c = L / 2
    zp, zbt = zc(P["plinth"]), zc(P["band_top"])
    pv = -0.4
    p0, p1 = c - P["corner_bay"] / 2, c + P["corner_bay"] / 2
    # --- base: plain rusticated chamfer with the single doorway
    door = (c - 1.3, c + 1.3, zp, zc(6.0))
    pavilion_base(mb, F, 0, L, pv, [], lod, extra_openings=[door])
    a, b, z0, z1 = door
    zs = z1 - (b - a) / 2
    F.box(mb, a, b, pv + 0.45, pv + 0.55, z0, zs - 0.08, bd)                   # bronze leaves
    F.box(mb, a, b, pv + 0.42, pv + 0.55, zs - 0.08, zs + 0.06, bd)            # transom
    state = RNG.randrange(16)
    if lod <= 1:
        arch_spandrels(mb, F, a, b, zs, pv, pv + 0.40, mat, lod)
        F.box(mb, a, b, pv + 0.48, pv + 0.50, zs + 0.06, z1, "M_F02_SOB_GlassInterior", atlas_uv(state))
    if lod == 0:
        F.box(mb, c - 0.03, c + 0.03, pv + 0.40, pv + 0.45, z0, zs - 0.08, bd)  # meeting stile
        for zz in (z0 + 0.5, z0 + 1.9):
            for (pa, pb) in ((a + 0.15, c - 0.12), (c + 0.12, b - 0.15)):
                F.box(mb, pa, pb, pv + 0.41, pv + 0.45, zz, zz + 1.1, bd)      # raised panels
        F.box(mb, c - 0.28, c + 0.28, pv - 0.10, pv, z1 - 0.12, z1 + 0.60, mat)  # keystone
        F.box(mb, a - 0.35, b + 0.35, pv - 0.10, pv, zs - 0.30, zs - 0.10, mat)  # impost band
    if lod <= 1:  # console brackets flanking the door head, carrying the band / balconette (E11, E15)
        for u in (a - 0.55, b + 0.15):
            F.box(mb, u, u + 0.40, pv - 0.55, pv, z1 + 0.25, zbt - 0.6, mat)
            F.box(mb, u - 0.05, u + 0.45, pv - 0.65, pv, zbt - 0.6, zbt - 0.15, mat)
    # --- stair between wide granite podium blocks spanning the chamfer (E11, E16)
    g = P["z_const"]
    nst, run, hw = 6, 0.42, 2.4
    rise = (zp - g) / nst
    for k in range(nst):
        F.box(mb, c - hw, c + hw, pv - run * (nst - k), pv + 0.2, g + k * rise - 0.3, g + (k + 1) * rise, matb)
    depth = run * nst + 0.3
    for (ca, cb) in ((0.6, c - hw), (c + hw, L - 0.6)):
        F.box(mb, ca, cb, pv - depth, pv + 0.2, g - 0.3, zp + 0.45, matb)
        F.box(mb, ca - 0.08, cb + 0.08, pv - depth - 0.10, pv + 0.2, zp + 0.45, zp + 0.62, matb)  # coping
    # --- order zone: plain piers and the recessed central bay
    for (a, b) in ((0.0, p0), (p1, L)):
        F.box(mb, a, b, pv, pv + T, zbt, zc(P["order_top"]), mat)
    cols = recessed_bay(mb, F, p0, p1, pv, lod, mat, win_w=3.0)
    zco = entablature(mb, F, 0, L, pv, pv + 2.0 + T, [0.55] + cols + [L - 0.55], lod, mat)
    balustrade(mb, F, 0, L, pv, zco, [], lod, mat, solid=True)
    # low raised central attic block carrying the tablet and the flagpole (E11, E15, E16)
    ha = P["balustrade"] + P["attic_raise"]
    F.box(mb, c - 4.2, c + 4.2, pv - 0.05, pv + 1.6, zco, zco + ha, mat)
    if lod <= 1:
        F.box(mb, c - 4.4, c + 4.4, pv - 0.20, pv + 1.6, zco + ha - 0.25, zco + ha, mat)  # coping
        F.box(mb, c - 3.0, c + 3.0, pv - 0.13, pv - 0.05, zco + 0.40, zco + ha - 0.45, mat)  # blank tablet


def court_facade(mb, F, lod):
    mat = "M_F02_SOB_LimestoneIndiana"
    T = 0.6
    zcourt = zc(-3.5)
    top = zc(P["order_top"] + P["architrave"] + P["frieze"])
    n, s = bays(0, F.L, P["bay"])
    floors = [zcourt + 1.0 + 3.6 * k for k in range(int((top - zcourt - 2.0) / 3.6))]
    centers = [(i + 0.5) * s for i in range(n)]
    ops = [(c - 0.65, c + 0.65, f, f + 2.3) for c in centers for f in floors]
    wall_with_openings(mb, F, 0, F.L, 0.0, top, 0.0, T, ops, mat)
    for (a, b, z0, z1) in ops:
        window(mb, F, a, b, z0, z1, 0.0, 0.25, max(lod, 1), kind="two", sill_mat=mat)
    F.box(mb, 0, F.L, -0.25, T, top, top + 0.35, mat)    # coping cornice
    F.box(mb, 0, F.L, 0.0, 0.35, top + 0.35, top + 1.1, mat)  # parapet


def roof(mb, lod):
    W, D, a, C = P["W"], P["D"], P["wing"], P["chamfer"]
    zr = zc(P["order_top"] + P["architrave"] + P["frieze"]) - 0.2
    m = "M_F02_SOB_RoofMembrane"
    t = 0.4
    # non-overlapping slabs (coplanar overlaps render black in Cycles and flicker in UE)
    mb.box((C, 0.0, zr - t), (W, a, zr), m)                   # south wing
    mb.box((0.0, a, zr - t), (a, D - a, zr), m)               # west wing
    mb.box((0.0, D - a, zr - t), (W, D, zr), m)               # north wing
    mb.box((W - a, a, zr - t), (W, D - a, zr), m)             # east wing
    mb.box((0.0, C, zr - t), (C, a, zr), m)                   # SW patch
    # chamfer triangle
    tri = [(0.0, C), (C, 0.0), (C, C)]
    pts = [(x, y, zr - t) for x, y in tri] + [(x, y, zr) for x, y in tri]
    faces = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    if signed_volume(pts, faces) < 0:
        faces = [tuple(reversed(f)) for f in faces]
    mb._add(pts, faces, m)
    if lod == 0:  # low skylight ridges over corridor lines (APPROXIMATE)
        g = "M_F02_SOB_WindowFramePaint"
        for (x0, y0, x1, y1) in ((C + 4, a / 2 - 0.8, W - a / 2 - 2, a / 2 + 0.8),
                                 (a / 2 - 0.8, C + 4, a / 2 + 0.8, D - a / 2 - 2),
                                 (a / 2 + 2, D - a / 2 - 0.8, W - a / 2 - 2, D - a / 2 + 0.8),
                                 (W - a / 2 - 0.8, a / 2 + 2, W - a / 2 + 0.8, D - a / 2 - 2)):
            mb.box((x0, y0, zr), (x1, y1, zr + 0.6), g)


def site(mb):
    """Optional sloped site apron + Constitution terrace + court floor (placement helper)."""
    W, D, A = P["W"], P["D"], 9.0
    m = "M_F02_SOB_SitePaving"
    g = "M_F02_SOB_GraniteNH"
    zt = P["z_const"]

    def slab(x0, x1, y0, y1, ztop_fn, mat):
        pts = [(x0, y0, 0.0), (x1, y0, 0.0), (x1, y0, ztop_fn(y0)), (x0, y0, ztop_fn(y0)),
               (x0, y1, 0.0), (x1, y1, 0.0), (x1, y1, ztop_fn(y1)), (x0, y1, ztop_fn(y1))]
        mb.hexa(pts, mat)

    slab(-A, W + A, -A, -3.5, lambda y: zt - 0.15, m)           # Constitution sidewalk
    slab(-A, W + A, -3.5, 0.0, lambda y: zt, g)                 # granite terrace
    slab(-A, 0.0, 0.0, D, grade_at_y, m)                        # Delaware side slope
    slab(W, W + A, 0.0, D, grade_at_y, m)                       # First St side slope
    slab(-A, W + A, D, D + A, lambda y: P["grade_cst"], m)      # C St sidewalk
    C = P["chamfer"]
    tri = [(0.0, 0.0), (C, 0.0), (0.0, C)]                      # corner terrace under the chamfer
    pts = [(x, y, 0.0) for x, y in tri] + [(x, y, zt) for x, y in tri]
    faces = [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)]
    if signed_volume(pts, faces) < 0:
        faces = [tuple(reversed(f)) for f in faces]
    mb._add(pts, faces, g)
    a = P["wing"]
    mb.box((a, a, 0.0), (W - a, D - a, zc(-3.5)), m)           # court floor


def build_lod(lod):
    mb = MB()
    W, D, C, a = P["W"], P["D"], P["chamfer"], P["wing"]
    RNG.seed(P["seed"])  # same window states in every LOD
    CUR_LOD[0] = lod
    FS = Frame(0, 0, 1, 0, W, "S")                    # Constitution Ave
    e = 0.004  # W/E fronts own the outer corners: pushed out e and up e/2 so nothing is coplanar
    FW = Frame(-e, D + e, 0, -1, D - C + e, "W", dz=e / 2)   # Delaware Ave (north -> south)
    FN = Frame(W, D, -1, 0, W, "N")                          # C St
    FE = Frame(W + e, 0, 0, 1, D + e, "E", dz=e / 2)         # First St
    s2 = math.sqrt(0.5)
    FC = Frame(0, C, s2, -s2, C * math.sqrt(2), "C", dz=e)   # SW rotunda chamfer
    constitution_facade(mb, FS, lod)
    pilastrade_facade(mb, FW, lod, "M_F02_SOB_MarbleVermont", "M_F02_SOB_GraniteNH",
                      u_end=FW.L - P["return_w"], recess_pavilion=True)
    corner_return(mb, FW, FW.L - P["return_w"], FW.L, lod)
    pilastrade_facade(mb, FN, lod, "M_F02_SOB_MarbleGeorgia", "M_F02_SOB_GraniteNH")
    pilastrade_facade(mb, FE, lod, "M_F02_SOB_MarbleGeorgia", "M_F02_SOB_GraniteNH")
    corner_rotunda(mb, FC, lod)
    # court fronts face into the court (viewer inside the court)
    court_facade(mb, Frame(W - a, a, -1, 0, W - 2 * a, "CS"), lod)    # south wing court face
    court_facade(mb, Frame(a + e, a - e, 0, 1, D - 2 * a + 2 * e, "CW", dz=e / 2), lod)  # west wing court face
    court_facade(mb, Frame(a, D - a, 1, 0, W - 2 * a, "CN"), lod)     # north wing court face
    court_facade(mb, Frame(W - a - e, D - a + e, 0, -1, D - 2 * a + 2 * e, "CE", dz=e / 2), lod)
    roof(mb, lod)
    return mb


# ---------------------------------------------------------------------------
# Textures (procedural, tileable, generated with a fixed seed)
# ---------------------------------------------------------------------------
def periodic_noise(n, scale, rng):
    w = rng.standard_normal((n, n))
    f = np.fft.fft2(w)
    ky = np.fft.fftfreq(n)[:, None]
    kx = np.fft.fftfreq(n)[None, :]
    k = np.sqrt(kx ** 2 + ky ** 2)
    filt = np.exp(-(k * n / scale) ** 2)
    out = np.real(np.fft.ifft2(f * filt))
    out -= out.min()
    out /= max(out.max(), 1e-9)
    return out


def save_png(name, arr):
    """arr HxWx3 or HxWx4 float 0..1 (row 0 = top)."""
    os.makedirs(TEX, exist_ok=True)
    h, w = arr.shape[:2]
    if arr.shape[2] == 3:
        arr = np.concatenate([arr, np.ones((h, w, 1))], axis=2)
    img = bpy.data.images.new(name, w, h, alpha=False)
    img.pixels.foreach_set(np.flipud(arr).astype(np.float32).ravel())
    path = os.path.join(TEX, name + ".png")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    return path


def normal_from_height(hgt, strength):
    gy, gx = np.gradient(hgt)
    nx, ny = -gx * strength, gy * strength
    nz = np.ones_like(hgt)
    l = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    return np.stack([nx / l * 0.5 + 0.5, ny / l * 0.5 + 0.5, nz / l * 0.5 + 0.5], axis=2)


def stone_set(name, base, vein, rng, n=1024, vein_amt=0.10, speck=0.0, rough=(0.45, 0.65)):
    n1 = periodic_noise(n, 6, rng)
    n2 = periodic_noise(n, 40, rng)
    n3 = periodic_noise(n, 160, rng)
    yy, xx = np.mgrid[0:n, 0:n] / n
    turb = n1 * 3.0 + n2 * 0.8
    veins = np.abs(np.sin(2 * math.pi * (2 * xx + 1 * yy) + turb * 4.0)) ** 0.15
    v = 1 - veins
    col = np.array(base)[None, None, :] * (0.92 + 0.10 * n2[..., None] + 0.05 * n3[..., None])
    col = col * (1 - vein_amt * v[..., None]) + np.array(vein)[None, None, :] * (vein_amt * v[..., None])
    if speck:
        s = (rng.random((n, n)) < speck).astype(float)
        col = col * (1 - 0.35 * s[..., None])
    col = np.clip(col, 0, 1)
    r = rough[0] + (rough[1] - rough[0]) * (0.6 * n2 + 0.4 * n3)
    orm = np.stack([np.ones_like(r), r, np.zeros_like(r)], axis=2)  # glTF: G=rough, B=metal
    nm = normal_from_height(n3 * 0.6 + n2 * 0.4, 2.0)
    return (save_png(f"T_{name}_BC", col), save_png(f"T_{name}_ORM", orm), save_png(f"T_{name}_N", nm))


def glass_atlas(rng, n=1024):
    """4x4 cells: window interior states for the night read (FICTIONALISED dressing)."""
    bc = np.zeros((n, n, 3))
    em = np.zeros((n, n, 3))
    c = n // 4
    cold = np.array([0xDF, 0xDF, 0xD4]) / 255
    tung = np.array([0xC4, 0x9D, 0x63]) / 255
    dark = np.array([0.035, 0.045, 0.05])
    states = []
    ATLAS_DARK.clear()
    for i in range(16):
        k = rng.random()
        states.append("lit" if k < 0.22 else "blind" if k < 0.55 else "litblind" if k < 0.65 else "dark")
    for i, st in enumerate(states):
        cx, cy = i % 4, i // 4
        y0 = n - (cy + 1) * c  # row 0 is top in the array, v=0 is bottom in UV
        cell = np.zeros((c, c, 3)) + dark
        ecell = np.zeros((c, c, 3))
        yy = np.linspace(0, 1, c)[:, None]
        reflect = 0.04 * (1 - yy)  # sky reflection gradient
        cell += reflect
        if st in ("blind", "litblind"):
            drop = 0.25 + 0.5 * rng.random()
            mask = (yy < drop).astype(float) * np.ones((1, c))
            slats = (np.sin(np.linspace(0, 1, c)[:, None] * c / 3.0) > -0.2).astype(float)
            bl = cold * 0.55 * (0.85 + 0.15 * slats)[..., None]
            cell = cell * (1 - mask[..., None]) + bl * mask[..., None]
            if st == "litblind":
                ecell += tung * 0.45 * mask[..., None]
        if st == "lit":
            cell = cell * 0.5 + tung * 0.35
            ecell += tung * 0.85 * np.ones((c, c, 1))
        bc[y0:y0 + c, cx * c:(cx + 1) * c] = cell
        em[y0:y0 + c, cx * c:(cx + 1) * c] = ecell
    ATLAS_DARK.extend(i for i, st in enumerate(states) if st == "dark")
    return save_png("T_SOB_GlassInterior_BC", np.clip(bc, 0, 1)), save_png("T_SOB_GlassInterior_E", np.clip(em, 0, 1))


def flat_set(name, col, rough, metal, rng, n=512, var=0.06):
    n1 = periodic_noise(n, 12, rng)
    c = np.clip(np.array(col)[None, None, :] * (1 - var + 2 * var * n1[..., None]), 0, 1)
    orm = np.stack([np.ones_like(n1), rough + 0.1 * (n1 - 0.5), np.full_like(n1, metal)], axis=2)
    return save_png(f"T_{name}_BC", c), save_png(f"T_{name}_ORM", np.clip(orm, 0, 1))


def make_materials():
    rng = np.random.default_rng(P["seed"])
    tex = {
        "M_F02_SOB_MarbleVermont": stone_set("SOB_MarbleVermont", (0.71, 0.70, 0.66), (0.50, 0.51, 0.50), rng),
        "M_F02_SOB_MarbleGeorgia": stone_set("SOB_MarbleGeorgia", (0.70, 0.66, 0.64), (0.55, 0.50, 0.50), rng),
        "M_F02_SOB_GraniteNH": stone_set("SOB_GraniteNH", (0.44, 0.44, 0.43), (0.3, 0.3, 0.3), rng,
                                         vein_amt=0.0, speck=0.08, rough=(0.55, 0.75)),
        "M_F02_SOB_LimestoneIndiana": stone_set("SOB_LimestoneIndiana", (0.66, 0.62, 0.53), (0.55, 0.52, 0.45), rng,
                                                vein_amt=0.03, rough=(0.65, 0.85)),
        "M_F02_SOB_WindowFramePaint": flat_set("SOB_WindowFramePaint", (0.075, 0.10, 0.09), 0.45, 0.0, rng),
        "M_F02_SOB_BronzeDoor": flat_set("SOB_BronzeDoor", (0.13, 0.10, 0.07), 0.42, 0.90, rng),
        "M_F02_SOB_RoofMembrane": flat_set("SOB_RoofMembrane", (0.17, 0.17, 0.17), 0.85, 0.0, rng, var=0.12),
        "M_F02_SOB_SitePaving": flat_set("SOB_SitePaving", (0.50, 0.49, 0.46), 0.85, 0.0, rng, var=0.10),
        "M_F02_SOB_GlassInterior": glass_atlas(rng),
    }
    mats = {}
    for name in MATS:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        t = tex[name]

        def img_node(path, non_color=False, loc=(-600, 0)):
            n = nt.nodes.new("ShaderNodeTexImage")
            n.image = bpy.data.images.load(path)
            if non_color:
                n.image.colorspace_settings.name = "Non-Color"
            n.location = loc
            return n

        bc = img_node(t[0])
        nt.links.new(bc.outputs["Color"], bsdf.inputs["Base Color"])
        if name == "M_F02_SOB_GlassInterior":
            em = img_node(t[1], loc=(-600, -300))
            nt.links.new(em.outputs["Color"], bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = 1.0
            bsdf.inputs["Roughness"].default_value = 0.06
            bsdf.inputs["Metallic"].default_value = 0.0
            bsdf.inputs["Specular IOR Level"].default_value = 0.8
        else:
            orm = img_node(t[1], non_color=True, loc=(-600, -300))
            sep = nt.nodes.new("ShaderNodeSeparateColor")
            nt.links.new(orm.outputs["Color"], sep.inputs["Color"])
            nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
            nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
            if len(t) > 2:
                nm = img_node(t[2], non_color=True, loc=(-600, -600))
                nmap = nt.nodes.new("ShaderNodeNormalMap")
                nmap.inputs["Strength"].default_value = 0.6
                nt.links.new(nm.outputs["Color"], nmap.inputs["Color"])
                nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
        mats[name] = m
    return mats


# ---------------------------------------------------------------------------
# Blender objects
# ---------------------------------------------------------------------------
def to_object(mb, name, mats):
    me = bpy.data.meshes.new(name)
    me.from_pydata(mb.v, [], mb.f)
    me.update(calc_edges=True)
    for m in MATS:
        me.materials.append(mats[m])
    nf = len(me.polygons)
    me.polygons.foreach_set("material_index", np.array(mb.m[:nf], dtype=np.int32))
    me.update()
    # world-scale box-projection UVs
    uvl = me.uv_layers.new(name="UVMap")
    nl = len(me.loops)
    co = np.zeros(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    lv = np.zeros(nl, dtype=np.int64)
    me.loops.foreach_get("vertex_index", lv)
    fn = np.zeros(nf * 3)
    me.polygons.foreach_get("normal", fn)
    fn = np.abs(fn.reshape(-1, 3))
    ls = np.zeros(nf, dtype=np.int64)
    me.polygons.foreach_get("loop_start", ls)
    lt = np.zeros(nf, dtype=np.int64)
    me.polygons.foreach_get("loop_total", lt)
    fidx = np.repeat(np.arange(nf), lt)
    mi = np.array(mb.m[:nf])
    tiles = np.array([UV_TILE[m] for m in MATS])[mi][fidx]
    ax = np.argmax(fn, axis=1)[fidx]
    p = co[lv]
    u = np.where(ax == 0, p[:, 1], p[:, 0])
    v = np.where(ax == 2, p[:, 1], p[:, 2])
    uv = np.stack([u / tiles, v / tiles], axis=1)
    for f, uvs in mb.uvo.items():
        if f < nf and len(uvs) == lt[f]:
            uv[ls[f]:ls[f] + lt[f]] = np.array(uvs)
    uvl.data.foreach_set("uv", uv.ravel())
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for poly in me.polygons:
        poly.use_smooth = False
    return ob


def collision(name_prefix, mats):
    W, D, a, C = P["W"], P["D"], P["wing"], P["chamfer"]
    top = zc(P["order_top"] + P["architrave"] + P["frieze"] + P["cornice"] + P["balustrade"])
    boxes = [((C, -0.8, 0), (W, a, top)), ((0, C, 0), (a, D, top)), ((a, D - a, 0), (W, D, top)),
             ((W - a, a, 0), (W, D - a, top)), ((0.5, 0.5, 0), (a, a, top))]
    obs = []
    for i, (lo, hi) in enumerate(boxes):
        mb = MB()
        mb.box(lo, hi, "M_F02_SOB_MarbleVermont")
        ob = to_object(mb, f"UCX_{name_prefix}_{i:02d}", mats)
        ob.data.materials.clear()
        obs.append(ob)
    return obs


def sockets():
    s = {
        "SOCKET_Grade_Constitution_SW": (0.0, 0.0, P["z_const"]),
        "SOCKET_Grade_Constitution_SE": (P["W"], 0.0, P["z_const"]),
        "SOCKET_Grade_CSt_NW": (0.0, P["D"], P["grade_cst"]),
        "SOCKET_Grade_CSt_NE": (P["W"], P["D"], P["grade_cst"]),
        "SOCKET_Entrance_Rotunda": (P["chamfer"] / 2 - 0.3, P["chamfer"] / 2 - 0.3, zc(P["plinth"])),
        # flagpole stands on the corner attic in E11 (c.1909) and E15/E16 (modern)
        "SOCKET_Flag_Corner_Attic": (P["chamfer"] / 2 + 0.6, P["chamfer"] / 2 + 0.6,
                                     zc(P["order_top"] + P["architrave"] + P["frieze"] + P["cornice"]
                                        + P["balustrade"] + P["attic_raise"])),
    }
    obs = []
    for n, loc in s.items():
        e = bpy.data.objects.new(n, None)
        e.empty_display_type = "ARROWS"
        e.location = loc
        bpy.context.scene.collection.objects.link(e)
        obs.append(e)
    return obs


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats = make_materials()
    stats = []
    objs = []
    for lod in (0, 1, 2):
        mb = build_lod(lod)
        ob = to_object(mb, f"{ASSET}_LOD{lod}", mats)
        objs.append(ob)
        stats.append((ob.name, len(ob.data.vertices), len(ob.data.polygons)))
    smb = MB()
    site(smb)
    so = to_object(smb, "SM_F02_SOB_SiteGrade_LOD0", mats)
    objs.append(so)
    stats.append((so.name, len(so.data.vertices), len(so.data.polygons)))
    objs += collision(ASSET, mats)
    objs += sockets()
    glb = os.path.join(OUT, f"{ASSET}.glb")
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=False,
                              export_apply=True, export_yup=True, export_image_format="AUTO",
                              export_extras=True)
    with open(os.path.join(OUT, "MESH_STATS.txt"), "w") as f:
        for n, v, p in stats:
            f.write(f"{n}: {v} verts, {p} faces\n")
    for n, v, p in stats:
        print(f"{n}: {v} verts, {p} faces")
    print("wrote", glb, os.path.getsize(glb), "bytes")


if __name__ == "__main__":
    main()
