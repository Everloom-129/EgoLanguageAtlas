#!/usr/bin/env python3
"""STAGE 3 + per-work STAGE 4 stats for HD-EPIC.

Reads the cached narration pickle, builds one normalized table (one row per
action segment), a deduped unique-narration table for clustering, and per-work
stats. Also summarizes the recipe-step (task-instruction) and VQA-benchmark
annotation streams. All counts trace to the downloaded files.

HD-EPIC narrations are full descriptive sentences with multiple verbs/nouns each;
the salient action is `main_actions` / `main_action_classes`, which we map to the
canonical verb/noun class keys via the class CSVs.

Outputs:
  hd-epic_annotations.parquet   normalized table, 1 row / segment
  hd-epic_sample.csv            500-row browsable sample
  hd-epic_stats.json            counts, lengths, verb/noun dists, vqa + recipes
  .cache/hd-epic_unique.parquet unique cleaned narrations + freq (cluster input)
"""
from __future__ import annotations

import json
import os
import re
import glob
from collections import Counter

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
SLUG = "hd-epic"
WORK = "HD-EPIC"
ANNOTATION_TYPE = "clip-narration"
WS = re.compile(r"\s+")

VQA_CATEGORIES = ["3d_perception", "fine_grained", "gaze", "ingredient",
                  "nutrition", "object_motion", "recipe"]


def clean_text(text):
    if not isinstance(text, str):
        return ""
    return WS.sub(" ", text).strip().lower()


def load_class_map(path):
    df = pd.read_csv(path)
    return {int(r.id): (str(r.key), str(r.category)) for r in df.itertuples()}


def first_or_none(seq):
    if isinstance(seq, (list, tuple)) and len(seq):
        return seq[0]
    return None


def main_vn(row, verb_map, noun_map):
    """Salient (verb_key, noun_key, verb_cat, noun_cat) from the main action."""
    mac = first_or_none(row.get("main_action_classes"))
    vid = nid = None
    if isinstance(mac, (list, tuple)) and len(mac) == 2:
        vid, nid = mac
    if vid is None:
        vid = first_or_none(row.get("verb_classes"))
    if nid is None:
        nid = first_or_none(row.get("noun_classes"))
    vk, vc = verb_map.get(int(vid), ("?", "")) if vid is not None else ("?", "")
    nk, nc = noun_map.get(int(nid), ("?", "")) if nid is not None else ("?", "")
    return vk, nk, vc, nc


def join_list(x):
    if isinstance(x, (list, tuple)):
        return ", ".join(str(i) for i in x)
    return ""


def summarize_vqa():
    by_cat = Counter()
    by_task = {}
    examples = []
    total = 0
    for path in sorted(glob.glob(os.path.join(CACHE, "vqa-benchmark", "*.json"))):
        name = os.path.basename(path)[:-5]
        cat = next((c for c in VQA_CATEGORIES if name.startswith(c + "_")), "other")
        task = name[len(cat) + 1:] if cat != "other" else name
        d = json.load(open(path, encoding="utf-8"))
        n = len(d)
        total += n
        by_cat[cat] += n
        by_task[name] = n
        if len(examples) < 8:
            entry = d[next(iter(d))] if isinstance(d, dict) else d[0]
            q = entry.get("question", "")
            if q:
                examples.append({"task": task, "category": cat, "question": q[:240]})
    return {
        "total": total,
        "n_categories": len([c for c in by_cat if c != "other"]),
        "n_tasks": len(by_task),
        "by_category": sorted([[c, n] for c, n in by_cat.items()], key=lambda x: -x[1]),
        "examples": examples,
    }


def summarize_recipes():
    path = os.path.join(CACHE, "high-level", "complete_recipes.json")
    if not os.path.exists(path):
        return {"n_recipes": 0, "n_steps": 0, "examples": []}
    r = json.load(open(path, encoding="utf-8"))
    n_steps = 0
    examples = []
    for rid, rec in r.items():
        steps = rec.get("steps", {}) if isinstance(rec, dict) else {}
        n_steps += len(steps)
        for sid, text in list(steps.items()):
            if len(examples) < 8 and isinstance(text, str) and text.strip():
                examples.append({"recipe": rec.get("name", rid), "step": text.strip()[:200]})
    return {"n_recipes": len(r), "n_steps": n_steps, "examples": examples}


def topk(series, k=25):
    return [[str(i), int(v)] for i, v in series.head(k).items()]


def main():
    verb_map = load_class_map(os.path.join(CACHE, "narrations-and-action-segments/HD_EPIC_verb_classes.csv"))
    noun_map = load_class_map(os.path.join(CACHE, "narrations-and-action-segments/HD_EPIC_noun_classes.csv"))

    raw = pd.read_pickle(os.path.join(CACHE, "narrations-and-action-segments/HD_EPIC_Narrations.pkl"))
    raw = raw[raw["narration"].notna()].copy()

    vk, nk, vc, nc = [], [], [], []
    for _, row in raw.iterrows():
        a, b, c, d = main_vn(row, verb_map, noun_map)
        vk.append(a); nk.append(b); vc.append(c); nc.append(d)

    df = pd.DataFrame()
    df["ann_id"] = raw["unique_narration_id"].astype(str)
    df["work"] = WORK
    df["source_dataset"] = WORK
    df["annotation_type"] = ANNOTATION_TYPE
    df["text"] = raw["narration"].astype(str)
    df["text_clean"] = df["text"].map(clean_text)
    df["t_start"] = raw["start_timestamp"].astype(float)
    df["t_end"] = raw["end_timestamp"].astype(float)
    df["clip_id"] = raw["video_id"].astype(str)
    df["verb"] = [str(x) for x in (first_or_none(v) or "" for v in raw["verbs"])]
    df["noun"] = [str(x) for x in (first_or_none(n) or "" for n in raw["nouns"])]
    df["split"] = "full"
    df["participant_id"] = raw["participant_id"].astype(str)
    df["verb_key"] = vk
    df["noun_key"] = nk
    df["verb_category"] = vc
    df["noun_category"] = nc
    df["hands"] = raw["hands"].map(join_list)
    df["n_verbs"] = raw["verbs"].map(lambda x: len(x) if isinstance(x, (list, tuple)) else 0)
    df["n_nouns"] = raw["nouns"].map(lambda x: len(x) if isinstance(x, (list, tuple)) else 0)
    df["seg_dur_s"] = (df["t_end"] - df["t_start"]).round(3)

    os.makedirs(CACHE, exist_ok=True)
    df.to_parquet(os.path.join(HERE, f"{SLUG}_annotations.parquet"), index=False)
    df.sample(min(500, len(df)), random_state=7).sort_values("ann_id").to_csv(
        os.path.join(HERE, f"{SLUG}_sample.csv"), index=False)

    g = df.groupby("text_clean", sort=False)
    uniq = pd.DataFrame({"text_clean": g.size().index, "count": g.size().values})
    modal = g.agg(
        verb=("verb_key", lambda s: s.value_counts().idxmax()),
        noun=("noun_key", lambda s: s.value_counts().idxmax()),
        verb_category=("verb_category", lambda s: s.value_counts().idxmax()),
        example=("text", "first"),
        in_train=("split", lambda s: True),
        in_val=("split", lambda s: False),
    ).reset_index()
    uniq = uniq.merge(modal, on="text_clean", how="left").sort_values(
        "count", ascending=False).reset_index(drop=True)
    uniq.to_parquet(os.path.join(CACHE, f"{SLUG}_unique.parquet"), index=False)

    tokens = df["text_clean"].str.split()
    tok_lens = tokens.map(len)
    char_lens = df["text_clean"].str.len()
    stop = {"the", "a", "an", "of", "to", "and", "with", "in", "on", "it", "is",
            "by", "into", "from", "your", "their", "his", "her", "as", "at"}
    vocab = Counter()
    words = Counter()
    for toks in tokens:
        vocab.update(toks)
        words.update(w for w in toks if w not in stop)

    n_videos = int(df["clip_id"].nunique())
    hours_paper = 41.0  # cited (HD-EPIC paper); no per-video duration file shipped
    span_hours = float(df.groupby("clip_id")["t_end"].max().sum() / 3600.0)

    vqa = summarize_vqa()
    recipes = summarize_recipes()

    stats = {
        "work": WORK,
        "annotation_type": ["clip-narration", "verb-noun-action", "task-instruction",
                            "vqa", "dense-multi-aspect"],
        "counts": {
            "labelled_segments": int(len(df)),
            "unique_narrations_clean": int(len(uniq)),
            "unique_share": round(len(uniq) / len(df), 4),
            "vocab_size_tokens": int(len(vocab)),
            "verb_classes": len(verb_map),
            "noun_classes": len(noun_map),
            "distinct_main_verbs": int(pd.Series(vk).nunique()),
            "distinct_main_nouns": int(pd.Series(nk).nunique()),
            "videos": n_videos,
            "participants": int(df["participant_id"].nunique()),
            "recipes": recipes["n_recipes"],
            "recipe_steps": recipes["n_steps"],
            "vqa_questions": vqa["total"],
            "vqa_categories": vqa["n_categories"],
            "vqa_tasks": vqa["n_tasks"],
        },
        "length": {
            "tokens_mean": round(float(tok_lens.mean()), 3),
            "tokens_median": float(tok_lens.median()),
            "tokens_p90": float(tok_lens.quantile(0.9)),
            "tokens_max": int(tok_lens.max()),
            "chars_mean": round(float(char_lens.mean()), 3),
            "chars_median": float(char_lens.median()),
            "multi_verb_share": round(float((df["n_verbs"] > 1).mean()), 4),
            "token_hist": [[int(k), int(v)] for k, v in
                           tok_lens.value_counts().sort_index().items() if k <= 30],
        },
        "hours": {
            "hours_paper_cited": hours_paper,
            "annotated_span_hours": round(span_hours, 3),
        },
        "density": {
            "segments_per_hour_cited": round(len(df) / hours_paper, 2),
            "segments_per_video": round(len(df) / n_videos, 2),
        },
        "granularity_tier": "clip-narration full-sentence + verb-noun-action + task-instruction + vqa (dense, multi-aspect)",
        "verb_top": topk(df["verb_key"].value_counts()),
        "noun_top": topk(df["noun_key"].value_counts()),
        "verb_category_dist": topk(df["verb_category"].value_counts(), 30),
        "noun_category_dist": topk(df["noun_category"].value_counts(), 30),
        "word_top": [[w, c] for w, c in words.most_common(40)],
        "vqa": vqa,
        "recipes": recipes,
    }
    with open(os.path.join(HERE, f"{SLUG}_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)

    print(f"narration segments       : {len(df):,}")
    print(f"unique cleaned narrations: {len(uniq):,} ({len(uniq)/len(df):.1%})")
    print(f"vocab tokens             : {len(vocab):,}")
    print(f"length tokens mean/med/max: {tok_lens.mean():.1f} / {tok_lens.median():.0f} / {tok_lens.max()}")
    print(f"videos / participants    : {n_videos} / {df['participant_id'].nunique()}")
    print(f"recipes / steps          : {recipes['n_recipes']} / {recipes['n_steps']}")
    print(f"VQA questions/cats/tasks  : {vqa['total']:,} / {vqa['n_categories']} / {vqa['n_tasks']}")
    print(f"annotated span hours      : {span_hours:.1f} (paper cites 41)")
    print("wrote: annotations.parquet, sample.csv, stats.json, .cache/unique.parquet")


if __name__ == "__main__":
    main()
