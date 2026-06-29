#!/usr/bin/env python3
"""STAGE 3 + per-work STAGE 4 stats for EgoVLP / EgoClip (sampled).

egoclip.csv has ~3.8M rows of Ego4D narrations in markup form ("#C C opens the
door"). This streams the CSV, strips the Ego4D tags (#C camera-wearer, #O other
person, #unsure, etc.), records the subject, aggregates unique cleaned narrations
with frequency, and keeps the top-frequency MAX_UNIQUE for clustering.

Outputs:
  egovlp_annotations.parquet   sampled rows (one row per kept exemplar)
  egovlp_sample.csv            500-row browsable sample
  egovlp_stats.json            counts, lengths, verb/subject/source distributions
  .cache/egovlp_unique.parquet unique cleaned narrations + freq (cluster input)
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter

import pandas as pd

csv.field_size_limit(10_000_000)

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
SLUG = "egovlp"
WORK = "EgoVLP (EgoClip)"
CSV_PATH = os.path.join(CACHE, "egoclip.csv")
MAX_UNIQUE = 60000
WS = re.compile(r"\s+")

# Leading Ego4D tag + subject pronoun, e.g. "#C C ", "#O X ", "#unsure".
TAG = re.compile(r"#\s*[A-Za-z]+\b")
LEAD_SUBJ = re.compile(r"^(?:[a-z]\b[\s,]*)+")  # leading single-letter subjects (c, o, x)

STOP = {"a", "an", "the", "of", "to", "and", "with", "in", "on", "it", "its", "into",
        "from", "onto", "at", "by", "for", "his", "her", "their", "down", "up", "out",
        "over", "off", "around", "through", "another", "other"}


def subject_of(text):
    t = text.lstrip()
    if t[:2].lower() == "#c":
        return "camera_wearer"
    if t[:2].lower() == "#o":
        return "other_person"
    return "other"


def clean_text(text):
    if not isinstance(text, str):
        return ""
    t = TAG.sub(" ", text)          # remove all #C / #O / #unsure markers
    t = WS.sub(" ", t).strip().lower()
    t = LEAD_SUBJ.sub("", t)        # drop leading subject pronoun(s): "c ", "o ", "x "
    t = WS.sub(" ", t).strip(" .,")
    return t


def norm_verb(w):
    """Light 3rd-person-singular to base form for readable labels."""
    if len(w) <= 2:
        return w
    if w.endswith("ies"):
        return w[:-3] + "y"
    if w.endswith(("shes", "ches", "sses", "xes", "zes")):
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def head_verb(text):
    toks = text.split()
    return norm_verb(toks[0]) if toks else "?"


def head_noun(text):
    toks = text.split()
    for w in toks[1:]:
        w = w.strip(",.")
        if w not in STOP and len(w) > 2:
            return w
    return toks[-1] if toks else "?"


def main():
    if not os.path.exists(CSV_PATH):
        raise SystemExit(f"missing {CSV_PATH}; run download_egovlp.py first")

    print(f"streaming {CSV_PATH} ...")
    freq = Counter()
    example = {}
    subj_by_text = {}
    n_rows = 0
    subj_counts = Counter()
    src_counts = Counter()

    reader = pd.read_csv(CSV_PATH, sep="\t", usecols=lambda c: c in
                         ("clip_text", "narration_source"),
                         chunksize=200_000, dtype=str, engine="c", quoting=csv.QUOTE_NONE)
    for chunk in reader:
        for txt, src in zip(chunk.get("clip_text", []),
                            chunk.get("narration_source", [""] * len(chunk))):
            n_rows += 1
            if not isinstance(txt, str):
                continue
            subj = subject_of(txt)
            subj_counts[subj] += 1
            if isinstance(src, str):
                src_counts[src] += 1
            cl = clean_text(txt)
            if not cl:
                continue
            freq[cl] += 1
            if cl not in example:
                example[cl] = WS.sub(" ", txt).strip()
                subj_by_text[cl] = subj
        if n_rows % 1_000_000 < 200_000:
            print(f"  {n_rows:,} rows, {len(freq):,} unique narrations")

    print(f"total rows: {n_rows:,}; unique cleaned narrations: {len(freq):,}")
    kept = freq.most_common(MAX_UNIQUE)
    sampled_note = (f"clustered {len(kept):,} of {len(freq):,} unique cleaned narrations "
                    f"(top-frequency cap {MAX_UNIQUE:,}); derived from {n_rows:,} rows")
    if len(freq) > MAX_UNIQUE:
        print(f"NOTE: capping at {MAX_UNIQUE:,} most-frequent uniques for clustering")

    rows = [{"text_clean": cl, "count": int(c),
             "verb": head_verb(cl), "noun": head_noun(cl),
             "verb_category": head_verb(cl), "example": example.get(cl, cl),
             "subject": subj_by_text.get(cl, "other"),
             "in_train": True, "in_val": False} for cl, c in kept]
    uniq = pd.DataFrame(rows)
    os.makedirs(CACHE, exist_ok=True)
    uniq.to_parquet(os.path.join(CACHE, f"{SLUG}_unique.parquet"), index=False)

    ann = pd.DataFrame({
        "ann_id": [f"egoclip-{i}" for i in range(len(uniq))],
        "work": WORK, "source_dataset": "Ego4D (EgoVLP/EgoClip filtering)",
        "annotation_type": "clip-narration",
        "text": uniq["example"], "text_clean": uniq["text_clean"],
        "t_start": pd.NA, "t_end": pd.NA, "clip_id": pd.NA,
        "verb": uniq["verb"], "noun": uniq["noun"], "verb_category": uniq["verb_category"],
        "subject": uniq["subject"], "split": "full", "count": uniq["count"],
    })
    ann.to_parquet(os.path.join(HERE, f"{SLUG}_annotations.parquet"), index=False)
    ann.head(500).to_csv(os.path.join(HERE, f"{SLUG}_sample.csv"), index=False)

    tok_lens = uniq["text_clean"].str.split().map(len)
    char_lens = uniq["text_clean"].str.len()
    vocab, words = Counter(), Counter()
    for cl in uniq["text_clean"]:
        toks = cl.split()
        vocab.update(toks)
        words.update(w for w in toks if w not in STOP and len(w) > 2)

    def topk(counter, k=25):
        return [[str(x), int(v)] for x, v in counter.most_common(k)]

    stats = {
        "work": WORK,
        "annotation_type": ["clip-narration", "verb-noun-action"],
        "counts": {
            "labelled_segments": int(n_rows),
            "unique_narrations_clean": int(len(freq)),
            "clustered_unique": int(len(kept)),
            "vocab_size_tokens": int(len(vocab)),
            "camera_wearer_share": round(subj_counts.get("camera_wearer", 0) / max(1, n_rows), 4),
            "other_person_share": round(subj_counts.get("other_person", 0) / max(1, n_rows), 4),
            "sampled_note": sampled_note,
        },
        "length": {
            "tokens_mean": round(float(tok_lens.mean()), 3),
            "tokens_median": float(tok_lens.median()),
            "tokens_p90": float(tok_lens.quantile(0.9)),
            "tokens_max": int(tok_lens.max()),
            "chars_mean": round(float(char_lens.mean()), 3),
            "chars_median": float(char_lens.median()),
            "token_hist": [[int(k), int(v)] for k, v in
                           tok_lens.value_counts().sort_index().items() if k <= 25],
        },
        "density": {},
        "granularity_tier": ("clip-narration: manually written Ego4D timestamped narrations "
                             "(camera-wearer #C and other-person #O), tags stripped"),
        "verb_top": topk(Counter(uniq["verb"])),
        "noun_top": topk(Counter(uniq["noun"])),
        "verb_category_dist": topk(Counter(uniq["verb_category"]), 20),
        "noun_category_dist": topk(Counter(uniq["noun"]), 20),
        "word_top": [[w, c] for w, c in words.most_common(40)],
        "subject_dist": topk(subj_counts, 5),
        "narration_source_dist": topk(src_counts, 8),
    }
    with open(os.path.join(HERE, f"{SLUG}_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)

    print(f"kept for clustering   : {len(kept):,}")
    print(f"camera-wearer / other : {subj_counts.get('camera_wearer',0):,} / {subj_counts.get('other_person',0):,}")
    print(f"length tokens mean/med: {tok_lens.mean():.1f} / {tok_lens.median():.0f}")
    print("wrote: annotations.parquet, sample.csv, stats.json, .cache/unique.parquet")


if __name__ == "__main__":
    main()
