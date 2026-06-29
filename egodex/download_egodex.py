#!/usr/bin/env python3
"""Download EgoDex language annotations (route: project-script, partial-zip over HTTP).

Source : https://github.com/apple/ml-egodex  (data on Apple CDN)
Archive: https://ml-site.cdn-apple.com/datasets/egodex/test.zip  (the 16 GB test split)
License: CC BY-NC-ND 4.0 (no-derivatives). Used here for internal, non-commercial
         analysis only; derived text is not redistributed outside this internal repo.

EgoDex stores the language per episode as HDF5 attributes (no video needed):
  llm_description, llm_description2, which_llm_description (1 or 2 active),
  llm_type, llm_verbs, llm_objects, task, environment, object.

To avoid downloading the ~14 GB of paired .mp4 video, this opens the remote zip
with HTTP range requests and reads only the .hdf5 members' bytes, extracting the
attributes from each. Idempotent and resumable: records stream to a JSONL cache
and a rerun skips episodes already read.

Usage:
    python download_egodex.py                 # read all hdf5 in the test split
    python download_egodex.py --per-task 40   # cap episodes per task
    python download_egodex.py --force         # ignore the resume cache
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import h5py

WORKERS = 16        # parallel range-request fetchers (network bound)
BATCH = 400         # episodes per batch (bounds memory, checkpoints resume)

URL = "https://ml-site.cdn-apple.com/datasets/egodex/test.zip"
REPO = "https://github.com/apple/ml-egodex"
SPLIT = "test"
UA = "ego-atlas-downloader/1.0 (research; internal)"

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
JSONL = os.path.join(CACHE, "egodex_episodes.jsonl")

# attributes to capture from each episode HDF5
STR_ATTRS = ("llm_description", "llm_description2", "which_llm_description",
             "llm_type", "task", "environment", "object", "session_name")
LIST_ATTRS = ("llm_verbs", "llm_objects")


class HttpFile(io.RawIOBase):
    """A seekable, read-only file over HTTP range requests (for zipfile)."""

    def __init__(self, url, retries=5):
        self.url = url
        self.pos = 0
        self.retries = retries
        self.size = int(self._head().headers["Content-Length"])

    def _head(self):
        req = urllib.request.Request(self.url, method="HEAD", headers={"User-Agent": UA})
        return urllib.request.urlopen(req, timeout=60)

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos

    def tell(self):
        return self.pos

    def seekable(self):
        return True

    def readable(self):
        return True

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        if n == 0:
            return b""
        end = min(self.pos + n, self.size) - 1
        last = None
        for attempt in range(self.retries):
            try:
                req = urllib.request.Request(
                    self.url, headers={"User-Agent": UA, "Range": f"bytes={self.pos}-{end}"})
                data = urllib.request.urlopen(req, timeout=180).read()
                self.pos += len(data)
                return data
            except (urllib.error.URLError, TimeoutError) as exc:
                last = exc
                time.sleep(min(2 ** attempt, 20))
        raise last

    def readinto(self, b):
        d = self.read(len(b))
        b[:len(d)] = d
        return len(d)


def task_of(filename):
    parts = filename.replace("\\", "/").split("/")
    return parts[-2] if len(parts) >= 2 else parts[0]


def decode_attr(v):
    if isinstance(v, bytes):
        return v.decode("utf-8", "replace")
    return v


def decode_list(v):
    try:
        return [decode_attr(x) for x in list(v)]
    except TypeError:
        return [decode_attr(v)]


def read_done_ids():
    done = set()
    if os.path.exists(JSONL):
        with open(JSONL, encoding="utf-8") as fh:
            for line in fh:
                try:
                    done.add(json.loads(line)["ann_id"])
                except Exception:
                    continue
    return done


def main():
    ap = argparse.ArgumentParser(description="Download EgoDex test-split language.")
    ap.add_argument("--per-task", type=int, default=0, help="cap episodes per task (0 = all)")
    ap.add_argument("--force", action="store_true", help="ignore resume cache")
    args = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)

    if args.force and os.path.exists(JSONL):
        os.remove(JSONL)

    print("EgoDex annotation download (test split, hdf5 attributes only)")
    print(f"archive: {URL}")
    hf = HttpFile(URL)
    print(f"size   : {hf.size / 1e9:.2f} GB")
    access = datetime.now(timezone.utc).isoformat()
    zf = zipfile.ZipFile(hf)
    h5 = [i for i in zf.infolist() if i.filename.lower().endswith(".hdf5")]
    print(f"episodes (hdf5): {len(h5)} across {len(set(task_of(i.filename) for i in h5))} tasks")

    if args.per_task > 0:
        per = Counter()
        sel = []
        for i in sorted(h5, key=lambda x: x.filename):
            tk = task_of(i.filename)
            if per[tk] < args.per_task:
                per[tk] += 1
                sel.append(i)
        h5 = sel
        print(f"capped to {len(h5)} episodes ({args.per_task}/task)")

    done = read_done_ids()
    if done:
        print(f"resume: {len(done)} episodes already cached")
    todo = [i for i in h5 if i.filename[:-5].replace("\\", "/") not in done]
    print(f"to fetch: {len(todo)} episodes with {WORKERS} parallel workers")

    # Per-thread ZipFile over its own HTTP connection (network fetch is parallel).
    tl = threading.local()

    def fetch(info):
        if not hasattr(tl, "zf"):
            tl.zf = zipfile.ZipFile(HttpFile(URL))
        return info.filename, tl.zf.read(info.filename)

    def parse(name, data):
        rec = {"ann_id": name[:-5].replace("\\", "/"), "task_folder": task_of(name)}
        with h5py.File(io.BytesIO(data), "r") as f:  # parsed in main thread only
            a = f.attrs
            for key in STR_ATTRS:
                if key in a:
                    rec[key] = decode_attr(a[key])
            for key in LIST_ATTRS:
                if key in a:
                    rec[key] = decode_list(a[key])
        return rec

    n_new = n_fail = 0
    t0 = time.time()
    out = open(JSONL, "a", encoding="utf-8")
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for b0 in range(0, len(todo), BATCH):
            batch = todo[b0:b0 + BATCH]
            for name, data in ex.map(fetch, batch):
                try:
                    out.write(json.dumps(parse(name, data), ensure_ascii=False) + "\n")
                    n_new += 1
                except Exception as exc:
                    n_fail += 1
                    sys.stderr.write(f"  fail {name}: {exc}\n")
            out.flush()
            rate = n_new / (time.time() - t0)
            print(f"  {min(b0 + BATCH, len(todo))}/{len(todo)}  new={n_new} fail={n_fail}  "
                  f"{rate:.1f}/s", flush=True)
    out.close()

    total = len(read_done_ids())
    prov = {
        "work": "EgoDex", "route": "project-script (partial-zip over HTTP)",
        "repo": REPO, "archive": URL, "split": SPLIT,
        "archive_bytes": hf.size, "access_utc": access,
        "license": "CC BY-NC-ND 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "license_note": ("no-derivatives; internal non-commercial analysis only, "
                         "derived text not redistributed externally"),
        "episodes_cached": total, "episodes_failed": n_fail,
        "fields": list(STR_ATTRS) + list(LIST_ATTRS),
    }
    for path in (os.path.join(CACHE, "provenance.json"),
                 os.path.join(HERE, "download_provenance.json")):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(prov, fh, indent=2)
    print(f"done. episodes cached: {total} (new {n_new}, failed {n_fail})")
    print(f"jsonl -> {JSONL}")


if __name__ == "__main__":
    main()
