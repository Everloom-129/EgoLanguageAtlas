#!/usr/bin/env python3
"""STAGE 3 + per-work STAGE 4 stats for PH2D (HAT).

Reads the per-session JSONL (HDF5 `description` attribute) and builds the
normalized table. The clusterable unit is the task description; descriptions are
session-level, so the corpus has many episodes but a small, coarse instruction
vocabulary. Each unique description is weighted by its total episode count, and
the human vs humanoid embodiment split (the point of PH2D) is recorded.

Outputs:
  ph2d_annotations.parquet   one row per session
  ph2d_sample.csv            browsable sample
  ph2d_stats.json            counts, lengths, verb + embodiment distributions
  .cache/ph2d_unique.parquet unique cleaned descriptions + episode weight
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
SLUG = "ph2d"
WORK = "HAT / PH2D"
JSONL = os.path.join(CACHE, "ph2d_sessions.jsonl")
WS = re.compile(r"\s+")
STOP = {"a", "an", "the", "of", "to", "and", "with", "in", "on", "it", "from",
        "into", "your", "his", "her", "their", "right", "left", "hand", "place",
        "put", "pick", "grasp", "up", "down", "onto"}


def clean_text(t):
    return WS.sub(" ", t).strip().lower() if isinstance(t, str) else ""


def norm_verb(w):
    if w.endswith("ies"):
        return w[:-3] + "y"
    if w.endswith(("shes", "ches")):
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def head_verb(t):
    toks = t.split()
    return norm_verb(toks[0]) if toks else "?"


def head_noun(t):
    for w in t.split():
        w = w.strip(",.")
        if w not in STOP and len(w) > 2:
            return w
    toks = t.split()
    return toks[-1] if toks else "?"


def embodiment_class(emb):
    e = (emb or "").lower()
    if e.startswith("human"):
        return "human"
    if "h1" in e or "inspire" in e or "humanoid" in e:
        return "humanoid"
    return "sim/other"


def topk(counter, k=25):
    return [[str(x), int(v)] for x, v in counter.most_common(k)]


def main():
    recs = [json.loads(l) for l in open(JSONL, encoding="utf-8")]
    rows = []
    for r in recs:
        desc = r.get("description", "") or ""
        rows.append({
            "ann_id": r["session"], "work": WORK, "source_dataset": "PH2D",
            "annotation_type": "task-instruction",
            "text": desc.strip(), "text_clean": clean_text(desc),
            "t_start": pd.NA, "t_end": pd.NA, "clip_id": r["session"],
            "verb": head_verb(clean_text(desc)), "noun": head_noun(clean_text(desc)),
            "verb_category": head_verb(clean_text(desc)), "split": "full",
            "embodiment": r.get("embodiment", ""),
            "embodiment_class": embodiment_class(r.get("embodiment", "")),
            "episode_count": int(r.get("episode_count", 0)),
        })
    df = pd.DataFrame(rows)
    df = df[df["text_clean"].str.len() > 0].reset_index(drop=True)
    total_eps = int(df["episode_count"].sum())

    os.makedirs(CACHE, exist_ok=True)
    df.to_parquet(os.path.join(HERE, f"{SLUG}_annotations.parquet"), index=False)
    df.sort_values("episode_count", ascending=False).to_csv(
        os.path.join(HERE, f"{SLUG}_sample.csv"), index=False)

    # unique descriptions, weighted by total episodes
    agg = defaultdict(lambda: {"count": 0, "verb": None, "noun": None, "example": None,
                               "emb": Counter()})
    for r in rows:
        u = agg[r["text_clean"]]
        u["count"] += r["episode_count"]
        u["verb"] = r["verb"]
        u["noun"] = r["noun"]
        u["example"] = r["text"]
        u["emb"][r["embodiment_class"]] += r["episode_count"]
    uniq = pd.DataFrame([{
        "text_clean": k, "count": v["count"], "verb": v["verb"], "noun": v["noun"],
        "verb_category": v["verb"], "example": v["example"],
        "in_train": True, "in_val": False,
    } for k, v in agg.items()]).sort_values("count", ascending=False).reset_index(drop=True)
    uniq.to_parquet(os.path.join(CACHE, f"{SLUG}_unique.parquet"), index=False)

    tok = uniq["text_clean"].str.split()
    tok_lens = tok.map(len)
    vocab, words = Counter(), Counter()
    for ts in tok:
        vocab.update(ts)
        words.update(w for w in ts if w not in STOP and len(w) > 2)

    emb_eps = Counter()
    for r in rows:
        emb_eps[r["embodiment_class"]] += r["episode_count"]
    emb_raw = Counter()
    for r in rows:
        emb_raw[r["embodiment"]] += r["episode_count"]

    stats = {
        "work": WORK,
        "annotation_type": ["task-instruction"],
        "counts": {
            "labelled_segments": total_eps,
            "sessions": int(len(df)),
            "unique_narrations_clean": int(len(uniq)),
            "vocab_size_tokens": int(len(vocab)),
            "distinct_verbs": int(df["verb"].nunique()),
            "human_episodes": int(emb_eps.get("human", 0)),
            "humanoid_episodes": int(emb_eps.get("humanoid", 0)),
            "sim_other_episodes": int(emb_eps.get("sim/other", 0)),
        },
        "length": {
            "tokens_mean": round(float(tok_lens.mean()), 3),
            "tokens_median": float(tok_lens.median()),
            "tokens_p90": float(tok_lens.quantile(0.9)),
            "tokens_max": int(tok_lens.max()),
            "chars_mean": round(float(uniq["text_clean"].str.len().mean()), 3),
            "chars_median": float(uniq["text_clean"].str.len().median()),
            "token_hist": [[int(k), int(v)] for k, v in
                           tok_lens.value_counts().sort_index().items() if k <= 25],
        },
        "density": {"episodes_per_session": round(total_eps / max(1, len(df)), 1)},
        "granularity_tier": ("task-instruction: one task description per session (coarse, "
                             "task-level), shared across many episodes; human and humanoid "
                             "embodiments"),
        "verb_top": topk(Counter(uniq["verb"])),
        "noun_top": topk(Counter(uniq["noun"])),
        "verb_category_dist": topk(Counter(uniq["verb"]), 15),
        "noun_category_dist": topk(Counter(uniq["noun"]), 15),
        "word_top": [[w, c] for w, c in words.most_common(40)],
        "embodiment_dist": topk(emb_eps, 6),
        "embodiment_raw_dist": topk(emb_raw, 8),
    }
    with open(os.path.join(HERE, f"{SLUG}_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)

    print(f"sessions               : {len(df)}")
    print(f"total episodes         : {total_eps:,}")
    print(f"unique descriptions    : {len(uniq)}")
    print(f"human / humanoid / sim : {emb_eps.get('human',0)} / {emb_eps.get('humanoid',0)} / {emb_eps.get('sim/other',0)} episodes")
    print(f"length tokens mean/med : {tok_lens.mean():.1f} / {tok_lens.median():.0f}")
    print("wrote: annotations.parquet, sample.csv, stats.json, .cache/unique.parquet")


if __name__ == "__main__":
    main()
