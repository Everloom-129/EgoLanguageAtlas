#!/usr/bin/env python3
"""Download EgoVid-5M language annotations (route: huggingface_hub).

Source repo : https://huggingface.co/datasets/Jeff-Wang/EgoVid-5M
License      : apache-2.0 for the hosted annotation tables (per the dataset card).
               The underlying clips are Ego4D (Ego4D License); this atlas only
               touches the openly-licensed annotation CSVs, never the videos.
What it pulls: the text-bearing annotation tables only
                 egovid-text.csv  (~5.2 GB: name = high-level action description,
                                   verb_cls / noun_cls, llava_cap = LLaVA caption)
                 egovid-val.csv   (~24 MB: the validation split, same columns)
               No videos, kinematics (egovid-kinematic.csv), or poses.zip.
Properties   : idempotent (skips files already in .cache), records provenance.

Usage:
    python download_egovid-5m.py            # fetch into ./.cache
    python download_egovid-5m.py --force    # re-download
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

REPO = "Jeff-Wang/EgoVid-5M"
FILES = ("egovid-text.csv", "egovid-val.csv")
LICENSE = "apache-2.0"
LICENSE_URL = "https://www.apache.org/licenses/LICENSE-2.0"

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(HERE, ".cache")


def resolve_commit():
    try:
        url = f"https://huggingface.co/api/datasets/{REPO}"
        req = urllib.request.Request(url, headers={"User-Agent": "ego-atlas/1.0"})
        return json.load(urllib.request.urlopen(req, timeout=30)).get("sha")
    except Exception as exc:  # pragma: no cover
        sys.stderr.write(f"  (could not resolve commit sha: {exc})\n")
        return None


def main():
    ap = argparse.ArgumentParser(description="Download EgoVid-5M annotation CSVs.")
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.cache, exist_ok=True)

    from huggingface_hub import hf_hub_download

    print("EgoVid-5M annotation download")
    print(f"repo   : https://huggingface.co/datasets/{REPO}")
    sha = resolve_commit()
    print(f"commit : {sha or 'n/a'}")
    access = datetime.now(timezone.utc).isoformat()
    print(f"access : {access} (UTC)")
    print("-" * 70)

    manifest = []
    for fn in FILES:
        dest = os.path.join(args.cache, fn)
        if args.force and os.path.exists(dest):
            os.remove(dest)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            size = os.path.getsize(dest)
            print(f"[have] {size:>14,} B  {fn}")
            manifest.append({"file": fn, "bytes": size, "status": "cached"})
            continue
        print(f"[get ] downloading {fn} ...", flush=True)
        path = hf_hub_download(repo_id=REPO, filename=fn, repo_type="dataset",
                               revision="main", local_dir=args.cache)
        size = os.path.getsize(path)
        print(f"[get ] {size:>14,} B  {fn}")
        manifest.append({"file": fn, "bytes": size, "status": "downloaded"})

    provenance = {
        "work": "EgoVid-5M",
        "route": "huggingface_hub (hf_hub_download)",
        "repo": f"https://huggingface.co/datasets/{REPO}",
        "repo_id": REPO,
        "commit_sha": sha,
        "access_utc": access,
        "license": LICENSE,
        "license_url": LICENSE_URL,
        "note": ("Annotation tables are apache-2.0; underlying clips are Ego4D "
                 "(Ego4D License). Only the annotation CSVs are downloaded."),
        "files": manifest,
    }
    with open(os.path.join(args.cache, "provenance.json"), "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=2)
    with open(os.path.join(HERE, "download_provenance.json"), "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=2)
    print("-" * 70)
    print(f"provenance -> {os.path.join(HERE, 'download_provenance.json')}")
    print("done.")


if __name__ == "__main__":
    main()
