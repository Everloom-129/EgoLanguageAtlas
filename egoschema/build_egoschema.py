#!/usr/bin/env python3
"""Single entry point for the EgoSchema atlas: download -> normalize -> cluster -> render."""
from __future__ import annotations
import argparse, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["download_egoschema.py", "normalize_egoschema.py", "cluster_egoschema.py", "render_egoschema.py"]
def main():
    ap = argparse.ArgumentParser(description="Build the EgoSchema atlas.")
    ap.add_argument("--force-download", action="store_true")
    args = ap.parse_args()
    for step in STEPS:
        extra = ["--force"] if (step.startswith("download") and args.force_download) else []
        print(f"\n{'='*70}\n=== {step} {' '.join(extra)}\n{'='*70}", flush=True)
        r = subprocess.run([sys.executable, os.path.join(HERE, step), *extra])
        if r.returncode != 0:
            print(f"step failed: {step} (exit {r.returncode})", file=sys.stderr); sys.exit(r.returncode)
    print("\nall stages complete: atlases written to egoschema_atlas[_cn].html")
if __name__ == "__main__":
    main()
