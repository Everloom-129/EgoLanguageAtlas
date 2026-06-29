#!/usr/bin/env python3
"""Single entry point for the HD-EPIC atlas: download -> normalize -> cluster -> render.

Idempotent: raw downloads and embeddings are cached under ./.cache.

    python build_hd-epic.py
    python build_hd-epic.py --force-download
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    "download_hd-epic.py",
    "normalize_hd-epic.py",
    "cluster_hd-epic.py",
    "render_hd-epic.py",
]


def main():
    ap = argparse.ArgumentParser(description="Build the HD-EPIC atlas.")
    ap.add_argument("--force-download", action="store_true")
    args = ap.parse_args()
    for step in STEPS:
        extra = ["--force"] if (step.startswith("download") and args.force_download) else []
        print(f"\n{'=' * 70}\n=== {step} {' '.join(extra)}\n{'=' * 70}", flush=True)
        result = subprocess.run([sys.executable, os.path.join(HERE, step), *extra])
        if result.returncode != 0:
            print(f"step failed: {step} (exit {result.returncode})", file=sys.stderr)
            sys.exit(result.returncode)
    print("\nall stages complete: atlases written to hd-epic_atlas[_cn].html")


if __name__ == "__main__":
    main()
