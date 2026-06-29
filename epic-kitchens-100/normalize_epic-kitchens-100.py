#!/usr/bin/env python3
"""STAGE 3 + per-work STAGE 4 stats for EPIC-KITCHENS-100.

Reads the cached annotation CSVs, builds one normalized table (one row per
action segment), derives a deduplicated unique-narration table for clustering,
and computes per-work statistics. All counts trace back to the downloaded files.

EPIC has two verb/noun granularities:
  - `verb` / `noun`        : fine-grained normalized tokens (hundreds of each)
  - `verb_class`/`noun_class` -> the official 97 verb / 300 noun classes, whose
    representative name is the class `key` and whose semantic group is `category`.
We keep the fine tokens and add the canonical class keys (`verb_key`/`noun_key`),
and feature the canonical class distributions in the stats.

Outputs (in this folder unless noted):
  epic-kitchens-100_annotations.parquet   normalized table, 1 row / segment
  epic-kitchens-100_sample.csv            500-row browsable sample
  epic-kitchens-100_stats.json            counts, lengths, verb/noun dists, density
  .cache/epic-kitchens-100_unique.parquet unique cleaned narrations + freq (cluster input)
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
SLUG = "epic-kitchens-100"

WORK = "EPIC-KITCHENS-100"
SOURCE_DATASET = "EPIC-KITCHENS-100"
ANNOTATION_TYPE = "verb-noun-action"  # free-form narration parsed to verb+noun

WS = re.compile(r"\s+")


def ts_to_sec(value):
    """'HH:MM:SS.ff' -> float seconds. Returns NaN on bad input."""
    if not isinstance(value, str):
        return float("nan")
    parts = value.split(":")
    try:
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        if len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        return float(value)
    except ValueError:
        return float("nan")


def clean_text(text):
    """EPIC narrations carry no #C/#O markup; normalize whitespace + case only."""
    if not isinstance(text, str):
        return ""
    return WS.sub(" ", text).strip().lower()


def load_class_map(path):
    """id -> (key, category) from a verb/noun classes CSV."""
    df = pd.read_csv(path)
    return {int(r.id): (str(r.key), str(r.category)) for r in df.itertuples()}


def load_split(name, split, verb_map, noun_map):
    df = pd.read_csv(os.path.join(CACHE, name))
    df = df[df["narration"].notna()].copy()
    out = pd.DataFrame()
    out["ann_id"] = df["narration_id"].astype(str)
    out["work"] = WORK
    out["source_dataset"] = SOURCE_DATASET
    out["annotation_type"] = ANNOTATION_TYPE
    out["text"] = df["narration"].astype(str)
    out["text_clean"] = out["text"].map(clean_text)
    out["t_start"] = df["start_timestamp"].map(ts_to_sec)
    out["t_end"] = df["stop_timestamp"].map(ts_to_sec)
    out["clip_id"] = df["video_id"].astype(str)
    out["verb"] = df["verb"].astype(str)          # fine-grained token
    out["noun"] = df["noun"].astype(str)          # fine-grained token
    out["split"] = split
    # work-specific signal
    out["participant_id"] = df["participant_id"].astype(str)
    out["verb_class"] = df["verb_class"].astype("Int64")
    out["noun_class"] = df["noun_class"].astype("Int64")
    out["verb_key"] = df["verb_class"].map(lambda i: verb_map.get(int(i), ("?", ""))[0])
    out["noun_key"] = df["noun_class"].map(lambda i: noun_map.get(int(i), ("?", ""))[0])
    out["verb_category"] = df["verb_class"].map(lambda i: verb_map.get(int(i), ("", ""))[1])
    out["noun_category"] = df["noun_class"].map(lambda i: noun_map.get(int(i), ("", ""))[1])
    out["n_nouns"] = df["all_nouns"].map(
        lambda s: len(re.findall(r"'[^']*'", s)) if isinstance(s, str) else 1
    )
    out["seg_dur_s"] = (out["t_end"] - out["t_start"]).round(3)
    return out


def topk(series, k=25):
    return [[str(i), int(v)] for i, v in series.head(k).items()]


def main():
    verb_map = load_class_map(os.path.join(CACHE, "EPIC_100_verb_classes.csv"))
    noun_map = load_class_map(os.path.join(CACHE, "EPIC_100_noun_classes.csv"))

    train = load_split("EPIC_100_train.csv", "train", verb_map, noun_map)
    val = load_split("EPIC_100_validation.csv", "val", verb_map, noun_map)
    df = pd.concat([train, val], ignore_index=True)

    os.makedirs(CACHE, exist_ok=True)
    df.to_parquet(os.path.join(HERE, f"{SLUG}_annotations.parquet"), index=False)
    df.sample(min(500, len(df)), random_state=7).sort_values("ann_id").to_csv(
        os.path.join(HERE, f"{SLUG}_sample.csv"), index=False
    )

    # --- unique cleaned narrations (cluster input): frequency + modal class keys ---
    g = df.groupby("text_clean", sort=False)
    uniq = pd.DataFrame({"text_clean": g.size().index, "count": g.size().values})
    modal = g.agg(
        verb=("verb_key", lambda s: s.value_counts().idxmax()),
        noun=("noun_key", lambda s: s.value_counts().idxmax()),
        verb_fine=("verb", lambda s: s.value_counts().idxmax()),
        verb_category=("verb_category", lambda s: s.value_counts().idxmax()),
        example=("text", "first"),
        in_train=("split", lambda s: bool((s == "train").any())),
        in_val=("split", lambda s: bool((s == "val").any())),
    ).reset_index()
    uniq = uniq.merge(modal, on="text_clean", how="left").sort_values(
        "count", ascending=False
    ).reset_index(drop=True)
    uniq.to_parquet(os.path.join(CACHE, f"{SLUG}_unique.parquet"), index=False)

    # --- statistics (STAGE 4, per-work) ---
    tokens = df["text_clean"].str.split()
    tok_lens = tokens.map(len)
    char_lens = df["text_clean"].str.len()
    vocab = Counter()
    for toks in tokens:
        vocab.update(toks)

    vinfo = pd.read_csv(os.path.join(CACHE, "EPIC_100_video_info.csv"))
    total_hours = float(vinfo["duration"].sum() / 3600.0)
    labelled_videos = sorted(set(df["clip_id"]))
    labelled_hours = float(
        vinfo[vinfo["video_id"].isin(labelled_videos)]["duration"].sum() / 3600.0
    )

    bad_verb_ids = sorted(set(int(x) for x in df["verb_class"].dropna()) - set(verb_map))
    bad_noun_ids = sorted(set(int(x) for x in df["noun_class"].dropna()) - set(noun_map))

    stats = {
        "work": WORK,
        "annotation_type": [ANNOTATION_TYPE, "clip-narration"],
        "counts": {
            "labelled_segments": int(len(df)),
            "train_segments": int((df["split"] == "train").sum()),
            "val_segments": int((df["split"] == "val").sum()),
            "test_segments_no_text": 13092,
            "total_segments_incl_test": int(len(df)) + 13092,
            "unique_narrations_clean": int(len(uniq)),
            "unique_narrations_train": 15968,
            "unique_narrations_val": 3835,
            "vocab_size_tokens": int(len(vocab)),
            "verb_classes": len(verb_map),
            "noun_classes": len(noun_map),
            "distinct_verb_tokens": int(df["verb"].nunique()),
            "distinct_noun_tokens": int(df["noun"].nunique()),
            "videos_total": int(len(vinfo)),
            "videos_labelled": len(labelled_videos),
            "participants": int(df["participant_id"].nunique()),
        },
        "length": {
            "tokens_mean": round(float(tok_lens.mean()), 3),
            "tokens_median": float(tok_lens.median()),
            "tokens_p90": float(tok_lens.quantile(0.9)),
            "tokens_max": int(tok_lens.max()),
            "chars_mean": round(float(char_lens.mean()), 3),
            "chars_median": float(char_lens.median()),
            "multi_noun_share": round(float((df["n_nouns"] > 1).mean()), 4),
            "token_hist": [[int(k), int(v)] for k, v in
                           tok_lens.value_counts().sort_index().items() if k <= 12],
        },
        "hours": {
            "total_hours_all_videos": round(total_hours, 3),
            "labelled_video_hours": round(labelled_hours, 3),
        },
        "density": {
            "segments_per_hour_labelled": round(len(df) / labelled_hours, 2),
            "segments_per_labelled_video": round(len(df) / len(labelled_videos), 2),
            "total_segments_per_hour_all": round((len(df) + 13092) / total_hours, 2),
        },
        "granularity_tier": "clip-narration / verb-noun-action (fine-grained, single-aspect)",
        "verb_top": topk(df["verb_key"].value_counts()),         # canonical 97-class
        "noun_top": topk(df["noun_key"].value_counts()),         # canonical 300-class
        "verb_category_dist": topk(df["verb_category"].value_counts(), 30),
        "noun_category_dist": topk(df["noun_category"].value_counts(), 30),
        "word_top": [[w, c] for w, c in vocab.most_common(40)],
        "sanity": {
            "verb_class_ids_unknown": bad_verb_ids,
            "noun_class_ids_unknown": bad_noun_ids,
            "narration_dropna": int(0),
        },
    }
    with open(os.path.join(HERE, f"{SLUG}_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)

    print(f"normalized segments      : {len(df):,}")
    print(f"unique cleaned narrations: {len(uniq):,}")
    print(f"vocab (tokens)           : {len(vocab):,}")
    print(f"distinct verb / noun tok : {df['verb'].nunique():,} / {df['noun'].nunique():,}")
    print(f"verb / noun classes      : {len(verb_map)} / {len(noun_map)}")
    print(f"total hours (700 videos) : {total_hours:.2f}")
    print(f"labelled video hours     : {labelled_hours:.2f}")
    print(f"density (seg/hour, lab.)  : {len(df) / labelled_hours:.1f}")
    print(f"length tokens mean/med   : {tok_lens.mean():.2f} / {tok_lens.median():.0f}")
    print(f"bad verb/noun class ids  : {bad_verb_ids or 'none'} / {bad_noun_ids or 'none'}")
    print("wrote: annotations.parquet, sample.csv, stats.json, .cache/unique.parquet")


if __name__ == "__main__":
    main()
