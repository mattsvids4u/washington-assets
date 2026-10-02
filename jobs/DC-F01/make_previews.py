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
    "F01_preview_Folger.png": ["SM_F01_Folger_textured_street_nw.png", "SM_F01_Folger_textured_street_n.png",
                               "SM_F01_Folger_textured_detail_bays.png", "SM_F01_Folger_night_street_ne.png"],
    "F01_preview_Cannon.png": ["SM_F01_Cannon_textured_street_ne.png", "SM_F01_Cannon_textured_street_nw.png",
                               "SM_F01_Cannon_textured_detail_colonnade.png", "SM_F01_Cannon_night_street_ne.png"],
}
TILE = (384, 216)


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
    d.text((6, 3), f"DC-F01 v001 actual exported GLB renders (Cycles) - {name[12:-4]} - full res in PR", fill=(220, 220, 210),
           font=font)
    q = img.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    os.makedirs(OUT, exist_ok=True)
    q.save(os.path.join(OUT, name), optimize=True)
    return os.path.getsize(os.path.join(OUT, name))


if __name__ == "__main__":
    for n, fs in SHEETS.items():
        print(n, sheet(n, fs), "bytes")
