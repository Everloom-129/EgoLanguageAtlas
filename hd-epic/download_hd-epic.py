#!/usr/bin/env python3
"""Download HD-EPIC language annotations (route: project-script over GitHub).

Source repo : https://github.com/hd-epic/hd-epic-annotations
License      : CC BY 4.0 (per the Bristol data.bris portal; confirmed against the
               repo README at download time). Redistribution permitted with
               attribution. This atlas is a non-commercial research survey and
               attributes the source.
What it pulls: narration + action-segment table (pickle), verb & noun class maps,
               high-level recipe steps, and the VQA-benchmark question files.
               No video / audio / 3D bytes are downloaded.
Properties   : idempotent + resumable, retries with backoff, prints provenance.

Usage:
    python download_hd-epic.py            # fetch into ./.cache
    python download_hd-epic.py --force    # re-download everything
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPO = "hd-epic/hd-epic-annotations"
BRANCH_CANDIDATES = ("main", "master")
RAW_URL = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"
TREE_API = "https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
COMMIT_API = "https://api.github.com/repos/{repo}/commits/{branch}"
USER_AGENT = "ego-atlas-downloader/1.0 (research; non-commercial)"

# Exact annotation files (language + class maps + recipe steps).
EXACT = (
    "README.md",
    "narrations-and-action-segments/HD_EPIC_Narrations.pkl",
    "narrations-and-action-segments/HD_EPIC_Narrations_erratum.csv",
    "narrations-and-action-segments/HD_EPIC_verb_classes.csv",
    "narrations-and-action-segments/HD_EPIC_noun_classes.csv",
    "high-level/complete_recipes.json",
)
# Prefixes: take every JSON under these folders (VQA question banks).
PREFIX_JSON = ("vqa-benchmark/",)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(HERE, ".cache")


def http_get(url, timeout=120, retries=5, accept=None):
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
    for branch in BRANCH_CANDIDATES:
        try:
            http_get(RAW_URL.format(repo=REPO, branch=branch, path="README.md"),
                     timeout=30, retries=1)
            return branch
        except Exception:
            continue
    return BRANCH_CANDIDATES[0]


def commit_sha(branch):
    try:
        data = http_get(COMMIT_API.format(repo=REPO, branch=branch),
                        timeout=30, retries=2, accept="application/vnd.github+json")
        return json.loads(data).get("sha")
    except Exception as exc:
        sys.stderr.write(f"  (could not resolve commit sha: {exc})\n")
        return None


def list_tree(branch):
    data = http_get(TREE_API.format(repo=REPO, branch=branch),
                    timeout=60, retries=3, accept="application/vnd.github+json")
    return json.loads(data).get("tree", [])


def select_paths(tree):
    want = set(EXACT)
    for node in tree:
        if node.get("type") != "blob":
            continue
        p = node["path"]
        if any(p.startswith(pre) and p.lower().endswith(".json") for pre in PREFIX_JSON):
            want.add(p)
    return sorted(want)


def download_file(branch, path, dest, force=False):
    if (not force) and os.path.exists(dest) and os.path.getsize(dest) > 0:
        return False
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    data = http_get(RAW_URL.format(repo=REPO, branch=branch, path=path))
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


def main():
    parser = argparse.ArgumentParser(description="Download HD-EPIC annotations.")
    parser.add_argument("--cache", default=DEFAULT_CACHE)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    os.makedirs(args.cache, exist_ok=True)

    print("HD-EPIC annotation download")
    print(f"repo   : https://github.com/{REPO}")
    branch = resolve_branch()
    print(f"branch : {branch}")
    sha = commit_sha(branch)
    print(f"commit : {sha or 'n/a'}")
    access = datetime.now(timezone.utc).isoformat()
    print(f"access : {access} (UTC)")
    paths = select_paths(list_tree(branch))
    print(f"files  : {len(paths)} selected")
    print("-" * 70)

    manifest = []
    for path in paths:
        dest = os.path.join(args.cache, path)
        try:
            fetched = download_file(branch, path, dest, force=args.force)
        except urllib.error.HTTPError as exc:
            print(f"FAIL {path}: HTTP {exc.code}")
            manifest.append({"file": path, "status": f"http_{exc.code}"})
            continue
        size = os.path.getsize(dest)
        manifest.append({"file": path, "bytes": size,
                         "status": "downloaded" if fetched else "cached",
                         "sha256": sha256_of(dest)})
        tag = "get" if fetched else "have"
        print(f"[{tag:>4}] {size:>11,} B  {path}")

    provenance = {
        "work": "HD-EPIC",
        "route": "project-script (GitHub raw)",
        "repo": f"https://github.com/{REPO}",
        "branch": branch,
        "commit_sha": sha,
        "access_utc": access,
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
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
