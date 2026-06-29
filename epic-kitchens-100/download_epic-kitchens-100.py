#!/usr/bin/env python3
"""Download EPIC-KITCHENS-100 language annotations (route: epic-csv).

Source repo : https://github.com/epic-kitchens/epic-kitchens-100-annotations
License      : CC BY-NC 4.0 (annotations). Redistribution permitted with
               attribution, for non-commercial use. This atlas is a
               non-commercial research survey and attributes the source.
What it pulls: action-segment CSVs (train / validation / test-timestamps),
               verb & noun class maps, per-video metadata, README, LICENSE.
               No video bytes are downloaded.
Properties   : idempotent + resumable (skips existing non-empty files unless
               --force), retries with backoff, prints a provenance summary.

Usage:
    python download_epic-kitchens-100.py            # fetch into ./.cache
    python download_epic-kitchens-100.py --force    # re-download everything
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPO = "epic-kitchens/epic-kitchens-100-annotations"
BRANCH_CANDIDATES = ("master", "main")
RAW_URL = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"
COMMIT_API = "https://api.github.com/repos/{repo}/commits/{branch}"
USER_AGENT = "ego-atlas-downloader/1.0 (research; non-commercial)"

# Files to fetch. Labelled segment CSVs first, then class maps, metadata, docs.
FILES = (
    "EPIC_100_train.csv",
    "EPIC_100_validation.csv",
    "EPIC_100_test_timestamps.csv",
    "EPIC_100_verb_classes.csv",
    "EPIC_100_noun_classes.csv",
    "EPIC_100_video_info.csv",
    "README.md",
    "LICENSE",
)
# CSVs whose free-form 'narration' column carries the language annotation.
LABELLED = ("EPIC_100_train.csv", "EPIC_100_validation.csv")

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(HERE, ".cache")


def http_get(url, timeout=60, retries=5, accept=None):
    """GET with exponential backoff. 404 is terminal (no retry)."""
    last = None
    for attempt in range(retries):
        try:
            headers = {"User-Agent": USER_AGENT}
            if accept:
                headers["Accept"] = accept
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise
            last = exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
        wait = min(2 ** attempt, 30)
        sys.stderr.write(f"  retry {attempt + 1}/{retries}: {last} (sleep {wait}s)\n")
        time.sleep(wait)
    raise last


def resolve_branch():
    """Return the first branch candidate that serves README.md."""
    for branch in BRANCH_CANDIDATES:
        url = RAW_URL.format(repo=REPO, branch=branch, path="README.md")
        try:
            http_get(url, timeout=30, retries=1)
            return branch
        except Exception:
            continue
    return BRANCH_CANDIDATES[0]


def commit_sha(branch):
    """Best-effort pinned version: the annotations repo HEAD commit sha."""
    try:
        data = http_get(
            COMMIT_API.format(repo=REPO, branch=branch),
            timeout=30, retries=2, accept="application/vnd.github+json",
        )
        return json.loads(data).get("sha")
    except Exception as exc:
        sys.stderr.write(f"  (could not resolve commit sha: {exc})\n")
        return None


def download_file(branch, path, dest, force=False):
    """Write path -> dest. Returns True if fetched, False if already cached."""
    if (not force) and os.path.exists(dest) and os.path.getsize(dest) > 0:
        return False
    url = RAW_URL.format(repo=REPO, branch=branch, path=path)
    data = http_get(url)
    tmp = dest + ".part"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, dest)
    return True


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_stats(path):
    """Return (n_rows, header, n_unique_narration) using only stdlib csv."""
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, [])
        narr_idx = header.index("narration") if "narration" in header else None
        n_rows = 0
        uniq = set()
        for row in reader:
            n_rows += 1
            if narr_idx is not None and narr_idx < len(row):
                uniq.add(row[narr_idx].strip().lower())
    return n_rows, header, (len(uniq) if narr_idx is not None else None)


def main():
    parser = argparse.ArgumentParser(description="Download EPIC-KITCHENS-100 annotations.")
    parser.add_argument("--cache", default=DEFAULT_CACHE, help="cache dir (gitignored)")
    parser.add_argument("--force", action="store_true", help="re-download even if present")
    args = parser.parse_args()
    os.makedirs(args.cache, exist_ok=True)

    print("EPIC-KITCHENS-100 annotation download")
    print(f"repo   : https://github.com/{REPO}")
    branch = resolve_branch()
    print(f"branch : {branch}")
    sha = commit_sha(branch)
    print(f"commit : {sha or 'n/a'}")
    access = datetime.now(timezone.utc).isoformat()
    print(f"access : {access} (UTC)")
    print("-" * 68)

    manifest = []
    for path in FILES:
        dest = os.path.join(args.cache, path)
        try:
            fetched = download_file(branch, path, dest, force=args.force)
        except urllib.error.HTTPError as exc:
            print(f"FAIL {path}: HTTP {exc.code}")
            manifest.append({"file": path, "status": f"http_{exc.code}"})
            continue
        except Exception as exc:
            print(f"FAIL {path}: {exc}")
            manifest.append({"file": path, "status": "error", "error": str(exc)})
            continue

        size = os.path.getsize(dest)
        entry = {
            "file": path,
            "bytes": size,
            "status": "downloaded" if fetched else "cached",
            "sha256": sha256_of(dest),
        }
        if path.endswith(".csv"):
            n_rows, header, uniq = csv_stats(dest)
            entry["rows"] = n_rows
            entry["columns"] = header
            if uniq is not None:
                entry["unique_narration"] = uniq
        manifest.append(entry)

        tag = "get" if fetched else "have"
        extra = ""
        if "rows" in entry:
            extra = f"  rows={entry['rows']:,}"
            if "unique_narration" in entry:
                extra += f"  uniq_narr={entry['unique_narration']:,}"
        print(f"[{tag:>4}] {path:34s} {size:>11,} B{extra}")

    labelled_rows = sum(e.get("rows", 0) for e in manifest if e["file"] in LABELLED)
    print("-" * 68)
    print(f"labelled action segments (train + val): {labelled_rows:,}")

    provenance = {
        "work": "EPIC-KITCHENS-100",
        "route": "epic-csv",
        "repo": f"https://github.com/{REPO}",
        "branch": branch,
        "commit_sha": sha,
        "access_utc": access,
        "license": "CC BY-NC 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
        "files": manifest,
        "labelled_segments_train_val": labelled_rows,
    }
    # Full provenance lives in the (gitignored) cache alongside the raw files.
    with open(os.path.join(args.cache, "provenance.json"), "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=2)
    # Committable copy: counts + hashes + columns only, no raw annotation text.
    out = os.path.join(HERE, "download_provenance.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=2)
    print(f"\nprovenance -> {out}")
    print("done.")


if __name__ == "__main__":
    main()
