#!/usr/bin/env python3
"""STAGE 3 + per-work STAGE 4 stats for EgoSchema (VQA).

Builds one row per question (the clusterable unit is the question text), plus the
5 options as work-specific signal. The 'category' used for scatter coloring is the
question type (what / how / why / which / describe / ...), derived from the first
interrogative cue in the question. Answers are public for only 500 questions.

Outputs:
  egoschema_annotations.parquet   one row per question
  egoschema_sample.csv            500-row browsable sample
  egoschema_stats.json            counts, lengths, question-type + term distributions
  .cache/egoschema_unique.parquet unique cleaned questions + freq (cluster input)
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
SLUG = "egoschema"
WORK = "EgoSchema"
WS = re.compile(r"\s+")

# question-type cues, scanned in order of first appearance in the question
QTYPES = ["what", "how", "why", "which", "where", "when", "who",
          "describe", "explain", "summarize", "identify", "determine", "analyze"]
# collapse to a compact set for coloring
QMAP = {"explain": "describe", "summarize": "describe", "identify": "describe",
        "determine": "describe", "analyze": "describe",
        "where": "where/when", "when": "where/when", "who": "who"}

STOP = {"a", "an", "the", "of", "to", "and", "with", "in", "on", "it", "its", "is",
        "are", "was", "were", "be", "by", "for", "from", "into", "that", "this",
        "their", "his", "her", "they", "them", "c", "video", "throughout", "during",
        "while", "what", "how", "why", "which", "where", "when", "who", "describe",
        "does", "did", "do", "can", "could", "would", "given", "overall", "based",
        # EgoSchema procedural / boilerplate vocabulary (skip so terms are content)
        "identify", "primary", "primarily", "summarize", "summarise", "considering",
        "consider", "analyze", "analyse", "main", "sequence", "determine", "taking",
        "account", "demonstrate", "factors", "factor", "role", "significance",
        "manner", "purpose", "performed", "perform", "performing", "various",
        "particular", "specific", "entire", "focus", "focused", "recurring",
        "including", "overarching", "briefly", "explain", "provide", "detail",
        "detailed", "relationship", "interaction", "interactions", "actions",
        "action", "activity", "activities", "task", "tasks", "throughout", "across",
        "general", "overall", "most", "important", "key", "how", "and", "or"}


def clean_text(text):
    if not isinstance(text, str):
        return ""
    return WS.sub(" ", text).strip().lower()


def qtype(text):
    low = " " + text.lower()
    best, bestpos = "other", 10 ** 9
    for cue in QTYPES:
        p = low.find(" " + cue)
        if 0 <= p < bestpos:
            bestpos, best = p, cue
    return QMAP.get(best, best)


def head_term(text):
    for w in text.split():
        w = w.strip(",.?'\"")
        if w not in STOP and len(w) > 3:
            return w
    return "general"


def topk(counter, k=25):
    return [[str(x), int(v)] for x, v in counter.most_common(k)]


def main():
    q = json.load(open(os.path.join(CACHE, "questions.json"), encoding="utf-8"))
    ans = {}
    ap = os.path.join(CACHE, "subset_answers.json")
    if os.path.exists(ap):
        ans = json.load(open(ap, encoding="utf-8"))

    rows = []
    opt_lens = []
    for r in q:
        qt = str(r.get("question", ""))
        opts = [str(r.get(f"option {i}", "")) for i in range(5)]
        opt_lens.extend(len(o.split()) for o in opts if o)
        qid = r.get("q_uid", "")
        rows.append({
            "ann_id": qid, "work": WORK, "source_dataset": "Ego4D (EgoSchema)",
            "annotation_type": "vqa",
            "text": qt, "text_clean": clean_text(qt),
            "t_start": pd.NA, "t_end": pd.NA, "clip_id": qid,
            "verb": qtype(qt), "noun": head_term(clean_text(qt)),
            "verb_category": qtype(qt), "split": "test",
            "has_answer": qid in ans,
            "answer_idx": int(ans[qid]) if qid in ans else -1,
            "options": " ||| ".join(opts),
            "n_options": sum(1 for o in opts if o),
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
    qtok_lens = tok.map(len)
    vocab, words = Counter(), Counter()
    for ts in tok:
        vocab.update(ts)
        words.update(w for w in ts if w not in STOP and len(w) > 3)

    import numpy as np
    stats = {
        "work": WORK,
        "annotation_type": ["vqa"],
        "counts": {
            "labelled_segments": int(len(df)),
            "unique_narrations_clean": int(len(uniq)),
            "questions": int(len(df)),
            "options_total": int(len(df) * 5),
            "public_answers": int(df["has_answer"].sum()),
            "vocab_size_tokens": int(len(vocab)),
            "question_types": int(df["verb_category"].nunique()),
            "split": "test",
        },
        "length": {
            "tokens_mean": round(float(qtok_lens.mean()), 3),
            "tokens_median": float(qtok_lens.median()),
            "tokens_p90": float(qtok_lens.quantile(0.9)),
            "tokens_max": int(qtok_lens.max()),
            "chars_mean": round(float(df["text_clean"].str.len().mean()), 3),
            "chars_median": float(df["text_clean"].str.len().median()),
            "option_tokens_mean": round(float(np.mean(opt_lens)), 3) if opt_lens else 0,
            "token_hist": [[int(k), int(v)] for k, v in
                           qtok_lens.value_counts().sort_index().items() if k <= 60],
        },
        "density": {"options_per_question": 5},
        "granularity_tier": ("vqa: long-form multiple-choice questions over 3-minute Ego4D "
                             "clips, five options each, requiring long temporal certificates"),
        "verb_top": topk(Counter(df["verb_category"])),
        "noun_top": topk(Counter(df["noun"])),
        "verb_category_dist": topk(Counter(df["verb_category"]), 12),
        "noun_category_dist": topk(Counter(df["noun"]), 20),
        "word_top": [[w, c] for w, c in words.most_common(40)],
        "qtype_dist": topk(Counter(df["verb_category"]), 12),
    }
    with open(os.path.join(HERE, f"{SLUG}_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)

    print(f"questions               : {len(df):,}")
    print(f"unique cleaned questions: {len(uniq):,}")
    print(f"public answers          : {int(df['has_answer'].sum())}")
    print(f"question types          : {df['verb_category'].nunique()} -> {[k for k,_ in stats['qtype_dist']]}")
    print(f"q length tokens mean/med: {qtok_lens.mean():.1f} / {qtok_lens.median():.0f}")
    print("wrote: annotations.parquet, sample.csv, stats.json, .cache/unique.parquet")


if __name__ == "__main__":
    main()
