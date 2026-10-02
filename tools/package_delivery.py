"""Write DELIVERY_MANIFEST.json and SHA256SUMS.txt for a delivery folder.

Usage: python tools/package_delivery.py deliveries/<ID>/asset-v###
Fails if any required stage-A file is missing or empty.
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

REQUIRED = [
    "PASS_PLAN.md", "CONTEXT_ACK.json", "EVIDENCE.md", "HANDOFF.md",
    "DEPENDENCY_LOCK.json", "PCG_INTERFACE.json", "REUSABLE_COMPONENTS.json",
]
SKIP = {"DELIVERY_MANIFEST.json", "SHA256SUMS.txt"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    root = sys.argv[1].rstrip("/")
    missing = [f for f in REQUIRED if not os.path.isfile(os.path.join(root, f)) or os.path.getsize(os.path.join(root, f)) == 0]
    files = []
    for dirpath, _, names in os.walk(root):
        for n in sorted(names):
            rel = os.path.relpath(os.path.join(dirpath, n), root).replace(os.sep, "/")
            if rel not in SKIP:
                files.append(rel)
    files.sort()
    has_mesh = any(f.lower().endswith((".glb", ".fbx", ".gltf")) for f in files)
    has_renders = any(f.lower().endswith(".png") for f in files)
    if not has_mesh:
        missing.append("a mesh (.glb/.fbx)")
    if not has_renders:
        missing.append("actual-output renders (.png)")
    if missing:
        sys.exit("Delivery incomplete, missing: " + ", ".join(missing))

    parts = root.replace("\\", "/").split("/")
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None

    entries = [{"path": f, "bytes": os.path.getsize(os.path.join(root, f)), "sha256": sha256(os.path.join(root, f))} for f in files]
    manifest = {
        "job_id": parts[-2],
        "version": parts[-1],
        "claimant": "claude-cloud-agent",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_commit": commit,
        "gates": {
            "clean_rebuild": "see HANDOFF.md",
            "glb_reopen_qa": "see HANDOFF.md",
            "unreal_import_readback": "NOT_RUN — needs local Unreal (UE 5.8)",
            "motion_tests": "NOT_RUN — needs local Unreal (UE 5.8)",
            "matt_approval": "PENDING",
        },
        "files": entries,
    }
    with open(os.path.join(root, "DELIVERY_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(root, "SHA256SUMS.txt"), "w", encoding="utf-8") as f:
        for e in entries:
            f.write(f"{e['sha256']}  {e['path']}\n")
    print(f"Packaged {len(entries)} files in {root}")


if __name__ == "__main__":
    main()
