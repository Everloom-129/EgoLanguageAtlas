#!/usr/bin/env python3
"""Single entry point for the EgoDex atlas: download -> normalize -> cluster -> render.
Idempotent and resumable: the download streams hdf5 attributes to a JSONL cache
(rerun skips cached episodes); embeddings are cached under ./.cache.
"""
from __future__ import annotations
import argparse, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["download_egodex.py", "normalize_egodex.py", "cluster_egodex.py", "render_egodex.py"]
def main():
    ap = argparse.ArgumentParser(description="Build the EgoDex atlas.")
    ap.add_argument("--force-download", action="store_true")
    args = ap.parse_args()
    for step in STEPS:
        extra = ["--force"] if (step.startswith("download") and args.force_download) else []
        print(f"\n{'='*70}\n=== {step} {' '.join(extra)}\n{'='*70}", flush=True)
        r = subprocess.run([sys.executable, os.path.join(HERE, step), *extra])
        if r.returncode != 0:
            print(f"step failed: {step} (exit {r.returncode})", file=sys.stderr); sys.exit(r.returncode)
    print("\nall stages complete: atlases written to egodex_atlas[_cn].html")
if __name__ == "__main__":
    main()
