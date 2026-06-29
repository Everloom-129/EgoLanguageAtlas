#!/usr/bin/env python3
"""Single entry point for the EPIC-KITCHENS-100 atlas: chains all stages.

    download -> normalize -> cluster -> render

Each stage is idempotent, so re-running is cheap (downloads and embeddings are
cached under ./.cache). Use --force-download to re-fetch the raw annotations.

    python build_epic-kitchens-100.py
    python build_epic-kitchens-100.py --force-download
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    "download_epic-kitchens-100.py",
    "normalize_epic-kitchens-100.py",
    "cluster_epic-kitchens-100.py",
    "render_epic-kitchens-100.py",
]


def main():
    ap = argparse.ArgumentParser(description="Build the EPIC-KITCHENS-100 atlas.")
    ap.add_argument("--force-download", action="store_true",
                    help="re-download raw annotations even if cached")
    args = ap.parse_args()

    for step in STEPS:
        extra = ["--force"] if (step.startswith("download") and args.force_download) else []
        print(f"\n{'=' * 70}\n=== {step} {' '.join(extra)}\n{'=' * 70}", flush=True)
        result = subprocess.run([sys.executable, os.path.join(HERE, step), *extra])
        if result.returncode != 0:
            print(f"step failed: {step} (exit {result.returncode})", file=sys.stderr)
            sys.exit(result.returncode)
    print("\nall stages complete: atlases written to epic-kitchens-100_atlas[_cn].html")


if __name__ == "__main__":
    main()
