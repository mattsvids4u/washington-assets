"""DC-X14 v006 — populate the X14 demo rooms with the WASHINGTON PCG systems that already exist:

  * desks and file-cabinet tops  -> WASHINGTON Tabletop PCG v003 (support-aware), DC-I18 family bank
  * bookcase shelves             -> DC-I05 v015 shelf personalities (the I05 v014 shelf-composition PCG
                                    output), cropped to the X14 shelf exactly as I05 v015 does for the
                                    approved DC-I06 stack: no scaling of canonical books.

Nothing here is X14 geometry and nothing is written into the X14 kit GLBs. Outputs are review/preview
payloads (GLB per surface or shelf, in that surface's local frame, glTF Y-up) plus a persisted record
per surface/shelf (seeds, resolved choices, placements) so the result can be regenerated or rebuilt in
Unreal from data.

Inputs are the dependency packages as downloaded from Drive (see DEPENDENCY_LOCK.json for IDs/SHA-256):
  --tabletop-code    WASHINGTON_TABLETOP_PCG_v003_SUPPORT_AWARE.zip, extracted (tabletop_pcg_v001.py,
                     pass6f_support_max_smoker.py)
  --tabletop-proofs  WASHINGTON_TABLETOP_PCG_v001_DELIVERABLE.zip, extracted .../generated_proofs
                     (the DC-I18 bank is recovered from these proof GLBs — see recover_i18_bank)
  --i05              DC-I05_asset_v015.zip, extracted DC-I05_asset_v015/

Usage:
  python3 jobs/DC-X14/dress_pcg.py --rooms jobs/DC-X14/out/X14_DEMO_LRS_Room.glb \
      jobs/DC-X14/out/X14_DEMO_LRS_Room_1953.glb --tabletop-code DIR --tabletop-proofs DIR \
      --i05 DIR --out DIR
Requires: trimesh, shapely, numpy (no Blender).
"""
import argparse
import collections
import copy
import glob
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import shutil
import struct
import sys

import numpy as np
import trimesh

ZUP_TO_GLTF = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])   # (x,y,z) -> (x,z,-y)
ROOM_ID = {"X14_DEMO_LRS_Room_1953": "LRS1953", "X14_DEMO_LRS_Room": "LRSGRAY"}


def stable_seed(text):
    return int(hashlib.sha256(text.encode()).hexdigest()[:7], 16)   # < 2**31 (Blender ID properties are C int)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def glb_nodes(path):
    """Top-level glTF nodes (name -> extras) of an exported X14 room."""
    b = open(path, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    return {nd.get("name", ""): nd.get("extras", {}) for nd in j["nodes"]}


# ------------------------------------------------------------------------------ DC-I18 bank recovery
def recover_i18_bank(proof_dir, stage):
    """Proof GLB nodes are PCG_<asset>_V<vv>_<idx>_<part>; all parts of one placement share the node
    transform and the geometry is stored in the asset's source frame, so the geometry objects are the
    source bank. Variants never placed in any proof cannot be recovered; they fall back to the nearest
    recovered variant and are flagged SUBSTITUTE in the library and the run manifest."""
    exp = os.path.join(stage, "exports_pass6b")
    os.makedirs(exp, exist_ok=True)
    os.makedirs(os.path.join(stage, "docs"), exist_ok=True)
    labels, bank = {}, {}
    for js in sorted(glob.glob(os.path.join(proof_dir, "PCG6C_*.json"))):
        for p in json.load(open(js)).get("resolved_placements", []):
            labels[(p["asset"], p["variant"])] = p["variant_label"]
    for g in sorted(glob.glob(os.path.join(proof_dir, "PCG6C_*.glb"))):
        kind = "shared" if "SHARED_NEUTRAL" in g else "dc"
        s = trimesh.load(g, force="scene")
        groups = collections.defaultdict(dict)
        for node in s.graph.nodes_geometry:
            m = re.match(r"PCG_([a-z_]+?)_V(\d\d)_(\d+)_(.+)$", node)
            if m:
                groups[(m.group(1), int(m.group(2)), int(m.group(3)))][m.group(4)] = s.geometry[s.graph[node][1]]
        for (asset, v, _), parts in groups.items():
            key = (asset, v, kind)
            if key not in bank or len(parts) > len(bank[key]):
                bank[key] = parts
    fam = collections.defaultdict(dict)
    for (asset, v, kind), parts in sorted(bank.items()):
        sc = trimesh.Scene()
        for k, geo in sorted(parts.items()):
            sc.add_geometry(geo.copy(), geom_name=k, node_name=k)
        fn = f"{asset}_V{v:02d}_{kind}.glb"
        sc.export(os.path.join(exp, fn))
        ent = fam[asset].setdefault(v, {"label": labels.get((asset, v), f"{asset}_{v}"),
                                         "readback": {"extents_m": (sc.bounds[1] - sc.bounds[0]).tolist()}})
        ent[kind] = fn
    lib, substitutes = {"families": {}}, []
    for asset, vs in sorted(fam.items()):
        lst = []
        for i in range(max(vs) + 1):
            if i in vs:
                ent = dict(vs[i])
            else:
                j = min(vs, key=lambda k: abs(k - i))
                ent = copy.deepcopy(vs[j])
                ent["label"] = f"SUBSTITUTE_V{i:02d}_uses_{vs[j]['label']}"
                substitutes.append(f"{asset} V{i:02d} -> V{j:02d} ({vs[j]['label']})")
            ent.setdefault("shared", ent.get("dc"))
            ent.setdefault("dc", ent.get("shared"))
            lst.append(ent)
        lib["families"][asset] = lst
    json.dump(lib, open(os.path.join(stage, "docs", "VARIATION_LIBRARY_PASS6B.json"), "w"), indent=1)
    return lib, substitutes


def load_tabletop(code_dir, stage):
    pcg = os.path.join(stage, "pcg")
    os.makedirs(pcg, exist_ok=True)
    for f in ("tabletop_pcg_v001.py", "pass6f_support_max_smoker.py"):
        shutil.copy(os.path.join(code_dir, f), os.path.join(pcg, f))
    spec = importlib.util.spec_from_file_location("x14_pass6f", os.path.join(pcg, "pass6f_support_max_smoker.py"))
    p6 = importlib.util.module_from_spec(spec)
    sys.modules["x14_pass6f"] = p6
    spec.loader.exec_module(p6)          # loads tabletop_pcg_v001 as p6.mod; main() is not run
    return p6.mod, p6


def run_tabletops(room_glb, mod, p6, out):
    room = ROOM_ID[os.path.splitext(os.path.basename(room_glb))[0]]
    recs = []
    for name, ex in sorted(glb_nodes(room_glb).items()):
        if not name.startswith("SURFACE_X14_Tabletop_") or "surface_id" not in ex:
            continue
        sid = ex["surface_id"]
        surf = mod.Surface(sid, float(ex["width_m"]), float(ex["depth_m"]), float(ex["edge_margin_m"]),
                           json.loads(ex["blocked_regions_json"]) or None)
        overrides = json.loads(ex.get("controls_json", "{}") or "{}")
        if not int(ex.get("smoking_allowed", 1)):
            overrides["smoking_intensity"] = 0.0
        random.seed(int(ex["master_seed"]))      # generator uses its own seeded streams; this pins any stray global use
        try:
            _glb, _mf, rec = mod.generate(surf, int(ex["master_seed"]), ex["archetype"], overrides, dc=False, out_name=sid)
        except ValueError as err:          # generator exports its pre-support scene; empty -> nothing fitted
            recs.append({"surface_id": sid, "node": name, "archetype": ex["archetype"], "seed": ex["master_seed"],
                         "placements": 0, "counts": {}, "unintended_3d_overlaps": 0, "note": f"EMPTY: {err}"})
            continue
        scene, resolved, _ = p6.resolve_scene(rec, False)
        issues = p6.qa_overlaps(resolved)
        rec["resolved_placements"] = resolved
        rec["support_qa"] = {"unintended_3d_overlap_count": len(issues), "issues": issues[:20]}
        rec["x14_surface_node"] = name
        rec["x14_room"] = room
        scene.apply_transform(ZUP_TO_GLTF)
        scene.export(os.path.join(out, "tabletop", f"{sid}.glb"))
        json.dump(rec, open(os.path.join(out, "tabletop", f"{sid}.json"), "w"), indent=1, default=float)
        counts = collections.Counter(p["asset"] for p in resolved)
        recs.append({"surface_id": sid, "node": name, "archetype": ex["archetype"], "seed": ex["master_seed"],
                     "placements": len(resolved), "counts": dict(counts), "unintended_3d_overlaps": len(issues)})
    return recs


# ------------------------------------------------------------------------------ DC-I05 shelf runs
I06_SOCKETS = {  # DC-I05 v015 docs/I05_I06_INTEGRATION.json (mm -> m)
    "A": (0.4572, -0.1334), "B": (0.4572, 0.1334)}
I06_ROW_Z = [0.090, 0.34365714, 0.59731429, 0.85097143, 1.10462857, 1.35828571, 1.61194286]


def i05_personalities(i05_dir):
    """Book groups per v014 shelf personality, in DC-I05 SOCKET_Books frame (origin on the shelf at
    the socket, +X along the run, spines facing -Y). Side-B runs are turned 180° into the same frame."""
    s = trimesh.load(os.path.join(i05_dir, "meshes", "DC-I05_I06_APPROVED_STACK_INTEGRATION.glb"), force="scene")
    pers = collections.defaultdict(lambda: collections.defaultdict(list))
    for node in s.graph.nodes_geometry:
        m = re.match(r"(S\d\d_[A-Z_]+?)_([AB])_\1_B(\d+)_", node)
        if not m:
            continue
        T, g = s.graph[node]
        pers[(m.group(1), m.group(2))][int(m.group(3))].append((node, T, s.geometry[g]))
    out = {}
    for (pid, side), books in pers.items():
        sx, sy = I06_SOCKETS[side]
        allz = [trimesh.transform_points(geo.vertices, T)[:, 2].min() for b in books.values() for _, T, geo in b]
        base_z = min(I06_ROW_Z, key=lambda z: abs(z - min(allz)))
        F = trimesh.transformations.translation_matrix([-sx, -sy, -base_z])
        if side == "B":
            F = trimesh.transformations.rotation_matrix(math.pi, [0, 0, 1]) @ F
        runs = []
        for bid, parts in sorted(books.items()):
            pts = np.vstack([trimesh.transform_points(geo.vertices, F @ T) for _, T, geo in parts])
            runs.append({"book": bid, "parts": [(n, F @ T, geo) for n, T, geo in parts],
                         "min": pts.min(0), "max": pts.max(0)})
        out[pid] = runs
    return out


def run_books(room_glb, pers, out):
    room = ROOM_ID[os.path.splitext(os.path.basename(room_glb))[0]]
    recs = []
    pids = sorted(pers)
    sockets = sorted((n, ex) for n, ex in glb_nodes(room_glb).items() if n.startswith("SOCKET_X14_Books_"))
    by_case = collections.defaultdict(list)
    for n, ex in sockets:
        by_case[n.split(".")[-1]].append((n, ex))
    for case, socks in sorted(by_case.items()):
        order = pids[:]
        random.Random(stable_seed(f"{room}:{case}:order")).shuffle(order)   # no repeated personality in one case
        for k, (n, ex) in enumerate(sorted(socks)):
            seed = stable_seed(f"{room}:{n}")                                 # BookSeed (I06 custom float 2 analogue)
            rng = random.Random(seed)
            pid = order[k % len(order)]
            W, clear = float(ex["usable_width_m"]), float(ex["clearance_m"])
            shift = rng.uniform(-0.12, 0.12)
            kept, dropped = [], 0
            sc = trimesh.Scene()
            for b in pers[pid]:
                x0, x1 = b["min"][0] + shift, b["max"][0] + shift
                if x0 < -W / 2 or x1 > W / 2 or b["max"][2] > clear - 0.008:
                    dropped += 1
                    continue
                kept.append(b["book"])
                S = trimesh.transformations.translation_matrix([shift, 0, 0])
                for pn, T, geo in b["parts"]:
                    sc.add_geometry(geo, geom_name=pn, node_name=pn, transform=S @ T)
            sid = f"X14_{room}_{n.replace('SOCKET_X14_Books_', 'BOOKS_').replace('.', '_')}"
            rec = {"shelf_id": sid, "socket_node": n, "room": room, "book_seed": seed, "personality": pid,
                   "run_shift_m": round(shift, 4), "usable_width_m": W, "clearance_m": clear,
                   "books_kept": kept, "books_cropped": dropped,
                   "rule": "DC-I05 v015: v014 personality cropped to carrier width/clearance; canonical books never scaled",
                   "source": "DC-I05 v015 meshes/DC-I05_I06_APPROVED_STACK_INTEGRATION.glb"}
            if len(sc.geometry):
                sc.apply_transform(ZUP_TO_GLTF)
                sc.export(os.path.join(out, "books", f"{sid}.glb"))
            json.dump(rec, open(os.path.join(out, "books", f"{sid}.json"), "w"), indent=1)
            recs.append(rec)
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rooms", nargs="+", required=True)
    ap.add_argument("--tabletop-code", required=True)
    ap.add_argument("--tabletop-proofs", required=True)
    ap.add_argument("--i05", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.path.isdir(a.out):
        shutil.rmtree(a.out)
    for d in ("tabletop", "books", "_stage"):
        os.makedirs(os.path.join(a.out, d))
    stage = os.path.join(a.out, "_stage")
    lib, subs = recover_i18_bank(a.tabletop_proofs, stage)
    mod, p6 = load_tabletop(a.tabletop_code, stage)
    pers = i05_personalities(a.i05)
    manifest = {"generator": "jobs/DC-X14/dress_pcg.py", "tabletop_generator_revision": getattr(mod, "GENERATOR_REVISION", "?"),
                "i18_bank_variants": {k: [e["label"] for e in v] for k, v in lib["families"].items()},
                "i18_bank_substitutes": subs, "i05_personalities": {k: len(v) for k, v in pers.items()},
                "rooms": {}}
    for room in a.rooms:
        rid = ROOM_ID[os.path.splitext(os.path.basename(room))[0]]
        manifest["rooms"][rid] = {"tabletops": run_tabletops(room, mod, p6, a.out), "shelves": run_books(room, pers, a.out)}
    shutil.rmtree(stage)
    json.dump(manifest, open(os.path.join(a.out, "DRESS_PCG_MANIFEST.json"), "w"), indent=1, default=float)
    for rid, r in manifest["rooms"].items():
        print(rid, "tabletops", [(t["surface_id"][-8:], t["archetype"], t["placements"], t["unintended_3d_overlaps"]) for t in r["tabletops"]])
        print(rid, "shelves", len(r["shelves"]), "books", sum(len(s["books_kept"]) for s in r["shelves"]))
    print("substitutes", subs)


if __name__ == "__main__":
    main()
