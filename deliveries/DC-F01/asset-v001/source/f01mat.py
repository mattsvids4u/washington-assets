"""Portable PBR textures and Blender materials for DC-F01 (deterministic, seeded).

Textures are generated procedurally with numpy (tileable via FFT noise) and written as PNG:
  <name>_BaseColor.png (sRGB), <name>_ORM.png (R=AO 1.0, G=roughness, B=metallic, linear),
  <name>_Normal.png (OpenGL / glTF convention, linear).
Stone textures carry real ashlar joint patterns whose course height matches the building's
documented or APPROXIMATE course module, mapped by world-space UVs (metres per UV unit =
TILE_M of that material), so joints line up across faces.

Material slots are stable names `M_F01_*`; UE should remap them to project master materials.
Colours: historical stone/metal colours, checked against the moodbook p11 relationships
(COLD PAPER #DFDFD4 ~ lifted marble neutral, CHARCOAL #131D1B ~ deepest shadows/roof).
"""
import math
import os

import numpy as np
from PIL import Image

import bpy

RES_STONE = 1024
RES_ROOF = 512


def srgb_to_linear(c):
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def pnoise(n, beta, seed, fmax=None):
    """Tileable n x n noise with ~1/f^beta power spectrum, zero mean, unit std."""
    rng = np.random.default_rng(seed)
    w = rng.standard_normal((n, n))
    F = np.fft.fft2(w)
    fx = np.fft.fftfreq(n)[:, None]
    fy = np.fft.fftfreq(n)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1.0
    F = F * f ** (-beta / 2.0)
    if fmax is not None:
        F = F * (f < fmax)
    F[0, 0] = 0
    out = np.real(np.fft.ifft2(F))
    out -= out.mean()
    out /= out.std() + 1e-12
    return out


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ashlar_fields(n, tile_m, course_m, len_range, seed, joint_mm=5.0, stagger=True, pattern=None):
    """Return (block_id, joint_dist_px, course_index) arrays for a tileable ashlar pattern.
    Rows are v (up), columns u. Courses divide tile_m exactly. pattern: optional list of
    (course_height_m, (len_min, len_max)) repeated up the tile (alternating tall/short rows)."""
    rng = np.random.default_rng(seed)
    px_per_m = n / tile_m
    if pattern:
        rep = sum(hh for hh, _ in pattern)
        nrep = max(1, int(round(tile_m / rep)))
        heights = [hh * tile_m / (rep * nrep) for _ in range(nrep) for hh, _ in pattern]
        lranges = [lr for _ in range(nrep) for _, lr in pattern]
    else:
        nc = max(1, int(round(tile_m / course_m)))
        heights = [tile_m / nc] * nc
        lranges = [len_range] * nc
    edges = np.concatenate([[0.0], np.cumsum(heights)]) * px_per_m
    ncourse = len(heights)
    vv = np.arange(n)[:, None] + 0.5
    uu = np.arange(n)[None, :] + 0.5
    course = np.clip(np.searchsorted(edges, vv[:, 0], side='right') - 1, 0, ncourse - 1)[:, None] * np.ones((1, n), dtype=int)
    block = np.zeros((n, n), dtype=np.int64)
    jdist = np.full((n, n), 1e9)
    dv = np.minimum(vv - edges[course], edges[course + 1] - vv)
    jdist = np.minimum(jdist, dv)
    for k in range(ncourse):
        lens = []
        tot = 0.0
        while tot < tile_m * 0.999:
            L = rng.uniform(*lranges[k])
            lens.append(L)
            tot += L
        lens = np.array(lens) * (tile_m / tot)
        bounds = np.concatenate([[0.0], np.cumsum(lens)]) * px_per_m
        off = rng.uniform(0, n) if stagger else 0.0
        rows = slice(int(round(edges[k])), int(round(edges[k + 1])))
        u = (uu[0] + off) % n
        idx = np.searchsorted(bounds, u, side='right') - 1
        idx = np.clip(idx, 0, len(lens) - 1)
        d_left = u - bounds[idx]
        d_right = bounds[idx + 1] - u
        du = np.minimum(d_left, d_right)
        block[rows, :] = (k * 1000 + idx)[None, :]
        jdist[rows, :] = np.minimum(jdist[rows, :], du[None, :])
    return block, jdist, course, px_per_m


def height_to_normal(h, strength):
    dx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) * 0.5
    dy = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) * 0.5
    nx = -dx * strength
    ny = -dy * strength
    nz = np.ones_like(h)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.stack([nx / ln, ny / ln, nz / ln], axis=-1)


def _save_rgb(arr01, path, srgb=True):
    a = np.clip(arr01, 0, 1)
    img = (a * 255.0 + 0.5).astype(np.uint8)
    img = img[::-1]                      # rows were generated v-up; images are top-down
    Image.fromarray(img, 'RGB').save(path, optimize=True)


def _per_block(block, values_fn, seed):
    ids, inv = np.unique(block, return_inverse=True)
    rng = np.random.default_rng(seed)
    vals = values_fn(rng, len(ids))
    return vals[inv].reshape(block.shape + vals.shape[1:])


# ----------------------------------------------------------------------------- stone

def stone_texture(out_dir, name, n, tile_m, course_m, len_range, base_srgb, seed,
                  vein=0.0, speckle=None, joint_mm=4.0, joint_srgb=None, rough=(0.5, 0.06),
                  block_var=0.025, joints=True, chamfer_mm=6.0, pattern=None):
    rng_seed = seed
    block, jdist, course, ppm = ashlar_fields(n, tile_m, course_m, len_range, rng_seed, pattern=pattern)
    if not joints:
        block = np.zeros_like(block)
        jdist = np.full(block.shape, 1e9)
    jw = max(joint_mm / 1000.0 * ppm, 0.75)          # joint width in px
    cw = max(chamfer_mm / 1000.0 * ppm, 0.75)
    joint = 1.0 - smoothstep(jw * 0.5, jw * 0.5 + 0.9, jdist)
    edge = 1.0 - smoothstep(jw * 0.5, jw * 0.5 + cw, jdist)       # arris softening band
    base = np.array(base_srgb, dtype=np.float64) / 255.0
    col = np.ones((n, n, 3)) * base
    # per-block tone (quarried blocks differ slightly)
    tone = _per_block(block, lambda r, k: 1.0 + block_var * r.standard_normal(k), seed + 11)
    warm = _per_block(block, lambda r, k: 0.006 * r.standard_normal(k), seed + 12)
    col *= tone[..., None]
    col[..., 0] += warm
    col[..., 2] -= warm
    # mottling
    mot = pnoise(n, 3.2, seed + 1)
    col *= (1.0 + 0.018 * mot)[..., None]
    if vein > 0:
        theta = _per_block(block, lambda r, k: r.uniform(0, math.pi, k), seed + 13)
        phase = _per_block(block, lambda r, k: r.uniform(0, 50, k), seed + 14)
        yy, xx = np.mgrid[0:n, 0:n] / n * tile_m
        warp = pnoise(n, 2.6, seed + 2) * 0.35 + pnoise(n, 3.4, seed + 3) * 0.6
        f = xx * np.cos(theta) + yy * np.sin(theta)
        v = np.abs(np.sin((f * 2.2 + warp + phase) * math.pi))
        veins = (1.0 - v) ** 18
        fine = (1.0 - np.abs(np.sin((f * 7.0 + warp * 2.0 + phase) * math.pi))) ** 40
        col *= (1.0 - vein * (0.75 * veins + 0.35 * fine))[..., None]
    if speckle is not None:
        # granite: three-mineral mix from thresholded high-frequency noises
        hf1 = pnoise(n, 0.6, seed + 4)
        hf2 = pnoise(n, 0.8, seed + 5)
        hf3 = pnoise(n, 0.4, seed + 6)
        fel = np.array(speckle['feldspar']) / 255.0
        qtz = np.array(speckle['quartz']) / 255.0
        bio = np.array(speckle['biotite']) / 255.0
        m_q = smoothstep(0.35, 0.9, hf1)[..., None]
        m_b = smoothstep(1.25, 1.7, hf2)[..., None]
        g = fel * (1 - m_q) + qtz * m_q
        g = g * (1 - m_b) + bio * m_b
        g *= (1.0 + 0.05 * hf3)[..., None]
        col = g * tone[..., None]
    if joints:
        jc = np.array(joint_srgb if joint_srgb else [c * 0.78 for c in base_srgb]) / 255.0
        col = col * (1 - joint[..., None]) + jc * joint[..., None]
        col *= (1.0 - 0.06 * edge)[..., None]
    _save_rgb(col, os.path.join(out_dir, f"{name}_BaseColor.png"))
    r = rough[0] + rough[1] * pnoise(n, 2.0, seed + 7)
    r = r * (1 - joint) + 0.88 * joint
    orm = np.stack([np.ones((n, n)), np.clip(r, 0.05, 1.0), np.zeros((n, n))], axis=-1)
    _save_rgb(orm, os.path.join(out_dir, f"{name}_ORM.png"))
    h = -1.0 * joint - 0.35 * edge + 0.06 * pnoise(n, 2.4, seed + 8)
    if speckle is not None:
        h += 0.05 * pnoise(n, 0.7, seed + 9)
    nrm = height_to_normal(h, 2.2)
    _save_rgb(nrm * 0.5 + 0.5, os.path.join(out_dir, f"{name}_Normal.png"))


def copper_roof_texture(out_dir, name, n, tile_m, seam_m, seed):
    """Aged (c. 25-year) copper: batten seams, brown-green patina streaks."""
    vv, uu = np.mgrid[0:n, 0:n] / n * tile_m
    seam = np.abs(((uu / seam_m) % 1.0) - 0.5) * seam_m      # metres from seam centre line... inverted
    seam_d = seam_m * 0.5 - seam                             # distance to seam
    bat = 1.0 - smoothstep(0.015, 0.03, seam_d)
    streak = pnoise(n, 2.2, seed) * 0.6 + pnoise(n, 3.0, seed + 1) * 0.4
    brown = np.array([112, 84, 60]) / 255.0
    green = np.array([92, 128, 104]) / 255.0
    t = smoothstep(-0.2, 1.4, streak)[..., None]
    col = brown * (1 - t) + green * t
    col *= (1 - 0.12 * bat)[..., None]
    _save_rgb(col, os.path.join(out_dir, f"{name}_BaseColor.png"))
    r = 0.55 + 0.1 * pnoise(n, 2.0, seed + 2)
    met = 0.35 * (1 - t[..., 0])
    _save_rgb(np.stack([np.ones((n, n)), np.clip(r, 0, 1), met], -1), os.path.join(out_dir, f"{name}_ORM.png"))
    h = 1.0 * bat + 0.04 * pnoise(n, 1.8, seed + 3)
    _save_rgb(height_to_normal(h, 3.0) * 0.5 + 0.5, os.path.join(out_dir, f"{name}_Normal.png"))


def tar_roof_texture(out_dir, name, n, seed):
    g = pnoise(n, 1.2, seed) * 0.5 + pnoise(n, 2.8, seed + 1) * 0.5
    base = np.array([62, 62, 60]) / 255.0
    col = base * (1 + 0.12 * g)[..., None]
    _save_rgb(col, os.path.join(out_dir, f"{name}_BaseColor.png"))
    r = 0.9 + 0.05 * g
    _save_rgb(np.stack([np.ones((n, n)), np.clip(r, 0, 1), np.zeros((n, n))], -1),
              os.path.join(out_dir, f"{name}_ORM.png"))
    _save_rgb(height_to_normal(0.3 * pnoise(n, 0.9, seed + 2), 1.5) * 0.5 + 0.5,
              os.path.join(out_dir, f"{name}_Normal.png"))


# ----------------------------------------------------------------------------- specs

# metres per UV unit (texture tile size) — must match the generator's tile_m
TEXTURED = {
    # Georgia white marble ashlar. Course module APPROXIMATE (no measured course heights found):
    # 0.61 m (2 ft) courses, typical of 1930s federal marble cladding.
    "M_F01_Marble_Ashlar": dict(kind="stone", tile_m=3.66, course_m=0.61, len_range=(0.9, 1.8),
                                base_srgb=(222, 219, 210), vein=0.10, rough=(0.46, 0.05), seed=101),
    # Folger: white Georgia marble ashlar "primarily in alternating rows of larger and smaller
    # panels" (VERIFIED wording, NRHP form S4); row heights 0.76 / 0.38 m APPROXIMATE
    "M_F01_Marble_Folger": dict(kind="stone", tile_m=3.43, course_m=0.57, len_range=(1.0, 1.8),
                                base_srgb=(223, 220, 211), vein=0.09, rough=(0.45, 0.05), seed=109,
                                pattern=[(0.762, (1.2, 2.1)), (0.381, (0.6, 1.2))]),
    # same marble, monolithic surfaces (columns, mouldings, sculpture stand-ins, pilasters)
    "M_F01_Marble_Smooth": dict(kind="stone", tile_m=2.0, course_m=2.0, len_range=(2.0, 2.0),
                                base_srgb=(224, 221, 212), vein=0.08, rough=(0.42, 0.05), seed=102,
                                joints=False),
    # Cannon House Office Building marble (Vermont/Georgia per evidence card) - slightly greyer
    "M_F01_Marble_Cannon": dict(kind="stone", tile_m=3.0, course_m=0.6, len_range=(0.9, 1.6),
                                base_srgb=(214, 212, 205), vein=0.07, rough=(0.5, 0.05), seed=103),
    # rusticated base stone (Cannon) - deeper joints handled in geometry where visible
    "M_F01_Granite_Grey": dict(kind="stone", tile_m=3.0, course_m=0.75, len_range=(1.0, 2.0),
                               base_srgb=(170, 168, 165), seed=104, rough=(0.58, 0.05),
                               speckle=dict(feldspar=(176, 172, 168), quartz=(204, 202, 198), biotite=(52, 50, 50))),
    # North Carolina pink granite skirt (Annex)
    "M_F01_Granite_Pink": dict(kind="stone", tile_m=3.0, course_m=0.75, len_range=(1.0, 2.2),
                               base_srgb=(188, 150, 140), seed=105, rough=(0.55, 0.05),
                               speckle=dict(feldspar=(190, 146, 136), quartz=(206, 196, 190), biotite=(60, 52, 52))),
    # Folger rear / courtyard walls: glazed brick (APPROXIMATE colour; listed material, location inferred)
    "M_F01_Brick_Glazed": dict(kind="stone", tile_m=1.2, course_m=0.075, len_range=(0.2, 0.2),
                               base_srgb=(206, 196, 170), seed=108, rough=(0.32, 0.04), vein=0.0,
                               joint_srgb=(170, 165, 152)),
    "M_F01_Roof_Copper": dict(kind="copper", tile_m=4.0, seam_m=0.5, seed=106),
    "M_F01_Roof_Tar": dict(kind="tar", tile_m=6.0, seed=107),
}

# factor-only materials: (base colour sRGB, metallic, roughness)
PLAIN = {
    "M_F01_Glass": ((14, 18, 22), 0.0, 0.06),            # day glazing (slot A)
    "M_F01_Glass_NightLit": ((14, 18, 22), 0.0, 0.06),   # identical by day; night emissive slot (B)
    "M_F01_Metal_Bronze": ((64, 51, 38), 0.75, 0.48),     # statuary bronze, ~25 yr patina (Annex doors/windows)
    "M_F01_Metal_Aluminium": ((186, 189, 191), 1.0, 0.34),  # Folger grilles and doors
    "M_F01_Window_Frame_Dark": ((38, 40, 36), 0.0, 0.55),   # painted sash (Cannon, APPROXIMATE)
    "M_F01_Interior_Shade": ((40, 36, 30), 0.0, 0.8),       # drawn shades / deep interior (not exported unless used)
    "M_F01_Marble_Incised": ((150, 147, 140), 0.0, 0.8),    # carved letter strokes (reads as incised shadow)
    "M_F01_Turf_Placeholder": ((78, 96, 52), 0.0, 0.95),    # labelled slot - replace with DC-N03 turf
    "M_F01_Lamp_Glass": ((236, 230, 214), 0.0, 0.3),        # opal lamp globes (night emissive slot)
    "M_F01_Paving_Bluestone": ((96, 102, 108), 0.0, 0.7),   # Folger forecourt accents (S14)
    "M_F01_Limestone_Court": ((198, 188, 164), 0.0, 0.75),  # Cannon court fronts: Bedford, Indiana limestone (AOC-H)
    "M_F01_Concrete": ((168, 166, 160), 0.0, 0.85),         # Cannon court garage deck (1955, AOC-H/AOC-CY)
}

TUNGSTEN = (196, 157, 99)    # moodbook #C49D63 - night window glow


def tile_of(name):
    spec = TEXTURED.get(name)
    return spec["tile_m"] if spec else 2.0


def make_textures(tex_dir, names):
    os.makedirs(tex_dir, exist_ok=True)
    for name in names:
        spec = TEXTURED.get(name)
        if spec is None:
            continue
        if spec["kind"] == "stone":
            stone_texture(tex_dir, name, RES_STONE, spec["tile_m"], spec["course_m"], spec["len_range"],
                          spec["base_srgb"], spec["seed"], vein=spec.get("vein", 0.0),
                          speckle=spec.get("speckle"), rough=spec.get("rough", (0.5, 0.06)),
                          joints=spec.get("joints", True), pattern=spec.get("pattern"),
                          joint_srgb=spec.get("joint_srgb"))
        elif spec["kind"] == "copper":
            copper_roof_texture(tex_dir, name, RES_ROOF, spec["tile_m"], spec["seam_m"], spec["seed"])
        elif spec["kind"] == "tar":
            tar_roof_texture(tex_dir, name, RES_ROOF, spec["seed"])


def make_material(name, tex_dir):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    # Every shell is closed and wound outward (build.py audits this), so materials are
    # single-sided: glTF doubleSided = false -> UE imports one-sided materials.
    mat.use_backface_culling = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    if name in TEXTURED:
        def img(kind, colorspace):
            path = os.path.join(tex_dir, f"{name}_{kind}.png")
            im = bpy.data.images.load(path, check_existing=True)
            im.colorspace_settings.name = colorspace
            node = nt.nodes.new("ShaderNodeTexImage")
            node.image = im
            node.interpolation = 'Linear'
            return node
        bc = img("BaseColor", "sRGB")
        nt.links.new(bc.outputs["Color"], bsdf.inputs["Base Color"])
        orm = img("ORM", "Non-Color")
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(orm.outputs["Color"], sep.inputs["Color"])
        nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
        nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
        nm = img("Normal", "Non-Color")
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        nmap.inputs["Strength"].default_value = 1.0
        nt.links.new(nm.outputs["Color"], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    else:
        srgb, metal, rough = PLAIN[name]
        lin = srgb_to_linear(np.array(srgb) / 255.0)
        bsdf.inputs["Base Color"].default_value = (lin[0], lin[1], lin[2], 1.0)
        bsdf.inputs["Metallic"].default_value = metal
        bsdf.inputs["Roughness"].default_value = rough
    return mat


def make_materials(tex_dir, names):
    return {n: make_material(n, tex_dir) for n in names}
