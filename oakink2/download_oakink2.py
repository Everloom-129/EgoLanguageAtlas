#!/usr/bin/env python3
"""Download OakInk2 language annotations (route: huggingface_hub).

Source repo : https://huggingface.co/datasets/kelvin34501/OakInk-v2
License      : CC BY-SA 4.0 (per the dataset card). Redistribution permitted with
               attribution and share-alike. This atlas attributes the source and
               shares its derived text under the same terms.
What it pulls: program.tar (~3.6 MB) only. It holds all the natural-language
               annotation the OakInk2 toolkit loads:
                 program/task_target.json            complex-task instructions
                 program/desc_info/<seq>.json         per-primitive descriptions
                                                      (English seg_desc + Chinese seg_desc_zh)
                 program/initial_condition_info/...   recipe + initial conditions
                 program/program_info, program/pdg    task graphs (structure only)
               No image tarballs (data/*.tar) or pose previews (anno_preview/*.pkl).
Properties   : idempotent, records provenance.

Usage:
    python download_oakink2.py            # fetch into ./.cache
    python download_oakink2.py --force    # re-download
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tarfile
import urllib.request
from datetime import datetime, timezone

REPO = "kelvin34501/OakInk-v2"
PROGRAM_TAR = "program.tar"
LICENSE = "CC BY-SA 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"

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


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    ap = argparse.ArgumentParser(description="Download OakInk2 program annotations.")
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.cache, exist_ok=True)

    from huggingface_hub import hf_hub_download

    print("OakInk2 annotation download")
    print(f"repo   : https://huggingface.co/datasets/{REPO}")
    sha = resolve_commit()
    print(f"commit : {sha or 'n/a'}")
    access = datetime.now(timezone.utc).isoformat()
    print(f"access : {access} (UTC)")
    print("-" * 70)

    dest = os.path.join(args.cache, PROGRAM_TAR)
    if args.force and os.path.exists(dest):
        os.remove(dest)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"[have] {os.path.getsize(dest):>11,} B  {PROGRAM_TAR}")
    else:
        print(f"[get ] downloading {PROGRAM_TAR} ...", flush=True)
        path = hf_hub_download(repo_id=REPO, filename=PROGRAM_TAR, repo_type="dataset",
                               revision="main", local_dir=args.cache)
        print(f"[get ] {os.path.getsize(path):>11,} B  {PROGRAM_TAR}")

    # extract the program/ tree into the cache (text json only)
    extract_dir = os.path.join(args.cache, "program_extracted")
    os.makedirs(extract_dir, exist_ok=True)
    with tarfile.open(dest) as tf:
        members = [m for m in tf.getmembers() if m.name.endswith(".json")]
        tf.extractall(extract_dir, members=members)
    n_json = sum(1 for _ in members)
    print(f"extracted {n_json} json files -> {extract_dir}")

    provenance = {
        "work": "OakInk2",
        "route": "huggingface_hub (hf_hub_download)",
        "repo": f"https://huggingface.co/datasets/{REPO}",
        "repo_id": REPO,
        "commit_sha": sha,
        "access_utc": access,
        "license": LICENSE,
        "license_url": LICENSE_URL,
        "files": [{"file": PROGRAM_TAR, "bytes": os.path.getsize(dest),
                   "sha256": sha256_of(dest), "json_members": n_json,
                   "status": "downloaded"}],
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
