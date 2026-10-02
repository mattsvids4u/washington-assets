#!/usr/bin/env python
"""DC-F01 v001 generator — C10 hard-lock background buildings, autumn 1963 state.

    python jobs/DC-F01/build.py            # clean rebuild of everything into jobs/DC-F01/out/
    python jobs/DC-F01/build.py folger     # rebuild one building (iteration; keeps other outputs)

Buildings (1963-facing names): Library of Congress Annex, Folger Shakespeare Library,
Cannon House Office Building. Every dimension below carries its provenance label:
  VERIFIED     stated by a named authoritative source (see EVIDENCE.md)
  PROBABLE     secondary source / consistent cross-check
  APPROXIMATE  reasoned estimate (no measured value reachable from this environment)
Reference images could not be opened in this cloud run (egress allowlist), so facade rhythm
details are APPROXIMATE until compared with the photo records listed in EVIDENCE.md.

Output per building: out/SM_F01_<Name>.glb with <name>_LOD0/1/2, UCX_ collision hulls and
SOCKET_ empties; out/textures/*.png (portable PBR sources); out/build_report.json.
Blender metres, Z up (glTF Y up on export); UE 5.8 glTF import gives centimetres.
Pivot: footprint bounding-box centre at grade (z = 0); +X east, +Y north (map-aligned).
"""
import hashlib
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy  # noqa: E402

import f01lib as L  # noqa: E402
import f01mat as M  # noqa: E402

FT = 0.3048
OUT = os.environ.get("F01_OUT", os.path.join(HERE, "out"))   # override only for rebuild-determinism checks
TEXDIR = os.path.join(OUT, "textures")
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"

GLASS = ["M_F01_Glass", "M_F01_Glass_NightLit"]


def glass_slot(key):
    """Deterministic ~35 % of windows on the night-lit slot (stable across rebuilds)."""
    h = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
    return 1 if (h % 100) < 35 else 0


def box_mats(m, x0, x1, y0, y1, z0, z1, side, top=None, bottom=None, n=None, s=None, e=None, w=None):
    """Axis box with per-face materials (n/s/e/w override `side`)."""
    if x1 - x0 < 1e-6 or y1 - y0 < 1e-6 or z1 - z0 < 1e-6:
        return
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    base = len(m.verts)
    f0 = len(m.faces)
    m.verts.extend(v)
    faces = [((0, 3, 2, 1), bottom or side), ((4, 5, 6, 7), top or side), ((0, 1, 5, 4), s or side),
             ((1, 2, 6, 5), e or side), ((2, 3, 7, 6), n or side), ((3, 0, 4, 7), w or side)]
    for f, mat in faces:
        m.faces.append((tuple(base + i for i in f), mat, None))
    m.shells.append((f0, len(m.faces)))


def flush_windows(m, fr, a0, a1, c_rows, w, h, spacing, b_face, lod, key, frame_mat="M_F01_Window_Frame_Dark"):
    """Simple windows for secondary (rear/court) walls: shallow 8 cm reveal box + glass."""
    n = max(1, int((a1 - a0) / spacing))
    for r, c0 in enumerate(c_rows):
        for i in range(n):
            ac = a0 + (i + 0.5) * (a1 - a0) / n
            gs = glass_slot(f"{key}-{r}-{i}")
            if lod >= 2:
                m.lbox(fr, ac - w / 2, ac + w / 2, b_face, b_face + 0.02, c0, c0 + h, GLASS[gs])
                continue
            # frame proud of the wall, glass slightly behind the frame face
            m.lbox(fr, ac - w / 2 - 0.06, ac + w / 2 + 0.06, b_face, b_face + 0.05, c0 - 0.06, c0, frame_mat)
            m.lbox(fr, ac - w / 2 - 0.06, ac + w / 2 + 0.06, b_face, b_face + 0.05, c0 + h, c0 + h + 0.06, frame_mat)
            m.lbox(fr, ac - w / 2 - 0.06, ac - w / 2, b_face, b_face + 0.05, c0, c0 + h, frame_mat)
            m.lbox(fr, ac + w / 2, ac + w / 2 + 0.06, b_face, b_face + 0.05, c0, c0 + h, frame_mat)
            m.lbox(fr, ac - w / 2, ac + w / 2, b_face, b_face + 0.025, c0, c0 + h, GLASS[gs])
            if lod == 0:
                m.lbox(fr, ac - 0.025, ac + 0.025, b_face + 0.025, b_face + 0.045, c0, c0 + h, frame_mat)
                m.lbox(fr, ac - w / 2, ac + w / 2, b_face + 0.025, b_face + 0.04, c0 + h * 0.5 - 0.025,
                       c0 + h * 0.5 + 0.025, frame_mat)      # transom 5 mm behind the mullion face


# =============================================================================
# FOLGER SHAKESPEARE LIBRARY (201 East Capitol St SE) — Paul P. Cret, 1929-32
# =============================================================================
FOLGER = dict(
    W=226 * FT,        # 68.88 m E-W  VERIFIED (NRHP amendment 2022, S3)
    D=111 * FT,        # 33.83 m N-S  VERIFIED (S3)
    H=48 * FT,         # 14.63 m      VERIFIED (S3) - taken as grade to top of attic
    zt=0.76,           # plinth / terrace top above East Capitol sidewalk  APPROXIMATE
    nbays=9,           # north window bays  VERIFIED (S2/S3)
    bay=15 * FT,       # 4.57 m  APPROXIMATE (nine bays = 135 ft lawn length, S4)
    win_w=6 * FT,      # 1.83 m  APPROXIMATE (= relief width; "long, narrow windows")
    relief=6 * FT,     # 1.83 m square  VERIFIED (Folger Collation S10)
    pil_w=1.4,         # fluted pilaster width  PROBABLE (ref 01: ~0.3 bay, 8 flutes)
    pil_proj=0.12,     # pilaster projection / central wall recess  APPROXIMATE
    reveal=0.45,       # window reveal depth  APPROXIMATE
    front_depth=13.0,  # front (gallery) range depth  APPROXIMATE
    west_wing=15.0, east_wing=17.0,   # wing widths  APPROXIMATE (U-plan VERIFIED S5/S6)
)


def folger_levels(F):
    zt = F["zt"]
    return dict(
        zt=zt,
        base1=zt + 0.55,                  # marble base course top
        rel0=zt + 0.78, rel1=zt + 0.78 + F["relief"],
        # heads / frieze photo-measured on ref 01 (Commons 2025), scaled from the 14.0 m attic line
        # and the 1.83 m relief panels: glass ~3.6-9.0 m, incised frieze ~9.9-10.8 m  PROBABLE
        win0=zt + 0.78 + F["relief"] + 0.62, win1=9.25,
        ent0=9.85, ent1=10.75,            # entablature with shallow incised ornament (S6)
        att1=14.0,                        # attic top below the "slight recession" (S6)
        top=F["H"],
        roof=F["H"] - 1.05,               # flat roof behind the parapet  APPROXIMATE
    )


def folger_window_grille(m, fr, a0, a1, c0, c1, b_glass, lod):
    """Cast-aluminium Art Deco grille in front of the glazing (pattern APPROXIMATE; VERIFIED
    material: aluminium, S4/S11)."""
    mat = "M_F01_Metal_Aluminium"
    bf0, bf1 = b_glass + 0.02, b_glass + 0.075
    w, h = a1 - a0, c1 - c0
    fw = 0.075
    m.lbox(fr, a0, a1, bf0, bf1 + 0.02, c0, c0 + fw, mat)
    m.lbox(fr, a0, a1, bf0, bf1 + 0.02, c1 - fw, c1, mat)
    m.lbox(fr, a0, a0 + fw, bf0, bf1 + 0.02, c0 + fw, c1 - fw, mat)
    m.lbox(fr, a1 - fw, a1, bf0, bf1 + 0.02, c0 + fw, c1 - fw, mat)
    if lod >= 1:
        m.lbox(fr, (a0 + a1) / 2 - 0.03, (a0 + a1) / 2 + 0.03, bf0, bf1, c0, c1, mat)
        return
    bar = 0.035
    for k in (1, 2, 3):
        x = a0 + w * k / 4
        m.lbox(fr, x - bar / 2, x + bar / 2, bf0 - 0.006, bf1 + 0.006, c0 + fw, c1 - fw, mat)
    # horizontal rails, then a rectilinear fret of interlocking rectangles in every cell
    # (ref 01, Commons 2025: stepped rectangles, no chevrons; exact pattern APPROXIMATE)
    rails = [k / 8 for k in range(1, 8)]
    for t in rails:
        z = c0 + h * t
        m.lbox(fr, a0 + fw, a1 - fw, bf0, bf1, z - bar / 2, z + bar / 2, mat)
    t = 0.025
    for col in range(4):
        x0 = a0 + (fw if col == 0 else 0.0) + w * col / 4 + bar / 2 + 0.05
        x1 = a0 + w * (col + 1) / 4 - (fw if col == 3 else 0.0) - bar / 2 - 0.05
        for row in range(8):
            z0 = c0 + (fw if row == 0 else 0.0) + h * row / 8 + bar / 2 + 0.06
            z1 = c0 + h * (row + 1) / 8 - (fw if row == 7 else 0.0) - bar / 2 - 0.06
            # inner rectangle tied to the bar on alternating sides -> interlocking "key" read
            xa, xb = (x0 - 0.055, x1 - 0.06) if (row + col) % 2 == 0 else (x0 + 0.06, x1 + 0.055)
            m.lbox(fr, xa, xb, bf0 + 0.004, bf1 - 0.004, z0, z0 + t, mat)
            m.lbox(fr, xa, xb, bf0 + 0.004, bf1 - 0.004, z1 - t, z1, mat)
            m.lbox(fr, xa, xa + t, bf0 + 0.004, bf1 - 0.004, z0 + t, z1 - t, mat)
            m.lbox(fr, xb - t, xb, bf0 + 0.004, bf1 - 0.004, z0 + t, z1 - t, mat)


def folger_bay_facade(m, fr, F, Z, a_start, nbays, lod, key, reliefs, wall_depth):
    """Central bay range: recessed wall (b = -pil_proj) with tall windows and sunk relief
    panels between fluted pilasters (faces at b = 0). The range spans from the outer edge of
    the first pilaster to the outer edge of the last; core face at b = -wall_depth.
    LOD2: no slab (core reaches b = 0); glass, pilasters and panels sit proud of the core."""
    bay, ww, rel = F["bay"], F["win_w"], F["relief"]
    pp, pw = F["pil_proj"], F["pil_w"]
    a_lo, a_hi = a_start - pw / 2, a_start + nbays * bay + pw / 2
    wins, rel_ops, fields = [], [], []
    fw2 = 1.2                            # half-width of the sunk window field (ref 01: ~2.4 m)  PROBABLE
    for i in range(nbays):
        ac = a_start + (i + 0.5) * bay
        wins.append((ac - ww / 2, ac + ww / 2, Z["win0"], Z["win1"]))
        fields.append((ac - fw2, ac + fw2, Z["win0"] - 0.1, Z["ent0"]))
        rel_ops.append((ac - rel / 2, ac + rel / 2, Z["rel0"], Z["rel1"]))
    if lod >= 2:
        for i, (wa0, wa1, wc0, wc1) in enumerate(wins):
            m.lbox(fr, wa0, wa1, 0.0, 0.015, wc0, wc1, GLASS[glass_slot(f"{key}-w{i}")])
        for i in range(nbays + 1):
            ac = a_start + i * bay
            m.lbox(fr, ac - pw / 2, ac + pw / 2, 0.0, pp, Z["base1"], Z["ent0"], "M_F01_Marble_Smooth")
        return
    # recessed wall slab b in [-wall_depth, -pp] with window + relief-field openings
    slab = L.Mesh_proxy(m, fr, -pp)
    L.wall_with_openings(slab, None, a_lo, a_hi, Z["base1"], Z["ent0"], wall_depth - pp,
                         fields + rel_ops, "M_F01_Marble_Folger")
    # sunk window field: back wall 0.15 m behind the slab face, keyed 2 cm into the reveals
    fld = L.Mesh_proxy(m, fr, -pp - 0.15)
    for (fa0, fa1, fc0, fc1), win in zip(fields, wins):
        L.wall_with_openings(fld, None, fa0 - 0.02, fa1 + 0.02, fc0, fc1 + 0.02, wall_depth - pp - 0.15, [win],
                             "M_F01_Marble_Smooth")
    for k, (ra0, ra1, rc0, rc1) in enumerate(rel_ops):
        m.lbox(fr, ra0, ra1, -wall_depth, -pp - 0.10, rc0, rc1, "M_F01_Marble_Smooth")
        if reliefs:
            # John Gregory reliefs (1932, rights unconfirmed) -> labelled simplified stand-ins
            L.relief_standin_smooth(m, fr, ra0, ra1, rc0, rc1, -pp - 0.10, 1000 + k, "M_F01_Marble_Smooth", lod=lod)
    for i, (wa0, wa1, wc0, wc1) in enumerate(wins):
        gs = glass_slot(f"{key}-w{i}")
        b_glass = -wall_depth + 0.08
        m.lbox(fr, wa0, wa1, b_glass - 0.015, b_glass, wc0, wc1, GLASS[gs])
        folger_window_grille(m, fr, wa0, wa1, wc0, wc1, b_glass, lod)
        m.lbox(fr, wa0 - 0.06, wa1 + 0.06, -wall_depth + 0.02, -pp + 0.05, wc0 - 0.10, wc0 + 0.025,
               "M_F01_Marble_Smooth")
    for i in range(nbays + 1):
        L.fluted_pilaster(m, fr, a_start + i * bay, pw, Z["base1"], Z["ent0"], -pp, pp, 8, lod,
                          "M_F01_Marble_Smooth", cap_h=0.30, base_h=0.0)


def folger_upper_bands(m, fr, F, Z, a0, a1, lod, wall_depth, frieze_marks=()):
    """Entablature (shallow incised ornament, S6), attic and the slight recession at the top,
    as solid bands b in [-wall_depth, 0] over a in [a0, a1] (corner rule applied by caller)."""
    if lod >= 2:
        m.lbox(fr, a0, a1, 0.0, 0.04, Z["ent0"], Z["ent1"], "M_F01_Marble_Smooth")
        return
    m.lbox(fr, a0, a1, -wall_depth, 0.0, Z["ent0"], Z["ent1"], "M_F01_Marble_Smooth")
    if lod == 0:
        grooves = []
        for x in frieze_marks:      # stylised triglyph-like triple grooves over the pilasters
            for dx in (-0.16, 0.0, 0.16):
                grooves.append((x + dx - 0.035, x + dx + 0.035, Z["ent0"] + 0.18, Z["ent1"] - 0.16))
        grooves.append((a0 + 0.25, a1 - 0.25, Z["ent0"] + 0.07, Z["ent0"] + 0.10))
        L.incised_band(m, fr, a0, a1, Z["ent0"] + 0.04, Z["ent1"] - 0.04, 0.0, 0.015, grooves, "M_F01_Marble_Smooth")
    m.lbox(fr, a0, a1, -wall_depth, 0.0, Z["ent1"], Z["att1"], "M_F01_Marble_Folger")
    m.lbox(fr, a0, a1, -wall_depth, -0.15, Z["att1"], Z["top"] - 0.08, "M_F01_Marble_Folger")


def folger_end_section(m, fr, F, Z, a0, a1, lod, key, door=True, wall_depth=0.57, inscription=None):
    """Solid end section (faces at b = 0, ent0 and below) with an optional raised entrance and
    comedy / tragedy mask stand-in above it (P: masks "hover over the entrances")."""
    dw, dh = 2.2, 4.5                   # door height photo-measured (ref 01)  PROBABLE
    ac = (a0 + a1) / 2
    zd = Z["base1"]                     # door threshold on the base course; stoop below
    # Entrance bay as seen in ref 01 (Commons 2025, north facade from the NE): the door sits in a
    # tall recessed panel that also holds the mask, under a projecting flat canopy at ~6.5 m.
    pa0, pa1 = ac - dw / 2 - 0.35, ac + dw / 2 + 0.35
    zcan, rd = Z["ent0"] - 0.9, 0.18    # canopy top meets the frieze band (ref 01); recess depth APPROXIMATE
    if lod >= 2:
        if door:
            m.lbox(fr, ac - dw / 2, ac + dw / 2, 0.0, 0.02, zd, zd + dh, "M_F01_Metal_Aluminium")
            m.lbox(fr, pa0 - 0.35, pa1 + 0.35, 0.0, 1.0, zcan, zcan + 0.9, "M_F01_Marble_Smooth")
        return
    ops = [(pa0, pa1, zd, zcan)] if door else []
    L.wall_with_openings(m, fr, a0, a1, Z["base1"], Z["ent0"], wall_depth, ops, "M_F01_Marble_Folger")
    if door:
        back = L.Mesh_proxy(m, fr, -rd)
        L.wall_with_openings(back, None, pa0 - 0.02, pa1 + 0.02, zd, zcan + 0.02, wall_depth - rd,   # keyed into the reveals
                             [(ac - dw / 2, ac + dw / 2, zd, zd + dh)], "M_F01_Marble_Smooth")
        # canopy slab with a stepped fascia, and a pendant lantern under it (fixture APPROXIMATE)
        m.lbox(fr, pa0 - 0.35, pa1 + 0.35, 0.0, 1.0, zcan, zcan + 0.62, "M_F01_Marble_Smooth")
        m.lbox(fr, pa0 - 0.25, pa1 + 0.25, 0.0, 0.9, zcan + 0.62, zcan + 0.88, "M_F01_Marble_Smooth")
        m.lbox(fr, ac - 0.04, ac + 0.04, 0.56, 0.64, zcan - 0.35, zcan, "M_F01_Metal_Aluminium")
        m.lbox(fr, ac - 0.16, ac + 0.16, 0.44, 0.76, zcan - 0.75, zcan - 0.35, "M_F01_Glass_NightLit")
        for s in (-1, 1):
            L.fluted_pilaster(m, fr, ac + s * (dw / 2 + 0.35 + 0.23), 0.4, zd, zcan, 0.0, 0.06, 3, lod,
                              "M_F01_Marble_Smooth")
        bd = -wall_depth + 0.12
        m.lbox(fr, ac - dw / 2, ac + dw / 2, -wall_depth, bd - 0.06, zd - 0.02, zd, "M_F01_Marble_Smooth")
        m.lbox(fr, ac - dw / 2, ac + dw / 2, bd - 0.06, bd, zd, zd + dh, "M_F01_Metal_Aluminium")
        m.lbox(fr, ac - dw / 2 + 0.1, ac + dw / 2 - 0.1, bd, bd + 0.01, zd + 0.2, zd + dh - 0.9, "M_F01_Glass")
        if lod == 0:
            for k in range(1, 6):
                x = ac - dw / 2 + dw * k / 6
                m.lbox(fr, x - 0.025, x + 0.025, bd + 0.01, bd + 0.05, zd + 0.2, zd + dh - 0.9, "M_F01_Metal_Aluminium")
            for t in (0.35, 0.7):
                z = zd + 0.2 + (dh - 1.1) * t
                m.lbox(fr, ac - dw / 2 + 0.1, ac + dw / 2 - 0.1, bd + 0.01, bd + 0.045, z - 0.025, z + 0.025,
                       "M_F01_Metal_Aluminium")
            m.lbox(fr, ac - dw / 2, ac + dw / 2, bd, bd + 0.05, zd + dh - 0.9, zd + dh - 0.82, "M_F01_Metal_Aluminium")
        # stoop: three risers down to the terrace (two step blocks; the terrace is the last tread)
        L.stairs(m, fr, ac - dw / 2 - 0.2, ac + dw / 2 + 0.2, 0.04, 2, (zd - Z["zt"]) / 3, 0.34, zd - (zd - Z["zt"]) / 3,
                 "M_F01_Marble_Smooth")
        zc = zd + dh + 0.95             # mask just above the door, inside the recess (ref 01)
        ring = [(ac + 0.62 * math.cos(2 * math.pi * k / 20), zc + 0.62 * math.sin(2 * math.pi * k / 20)) for k in range(20)]
        m.lprism(fr, ring, -rd, -rd + 0.06, "M_F01_Marble_Smooth")
        if lod == 0:
            face = [(ac + 0.3 * math.cos(2 * math.pi * k / 16), zc + 0.4 * math.sin(2 * math.pi * k / 16)) for k in range(16)]
            m.lprism(fr, face, -rd + 0.06, -rd + 0.11, "M_F01_Marble_Smooth")
    if inscription and lod == 0:
        L.text_inscription(m, fr, inscription, ac, Z["att1"] - 0.38, 0.33, 0.2, 0.0, "M_F01_Marble_Incised",
                           FONT, max_width=(a1 - a0) - 1.2)


def build_folger(lod):
    F = FOLGER
    Z = folger_levels(F)
    W, D, H = F["W"], F["D"], F["H"]
    x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
    m = L.Mesh(f"SM_F01_Folger_LOD{lod}")
    dN, dS = (0.57, 0.45) if lod < 2 else (0.0, 0.0)      # facade slab depths (north / sides)
    nb, bay, pw = F["nbays"], F["bay"], F["pil_w"]
    fd, wwg, ewg = F["front_depth"], F["west_wing"], F["east_wing"]
    zr = Z["roof"] if lod < 2 else H
    # ---- plinth under the building, front terrace with lawn bed, low wall, stairs (S1/S4/S14)
    terr_y1 = y1 + 10.4                        # terrace depth ~34 ft incl. the 25 ft lawn  APPROXIMATE
    lawn = (-20.6, 20.6, y1 + 1.8, y1 + 1.8 + 25 * FT)   # 135 x 25 ft  VERIFIED (S4)
    m.box(x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 1.8, 0.0, Z["zt"], "M_F01_Marble_Smooth")
    m.box(x0 - 0.3, lawn[0], y1 + 1.8, terr_y1, 0.0, Z["zt"], "M_F01_Marble_Smooth")
    m.box(lawn[1], x1 + 0.3, y1 + 1.8, terr_y1, 0.0, Z["zt"], "M_F01_Marble_Smooth")
    m.box(lawn[0], lawn[1], lawn[3], terr_y1, 0.0, Z["zt"], "M_F01_Marble_Smooth")
    m.box(lawn[0], lawn[1], lawn[2], lawn[3], 0.0, Z["zt"] - 0.06, "M_F01_Turf_Placeholder")
    if lod < 2:
        for (a, b) in ((x0 - 0.3, -24.0), (-17.0, 17.0), (24.0, x1 + 0.3)):
            m.box(a, b, terr_y1 - 0.45, terr_y1, Z["zt"], Z["zt"] + 0.55, "M_F01_Marble_Smooth")
        frs = L.Frame((0, terr_y1), (-1, 0))   # terrace front, facing north; a = -x
        for (xa, xb) in ((-24.0, -17.0), (17.0, 24.0)):
            L.stairs(m, frs, -xb, -xa, 0.0, 5, Z["zt"] / 5, 0.36, Z["zt"], "M_F01_Marble_Smooth")
        m.box(-20.6, 20.6, y1 + 0.75, y1 + 1.05, Z["zt"], Z["zt"] + 0.004, "M_F01_Paving_Bluestone")
    # ---- cores (behind facade slabs); flat roof below the parapet
    box_mats(m, x0 + dS, x1 - dS, y1 - fd, y1 - dN, Z["zt"], zr, "M_F01_Marble_Folger", top="M_F01_Roof_Tar",
             s="M_F01_Brick_Glazed")
    box_mats(m, x0 + dS, x0 + wwg, y0, y1 - fd, Z["zt"], zr, "M_F01_Marble_Folger", top="M_F01_Roof_Tar",
             e="M_F01_Brick_Glazed", n="M_F01_Brick_Glazed")
    box_mats(m, x1 - ewg, x1 - dS, y0, y1 - fd, Z["zt"], zr, "M_F01_Marble_Folger", top="M_F01_Roof_Tar",
             w="M_F01_Brick_Glazed", n="M_F01_Brick_Glazed")
    if lod < 2:
        # parapet walls along the rear (wing south ends) so the roof is hidden from the alley
        for (xa, xb) in ((x0 + dS, x0 + wwg), (x1 - ewg, x1 - dS)):
            m.box(xa, xb, y0, y0 + 0.35, zr, H - 0.4, "M_F01_Marble_Folger")
    # reading room in the centre of the U (trussed roof kept below the parapet)  APPROXIMATE
    box_mats(m, -11.0, 11.0, y0 + 7.0, y1 - fd, Z["zt"], 13.4, "M_F01_Brick_Glazed", top="M_F01_Roof_Tar")
    # 1958-59 one-storey rear addition filling the U (VERIFIED present in 1963, S5/S8)
    box_mats(m, x0 + wwg, x1 - ewg, y0, y1 - fd, Z["zt"], Z["zt"] + 4.3, "M_F01_Brick_Glazed", top="M_F01_Roof_Tar")
    if lod < 2:
        m.box(x0 + wwg, x1 - ewg, y0, y0 + 0.3, Z["zt"] + 4.3, Z["zt"] + 4.6, "M_F01_Marble_Smooth")
    frS = L.Frame((x0, y0), (1, 0))
    flush_windows(m, frS, dS + 1.6, wwg - 1.6, [Z["zt"] + 1.8, Z["zt"] + 6.3, Z["zt"] + 9.8], 1.2, 2.2, 4.0, 0.0,
                  lod, "folger-sW")
    flush_windows(m, frS, W - ewg + 1.6, W - dS - 1.6, [Z["zt"] + 6.3, Z["zt"] + 9.8], 1.2, 2.2, 4.4, 0.0,
                  lod, "folger-sE")
    flush_windows(m, frS, wwg + 1.5, W - ewg - 1.5, [Z["zt"] + 1.0], 1.6, 2.0, 3.6, 0.0, lod, "folger-sAdd")
    frC = L.Frame((x0 + wwg, y1 - fd), (1, 0))
    flush_windows(m, frC, 0.6, W - wwg - ewg - 0.6, [Z["zt"] + 6.2, Z["zt"] + 9.6], 1.4, 2.4, 3.4, 0.0, lod, "folger-c1")
    # ---- North facade (East Capitol St): edge NE -> NW, u = -x. Corner rule: spans a in [0, W - dS].
    frN = L.Frame((x1, y1), (-1, 0))
    LN = W - dS
    a_c0 = (W - nb * bay) / 2
    ca_lo, ca_hi = a_c0 - pw / 2, a_c0 + nb * bay + pw / 2
    insc_jonson = ["THOU ART A MONUMENT WITHOUT A TOMBE", "AND ART ALIVE STILL WHILE THY BOOKE DOTH LIVE",
              "AND WE HAVE WITS TO READ AND PRAISE TO GIVE"]
    insc_johnson = ["THIS THEREFORE IS THE PRAISE OF SHAKESPEARE", "THAT HIS DRAMA IS THE MIRROUR OF LIFE"]
    folger_end_section(m, frN, F, Z, 0.0, ca_lo, lod, "fN-E", door=True, wall_depth=dN)
    folger_bay_facade(m, frN, F, Z, a_c0, nb, lod, "fN", True, dN)
    folger_end_section(m, frN, F, Z, ca_hi, LN, lod, "fN-W", door=True, wall_depth=dN)
    if lod == 0:
        # inscriptions in the attic over the window row, Johnson over the east half (ref 01)
        for t, lines in ((0.25, insc_johnson), (0.75, insc_jonson)):
            L.text_inscription(m, frN, lines, a_c0 + nb * bay * t, Z["ent1"] + 1.6, 0.33, 0.2, 0.0,
                               "M_F01_Marble_Incised", FONT, max_width=nb * bay / 2 - 1.0)
    folger_upper_bands(m, frN, F, Z, 0.0, LN, lod, dN, frieze_marks=[a_c0 + i * bay for i in range(nb + 1)])
    # ---- West facade (2nd St; "two similar facades", P): edge NW -> SW, u = -y, spans a in [0, D]
    frW = L.Frame((x0, y1), (0, -1))
    nbw = 3
    a_w0 = 10.0
    folger_end_section(m, frW, F, Z, 0.0, a_w0 - pw / 2, lod, "fW-N", door=False, wall_depth=dS)
    folger_bay_facade(m, frW, F, Z, a_w0, nbw, lod, "fW", False, dS)
    folger_end_section(m, frW, F, Z, a_w0 + nbw * bay + pw / 2, D, lod, "fW-S", door=False, wall_depth=dS)
    folger_upper_bands(m, frW, F, Z, 0.0, D, lod, dS, frieze_marks=[a_w0 + i * bay for i in range(nbw + 1)])
    # ---- East facade (3rd St): "a blank wall broken only by masks of comedy and tragedy" (S6)
    frE = L.Frame((x1, y0), (0, 1))
    LE = D - dN
    if lod < 2:
        L.wall_with_openings(m, frE, 0.0, LE, Z["base1"], Z["ent0"], dS, [], "M_F01_Marble_Folger")
    folger_upper_bands(m, frE, F, Z, 0.0, LE, lod, dS)
    if lod < 2:
        for k, a in enumerate((D * 0.36, D * 0.64)):
            zc = 7.2
            ring = [(a + 0.75 * math.cos(2 * math.pi * j / 20), zc + 0.75 * math.sin(2 * math.pi * j / 20)) for j in range(20)]
            m.lprism(frE, ring, 0.0, 0.07, "M_F01_Marble_Smooth")
            if lod == 0:
                face = [(a + 0.36 * math.cos(2 * math.pi * j / 16), zc + 0.5 * math.sin(2 * math.pi * j / 16)) for j in range(16)]
                m.lprism(frE, face, 0.07, 0.13, "M_F01_Marble_Smooth")
                zm = zc - 0.22 + (0.0 if k == 0 else 0.04)
                m.lbox(frE, a - 0.16, a + 0.16, 0.13, 0.136, zm, zm + 0.05, "M_F01_Marble_Incised")
                for ex in (-0.13, 0.13):
                    m.lbox(frE, a + ex - 0.06, a + ex + 0.06, 0.13, 0.136, zc + 0.1, zc + 0.16, "M_F01_Marble_Incised")
    # ---- continuous mouldings as mitred sweeps (no corner notches / z-fighting)
    if lod < 2:
        loop = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        m.sweep(loop, [(-0.3, 0.0), (0.04, 0.0), (0.04, Z["base1"] - Z["zt"]), (-0.3, Z["base1"] - Z["zt"])],
                "M_F01_Marble_Smooth", closed=True, z=Z["zt"])
        prim = [(x1, y0 + 0.01), (x1, y1), (x0, y1), (x0, y0 + 0.01)]    # caps 1 cm short of the band ends
        m.sweep(prim, [(-0.25, 0.0), (0.05, 0.0), (0.05, 0.08), (-0.25, 0.08)], "M_F01_Marble_Smooth",
                closed=False, z=Z["ent1"] - 0.05)
        m.sweep(prim, [(-0.5, 0.0), (-0.12, 0.0), (-0.12, 0.08), (-0.5, 0.08)], "M_F01_Marble_Smooth",
                closed=False, z=H - 0.08)
    # ---- Puck fountain on the west lawn (marble Puck in place in 1963, S13): labelled stand-in
    px, py = x0 - 13.0, 0.0                     # APPROXIMATE position; faces west
    if lod < 2:
        seg = 24 if lod == 0 else 12
        m.lathe(px, py, [(3.2, 0.0), (3.2, 0.55), (2.9, 0.55), (2.9, 0.2), (0.0, 0.2)], seg, "M_F01_Marble_Smooth")
        m.lathe(px, py, [(0.85, 0.2), (0.85, 0.5), (0.6, 0.6), (0.5, 1.7), (0.7, 1.85), (0.7, 2.0)], seg,
                "M_F01_Marble_Smooth")
        m.lathe(px, py, [(0.22, 2.0), (0.24, 2.6), (0.3, 3.0), (0.26, 3.35), (0.12, 3.45), (0.16, 3.62),
                         (0.13, 3.78), (0.0, 3.82)], seg, "M_F01_Marble_Smooth")
        m.lathe(px, py, [(2.88, 0.2), (2.88, 0.42), (0.0, 0.42)], seg, "M_F01_Glass")
    sockets = [
        ("SOCKET_Entrance_North_East", (x1 - ca_lo / 2, y1 + 0.2, Z["base1"]), math.pi / 2),
        ("SOCKET_Entrance_North_West", (x0 + (W - ca_hi - dS) / 2 + dS, y1 + 0.2, Z["base1"]), math.pi / 2),
        ("SOCKET_PuckFountain", (px, py, 0.0), math.pi),
        ("SOCKET_Lawn_N03_Turf", ((lawn[0] + lawn[1]) / 2, (lawn[2] + lawn[3]) / 2, Z["zt"] - 0.06), 0.0),
        ("SOCKET_Signage_BuildingName_PENDING", (0.0, y1 + 0.05, 12.9), math.pi / 2),
    ]
    hulls = [
        _box_pts(x0 - 0.3, x1 + 0.3, y0 - 0.3, terr_y1, 0.0, Z["zt"]),
        _box_pts(x0, x1, y1 - fd, y1 + 0.05, Z["zt"], H),
        _box_pts(x0, x0 + wwg, y0, y1 - fd, Z["zt"], H),
        _box_pts(x1 - ewg, x1, y0, y1 - fd, Z["zt"], H),
        _box_pts(x0 + wwg, x1 - ewg, y0, y1 - fd, Z["zt"], Z["zt"] + 4.6),
        _box_pts(px - 3.2, px + 3.2, py - 3.2, py + 3.2, 0.0, 3.82),
    ]
    return m, sockets, hulls


# =============================================================================
# LIBRARY OF CONGRESS ANNEX (Adams Building after 1980) — Pierson & Wilson / Trowbridge, 1935-39
# =============================================================================
ANNEX = dict(
    W=400 * FT,        # 121.92 m E-W (north/south facades)  VERIFIED (Evening Star 1936 via LoC blog)
    D=225 * FT,        # 68.58 m N-S (east/west facades)     VERIFIED (same)
    setback=35 * FT,   # 10.67 m attic setback on all sides   VERIFIED (STAR36 / AOC)
    zg=1.35,           # ground-floor level = top of the pink granite skirt  APPROXIMATE
    z_band=5.6,        # band course under the vertically linked bays  APPROXIMATE
    floor_h=3.9,       # floors 1-4  APPROXIMATE (12 stack tiers cellar-4th, ~15 ft/level)
    z_parapet=24.0,    # main parapet  APPROXIMATE (est. 70-80 ft)
    z_pav=24.6,        # pavilion parapets slightly higher  APPROXIMATE
    z_roof=23.2,       # lower copper roof ring  APPROXIMATE
    z_attic=29.6,      # top of the "high recessed attic"  APPROXIMATE (est. 90-100 ft)
    cpw=11.6,          # corner pavilion width  APPROXIMATE
    mpw_long=24.4, mpw_short=19.5,   # central pavilion widths  APPROXIMATE
    pav_proj=0.9,      # pavilion projection  APPROXIMATE
    slab=1.5,          # facade construction depth (pavilion face to core)
    strip_recess=0.28, # "sunken window frames" (SAH): spandrel recess behind the pier face  APPROXIMATE
)


def annex_levels(A):
    z0 = A["z_band"] + 0.3
    floors = [z0 + k * A["floor_h"] for k in range(4)]
    return dict(zg=A["zg"], band0=A["z_band"], band1=z0, strip0=z0, strip1=z0 + 4 * A["floor_h"],
                floors=floors, gw0=2.05, gw1=4.75)


def anthemion(m, fr, ac, cc, size, b, mat, segs=6):
    """Stylised honeysuckle (anthemion) fan in low relief - the Annex's recurring ornament (SAH)."""
    for k in range(5):
        ang = (k - 2) * 0.36
        L.relief_blob(m, fr, ac + math.sin(ang) * size * 0.45, cc + math.cos(ang) * size * 0.45,
                      size * 0.09, size * 0.34, size * 0.06, b, mat, angle=-ang, segs=segs, rings=2)
    L.relief_blob(m, fr, ac, cc - size * 0.05, size * 0.16, size * 0.1, size * 0.07, b, mat, segs=segs, rings=2)


def annex_strip(m, fr, A, Z, ac, sw, b_face, b_spandrel, glass_b, lod, key, ornament=True):
    """One vertically linked bay: window per floor (1-4) with recessed spandrels between,
    cut as a full-height strip opening by the caller. b_face = wall face of the strip."""
    a0, a1 = ac - sw / 2, ac + sw / 2
    core = -A["slab"]
    fl = Z["floors"]
    wins = []
    for k, zf in enumerate(fl):
        wins.append((zf + 0.55, zf + A["floor_h"] - 0.35))
    # spandrels (incl. below first and above last window)
    edges = [Z["strip0"]] + [z for w in wins for z in w] + [Z["strip1"]]
    for i in range(0, len(edges), 2):
        c0, c1 = edges[i], edges[i + 1]
        if lod >= 2:
            continue
        # spandrel panels: bronze, PROBABLE - inferred from SAH "vertically linked window bays
        # alternate with narrow strips of marble-clad walls" (bays are not marble-clad)
        m.lbox(fr, a0, a1, core, b_spandrel, c0, c1, "M_F01_Metal_Bronze")
        if ornament and lod == 0 and 0 < i < len(edges) - 2:
            anthemion(m, fr, ac, (c0 + c1) / 2 - 0.04, min(sw * 0.5, (c1 - c0) * 0.85), b_spandrel,
                      "M_F01_Metal_Bronze")
    for k, (c0, c1) in enumerate(wins):
        gs = glass_slot(f"{key}-{k}")
        if lod >= 2:
            m.lbox(fr, a0 + 0.1, a1 - 0.1, b_face, b_face + 0.02, c0, c1, GLASS[gs])
            continue
        L.window_unit(m, fr, a0 + 0.06, a1 - 0.06, c0, c1, -core, lod,
                      {"frame": "M_F01_Metal_Bronze", "glass": GLASS}, cols=3, rows=3,
                      glass_set_back=glass_b - core, glass_slot=gs, frame_w=0.08, mullion_w=0.045)


def annex_segment(m, fr, A, Z, kind, a0, a1, nstrips, lod, key, entrance=None, proud_a1=None):
    """kind: 'pav' (face b = 0, parapet z_pav) or 'cur' (face b = -pav_proj, parapet z_parapet)."""
    core = -A["slab"]
    face = 0.0 if kind == "pav" else -A["pav_proj"]
    top = A["z_pav"] if kind == "pav" else A["z_parapet"]
    width = a1 - a0
    pitch = width / nstrips
    sw = min(2.3, pitch * 0.68) if kind == "cur" else min(1.9, pitch * 0.42)
    centres = [a0 + (i + 0.5) * pitch for i in range(nstrips)]
    if lod >= 2:
        if kind == "pav":
            m.lbox(fr, a0, a1, -A["pav_proj"] - 0.01, 0.0, 0.0, top, "M_F01_Marble_Ashlar")
        else:
            m.lbox(fr, a0, a1, -A["pav_proj"] - 0.01, -A["pav_proj"] + 0.0001, A["z_parapet"] - 0.6, top, "M_F01_Marble_Ashlar")
        for i, ac in enumerate(centres):
            annex_strip(m, fr, A, Z, ac, sw, face, face, face, 2, f"{key}-s{i}")
        return
    ops = []
    for ac in centres:
        ops.append((ac - sw / 2, ac + sw / 2, Z["strip0"], Z["strip1"]))
        if not entrance:
            ops.append((ac - sw / 2 + 0.25, ac + sw / 2 - 0.25, Z["gw0"], Z["gw1"]))
    doors = []
    if entrance:
        nd, dw, dh, spacing = entrance
        for j in range(nd):
            dc = (a0 + a1) / 2 + (j - (nd - 1) / 2) * spacing
            doors.append((dc - dw / 2, dc + dw / 2, Z["zg"], Z["zg"] + dh))
        ops += doors
    slab = L.Mesh_proxy(m, fr, face)
    L.wall_with_openings(slab, None, a0, a1, A["zg"] * 0.0 + 1.35, top, face - core, ops, "M_F01_Marble_Ashlar")
    # ground windows
    for i, ac in enumerate(centres):
        if not entrance:
            gs = glass_slot(f"{key}-g{i}")
            L.window_unit(m, fr, ac - sw / 2 + 0.25, ac + sw / 2 - 0.25, Z["gw0"], Z["gw1"], -core, lod,
                          {"frame": "M_F01_Metal_Bronze", "glass": GLASS}, cols=2, rows=2,
                          glass_set_back=((face - 0.5) if kind == "pav" else (core + 0.12)) - core, glass_slot=gs)
        annex_strip(m, fr, A, Z, ac, sw, face, face - A["strip_recess"],
                    (face - 0.5) if kind == "pav" else (core + 0.12), lod, f"{key}-s{i}")
    # band course and coping
    # band course: only the projecting part (avoids coincident same-direction faces with the
    # slab cells, which self-shadow black in a path tracer); runs to the true end at corners
    a1p = proud_a1 if proud_a1 is not None else a1
    m.lbox(fr, a0, a1p, face, face + 0.05, Z["band0"], Z["band1"], "M_F01_Marble_Smooth")
    # coping: a cap ON the wall top with a 4 cm overhang, flush with the slab's inner face
    m.lbox(fr, a0, a1, core, face + 0.04, top, top + 0.06, "M_F01_Marble_Smooth")
    if a1p > a1 + 1e-6:
        m.lbox(fr, a1, a1p, face, face + 0.04, top, top + 0.06, "M_F01_Marble_Smooth")
    # honeysuckle ornament over the piers in the parapet frieze
    if lod == 0 and kind == "pav":
        piers = [a0 + i * pitch for i in range(nstrips + 1)]
        for k, ap in enumerate(piers):
            if ap - a0 < 0.4 or a1 - ap < 0.4:
                continue
            anthemion(m, fr, ap, Z["strip1"] + 1.15, 0.95, face, "M_F01_Marble_Smooth")
    for j, (da0, da1, dc0, dc1) in enumerate(doors):
        bd = core + 0.25
        mid = (da0 + da1) / 2
        m.lbox(fr, da0, da1, core, bd, dc0 - 0.02, dc0, "M_F01_Marble_Smooth")
        for leaf, (la0, la1) in enumerate(((da0, mid - 0.01), (mid + 0.01, da1))):
            m.lbox(fr, la0, la1, bd, bd + 0.08, dc0, dc1, "M_F01_Metal_Bronze")
            if lod == 0:
                # Lee Lawrie bronze doors: one figure per leaf (six figures per three-pair entrance,
                # COLE). Rights unconfirmed -> labelled stand-in figure in a framed panel.
                pa0, pa1 = la0 + 0.14, la1 - 0.14
                pc0, pc1 = dc0 + 0.9, dc1 - 0.35
                for (q0, q1, r0, r1) in ((pa0 - 0.05, pa1 + 0.05, pc0 - 0.05, pc0), (pa0 - 0.05, pa1 + 0.05, pc1, pc1 + 0.05),
                                         (pa0 - 0.05, pa0, pc0, pc1), (pa1, pa1 + 0.05, pc0, pc1)):
                    m.lbox(fr, q0, q1, bd + 0.08, bd + 0.11, r0, r1, "M_F01_Metal_Bronze")
                fx = (pa0 + pa1) / 2
                fh = pc1 - pc0 - 0.12
                gz = pc0 + 0.06
                L.relief_blob(m, fr, fx, gz + fh * 0.28, (pa1 - pa0) * 0.2, fh * 0.29, 0.03, bd + 0.08, "M_F01_Metal_Bronze", segs=10, rings=3)
                L.relief_blob(m, fr, fx, gz + fh * 0.64, (pa1 - pa0) * 0.17, fh * 0.17, 0.035, bd + 0.08, "M_F01_Metal_Bronze", segs=10, rings=3)
                L.relief_blob(m, fr, fx, gz + fh * 0.88, (pa1 - pa0) * 0.1, fh * 0.065, 0.04, bd + 0.08, "M_F01_Metal_Bronze", segs=10, rings=3)
                side = 1 if leaf == 0 else -1
                L.relief_blob(m, fr, fx + side * (pa1 - pa0) * 0.22, gz + fh * 0.66, (pa1 - pa0) * 0.05, fh * 0.15, 0.025,
                              bd + 0.08, "M_F01_Metal_Bronze", angle=side * 0.5, segs=8, rings=2)
                # lower kick panel
                m.lbox(fr, pa0, pa1, bd + 0.08, bd + 0.1, dc0 + 0.2, dc0 + 0.7, "M_F01_Metal_Bronze")
        # stepped marble surround
        m.lbox(fr, da0 - 0.35, da0, face, face + 0.06, dc0, dc1 + 0.35, "M_F01_Marble_Smooth")
        m.lbox(fr, da1, da1 + 0.35, face, face + 0.06, dc0, dc1 + 0.35, "M_F01_Marble_Smooth")
        m.lbox(fr, da0, da1, face, face + 0.06, dc1, dc1 + 0.35, "M_F01_Marble_Smooth")
    # glazed transoms above the doors are part of the strips (strip0 = band1 sits above the doors)


def annex_layout(A, L_total, short):
    cpw = A["cpw"]
    mpw = A["mpw_short"] if short else A["mpw_long"]
    cur = (L_total - 2 * cpw - mpw) / 2
    pitch = 3.24 if short else 3.38
    ncur = max(2, int(round(cur / pitch)))
    return [("pav", 0.0, cpw, 2), ("cur", cpw, cpw + cur, ncur), ("pav", cpw + cur, cpw + cur + mpw, 3),
            ("cur", cpw + cur + mpw, L_total - cpw, ncur), ("pav", L_total - cpw, L_total, 2)]


def owl_standin(m, x, y, z, s, mat, face_rz):
    """Stylised owl on the south stair cheek walls (COLE) - simplified stand-in."""
    m.lathe(x, y, [(0.0, 0.0), (0.22 * s, 0.02), (0.3 * s, 0.25 * s), (0.27 * s, 0.55 * s), (0.2 * s, 0.7 * s),
                   (0.23 * s, 0.82 * s), (0.2 * s, 0.98 * s), (0.0, 1.05 * s)], 12, mat, z_off=z)
    for side in (-1, 1):
        ex = x + math.cos(face_rz + side * 1.2) * 0.14 * s
        ey = y + math.sin(face_rz + side * 1.2) * 0.14 * s
        m.lathe(ex, ey, [(0.0, 0.0), (0.05 * s, 0.01), (0.03 * s, 0.12 * s), (0.0, 0.16 * s)], 6, mat, z_off=z + 0.98 * s)


def build_annex(lod):
    A = ANNEX
    Z = annex_levels(A)
    W, D = A["W"], A["D"]
    x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
    m = L.Mesh(f"SM_F01_LOCAnnex_LOD{lod}")
    sl = A["slab"]
    zr = A["z_roof"]
    # ---- core and roofs (three tiers: lower ring, attic, upper - AOC-R VERIFIED, heights APPROXIMATE)
    inset = sl if lod < 2 else A["pav_proj"]
    box_mats(m, x0 + inset, x1 - inset, y0 + inset, y1 - inset, 0.0, zr, "M_F01_Marble_Ashlar", top="M_F01_Roof_Copper")
    sb = A["setback"]
    ax0, ax1, ay0, ay1 = x0 + sb, x1 - sb, y0 + sb, y1 - sb
    box_mats(m, ax0, ax1, ay0, ay1, zr, A["z_attic"], "M_F01_Marble_Ashlar", top="M_F01_Roof_Copper")
    box_mats(m, -30.0, 30.0, -10.0, 10.0, A["z_attic"], A["z_attic"] + 1.6, "M_F01_Marble_Ashlar",
             top="M_F01_Roof_Copper")
    if lod < 2:
        # attic windows (regular rhythm aligned with the bays below)  APPROXIMATE
        for (o, u, ln, pitch) in (((ax0, ay0), (1, 0), ax1 - ax0, 3.38), ((ax1, ay0), (0, 1), ay1 - ay0, 3.24),
                                  ((ax1, ay1), (-1, 0), ax1 - ax0, 3.38), ((ax0, ay1), (0, -1), ay1 - ay0, 3.24)):
            fr = L.Frame(o, u)
            flush_windows(m, fr, 1.2, ln - 1.2, [zr + 1.3], 1.5, 2.6, pitch, 0.0, lod, f"annex-att-{u}",
                          frame_mat="M_F01_Metal_Bronze")
        m.sweep([(ax0, ay0), (ax1, ay0), (ax1, ay1), (ax0, ay1)], [(-0.3, 0.0), (0.06, 0.0), (0.06, 0.1), (-0.3, 0.1)],
                "M_F01_Marble_Smooth", closed=True, z=A["z_attic"])
    # ---- facades (CCW: S, E, N, W) with the corner rule (each spans a in [0, L - slab])
    facs = [("S", L.Frame((x0, y0), (1, 0)), W, False), ("E", L.Frame((x1, y0), (0, 1)), D, True),
            ("N", L.Frame((x1, y1), (-1, 0)), W, False), ("W", L.Frame((x0, y1), (0, -1)), D, True)]
    for name, fr, ln, short in facs:
        segs = annex_layout(A, ln, short)
        for si, (kind, a0, a1, n) in enumerate(segs):
            a1c = min(a1, ln - (sl if lod < 2 else A["pav_proj"] + 0.01))     # corner rule (LOD2: pavilion slab)
            ent = None
            if si == 2:
                if name in ("W", "E"):
                    ent = (3, 2.3, 4.1, 3.9)       # three pairs of bronze doors (COLE/WP)
                elif name == "S":
                    ent = (1, 2.8, 4.1, 0.0)       # former Copyright Office doors (LAB23)
            proud_a1 = (a1 + 0.05) if si == len(segs) - 1 else a1
            annex_segment(m, fr, A, Z, kind, a0, a1c, n, lod, f"annex-{name}{si}", entrance=ent,
                          proud_a1=proud_a1 if lod < 2 else None)
    # ---- pink granite skirt along the stepped outline (MARB VERIFIED)
    if lod < 2:
        outline = annex_outline(A)
        m.sweep(outline, [(-0.4, 0.0), (0.06, 0.0), (0.06, 1.25), (0.0, 1.35), (-0.4, 1.35)],
                "M_F01_Granite_Pink", closed=True, z=0.0)
    # ---- entrance stairs
    pp = A["pav_proj"]
    if lod < 2:
        # west (2nd St, main) and east (3rd St): broad flights in front of the three door pairs
        for fr, cx in ((L.Frame((x0, y1), (0, -1)), D / 2), (L.Frame((x1, y0), (0, 1)), D / 2)):
            L.stairs(m, fr, cx - 7.2, cx + 7.2, 0.0, 7, Z["zg"] / 7, 0.36, Z["zg"] - Z["zg"] / 7, "M_F01_Granite_Pink",
                     cheek=(0.8, 0.45, "M_F01_Granite_Pink"))
        # south (Independence Ave): stair with stylised owls and lamps (COLE)
        frS = L.Frame((x0, y0), (1, 0))
        L.stairs(m, frS, W / 2 - 4.6, W / 2 + 4.6, 0.0, 7, Z["zg"] / 7, 0.42, Z["zg"] - Z["zg"] / 7,
                 "M_F01_Granite_Pink", cheek=(1.0, 0.75, "M_F01_Granite_Pink"))
        run = 7 * 0.42
        for side in (-1, 1):
            ax = W / 2 + side * 5.1
            ox, oy, _ = frS.p(ax, run - 0.55, 0)
            owl_standin(m, ox, oy, Z["zg"] - Z["zg"] / 7 + 0.75, 0.85, "M_F01_Marble_Smooth", -math.pi / 2)
            lx, ly, _ = frS.p(ax, run + 0.9, 0)
            m.box(lx - 0.35, lx + 0.35, ly - 0.35, ly + 0.35, 0.0, 0.9, "M_F01_Granite_Pink")
            L.lamp_standard(m, lx, ly, 0.9, 3.2, "M_F01_Metal_Bronze", "M_F01_Lamp_Glass", lod)
    sockets = [
        ("SOCKET_Entrance_West_2ndSt", (x0 - 0.2, 0.0, Z["zg"]), math.pi),
        ("SOCKET_Entrance_East_3rdSt", (x1 + 0.2, 0.0, Z["zg"]), 0.0),
        ("SOCKET_Entrance_South_Independence", (0.0, y0 - 0.2, Z["zg"]), -math.pi / 2),
        ("SOCKET_Lamp_SouthStair_W", (-5.1, y0 - 7 * 0.42 - 0.9, 0.9), -math.pi / 2),
        ("SOCKET_Lamp_SouthStair_E", (5.1, y0 - 7 * 0.42 - 0.9, 0.9), -math.pi / 2),
        ("SOCKET_Signage_PENDING_NoInscriptionFound", (0.0, y0 - 0.1, 22.5), -math.pi / 2),
    ]
    hulls = [
        _box_pts(x0, x1, y0, y1, 0.0, A["z_pav"]),
        _box_pts(ax0, ax1, ay0, ay1, zr, A["z_attic"] + 1.6),
        _box_pts(x0 - 2.6, x0, D / 2 - 8.0 - D / 2, D / 2 + 8.0 - D / 2, 0.0, Z["zg"] + 0.45),
        _box_pts(x1, x1 + 2.6, -8.0, 8.0, 0.0, Z["zg"] + 0.45),
        _box_pts(-5.6, 5.6, y0 - 3.0, y0, 0.0, Z["zg"] + 0.75),
    ]
    return m, sockets, hulls


def annex_outline(A):
    """CCW stepped outline (pavilion faces at the footprint edge, curtains recessed)."""
    W, D, pp = A["W"], A["D"], A["pav_proj"]
    x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
    pts = []
    for name, (ox, oy), (ux, uy), ln, short in (("S", (x0, y0), (1, 0), W, False), ("E", (x1, y0), (0, 1), D, True),
                                                 ("N", (x1, y1), (-1, 0), W, False), ("W", (x0, y1), (0, -1), D, True)):
        nx, ny = uy, -ux
        for kind, a0, a1, _ in annex_layout(A, ln, short):
            b = 0.0 if kind == "pav" else -pp
            pts.append((ox + ux * a0 + nx * b, oy + uy * a0 + ny * b))
            pts.append((ox + ux * a1 + nx * b, oy + uy * a1 + ny * b))
    return L._clean_poly(pts)


# =============================================================================
# CANNON HOUSE OFFICE BUILDING (named 1962) — Carrere & Hastings, 1905-08; 5th storey 1913-14
# =============================================================================
CANNON = dict(
    D=380 * FT,        # 115.82 m N-S  APPROXIMATE - cross-check: with 65 ft wings this gives a court
    Ln=440 * FT,       # 134.11 m      300 ft wide / ~69,500 sq ft vs AOC "300-foot-wide ... 70,000 sq ft"
    nj_angle=13.5,     # New Jersey Ave, deg east of due south  APPROXIMATE (L'Enfant avenue geometry)
    wing=65 * FT,      # 19.81 m wing depth  APPROXIMATE
    chamfer=14.0,      # NW rotunda-corner entrance face  APPROXIMATE ("rotunda at the main entrance", AOC)
    z_plinth=0.45,     # granite plinth course  APPROXIMATE (granite listed by MTFA, location NF)
    z_base=9.0, z_styl=9.4,          # rusticated arcaded base + stylobate band  APPROXIMATE (two storeys)
    z_arch0=19.0, z_frieze=19.75, z_cor0=20.65, z_cor1=21.4,   # Doric entablature  APPROXIMATE
    z_bal=22.6, z_roof=28.0, z_attic=28.4,                     # balustrade; recessed attic (4th+5th)  APPROXIMATE
    col_d=1.2,         # Doric column lower diameter (order 9.6 m incl. plinth)  APPROXIMATE
    n_pairs=17,        # 34 fluted Doric columns  VERIFIED (AOC); coupled  PROBABLE (SAH "doubled")
    pair_cc=1.75,      # coupled-column centre spacing  APPROXIMATE
    loggia=2.9,        # loggia wall behind the colonnade  APPROXIMATE
    pil=0.3,           # pilastrade wall setback  APPROXIMATE
    base_d=0.6, upper_d=0.5,
    attic_set=2.4,     # attic setback behind the balustrade  APPROXIMATE
    pav_ne=12.0, pav_nw=6.0,
)


def cannon_geometry(C):
    D, Ln = C["D"], C["Ln"]
    off = D * math.tan(math.radians(C["nj_angle"]))
    NW, NE, SE, SW = (-Ln / 2, D / 2), (Ln / 2, D / 2), (Ln / 2, -D / 2), (-Ln / 2 + off, -D / 2)
    e1 = (1.0, 0.0)
    dx, dy = SW[0] - NW[0], SW[1] - NW[1]
    ln = math.hypot(dx, dy)
    e2 = (dx / ln, dy / ln)
    theta = math.acos(e1[0] * e2[0] + e1[1] * e2[1])
    t = C["chamfer"] / (2 * math.sin(theta / 2))
    Pn = (NW[0] + t * e1[0], NW[1] + t * e1[1])
    Pw = (NW[0] + t * e2[0], NW[1] + t * e2[1])
    outer = [SW, SE, NE, Pn, Pw]                     # CCW: S, E, N, chamfer, W
    court = L.offset_polygon_per_edge([SW, SE, NE, NW], [C["wing"]] * 4)
    # corner at the END of edge i: S->SE and E->NE are right angles; N->chamfer, chamfer->W and W->SW
    # (103.5 deg) are obtuse
    right = [True, True, False, False, False]
    return outer, court, right


def cannon_bays(C, ei, Lw):
    """Return (pairs, windows, entrance) along edge ei (a-coordinates)."""
    if ei == 3:          # chamfer: main entrance + large window; coupled pilasters at both edges
        return [1.6, Lw - 1.6], [], Lw / 2
    if ei == 2:          # north: NE pavilion | colonnade (17 coupled pairs) | NW pavilion segment
        s0, s1 = C["pav_ne"], Lw - C["pav_nw"]
        n = C["n_pairs"]
        pairs = [s0 + 2.0 + (s1 - s0 - 4.0) * k / (n - 1) for k in range(n)]
        wins = [(pairs[k] + pairs[k + 1]) / 2 for k in range(n - 1)]
        pav_pairs = [1.6, s0 - 1.6, s1 + 1.0]
        wins = [s0 / 2] + wins + [(s1 + Lw) / 2 + 0.6]
        return pav_pairs + pairs, wins, None
    margin = 1.6
    n = max(2, int(round((Lw - 2 * margin) / 6.2)) + 1)
    pairs = [margin + (Lw - 2 * margin) * k / (n - 1) for k in range(n)]
    wins = [(pairs[k] + pairs[k + 1]) / 2 for k in range(n - 1)]
    return pairs, wins, None


def cannon_slab_edges(m, poly, depths, c0, c1, right, openings, mat, lod, extra=None):
    """Facade slabs on each edge of `poly` (b in [-depths[i], 0] from the edge) with the corner
    rule at right-angle corners and wedge fillers at obtuse corners."""
    n = len(poly)
    inner = L.offset_polygon_per_edge(poly, depths)
    for i in range(n):
        p0, p1 = poly[i], poly[(i + 1) % n]
        fr = L.Frame.from_edge(p0, p1)
        j = (i + 1) % n
        a_end = fr.length - (depths[j] if right[i] else 0.0)
        ops = openings(i, fr) if openings else []
        if depths[i] > 1e-6:
            L.wall_with_openings(m, fr, 0.0, a_end, c0, c1, depths[i], ops, mat)
        if not right[i] and depths[i] > 1e-6:
            frj = L.Frame.from_edge(poly[j], poly[(j + 1) % n])
            O = p1
            Pi = (O[0] - fr.n[0] * depths[i], O[1] - fr.n[1] * depths[i])
            Pj = (O[0] - frj.n[0] * depths[j], O[1] - frj.n[1] * depths[j])
            Cc = inner[j]
            m.prism([O, Pj, Cc, Pi], c0, c1, mat)


def cannon_window(m, fr, a0, a1, c0, c1, depth, lod, key, arch=False):
    gs = glass_slot(key)
    mats = {"frame": "M_F01_Window_Frame_Dark", "glass": GLASS}
    if lod >= 2:
        m.lbox(fr, a0, a1, 0.0, 0.015, c0, c1 + ((a1 - a0) / 2 if arch else 0.0), GLASS[gs])
        return
    L.window_unit(m, fr, a0, a1, c0, c1, depth, lod, mats, cols=2, rows=3, glass_set_back=0.1, glass_slot=gs)
    if arch:
        r = (a1 - a0) / 2
        am = (a0 + a1) / 2
        pts = [(am + r * math.cos(math.pi * k / 14), c1 + r * math.sin(math.pi * k / 14)) for k in range(15)]
        m.lprism(fr, pts, -depth + 0.088, -depth + 0.1, GLASS[gs])
        if lod == 0:
            m.lbox(fr, am - 0.03, am + 0.03, -depth + 0.1, -depth + 0.14, c1, c1 + r, "M_F01_Window_Frame_Dark")


def cannon_column(m, x, y, C, lod):
    z0 = C["z_styl"] + 0.35
    hcol = C["z_arch0"] - z0
    if lod >= 2:
        r = C["col_d"] / 2
        m.prism([(x + r * math.cos(k * math.pi / 4), y + r * math.sin(k * math.pi / 4)) for k in range(8)],
                C["z_styl"], C["z_arch0"], "M_F01_Marble_Cannon")
        return
    prof, zb, zc, tr = L.doric_profile(hcol - 0.18, C["col_d"])
    if lod == 0:
        m.lathe(x, y, prof, 40, "M_F01_Marble_Cannon", flutes=20, flute_depth=0.05,
                flute_zone=(zb + 0.12, zc - 0.05), z_off=z0)
    else:
        simple = [prof[0], prof[3], prof[6]] + [p for p in prof if p[1] > zb and abs(p[1] - zb) > 0.01][::3] + prof[-3:]
        simple = sorted({(round(r, 4), round(z, 4)) for r, z in simple}, key=lambda t: t[1])
        m.lathe(x, y, simple, 12, "M_F01_Marble_Cannon", z_off=z0)
    ab = tr * 1.42
    top = prof[-1][1] + z0
    m.box(x - ab, x + ab, y - ab, y + ab, top, C["z_arch0"], "M_F01_Marble_Cannon")


def build_cannon(lod):
    C = CANNON
    outer, court, right = cannon_geometry(C)
    m = L.Mesh(f"SM_F01_Cannon_LOD{lod}")
    MAT = "M_F01_Marble_Cannon"
    n = len(outer)
    frames = [L.Frame.from_edge(outer[i], outer[(i + 1) % n]) for i in range(n)]
    lw = [f.length for f in frames]
    bays = [cannon_bays(C, i, lw[i]) for i in range(n)]
    ww, w_arch = 2.0, 2.2
    zb1, zs = C["z_base"], C["z_styl"]
    z2a, z2b, z3a, z3b = 10.4, 13.1, 14.7, 17.7         # 2nd / 3rd floor windows  APPROXIMATE
    # ---------------- cores (rings around the court)
    if lod < 2:
        base_core = L.offset_polygon_per_edge(outer, [C["base_d"]] * n)
        up_d = [C["pil"] + C["upper_d"]] * n
        up_d[2] = C["loggia"] + C["upper_d"]
        up_core = L.offset_polygon_per_edge(outer, up_d)
        L.ring_prism(m, base_core, court, 0.0, zs, MAT, "M_F01_Limestone_Court", MAT)
        L.ring_prism(m, up_core, court, zs, C["z_arch0"], MAT, "M_F01_Limestone_Court", MAT)
        L.ring_prism(m, L.offset_polygon_per_edge(outer, [0.2] * n), court, C["z_arch0"], C["z_cor1"], MAT,
                     "M_F01_Limestone_Court", MAT)
    else:
        L.ring_prism(m, outer, court, 0.0, C["z_cor1"], MAT, "M_F01_Limestone_Court", MAT)
    att = L.offset_polygon_per_edge(outer, [C["attic_set"]] * n)
    L.ring_prism(m, att, court, C["z_cor1"], C["z_roof"], MAT, "M_F01_Limestone_Court", "M_F01_Roof_Tar")
    # court deck (1955 garage roof, in place in Nov 1963)
    m.prism(court, 0.0, 0.18, "M_F01_Concrete")
    # ---------------- rusticated arcaded base (0 -> 9.0) with basement + arched first-floor windows
    def frame_shift(i, fr):
        """a-offset of a slab-polygon edge frame relative to the outer edge frame (inset polygons
        slide their vertices along the edges); openings are authored in outer coordinates."""
        return (fr.o[0] - frames[i].o[0]) * frames[i].u[0] + (fr.o[1] - frames[i].o[1]) * frames[i].u[1]

    def base_openings(i, fr):
        pairs, wins, ent = bays[i]
        sh = frame_shift(i, fr)
        ops = []
        for k, ac in enumerate(wins):
            ops.append((ac - w_arch / 2 - sh, ac + w_arch / 2 - sh, 3.3, 6.9 + w_arch / 2))
            ops.append((ac - 0.75 - sh, ac + 0.75 - sh, 0.85, 1.95))
        if ent is not None:
            ops.append((ent - 2.1 - sh, ent + 2.1 - sh, C["z_plinth"], 5.6 + 2.1))
        return ops
    if lod < 2:
        bd = [C["base_d"]] * n
        if lod == 0:
            # rustication: courses 0.55 m + recessed channel 0.05 m (deep horizontal joints)
            z = C["z_plinth"]
            while z < zb1 - 1e-6:
                z1 = min(z + 0.55, zb1)
                cannon_slab_edges(m, outer, bd, z, z1, right, base_openings, MAT, lod)
                if z1 < zb1 - 1e-6:
                    z2 = min(z1 + 0.05, zb1)
                    cannon_slab_edges(m, L.offset_polygon_per_edge(outer, [0.04] * n), [C["base_d"] - 0.04] * n,
                                      z1, z2, right, base_openings, MAT, lod)
                    z = z2
                else:
                    z = z1
        else:
            cannon_slab_edges(m, outer, bd, C["z_plinth"], zb1, right, base_openings, MAT, lod)
        for i in range(n):
            fr = frames[i]
            pairs, wins, ent = bays[i]
            for k, ac in enumerate(wins):
                L.arch_fillers(m, fr, ac - w_arch / 2, ac + w_arch / 2, 6.9, C["base_d"], MAT, segs=10)
                cannon_window(m, fr, ac - w_arch / 2, ac + w_arch / 2, 3.3, 6.9, C["base_d"], lod,
                              f"cannon-{i}-a{k}", arch=True)
                cannon_window(m, fr, ac - 0.75, ac + 0.75, 0.85, 1.95, C["base_d"], lod, f"cannon-{i}-b{k}")
                if lod == 0:
                    m.lbox(fr, ac - 0.22, ac + 0.22, 0.0, 0.1, 6.9 + w_arch / 2 - 0.35, 6.9 + w_arch / 2 + 0.25, MAT)
            if ent is not None:
                L.arch_fillers(m, fr, ent - 2.1, ent + 2.1, 5.6, C["base_d"], MAT, segs=14)
                bdoor = -C["base_d"] + 0.12
                m.lbox(fr, ent - 2.1, ent + 2.1, bdoor - 0.08, bdoor, C["z_plinth"], 5.6, "M_F01_Metal_Bronze")
                if lod == 0:
                    # door pair with glazed upper panels and a transom bar (period entrance, APPROXIMATE)
                    for (q0, q1) in ((ent - 1.45, ent - 0.08), (ent + 0.08, ent + 1.45)):
                        m.lbox(fr, q0 + 0.15, q1 - 0.15, bdoor, bdoor + 0.01, 2.2, 4.1, GLASS[0])
                        m.lbox(fr, q0, q1, bdoor, bdoor + 0.05, C["z_plinth"], C["z_plinth"] + 0.12, "M_F01_Metal_Bronze")
                    m.lbox(fr, ent - 2.1, ent + 2.1, bdoor, bdoor + 0.06, 4.45, 4.65, "M_F01_Metal_Bronze")
                    m.lbox(fr, ent - 2.1, ent - 1.45, bdoor, bdoor + 0.04, C["z_plinth"], 4.45, "M_F01_Marble_Cannon")
                    m.lbox(fr, ent + 1.45, ent + 2.1, bdoor, bdoor + 0.04, C["z_plinth"], 4.45, "M_F01_Marble_Cannon")
                fan = [(ent + 2.1 * math.cos(math.pi * k / 16), 5.6 + 2.1 * math.sin(math.pi * k / 16)) for k in range(17)]
                m.lprism(fr, fan, bdoor - 0.02, bdoor, GLASS[1])
                L.stairs(m, fr, ent - 3.4, ent + 3.4, 0.05, 3, C["z_plinth"] / 3, 0.4, C["z_plinth"], "M_F01_Granite_Grey")
        # granite plinth + stylobate band (continuous sweeps)
        m.sweep(outer, [(-0.4, 0.0), (0.05, 0.0), (0.05, C["z_plinth"]), (-0.4, C["z_plinth"])], "M_F01_Granite_Grey",
                closed=True, z=0.0)
        m.sweep(outer, [(-0.6, 0.0), (0.0, 0.0), (0.06, 0.06), (0.1, 0.12), (0.1, 0.4), (-0.6, 0.4)], MAT,
                closed=True, z=zb1)
    else:
        for i in range(n):
            fr = frames[i]
            for k, ac in enumerate(bays[i][1]):
                cannon_window(m, fr, ac - w_arch / 2, ac + w_arch / 2, 3.3, 6.9, 0.0, 2, f"cannon-{i}-a{k}", arch=True)
    # ---------------- upper storeys (2nd-3rd): pilastrade walls; Independence Ave loggia + colonnade
    face_up = L.offset_polygon_per_edge(outer, [C["pil"]] * n)
    if lod < 2:
        depths = [C["upper_d"]] * n
        depths[2] = C["loggia"] + C["upper_d"] - C["pil"]
        s0n, s1n = C["pav_ne"], lw[2] - C["pav_nw"]

        def up_openings(i, fr):
            pairs, wins, ent = bays[i]
            sh = frame_shift(i, fr)
            ops = []
            if i == 3:
                ops.append((ent - 1.6 - sh, ent + 1.6 - sh, 10.6, 15.8))
                return ops
            for ac in wins:
                if i == 2 and s0n < ac < s1n:
                    continue          # colonnade bays are built on the loggia wall below
                ops += [(ac - ww / 2 - sh, ac + ww / 2 - sh, z2a, z2b), (ac - ww / 2 - sh, ac + ww / 2 - sh, z3a, z3b)]
            if i == 2:
                ops.append((s0n - sh, s1n - sh, zs, C["z_arch0"]))   # open loggia (whole span)
            return ops
        cannon_slab_edges(m, face_up, depths, zs, C["z_arch0"], right, up_openings, MAT, lod)
        # loggia wall with windows behind the colonnade
        frN = frames[2]
        lg = L.Mesh_proxy(m, frN, -C["loggia"])
        wins_lg = [ac for ac in bays[2][1] if s0n < ac < s1n]
        ops_lg = [o for ac in wins_lg for o in ((ac - ww / 2, ac + ww / 2, z2a, z2b), (ac - ww / 2, ac + ww / 2, z3a, z3b))]
        L.wall_with_openings(lg, None, s0n, s1n, zs, C["z_arch0"], C["upper_d"], ops_lg, MAT)
        # windows (pilastrade + loggia)
        for i in range(n):
            fr = frames[i]
            pairs, wins, ent = bays[i]
            if i == 3:
                frc = L.Frame((fr.o[0] - fr.n[0] * C["pil"], fr.o[1] - fr.n[1] * C["pil"]), fr.u)
                cannon_window(m, frc, ent - 1.6, ent + 1.6, 10.6, 14.2, C["upper_d"], lod, "cannon-ch-big", arch=True)
                continue
            for k, ac in enumerate(wins):
                in_lg = (i == 2 and s0n < ac < s1n)
                bshift = C["loggia"] if in_lg else C["pil"]
                frw = L.Frame((fr.o[0] - fr.n[0] * bshift, fr.o[1] - fr.n[1] * bshift), fr.u)
                for r, (c0, c1) in enumerate(((z2a, z2b), (z3a, z3b))):
                    cannon_window(m, frw, ac - ww / 2, ac + ww / 2, c0, c1, C["upper_d"], lod, f"cannon-{i}-u{k}-{r}")
                    if lod == 0:
                        # architrave surround + sill
                        m.lbox(frw, ac - ww / 2 - 0.2, ac + ww / 2 + 0.2, 0.0, 0.06, c1, c1 + 0.2, MAT)
                        m.lbox(frw, ac - ww / 2 - 0.2, ac - ww / 2, 0.0, 0.06, c0, c1, MAT)
                        m.lbox(frw, ac + ww / 2, ac + ww / 2 + 0.2, 0.0, 0.06, c0, c1, MAT)
                        m.lbox(frw, ac - ww / 2 - 0.25, ac + ww / 2 + 0.25, 0.0, 0.1, c0 - 0.12, c0, MAT)
        # coupled pilasters (pilastrade) and responds on the loggia wall
        for i in range(n):
            fr = frames[i]
            pairs, wins, ent = bays[i]
            for k, pc in enumerate(pairs):
                in_lg = (i == 2 and s0n + 0.5 < pc < s1n - 0.5)
                bshift = C["loggia"] if in_lg else C["pil"]
                frp = L.Frame((fr.o[0] - fr.n[0] * bshift, fr.o[1] - fr.n[1] * bshift), fr.u)
                for dx in (-C["pair_cc"] / 2, C["pair_cc"] / 2):
                    L.fluted_pilaster(m, frp, pc + dx, 0.95, zs, C["z_arch0"], 0.0, 0.22, 7 if not in_lg else 0, lod,
                                      MAT, cap_h=0.55, base_h=0.4)
        # colonnade: 17 coupled pairs of fluted Doric columns on a continuous plinth
        frN = frames[2]
        for k, pc in enumerate(bays[2][0][3:]):
            px0, py0, _ = frN.p(pc, -0.85, 0)
            m.lbox(frN, pc - C["pair_cc"] / 2 - 0.82, pc + C["pair_cc"] / 2 + 0.82, -1.67, -0.03, zs, zs + 0.35, MAT)
            for dx in (-C["pair_cc"] / 2, C["pair_cc"] / 2):
                x, y, _ = frN.p(pc + dx, -0.85, 0)
                cannon_column(m, x, y, C, lod)
    else:
        frN = frames[2]
        for pc in bays[2][0][3:]:
            for dx in (-C["pair_cc"] / 2, C["pair_cc"] / 2):
                x, y, _ = frN.p(pc + dx, 0.6, 0)
                cannon_column(m, x, y, C, 2)
        for i in range(n):
            fr = frames[i]
            for k, ac in enumerate(bays[i][1]):
                for (c0, c1) in ((z2a, z2b), (z3a, z3b)):
                    cannon_window(m, fr, ac - ww / 2, ac + ww / 2, c0, c1, 0.0, 2, f"cannon-{i}-u{k}")
    # ---------------- entablature: architrave fascia, frieze with triglyphs, cornice (sweeps)
    if lod < 2:
        # profiles end exactly at the entablature core face (out = -0.2): adjacent, never coplanar-overlapping
        m.sweep(outer, [(-0.2, 0.0), (-0.12, 0.0), (-0.12, 0.33), (-0.08, 0.37), (-0.08, 0.75), (-0.2, 0.75)], MAT,
                closed=True, z=C["z_arch0"])
        m.sweep(outer, [(-0.2, 0.0), (0.0, 0.0), (0.08, 0.1), (0.48, 0.22), (0.62, 0.32), (0.62, 0.62), (0.56, 0.75),
                        (-0.2, 0.75)], MAT, closed=True, z=C["z_cor0"])
        if lod == 0:
            frz0, frz1 = C["z_frieze"] + 0.04, C["z_cor0"] - 0.04
            for i in range(n):
                fr = frames[i]
                step = 1.55
                cnt = int((lw[i] - 1.0) / step)
                for k in range(cnt):
                    a = 0.5 + (k + 0.5) * (lw[i] - 1.0) / cnt
                    # triglyph (three bars) and a mutule block under the cornice soffit
                    for dx in (-0.2, 0.0, 0.2):
                        m.lbox(fr, a + dx - 0.07, a + dx + 0.07, -0.2, -0.12, frz0, frz1, MAT)
                    m.lbox(fr, a - 0.32, a + 0.32, -0.1, 0.42, C["z_cor0"] + 0.12, C["z_cor0"] + 0.2, MAT)
    else:
        # LOD2 cornice: starts at the wall face (out = 0) so its top never shares the core ring's top plane
        m.sweep(outer, [(0.0, 0.0), (0.5, 0.0), (0.5, 0.75), (0.0, 0.75)], MAT, closed=True, z=C["z_cor0"])
    # ---------------- balustrade (plinth + rail sweeps, balusters per edge) and recessed attic
    bal_poly = L.offset_polygon_per_edge(outer, [0.3] * n)
    hb = C["z_bal"] - C["z_cor1"]
    m.sweep(bal_poly, [(-0.55, 0.0), (0.0, 0.0), (0.0, 0.2), (-0.55, 0.2)], MAT, closed=True, z=C["z_cor1"])
    m.sweep(bal_poly, [(-0.6, 0.0), (0.04, 0.0), (0.04, 0.17), (-0.6, 0.17)], MAT, closed=True, z=C["z_bal"] - 0.17)
    for i in range(n):
        frb = L.Frame.from_edge(bal_poly[i], bal_poly[(i + 1) % n])
        peds = [p for p in bays[i][0]] if i != 3 else []
        # balusters only (plinth/rail are the sweeps above)
        nbal = int((frb.length - 1.2) / 0.36)
        for k in range(nbal):
            a = 0.6 + (k + 0.5) * (frb.length - 1.2) / nbal
            if any(abs(a - p) < 0.65 for p in peds):
                continue
            x, y, _ = frb.p(a, -0.28, 0)
            turned = lod == 0 and i in (1, 2, 3)          # visible fronts: Independence, 1st St, chamfer
            if lod == 1 and k % 2:
                continue
            if turned:
                r = 0.13
                bh = hb - 0.37
                prof = [(r * 0.6, 0.0), (r * 0.42, 0.14 * bh), (r * 0.95, 0.4 * bh), (r * 0.36, 0.74 * bh),
                        (r * 0.6, 0.88 * bh), (r * 0.6, bh)]
                m.lathe(x, y, prof, 6, MAT, z_off=C["z_cor1"] + 0.2, angle0=math.pi / 6)
            elif lod <= 1:
                w2 = 0.07 if lod == 0 else 0.09
                m.lbox(frb, a - w2, a + w2, -0.35, -0.21, C["z_cor1"] + 0.2, C["z_bal"] - 0.17, MAT)
        for p in peds:
            m.lbox(frb, p - 0.42, p + 0.42, -0.58, 0.02, C["z_cor1"] + 0.2, C["z_bal"] - 0.17, MAT)
        if lod >= 2:
            m.lbox(frb, 0.6, frb.length - 0.6, -0.45, -0.1, C["z_cor1"] + 0.2, C["z_bal"] - 0.17, MAT)
    m.sweep(att, [(-0.4, 0.0), (0.06, 0.0), (0.06, 0.4), (-0.4, 0.4)], MAT, closed=True, z=C["z_roof"])
    na = len(att)
    for i in range(na):
        fra = L.Frame.from_edge(att[i], att[(i + 1) % na])
        # one window per facade bay below, projected onto the attic face  APPROXIMATE
        fr_out = frames[i]
        for k, ac in enumerate(bays[i][1]):
            px, py, _ = fr_out.p(ac, 0.0, 0)
            a_att = (px - fra.o[0]) * fra.u[0] + (py - fra.o[1]) * fra.u[1]
            if 1.0 < a_att < fra.length - 1.0:
                flush_windows(m, fra, a_att - 0.7, a_att + 0.7, [22.7, 25.5], 1.2, 1.7, 1.4, 0.0, lod,
                              f"cannon-att{i}-{k}")
    # court-facing windows (limestone fronts, basement exposed on the court)
    if lod < 2:
        nc = len(court)
        for i in range(nc):
            p0, p1 = court[(i + 1) % nc], court[i]           # walk CW so n faces into the court
            frc = L.Frame.from_edge(p0, p1)
            # court windows: glass only (court seen from the air / through the archway only)
            flush_windows(m, frc, 2.0, frc.length - 2.0, [1.2, 5.0, 10.6, 15.0], 1.4, 2.3, 4.0, 0.0, 2,
                          f"cannon-court{i}", frame_mat="M_F01_Window_Frame_Dark")
    # ---------------- sockets / collision
    frc = frames[3]
    ex, ey, _ = frc.p(lw[3] / 2, 0.2, 0)
    sockets = [
        ("SOCKET_Entrance_Main_NW_Rotunda", (ex, ey, C["z_plinth"]), math.atan2(frc.n[1], frc.n[0])),
        ("SOCKET_CourtArchway_PENDING_location_NF", (0.0, -C["D"] / 2 - 0.2, 0.0), -math.pi / 2),
        ("SOCKET_C19_Order_Swap_Colonnade", frames[2].p(lw[2] / 2, -0.85, C["z_styl"]), math.pi / 2),
        ("SOCKET_Signage_PENDING", frames[2].p(lw[2] / 2, 0.1, C["z_frieze"]), math.pi / 2),
    ]
    hulls = []
    for i in range(n):
        p0, p1 = outer[i], outer[(i + 1) % n]
        fr = frames[i]
        q0 = fr.p(0.0, -C["wing"], 0)
        q1 = fr.p(lw[i], -C["wing"], 0)
        pts = []
        for (x, y) in (p0, p1, q0[:2], q1[:2]):
            pts += [(x, y, 0.0), (x, y, C["z_bal"])]
        hulls.append(pts)
    return m, sockets, hulls


def _box_pts(x0, x1, y0, y1, z0, z1):
    return [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]


# =============================================================================
# export
# =============================================================================
BUILDINGS = {
    "folger": ("SM_F01_Folger", build_folger),
    "annex": ("SM_F01_LOCAnnex", build_annex),
    "cannon": ("SM_F01_Cannon", build_cannon),
}


def export_building(key, tex_dir, out_dir):
    name, builder = BUILDINGS[key]
    L.reset_scene()
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    meshes = {}
    sockets = hulls = None
    inverted = {}
    for lod in (0, 1, 2):
        mesh, s, h = builder(lod)
        if lod == 0:
            sockets, hulls = s, h
        meshes[lod] = mesh
        bad = L.orientation_audit(mesh)
        inverted[f"LOD{lod}"] = len(bad)
        for vol, mname, c in bad[:10]:
            print(f"[audit] {mesh.name}: inward-wound shell {mname} at {c} (volume {vol:.4f} m^3)")
    used = sorted({mname for mesh in meshes.values() for _, mname, _ in mesh.faces})
    mats = M.make_materials(tex_dir, used)
    tiles = {n: M.tile_of(n) for n in used}
    objs = {}
    for lod, mesh in meshes.items():
        objs[lod] = L.to_object(mesh, col, mats, tiles)
    for i, pts in enumerate(hulls):
        L.convex_hull_object(f"UCX_{name}_{i:02d}", pts, col, mats[used[0]])
    for sname, loc, rz in sockets:
        L.socket(sname, loc, col, rz, parent=objs[0])
    path = os.path.join(out_dir, f"{name}.glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_yup=True, export_apply=False,
                              export_image_format='JPEG', export_jpeg_quality=92, export_extras=False,
                              export_cameras=False)
    stats = {f"LOD{lod}": L.mesh_stats(o) for lod, o in objs.items()}
    stats["materials"] = used
    stats["sockets"] = [{"name": sn, "location_m": [round(v, 4) for v in loc], "rotation_z_rad": round(rz, 5)}
                        for sn, loc, rz in sockets]
    stats["collision_hulls"] = len(hulls)
    stats["inward_wound_shells"] = inverted
    stats["glb_bytes"] = os.path.getsize(path)
    return path, stats


def all_material_names():
    return list(M.TEXTURED.keys())


def main(argv):
    keys = [a for a in argv if a in BUILDINGS] or list(BUILDINGS)
    full = not [a for a in argv if a in BUILDINGS]
    if full and os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    if full or not os.path.isdir(TEXDIR):
        M.make_textures(TEXDIR, all_material_names())
    report_path = os.path.join(OUT, "build_report.json")
    report = {}
    if not full and os.path.exists(report_path):
        report = json.load(open(report_path))
    for k in keys:
        path, stats = export_building(k, TEXDIR, OUT)
        report[BUILDINGS[k][0]] = stats
        lod0 = stats["LOD0"]
        print(f"[build] {os.path.basename(path)}: LOD0 {lod0['tris']} tris, size "
              f"{lod0['size_m'][0]:.2f} x {lod0['size_m'][1]:.2f} x {lod0['size_m'][2]:.2f} m, "
              f"LOD1 {stats['LOD1']['tris']}, LOD2 {stats['LOD2']['tris']}, {stats['glb_bytes'] / 1e6:.1f} MB")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    write_pcg_interface(report, os.path.join(OUT, "PCG_INTERFACE.json"))


# ITS ALIVE typing of every material slot: (material family, exposure topologies, role)
SLOT_TYPES = {
    "M_F01_Marble_Ashlar": ("UM", ["VE", "RE"], "Annex Georgia white marble ashlar walls"),
    "M_F01_Marble_Folger": ("UM", ["VE", "RE", "HW"], "Folger Georgia marble ashlar, alternating course heights"),
    "M_F01_Marble_Cannon": ("UM", ["VE", "RE", "HW"], "Cannon marble (South Dover NY / Georgia) walls, order, entablature"),
    "M_F01_Marble_Smooth": ("UM", ["VE", "RE", "HW"], "monolithic marble trim, pilasters, plinths, relief stand-ins"),
    "M_F01_Marble_Incised": ("UM", ["VE"], "carved inscription strokes (reads as incised shadow)"),
    "M_F01_Granite_Pink": ("UM", ["VE", "HW", "GT"], "Annex North Carolina pink granite skirt and stairs"),
    "M_F01_Granite_Grey": ("UM", ["VE", "HW", "GT"], "Cannon granite plinth course and steps (APPROXIMATE)"),
    "M_F01_Brick_Glazed": ("UM", ["VE"], "Folger rear / courtyard glazed brick (location PROBABLE)"),
    "M_F01_Limestone_Court": ("UM", ["VE"], "Cannon court fronts, Bedford Indiana limestone"),
    "M_F01_Paving_Bluestone": ("UM", ["HW"], "Folger forecourt bluestone accents"),
    "M_F01_Concrete": ("MM", ["HW"], "Cannon court garage deck (1955)"),
    "M_F01_Glass": ("GL", ["VE"], "glazing, day slot A"),
    "M_F01_Glass_NightLit": ("GL", ["VE"], "glazing slot B (~35 % of windows): identical by day; drive emissive for night"),
    "M_F01_Lamp_Glass": ("GL", ["FH"], "opal lamp globes: night emissive slot"),
    "M_F01_Metal_Bronze": ("MT", ["FH", "VE"], "statuary bronze doors, window metal, Annex spandrels (PROBABLE)"),
    "M_F01_Metal_Aluminium": ("MT", ["FH", "VE"], "Folger cast-aluminium grilles and doors"),
    "M_F01_Window_Frame_Dark": ("CT", ["VE"], "painted sash over WD/MT substrate (APPROXIMATE)"),
    "M_F01_Roof_Copper": ("MT", ["RE"], "Annex copper roof tiers (~25-year patina)"),
    "M_F01_Roof_Tar": ("AP", ["RE"], "flat bituminous roofs behind parapets"),
    "M_F01_Turf_Placeholder": ("LG", ["GT"], "PLACEHOLDER lawn bed: replace with DC-N03 turf via SOCKET_Lawn_N03_Turf"),
}


def write_pcg_interface(report, path):
    assets = {}
    for name, st in sorted(report.items()):
        assets[name] = {
            "file": f"{name}.glb",
            "units": "glTF metres (UE 5.8 import -> cm); Blender source Z-up, glTF Y-up",
            "pivot": "footprint bounding-box centre at grade (z = 0); Cannon: centre of the un-chamfered trapezoid bbox",
            "axes": "+X east, +Y north (map-aligned named building; R02 UE frame is +X east, +Y south, cm)",
            "lods": {k: {"object": f"{name}_{k}", "tris": st[k]["tris"], "size_m": [round(v, 3) for v in st[k]["size_m"]]}
                     for k in ("LOD0", "LOD1", "LOD2")},
            "suggested_lod_screen_size": {"LOD0": 1.0, "LOD1": 0.35, "LOD2": 0.12},
            "collision": f"{st['collision_hulls']} convex hulls named UCX_{name}_NN",
            "sockets": st["sockets"],
            "material_slots": [{"slot": mname, "its_alive_family": SLOT_TYPES.get(mname, ("?", [], ""))[0],
                                "exposure": SLOT_TYPES.get(mname, ("?", [], ""))[1],
                                "role": SLOT_TYPES.get(mname, ("?", [], ""))[2]} for mname in st["materials"]],
        }
    data = {
        "job_id": "DC-F01", "version": "v001", "kind": "PCG assembly - named overrides (not generic repetition)",
        "assets": assets,
        "typed_slots": {
            "night_glazing": "M_F01_Glass_NightLit carries ~35 % of windows, chosen by md5(window key) % 100 < 35 "
                             "(stable across rebuilds). Drive emissive (moodbook TUNGSTEN #C49D63) for night states (DC-L01).",
            "kit_swaps": {
                "DC-C19": "SOCKET_C19_Order_Swap_Colonnade on the Cannon: the coupled Doric columns are a lightweight "
                          "background-LOD derivation of C19 vocabulary; swap to a C19 runtime variant when one exists.",
                "DC-C18": "no approved C18 delivery; Annex curtain bays / Cannon pilastrade bays are named-building bays, "
                          "not C18 substitutes (request: kits are vocabulary, not silhouette substitutes).",
                "DC-C20": "not applicable to C10 (no red tile roofs).",
                "DC-N03": "SOCKET_Lawn_N03_Turf (Folger terrace lawn bed placeholder).",
            },
            "signage_pending": "SOCKET_Signage_* mark positions where 1963 building names may be carved; "
                               "positions NOT verified, nothing carved except the two verified Folger quotations.",
        },
        "seeds": {
            "glass_slot": "md5 hash of '<building>-<facade>-<window index>' keys",
            "textures": {k: v.get("seed") for k, v in M.TEXTURED.items()},
            "relief_standins": "Python random.Random(seed) per panel (Folger 1000+k); deterministic",
        },
        "placement": "NOT placed. Re-snap footprints to DC-R02 v001 evidence cards; DC-B01 owns the level. Base is flat "
                     "at z = 0 (real sites slope: Folger/Annex block falls toward Independence Ave) - B01 to sink / "
                     "extend plinths into terrain.",
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main(sys.argv[1:])
