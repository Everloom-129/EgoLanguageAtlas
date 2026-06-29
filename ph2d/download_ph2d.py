#!/usr/bin/env python3
"""Download PH2D language annotations (route: huggingface, attributes only).

Source : https://huggingface.co/datasets/RogerQi/PH2D  (HAT / Humanoid Policy ~
         Human Policy, CoRL 2025). License MIT.
Layout : 1,848 HDF5 episodes across 42 sessions (one task per session). The task
         language is the HDF5 root attribute `description`; `embodiment` and `sim`
         flag human vs humanoid and sim vs real. Each ~4 MB file also holds video
         and 3D hand pose, which we do not need.

The `description` is constant within a session, so this downloads only a few
episodes per session (default 2) to read the attributes, and weights each session
by its true episode count from the file listing. Parallel fetch, parse in the
main thread (h5py is not thread-safe). Idempotent: a rerun reuses the JSONL cache.

Usage:
    python download_ph2d.py                 # 2 episodes per session
    python download_ph2d.py --per-session 1
    python download_ph2d.py --force
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import h5py
from huggingface_hub import HfApi

REPO = "RogerQi/PH2D"
RESOLVE = "https://huggingface.co/datasets/{repo}/resolve/main/{path}"
UA = "ego-atlas-downloader/1.0 (research; internal)"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
JSONL = os.path.join(CACHE, "ph2d_sessions.jsonl")
WORKERS = 12


def session_of(path):
    return path.split("/")[0]


def fetch_bytes(path, retries=4):
    url = RESOLVE.format(repo=REPO, path=urllib.parse.quote(path))
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=180).read()
        except Exception as exc:
            last = exc
            time.sleep(min(2 ** a, 15))
    raise last


def read_attrs(data):
    with h5py.File(io.BytesIO(data), "r") as f:
        return {k: (f.attrs[k].decode() if isinstance(f.attrs[k], bytes) else str(f.attrs[k]))
                for k in f.attrs}


def main():
    ap = argparse.ArgumentParser(description="Download PH2D task descriptions.")
    ap.add_argument("--per-session", type=int, default=2)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    if args.force and os.path.exists(JSONL):
        os.remove(JSONL)

    print("PH2D annotation download (HDF5 attributes only)")
    api = HfApi()
    files = [f for f in api.list_repo_files(REPO, repo_type="dataset")
             if f.lower().endswith(".hdf5")]
    by_sess = defaultdict(list)
    for f in files:
        by_sess[session_of(f)].append(f)
    counts = {s: len(v) for s, v in by_sess.items()}
    print(f"episodes: {len(files):,} across {len(by_sess)} sessions")

    done = set()
    if os.path.exists(JSONL):
        for line in open(JSONL, encoding="utf-8"):
            try:
                done.add(json.loads(line)["session"])
            except Exception:
                pass
        if done:
            print(f"resume: {len(done)} sessions cached")

    todo = [s for s in by_sess if s not in done]
    sample = {s: sorted(by_sess[s])[:args.per_session] for s in todo}
    tl = threading.local()

    def fetch(path):
        return path, fetch_bytes(path)

    access = datetime.now(timezone.utc).isoformat()
    out = open(JSONL, "a", encoding="utf-8")
    n_ok = n_fail = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for s in todo:
            paths = sample[s]
            descs, attrs0 = [], {}
            try:
                for path, data in ex.map(fetch, paths):
                    a = read_attrs(data)
                    if not attrs0:
                        attrs0 = a
                    if a.get("description"):
                        descs.append(a["description"].strip())
                rec = {
                    "session": s,
                    "description": descs[0] if descs else "",
                    "description_varies": len(set(descs)) > 1,
                    "embodiment": attrs0.get("embodiment", ""),
                    "sim": attrs0.get("sim", ""),
                    "episode_count": counts[s],
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
                n_ok += 1
            except Exception as exc:
                n_fail += 1
                sys.stderr.write(f"  fail {s}: {exc}\n")
            if (n_ok + n_fail) % 10 == 0:
                print(f"  {n_ok + n_fail}/{len(todo)} sessions", flush=True)
    out.close()

    total_sessions = sum(1 for _ in open(JSONL, encoding="utf-8"))
    prov = {
        "work": "HAT / PH2D", "route": "huggingface (hdf5 attributes only)",
        "repo": f"https://huggingface.co/datasets/{REPO}",
        "episodes_total": len(files), "sessions": len(by_sess),
        "sessions_read": total_sessions, "per_session_sampled": args.per_session,
        "access_utc": access, "license": "MIT",
        "license_url": "https://opensource.org/license/mit",
        "language_attr": "description", "source_dataset": "PH2D (own egocentric capture)",
    }
    for p in (os.path.join(CACHE, "provenance.json"),
              os.path.join(HERE, "download_provenance.json")):
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(prov, fh, indent=2)
    print(f"done. sessions cached: {total_sessions} (ok {n_ok}, fail {n_fail})")
    print(f"jsonl -> {JSONL}")


if __name__ == "__main__":
    main()
