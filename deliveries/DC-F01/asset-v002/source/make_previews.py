"""Small palette-quantised contact sheets of the actual renders for the Drive delivery folder
(the Drive connector only accepts inline base64, so full-resolution renders stay in the PR).

    python jobs/DC-F01/make_previews.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, "renders", "review")
OUT = os.path.join(HERE, "renders", "previews")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SHEETS = {
    "F01_preview_LOCAnnex.png": ["SM_F01_LOCAnnex_textured_street_sw.png", "SM_F01_LOCAnnex_textured_street_w.png",
                                 "SM_F01_LOCAnnex_textured_detail_entrance_s.png", "SM_F01_LOCAnnex_night_street_sw.png"],
    "F01_preview_Folger.png": ["SM_F01_Folger_textured_photo01_ne.png", "SM_F01_Folger_textured_street_n.png",
                               "SM_F01_Folger_textured_detail_bays.png", "SM_F01_Folger_night_street_ne.png"],
    "F01_preview_Cannon.png": ["SM_F01_Cannon_textured_photo03_nw.png", "SM_F01_Cannon_textured_detail_corner.png",
                               "SM_F01_Cannon_textured_detail_colonnade.png", "SM_F01_Cannon_night_street_ne.png"],
}
TILE = (384, 216)
VERSION = "v002"   # Cannon changed in v002; Annex and Folger GLBs are unchanged from v001


def sheet(name, files):
    w, h = TILE
    img = Image.new("RGB", (w * 2, h * 2 + 18), (24, 26, 28))
    font = ImageFont.truetype(FONT, 11)
    d = ImageDraw.Draw(img)
    for i, f in enumerate(files):
        p = os.path.join(REV, f)
        if not os.path.exists(p):
            continue
        t = Image.open(p).convert("RGB").resize(TILE, Image.LANCZOS)
        img.paste(t, ((i % 2) * w, 18 + (i // 2) * h))
    d.text((6, 3), f"DC-F01 {VERSION} actual exported GLB renders (Cycles) - {name[12:-4]} - full res in PR", fill=(220, 220, 210),
           font=font)
    q = img.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    os.makedirs(OUT, exist_ok=True)
    q.save(os.path.join(OUT, name), optimize=True)
    return os.path.getsize(os.path.join(OUT, name))


def photo_compare():
    """Side-by-side of Drive ref 01 (Folger, Commons 2025, CC BY-SA 4.0) and the matched-vantage render."""
    ref = os.path.join(HERE, "refs", "01_Folger_2025.jpg")
    ren = os.path.join(REV, "SM_F01_Folger_textured_photo01_ne.png")
    if not (os.path.exists(ref) and os.path.exists(ren)):
        return 0
    a = Image.open(ref).convert("RGB").resize((960, 720), Image.LANCZOS)
    b = Image.open(ren).convert("RGB").resize((960, 540), Image.LANCZOS)
    img = Image.new("RGB", (1920, 740), (24, 26, 28))
    img.paste(a, (0, 20))
    img.paste(b, (960, 110))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 12)
    d.text((6, 3), "ref 01: Folger from the NE, 3 Jun 2025, Ser Amantio di Nicolao, CC BY-SA 4.0 (Wikimedia Commons)",
           fill=(220, 220, 210), font=font)
    d.text((966, 3), "DC-F01 SM_F01_Folger LOD0, matched camera photo01_ne (Cycles, neutral review light)",
           fill=(220, 220, 210), font=font)
    out = os.path.join(REV, "CMP_ref01_vs_photo01_ne.png")
    img.save(out, optimize=True)
    small = os.path.join(OUT, "F01_compare_ref01_Folger.png")
    os.makedirs(OUT, exist_ok=True)
    img.resize((960, 370), Image.LANCZOS).quantize(colors=96, method=Image.Quantize.MEDIANCUT,
                                                     dither=Image.Dither.NONE).save(small, optimize=True)
    return os.path.getsize(small)


def cannon_compare():
    """HABS ref 03 (Cannon NW corner, 1976, public domain) | v001 | v002 at the matched camera photo03_nw."""
    ref = os.path.join(HERE, "refs", "incoming", "03_Cannon_NW_corner_HABS_DC-2_color.jpg")
    v1 = os.path.join(REV, "V001_SM_F01_Cannon_textured_photo03_nw.png")
    v2 = os.path.join(REV, "SM_F01_Cannon_textured_photo03_nw.png")
    if not all(os.path.exists(x) for x in (ref, v1, v2)):
        return 0
    W = 760
    a = Image.open(ref).convert("RGB")
    a = a.resize((W, int(a.height * W / a.width)), Image.LANCZOS)
    b = Image.open(v1).convert("RGB").resize((W, int(W * 9 / 16)), Image.LANCZOS)
    c = Image.open(v2).convert("RGB").resize((W, int(W * 9 / 16)), Image.LANCZOS)
    H = max(a.height, b.height) + 22
    img = Image.new("RGB", (3 * W, H), (24, 26, 28))
    img.paste(a, (0, 22))
    img.paste(b, (W, 22 + (a.height - b.height) // 2))
    img.paste(c, (2 * W, 22 + (a.height - c.height) // 2))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 12)
    d.text((6, 4), "ref 03: Cannon HOB, NW corner, HABS DC-2 (J. E. Boucher, 1976), public domain", fill=(220, 220, 210), font=font)
    d.text((W + 6, 4), "DC-F01 v001 Cannon LOD0, camera photo03_nw", fill=(220, 220, 210), font=font)
    d.text((2 * W + 6, 4), "DC-F01 v002 Cannon LOD0, camera photo03_nw (corrected)", fill=(220, 220, 210), font=font)
    out = os.path.join(REV, "CMP_ref03_vs_photo03_nw.png")
    img.save(out, optimize=True)
    small = os.path.join(OUT, "F01_compare_ref03_Cannon.png")
    img.resize((1140, int(H / 2)), Image.LANCZOS).quantize(colors=96, method=Image.Quantize.MEDIANCUT,
                                                           dither=Image.Dither.NONE).save(small, optimize=True)
    return os.path.getsize(small)


if __name__ == "__main__":
    for n, fs in SHEETS.items():
        print(n, sheet(n, fs), "bytes")
    print("F01_compare_ref01_Folger.png", photo_compare(), "bytes")
    print("F01_compare_ref03_Cannon.png", cannon_compare(), "bytes")
