#!/usr/bin/env python3
"""Download EgoClip metadata (route: project-script via Google Drive).

Source : https://github.com/showlab/EgoVLP  (EgoVLP / EgoClip / EgoNCE / EgoMCQ)
File   : egoclip.csv (tab-separated; ~3.8M clip-text pairs filtered from Ego4D)
License: EgoClip text is derived from Ego4D and carries the Ego4D License. Used
         here for internal, non-commercial analysis; derived text not
         redistributed externally.

egoclip.csv columns: video_uid, video_dur, narration_source, narration_ind,
narration_time, clip_start, clip_end, clip_text, tag_verb, tag_noun. The
narration is clip_text, in Ego4D markup form ("#C C opens the door").

Usage:
    python download_egovlp.py            # fetch into ./.cache (skips if present)
    python download_egovlp.py --force    # re-download
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, timezone

REPO = "https://github.com/showlab/EgoVLP"
DRIVE_ID = "1-aaDu_Gi-Y2sQI_2rsI2D1zvQBJnHpXl"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
CSV_PATH = os.path.join(CACHE, "egoclip.csv")

csv.field_size_limit(10_000_000)


def count_rows(path):
    n = 0
    with open(path, encoding="utf-8", newline="") as fh:
        rd = csv.reader(fh, delimiter="\t")
        header = next(rd, [])
        for _ in rd:
            n += 1
    return n, header


def main():
    ap = argparse.ArgumentParser(description="Download EgoClip (egoclip.csv).")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)

    if args.force and os.path.exists(CSV_PATH):
        os.remove(CSV_PATH)

    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
        print(f"have egoclip.csv ({os.path.getsize(CSV_PATH)/1e6:.0f} MB)")
    else:
        import gdown
        print(f"downloading egoclip.csv from Google Drive id {DRIVE_ID} ...")
        gdown.download(id=DRIVE_ID, output=CSV_PATH, quiet=False)

    access = datetime.now(timezone.utc).isoformat()
    n_rows, header = count_rows(CSV_PATH)
    print(f"rows: {n_rows:,}")
    prov = {
        "work": "EgoVLP (EgoClip)", "route": "project-script (Google Drive)",
        "repo": REPO, "drive_id": DRIVE_ID,
        "file": "egoclip.csv", "bytes": os.path.getsize(CSV_PATH),
        "rows": n_rows, "columns": [c for c in header if c],
        "access_utc": access,
        "license": "Ego4D License (EgoClip text is Ego4D-derived)",
        "license_note": ("internal non-commercial analysis; derived text not "
                         "redistributed externally"),
        "source_dataset": "Ego4D (filtered by EgoVLP)",
    }
    for path in (os.path.join(CACHE, "provenance.json"),
                 os.path.join(HERE, "download_provenance.json")):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(prov, fh, indent=2)
    print(f"provenance -> {os.path.join(HERE, 'download_provenance.json')}")
    print("done.")


if __name__ == "__main__":
    main()
