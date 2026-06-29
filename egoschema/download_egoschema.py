#!/usr/bin/env python3
"""Download EgoSchema VQA benchmark (route: GitHub raw).

Source : https://github.com/egoschema/EgoSchema
Files  : questions.json (5,031 long-form multiple-choice questions, 5 options each),
         subset_answers.json (correct answers for 500 of them; full key withheld),
         uid_to_ego4d.json (q_uid to Ego4D source clip mapping).
License: questions are open; the dataset is released under the Ego4D License (the
         clips are Ego4D). Questions were LLM-generated then human-curated.

Usage:
    python download_egoschema.py            # fetch into ./.cache
    python download_egoschema.py --force
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPO = "egoschema/EgoSchema"
BRANCHES = ("main", "master")
RAW = "https://raw.githubusercontent.com/{repo}/{branch}/{path}"
COMMIT_API = "https://api.github.com/repos/{repo}/commits/{branch}"
UA = "ego-atlas-downloader/1.0 (research; internal)"
FILES = ("questions.json", "subset_answers.json", "uid_to_ego4d.json")

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")


def http_get(url, timeout=120, retries=5, accept=None):
    last = None
    for attempt in range(retries):
        try:
            h = {"User-Agent": UA}
            if accept:
                h["Accept"] = accept
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise
            last = exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
        time.sleep(min(2 ** attempt, 20))
    raise last


def resolve_branch():
    for b in BRANCHES:
        try:
            http_get(RAW.format(repo=REPO, branch=b, path="questions.json"), timeout=30, retries=1)
            return b
        except Exception:
            continue
    return BRANCHES[0]


def main():
    ap = argparse.ArgumentParser(description="Download EgoSchema benchmark.")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)

    print("EgoSchema VQA download")
    branch = resolve_branch()
    print(f"repo/branch: {REPO}@{branch}")
    try:
        sha = json.loads(http_get(COMMIT_API.format(repo=REPO, branch=branch),
                                  timeout=30, retries=2,
                                  accept="application/vnd.github+json")).get("sha")
    except Exception:
        sha = None
    access = datetime.now(timezone.utc).isoformat()

    manifest = []
    for path in FILES:
        dest = os.path.join(CACHE, path)
        if args.force or not (os.path.exists(dest) and os.path.getsize(dest) > 0):
            try:
                data = http_get(RAW.format(repo=REPO, branch=branch, path=path))
            except urllib.error.HTTPError as exc:
                print(f"FAIL {path}: HTTP {exc.code}")
                manifest.append({"file": path, "status": f"http_{exc.code}"})
                continue
            with open(dest, "wb") as fh:
                fh.write(data)
        size = os.path.getsize(dest)
        manifest.append({"file": path, "bytes": size, "status": "ok"})
        print(f"[ ok ] {size:>10,} B  {path}")

    # quick counts
    q = json.load(open(os.path.join(CACHE, "questions.json"), encoding="utf-8"))
    n_q = len(q)
    ans = {}
    ap_ = os.path.join(CACHE, "subset_answers.json")
    if os.path.exists(ap_):
        ans = json.load(open(ap_, encoding="utf-8"))
    print(f"questions: {n_q:,}  public answers: {len(ans):,}")

    prov = {
        "work": "EgoSchema", "route": "github-raw",
        "repo": f"https://github.com/{REPO}", "branch": branch, "commit_sha": sha,
        "access_utc": access, "files": manifest,
        "n_questions": n_q, "n_public_answers": len(ans),
        "license": "Ego4D License (questions LLM-generated then human-curated)",
        "license_url": "https://ego4ddataset.com/",
        "source_dataset": "Ego4D",
    }
    for p in (os.path.join(CACHE, "provenance.json"),
              os.path.join(HERE, "download_provenance.json")):
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(prov, fh, indent=2)
    print(f"provenance -> {os.path.join(HERE, 'download_provenance.json')}\ndone.")


if __name__ == "__main__":
    main()
