#!/usr/bin/env python3
"""STAGE 3 + per-work STAGE 4 stats for EgoDex (test split).

Reads the cached per-episode JSONL (HDF5 attributes) and builds one normalized
table (one row per episode), a deduped unique-description table for clustering,
and per-work statistics. The clusterable text is the ACTIVE task instruction:
llm_description when which_llm_description == 1, else llm_description2.

Outputs:
  egodex_annotations.parquet   normalized table, 1 row / episode
  egodex_sample.csv            500-row browsable sample
  egodex_stats.json            counts, lengths, verb/object/task/env distributions
  .cache/egodex_unique.parquet unique cleaned descriptions + freq (cluster input)
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
SLUG = "egodex"
WORK = "EgoDex"
JSONL = os.path.join(CACHE, "egodex_episodes.jsonl")
WS = re.compile(r"\s+")


def clean_text(text):
    if not isinstance(text, str):
        return ""
    return WS.sub(" ", text).strip().lower()


def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return 1


def active_desc(rec):
    which = to_int(rec.get("which_llm_description", 1))
    d1 = rec.get("llm_description") or ""
    d2 = rec.get("llm_description2") or ""
    if which == 2 and d2:
        return d2, d1
    return d1, d2


def active_verb(rec, which):
    verbs = rec.get("llm_verbs") or []
    if isinstance(verbs, list) and verbs:
        idx = which - 1
        if 0 <= idx < len(verbs):
            return str(verbs[idx]).lower()
        return str(verbs[0]).lower()
    return "?"


def first_obj(rec):
    objs = rec.get("llm_objects") or []
    if isinstance(objs, list) and objs:
        return str(objs[0]).lower()
    return "?"


def parse_env(env, key):
    if not isinstance(env, str):
        return ""
    for part in env.split(","):
        part = part.strip()
        if part.startswith(key + ":"):
            return part.split(":", 1)[1]
    return ""


def topk(counter, k=25):
    return [[str(x), int(v)] for x, v in counter.most_common(k)]


def main():
    if not os.path.exists(JSONL):
        raise SystemExit(f"missing {JSONL}; run download_egodex.py first")
    recs = [json.loads(l) for l in open(JSONL, encoding="utf-8")]
    print(f"episodes read: {len(recs):,}")

    rows = []
    for r in recs:
        which = to_int(r.get("which_llm_description", 1))
        act, other = active_desc(r)
        rows.append({
            "ann_id": r["ann_id"],
            "work": WORK, "source_dataset": WORK, "annotation_type": "task-instruction",
            "text": act, "text_clean": clean_text(act),
            "t_start": pd.NA, "t_end": pd.NA,
            "clip_id": r.get("ann_id", "").split("/")[-2] if "/" in r.get("ann_id", "") else r.get("task_folder", ""),
            "verb": active_verb(r, which), "noun": first_obj(r),
            "verb_category": active_verb(r, which), "split": "test",
            "task": r.get("task", r.get("task_folder", "")),
            "llm_type": r.get("llm_type", ""),
            "which": which,
            "alt_description": other,
            "env_table": parse_env(r.get("environment"), "table"),
            "env_position": parse_env(r.get("environment"), "position"),
            "env_background": parse_env(r.get("environment"), "background"),
            "n_objects": len(r.get("llm_objects") or []),
        })
    df = pd.DataFrame(rows)
    df = df[df["text_clean"].str.len() > 0].reset_index(drop=True)

    os.makedirs(CACHE, exist_ok=True)
    df.to_parquet(os.path.join(HERE, f"{SLUG}_annotations.parquet"), index=False)
    df.sample(min(500, len(df)), random_state=7).sort_values("ann_id").to_csv(
        os.path.join(HERE, f"{SLUG}_sample.csv"), index=False)

    g = df.groupby("text_clean", sort=False)
    uniq = pd.DataFrame({"text_clean": g.size().index, "count": g.size().values})
    modal = g.agg(
        verb=("verb", lambda s: s.value_counts().idxmax()),
        noun=("noun", lambda s: s.value_counts().idxmax()),
        verb_category=("verb_category", lambda s: s.value_counts().idxmax()),
        example=("text", "first"),
        in_train=("split", lambda s: False),
        in_val=("split", lambda s: True),
    ).reset_index()
    uniq = uniq.merge(modal, on="text_clean", how="left").sort_values(
        "count", ascending=False).reset_index(drop=True)
    uniq.to_parquet(os.path.join(CACHE, f"{SLUG}_unique.parquet"), index=False)

    tok = df["text_clean"].str.split()
    tok_lens = tok.map(len)
    char_lens = df["text_clean"].str.len()
    vocab, words = Counter(), Counter()
    stop = {"a", "an", "the", "of", "to", "and", "with", "in", "on", "it", "is",
            "by", "into", "from", "onto", "at", "your", "their"}
    for ts in tok:
        vocab.update(ts)
        words.update(w for w in ts if w not in stop and len(w) > 2)

    reversible = int((df["llm_type"].astype(str).str.lower() == "reversible").sum())
    stats = {
        "work": WORK,
        "annotation_type": ["task-instruction"],
        "counts": {
            "labelled_segments": int(len(df)),
            "unique_narrations_clean": int(len(uniq)),
            "unique_share": round(len(uniq) / len(df), 4),
            "vocab_size_tokens": int(len(vocab)),
            "tasks": int(df["task"].nunique()),
            "distinct_verbs": int(df["verb"].nunique()),
            "distinct_objects": int(df["noun"].nunique()),
            "reversible_episodes": reversible,
            "reversible_share": round(reversible / len(df), 4),
            "environments": int((df["env_table"] + "|" + df["env_background"]).nunique()),
            "split": "test",
        },
        "length": {
            "tokens_mean": round(float(tok_lens.mean()), 3),
            "tokens_median": float(tok_lens.median()),
            "tokens_p90": float(tok_lens.quantile(0.9)),
            "tokens_max": int(tok_lens.max()),
            "chars_mean": round(float(char_lens.mean()), 3),
            "chars_median": float(char_lens.median()),
            "token_hist": [[int(k), int(v)] for k, v in
                           tok_lens.value_counts().sort_index().items() if k <= 30],
        },
        "density": {
            "episodes_per_task": round(len(df) / max(1, df["task"].nunique()), 2),
        },
        "granularity_tier": ("task-instruction: per-episode GPT-authored task descriptions "
                             "(single imperative sentence), reversible tasks carry both directions"),
        "verb_top": topk(Counter(df["verb"])),
        "noun_top": topk(Counter(df["noun"])),
        "verb_category_dist": topk(Counter(df["verb_category"]), 20),
        "noun_category_dist": topk(Counter(df["noun"]), 20),
        "word_top": [[w, c] for w, c in words.most_common(40)],
        "task_top": topk(Counter(df["task"]), 25),
        "env_table_dist": topk(Counter(df[df["env_table"] != ""]["env_table"]), 12),
        "env_position_dist": topk(Counter(df[df["env_position"] != ""]["env_position"]), 12),
        "llm_type_dist": topk(Counter(df[df["llm_type"].astype(str) != ""]["llm_type"]), 10),
    }
    with open(os.path.join(HERE, f"{SLUG}_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)

    print(f"episodes (with text)   : {len(df):,}")
    print(f"unique descriptions    : {len(uniq):,} ({len(uniq)/len(df):.1%})")
    print(f"tasks / verbs / objects: {df['task'].nunique()} / {df['verb'].nunique()} / {df['noun'].nunique()}")
    print(f"reversible episodes    : {reversible} ({reversible/len(df):.1%})")
    print(f"length tokens mean/med : {tok_lens.mean():.1f} / {tok_lens.median():.0f}")
    print("wrote: annotations.parquet, sample.csv, stats.json, .cache/unique.parquet")


if __name__ == "__main__":
    main()
