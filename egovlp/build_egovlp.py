#!/usr/bin/env python3
"""Single entry point for the EgoVLP/EgoClip atlas: download -> normalize -> cluster -> render.
Idempotent: egoclip.csv and embeddings are cached under ./.cache.
"""
from __future__ import annotations
import argparse, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["download_egovlp.py", "normalize_egovlp.py", "cluster_egovlp.py", "render_egovlp.py"]
def main():
    ap = argparse.ArgumentParser(description="Build the EgoVLP/EgoClip atlas.")
    ap.add_argument("--force-download", action="store_true")
    args = ap.parse_args()
    for step in STEPS:
        extra = ["--force"] if (step.startswith("download") and args.force_download) else []
        print(f"\n{'='*70}\n=== {step} {' '.join(extra)}\n{'='*70}", flush=True)
        r = subprocess.run([sys.executable, os.path.join(HERE, step), *extra])
        if r.returncode != 0:
            print(f"step failed: {step} (exit {r.returncode})", file=sys.stderr); sys.exit(r.returncode)
    print("\nall stages complete: atlases written to egovlp_atlas[_cn].html")
if __name__ == "__main__":
    main()
