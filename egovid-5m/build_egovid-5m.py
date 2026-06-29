#!/usr/bin/env python3
"""Single entry point for the egovid-5m atlas: download -> normalize -> cluster -> render.
Idempotent: raw downloads and embeddings are cached under ./.cache.
"""
from __future__ import annotations
import argparse, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["download_egovid-5m.py", "normalize_egovid-5m.py", "cluster_egovid-5m.py", "render_egovid-5m.py"]
def main():
    ap = argparse.ArgumentParser(description="Build the egovid-5m atlas.")
    ap.add_argument("--force-download", action="store_true")
    args = ap.parse_args()
    for step in STEPS:
        extra = ["--force"] if (step.startswith("download") and args.force_download) else []
        print(f"\n{'='*70}\n=== {step} {' '.join(extra)}\n{'='*70}", flush=True)
        r = subprocess.run([sys.executable, os.path.join(HERE, step), *extra])
        if r.returncode != 0:
            print(f"step failed: {step} (exit {r.returncode})", file=sys.stderr); sys.exit(r.returncode)
    print("\nall stages complete: atlases written to egovid-5m_atlas[_cn].html")
if __name__ == "__main__":
    main()
