#!/usr/bin/env python3
"""STAGE 3 + per-work STAGE 4 stats for EgoVid-5M (sampled).

EgoVid-5M has ~4.9M rows. The committable, clusterable signal is the VLM-authored
high-level action description in the `name` column (and the longer `llava_cap`).
We stream the text CSV in chunks, aggregate unique cleaned `name` strings with
their frequency, and keep at most MAX_UNIQUE for clustering (all of them here,
since uniques are far fewer than rows). Counts trace to the downloaded file.

Outputs:
  egovid-5m_annotations.parquet   sampled rows (one row per kept exemplar)
  egovid-5m_sample.csv            500-row browsable sample
  egovid-5m_stats.json            counts, lengths, head verb/noun dists
  .cache/egovid-5m_unique.parquet unique cleaned descriptions + freq (cluster input)
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
SLUG = "egovid-5m"
WORK = "EgoVid-5M"
ANNOTATION_TYPE = "clip-narration"
TEXT_CSV = os.path.join(CACHE, "egovid-text.csv")

MAX_UNIQUE = 60000          # cap on unique strings sent to clustering
WS = re.compile(r"\s+")

# light verb lexicon to derive a head verb from a description for coloring
COMMON_VERBS = {
    "hold", "holding", "pick", "place", "placing", "move", "moving", "cut", "cutting",
    "pour", "pouring", "open", "close", "wash", "washing", "mix", "mixing", "take",
    "put", "apply", "applying", "work", "working", "use", "using", "stir", "stirring",
    "remove", "clean", "cleaning", "wipe", "press", "turn", "grab", "grabbing",
    "assemble", "attach", "insert", "lift", "carry", "push", "pull", "throw", "fold",
    "scoop", "spread", "shake", "rotate", "adjust", "operate", "handle", "handling",
    "prepare", "preparing", "arrange", "arranging", "examine", "inspect", "smooth",
    "smoothing", "demonstrate", "demonstrating", "perform", "performing", "seated",
    "standing", "walking", "sitting", "reaching", "reach",
}


def clean_text(text):
    if not isinstance(text, str):
        return ""
    return WS.sub(" ", text).strip().lower()


# gerund -> base form for the common verbs, for readable cluster labels
_GERUND = {
    "holding": "hold", "sitting": "sit", "picking": "pick", "placing": "place",
    "moving": "move", "cutting": "cut", "pouring": "pour", "washing": "wash",
    "mixing": "mix", "applying": "apply", "working": "work", "using": "use",
    "stirring": "stir", "cleaning": "clean", "grabbing": "grab", "handling": "handle",
    "preparing": "prepare", "arranging": "arrange", "examining": "examine",
    "smoothing": "smooth", "demonstrating": "demonstrate", "performing": "perform",
    "standing": "stand", "walking": "walk", "reaching": "reach",
}


def head_verb(text):
    for tok in text.split():
        w = tok.strip(",.;:")
        if w in COMMON_VERBS:
            return _GERUND.get(w, w)
    toks = text.split()
    return (toks[0].strip(",.;:") if toks else "?")


def head_noun(text):
    toks = [w.strip(",.;:") for w in text.split()]
    for w in toks:
        if len(w) > 3 and w not in COMMON_VERBS:
            return w
    return (toks[0] if toks else "?")


def main():
    if not os.path.exists(TEXT_CSV):
        print(f"missing {TEXT_CSV}; run download first", file=sys.stderr)
        sys.exit(1)

    print(f"streaming {TEXT_CSV} ...")
    name_freq = Counter()
    name_example = {}
    n_rows = 0
    noun_cls = Counter()
    verb_cls = Counter()

    reader = pd.read_csv(TEXT_CSV, usecols=lambda c: c in ("name", "noun_cls", "verb_cls"),
                         chunksize=200_000, dtype=str, engine="c")
    for chunk in reader:
        for name, nc, vc in zip(chunk.get("name", []), chunk.get("noun_cls", []),
                                chunk.get("verb_cls", [])):
            n_rows += 1
            cl = clean_text(name)
            if not cl:
                continue
            name_freq[cl] += 1
            if cl not in name_example:
                name_example[cl] = name if isinstance(name, str) else cl
            if isinstance(vc, str) and vc:
                verb_cls[vc] += 1
            if isinstance(nc, str) and nc:
                noun_cls[nc] += 1
        if n_rows % 1_000_000 < 200_000:
            print(f"  {n_rows:,} rows, {len(name_freq):,} unique descriptions")

    print(f"total rows: {n_rows:,}; unique cleaned descriptions: {len(name_freq):,}")

    # keep top-frequency uniques up to the cap
    most = name_freq.most_common()
    kept = most[:MAX_UNIQUE]
    sampled_note = (f"clustered {len(kept):,} of {len(name_freq):,} unique cleaned "
                    f"descriptions (top-frequency cap {MAX_UNIQUE:,}); "
                    f"derived from {n_rows:,} rows")
    if len(name_freq) > MAX_UNIQUE:
        print(f"NOTE: capping at {MAX_UNIQUE:,} most-frequent uniques for clustering")

    rows = []
    for cl, cnt in kept:
        ex = name_example.get(cl, cl)
        rows.append({
            "text_clean": cl, "count": int(cnt),
            "verb": head_verb(cl), "noun": head_noun(cl),
            "verb_category": head_verb(cl),
            "example": ex, "in_train": True, "in_val": False,
        })
    uniq = pd.DataFrame(rows)
    os.makedirs(CACHE, exist_ok=True)
    uniq.to_parquet(os.path.join(CACHE, f"{SLUG}_unique.parquet"), index=False)

    # normalized annotations table: one row per kept exemplar (license: apache-2.0)
    ann = pd.DataFrame({
        "ann_id": [f"egovid-{i}" for i in range(len(uniq))],
        "work": WORK, "source_dataset": "Ego4D (EgoVid-5M curation)",
        "annotation_type": ANNOTATION_TYPE,
        "text": uniq["example"], "text_clean": uniq["text_clean"],
        "t_start": pd.NA, "t_end": pd.NA, "clip_id": pd.NA,
        "verb": uniq["verb"], "noun": uniq["noun"],
        "verb_category": uniq["verb_category"], "split": "full",
        "count": uniq["count"],
    })
    ann.to_parquet(os.path.join(HERE, f"{SLUG}_annotations.parquet"), index=False)
    ann.head(500).to_csv(os.path.join(HERE, f"{SLUG}_sample.csv"), index=False)

    tok_lens = uniq["text_clean"].str.split().map(len)
    char_lens = uniq["text_clean"].str.len()
    vocab = Counter()
    words = Counter()
    stop = {"a", "an", "the", "of", "to", "and", "with", "in", "on", "is", "by",
            "into", "from", "their", "its", "as", "at", "while", "for", "over"}
    for cl in uniq["text_clean"]:
        toks = cl.split()
        vocab.update(toks)
        words.update(w for w in toks if w not in stop and len(w) > 2)

    def topk(counter, k=25):
        return [[str(x), int(v)] for x, v in counter.most_common(k)]

    stats = {
        "work": WORK,
        "annotation_type": ["clip-narration", "verb-noun-action"],
        "counts": {
            "labelled_segments": int(n_rows),
            "unique_narrations_clean": int(len(name_freq)),
            "clustered_unique": int(len(kept)),
            "vocab_size_tokens": int(len(vocab)),
            "distinct_verb_cls": int(len(verb_cls)),
            "distinct_noun_cls": int(len(noun_cls)),
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
                           tok_lens.value_counts().sort_index().items() if k <= 40],
        },
        "density": {},
        "granularity_tier": ("clip-narration: VLM-authored high-level action descriptions "
                             "(Qwen) plus long LLaVA captions, over Ego4D clips"),
        "verb_top": topk(Counter(dict(Counter(uniq["verb"]).most_common()))),
        "noun_top": topk(Counter(dict(Counter(uniq["noun"]).most_common()))),
        "verb_category_dist": topk(Counter(uniq["verb_category"]), 20),
        "noun_category_dist": topk(noun_cls, 20),
        "word_top": [[w, c] for w, c in words.most_common(40)],
        "source_verb_cls_top": topk(verb_cls, 25),
        "source_noun_cls_top": topk(noun_cls, 25),
    }
    with open(os.path.join(HERE, f"{SLUG}_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)

    print(f"kept for clustering   : {len(kept):,}")
    print(f"length tokens mean/med: {tok_lens.mean():.1f} / {tok_lens.median():.0f}")
    print(f"distinct verb/noun cls: {len(verb_cls)} / {len(noun_cls)}")
    print("wrote: annotations.parquet, sample.csv, stats.json, .cache/unique.parquet")


if __name__ == "__main__":
    main()
