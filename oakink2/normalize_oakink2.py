#!/usr/bin/env python3
"""STAGE 3 + per-work STAGE 4 stats for OakInk2.

Reads the extracted OakInk2 `program/` json (downloaded as program.tar) and builds
one normalized table (one row per language annotation unit), a deduped
unique-string table for clustering, and per-work stats. OakInk2 carries three
language streams, all redistributable under CC BY-SA 4.0:

  task_target.json            complex-task instruction  (one per sequence)
  desc_info/<seq>.json         primitive-task descriptions (atomic substeps,
                               English seg_desc + Chinese seg_desc_zh), with a
                               mocap frame range per segment (120 fps)
  initial_condition_info/...   recipe steps (high-level task instructions)

OakInk2 ships no verb/noun taxonomy, so a head verb and head noun are derived
from each imperative sentence; verb_category is a semantic family (from a fixed
manipulation map) so the scatter can color by it.

Outputs:
  oakink2_annotations.parquet   normalized table, 1 row / annotation
  oakink2_sample.csv            500-row browsable sample
  oakink2_stats.json            counts, lengths, head verb/noun dists, streams
  .cache/oakink2_unique.parquet unique cleaned strings + freq (cluster input)
"""
from __future__ import annotations

import ast
import json
import os
import re
from collections import Counter

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
PROG = os.path.join(CACHE, "program_extracted", "program")
SLUG = "oakink2"
WORK = "OakInk2"
FPS_MOCAP = 120.0
WS = re.compile(r"\s+")
WORD = re.compile(r"[a-z]+")

# Head verb -> semantic family (palette keys in atlas_lib.CATCOLORS), so the
# scatter colors meaningfully without a dataset-native taxonomy.
VERB_FAMILY = {
    # retrieve (acquire / bring to hand)
    "take": "retrieve", "pick": "retrieve", "grab": "retrieve", "grasp": "retrieve",
    "grip": "retrieve", "get": "retrieve", "lift": "retrieve", "collect": "retrieve",
    "retrieve": "retrieve", "fetch": "retrieve", "scoop": "retrieve", "pull": "retrieve",
    "draw": "retrieve", "gather": "retrieve", "catch": "retrieve", "hold": "retrieve",
    "carry": "retrieve", "raise": "retrieve",
    # leave (release / put down)
    "put": "leave", "place": "leave", "drop": "leave", "leave": "leave", "release": "leave",
    "return": "leave", "insert": "leave", "deposit": "leave", "set": "leave", "store": "leave",
    "stack": "leave", "load": "leave", "lay": "leave", "rest": "leave", "lower": "leave",
    # clean
    "wash": "clean", "clean": "clean", "wipe": "clean", "rinse": "clean", "dry": "clean",
    "scrub": "clean", "dust": "clean", "sweep": "clean", "mop": "clean", "polish": "clean",
    # access (open / close / operate switches)
    "open": "access", "close": "access", "uncap": "access", "cap": "access", "unlock": "access",
    "lock": "access", "press": "access", "switch": "access", "ignite": "access", "plug": "access",
    "unplug": "access", "click": "access", "push": "access", "turn": "access",
    # split (cut / divide)
    "cut": "split", "chop": "split", "slice": "split", "peel": "split", "divide": "split",
    "split": "split", "break": "split", "tear": "split", "crack": "split", "saw": "split",
    "trim": "split", "carve": "split", "snap": "split", "halve": "split",
    # merge (combine / join)
    "mix": "merge", "stir": "merge", "combine": "merge", "pour": "merge", "add": "merge",
    "attach": "merge", "connect": "merge", "assemble": "merge", "fill": "merge", "join": "merge",
    "stick": "merge", "glue": "merge", "tie": "merge", "knot": "merge", "sew": "merge",
    "blend": "merge", "whisk": "merge", "screw": "merge", "transfer": "merge",
    # manipulate (move / adjust / operate generic)
    "move": "manipulate", "rotate": "manipulate", "adjust": "manipulate", "shake": "manipulate",
    "squeeze": "manipulate", "fold": "manipulate", "manipulate": "manipulate",
    "rearrange": "manipulate", "flip": "manipulate", "swap": "manipulate", "operate": "manipulate",
    "use": "manipulate", "roll": "manipulate", "bend": "manipulate", "twist": "manipulate",
    "position": "manipulate", "tilt": "manipulate", "hang": "manipulate", "drag": "manipulate",
    # monitor (inspect / read)
    "check": "monitor", "look": "monitor", "watch": "monitor", "inspect": "monitor",
    "observe": "monitor", "examine": "monitor", "read": "monitor", "view": "monitor",
    "search": "monitor", "measure": "monitor",
    # block (cover / seal)
    "cover": "block", "block": "block", "shield": "block", "seal": "block", "wrap": "block",
    # transition (locomotion / posture)
    "walk": "transition", "go": "transition", "enter": "transition", "exit": "transition",
    "step": "transition", "climb": "transition", "stand": "transition", "sit": "transition",
    "approach": "transition",
    # sense
    "feel": "sense", "taste": "sense", "smell": "sense", "touch": "sense", "sniff": "sense",
    # distribute (spread / apply / serve)
    "distribute": "distribute", "spread": "distribute", "apply": "distribute",
    "sprinkle": "distribute", "scatter": "distribute", "serve": "distribute", "spray": "distribute",
    "paint": "distribute", "smear": "distribute", "coat": "distribute", "brush": "distribute",
    "give": "distribute", "dispense": "distribute", "squeeze-out": "distribute",
    # order (sort / arrange)
    "sort": "order", "order": "order", "organize": "order", "align": "order", "arrange": "order",
    "classify": "order", "stash": "order",
}
PREPS = {"to", "into", "onto", "from", "on", "in", "with", "at", "for", "off", "out",
         "over", "under", "inside", "outside", "through", "across", "of", "up", "down",
         "and", "then", "by", "near", "toward", "towards", "around", "between"}
ARTICLES = {"the", "a", "an", "its", "his", "her", "their", "your", "this", "that",
            "some", "one", "another", "it"}


def clean_text(text):
    if not isinstance(text, str):
        return ""
    return WS.sub(" ", text).strip().lower()


def head_verb_noun(text):
    """Head verb (first token) and head object noun (token before the first
    preposition, else last content token) from an imperative sentence."""
    toks = WORD.findall(text.lower())
    if not toks:
        return "?", "?"
    verb = toks[0]
    rest = toks[1:]
    noun = "?"
    for i, w in enumerate(rest):
        if w in PREPS:
            # walk back to last non-article token before the preposition
            for j in range(i - 1, -1, -1):
                if rest[j] not in ARTICLES and rest[j] not in PREPS:
                    noun = rest[j]
                    break
            break
    if noun == "?":
        for w in reversed(rest):
            if w not in ARTICLES and w not in PREPS:
                noun = w
                break
    return verb, noun


def family(verb):
    return VERB_FAMILY.get(verb, "manipulate")


def enclose(rng):
    """A desc_info key encodes (lh_range, rh_range); return (beg, end) seconds."""
    try:
        pair = ast.literal_eval(rng)
    except Exception:
        return float("nan"), float("nan")
    a, b = (pair if isinstance(pair, (list, tuple)) and len(pair) == 2 else (None, None))
    cands = [x for x in (a, b) if isinstance(x, (list, tuple)) and len(x) == 2]
    if not cands:
        return float("nan"), float("nan")
    beg = min(c[0] for c in cands)
    end = max(c[1] for c in cands)
    return round(beg / FPS_MOCAP, 3), round(end / FPS_MOCAP, 3)


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def topk(series, k=25):
    return [[str(i), int(v)] for i, v in series.head(k).items()]


def main():
    rows = []

    # 1) complex-task instructions
    task_target = load_json(os.path.join(PROG, "task_target.json"))
    for seq_key, target in task_target.items():
        if not isinstance(target, str) or not target.strip():
            continue
        v, n = head_verb_noun(target)
        rows.append(dict(ann_id=f"task:{seq_key}", annotation_type="task-instruction",
                         stream="complex_task", text=target.strip(), text_zh="",
                         t_start=float("nan"), t_end=float("nan"), clip_id=seq_key,
                         verb=v, noun=n, verb_category=family(v)))

    # 2) primitive-task descriptions (atomic substeps)
    desc_dir = os.path.join(PROG, "desc_info")
    n_zh = 0
    for fn in sorted(os.listdir(desc_dir)):
        if not fn.endswith(".json"):
            continue
        seq_token = fn[:-5]
        d = load_json(os.path.join(desc_dir, fn))
        for i, (rng, seg) in enumerate(d.items()):
            sd = seg.get("seg_desc") if isinstance(seg, dict) else None
            if not isinstance(sd, str) or not sd.strip():
                continue
            zh = seg.get("seg_desc_zh", "") if isinstance(seg, dict) else ""
            if zh:
                n_zh += 1
            ts, te = enclose(rng)
            v, n = head_verb_noun(sd)
            rows.append(dict(ann_id=f"prim:{seq_token}:{i}", annotation_type="atomic-substep",
                             stream="primitive_task", text=sd.strip(), text_zh=zh,
                             t_start=ts, t_end=te, clip_id=seq_token,
                             verb=v, noun=n, verb_category=family(v)))

    # 3) recipe steps (high-level task instructions)
    ic_dir = os.path.join(PROG, "initial_condition_info")
    n_recipes = 0
    if os.path.isdir(ic_dir):
        for fn in sorted(os.listdir(ic_dir)):
            if not fn.endswith(".json"):
                continue
            seq_token = fn[:-5]
            d = load_json(os.path.join(ic_dir, fn))
            steps = d.get("recipe", []) if isinstance(d, dict) else []
            if steps:
                n_recipes += 1
            for i, step in enumerate(steps):
                if not isinstance(step, str) or not step.strip():
                    continue
                v, n = head_verb_noun(step)
                rows.append(dict(ann_id=f"recipe:{seq_token}:{i}", annotation_type="task-instruction",
                                 stream="recipe_step", text=step.strip(), text_zh="",
                                 t_start=float("nan"), t_end=float("nan"), clip_id=seq_token,
                                 verb=v, noun=n, verb_category=family(v)))

    df = pd.DataFrame(rows)
    df["work"] = WORK
    df["source_dataset"] = WORK
    df["split"] = "full"
    df["text_clean"] = df["text"].map(clean_text)
    df["seg_dur_s"] = (df["t_end"] - df["t_start"]).round(3)

    os.makedirs(CACHE, exist_ok=True)
    df.to_parquet(os.path.join(HERE, f"{SLUG}_annotations.parquet"), index=False)
    df.sample(min(500, len(df)), random_state=7).sort_values("ann_id").to_csv(
        os.path.join(HERE, f"{SLUG}_sample.csv"), index=False)

    # unique cleaned strings (frequency-weighted) -> cluster input
    g = df.groupby("text_clean", sort=False)
    uniq = pd.DataFrame({"text_clean": g.size().index, "count": g.size().values})
    modal = g.agg(
        verb=("verb", lambda s: s.value_counts().idxmax()),
        noun=("noun", lambda s: s.value_counts().idxmax()),
        verb_category=("verb_category", lambda s: s.value_counts().idxmax()),
        example=("text", "first"),
    ).reset_index()
    uniq = uniq.merge(modal, on="text_clean", how="left").sort_values(
        "count", ascending=False).reset_index(drop=True)
    uniq.to_parquet(os.path.join(CACHE, f"{SLUG}_unique.parquet"), index=False)

    tokens = df["text_clean"].str.split()
    tok_lens = tokens.map(len)
    char_lens = df["text_clean"].str.len()
    stop = ARTICLES | PREPS | {"is", "are", "be", "as"}
    vocab, words = Counter(), Counter()
    for toks in tokens:
        vocab.update(toks)
        words.update(w for w in toks if w not in stop)

    n_videos = int(df["clip_id"].nunique())
    by_type = df["annotation_type"].value_counts().to_dict()
    by_stream = df["stream"].value_counts().to_dict()

    stats = {
        "work": WORK,
        "annotation_type": ["task-instruction", "atomic-substep"],
        "counts": {
            "labelled_segments": int(len(df)),
            "unique_narrations_clean": int(len(uniq)),
            "unique_share": round(len(uniq) / len(df), 4),
            "vocab_size_tokens": int(len(vocab)),
            "sequences": n_videos,
            "complex_tasks": int(by_stream.get("complex_task", 0)),
            "primitive_segments": int(by_stream.get("primitive_task", 0)),
            "recipe_steps": int(by_stream.get("recipe_step", 0)),
            "recipes": n_recipes,
            "primitive_with_chinese": n_zh,
            "distinct_head_verbs": int(df["verb"].nunique()),
            "distinct_head_nouns": int(df["noun"].nunique()),
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
            "segments_per_video": round(len(df) / n_videos, 2),
            "primitives_per_sequence": round(by_stream.get("primitive_task", 0) /
                                             max(1, df[df.stream == "primitive_task"]["clip_id"].nunique()), 2),
        },
        "granularity_tier": ("task-instruction (complex task) + atomic-substep "
                             "(primitive descriptions) + recipe steps, bilingual EN/ZH primitives"),
        "annotation_type_dist": [[k, int(v)] for k, v in
                                 sorted(by_type.items(), key=lambda x: -x[1])],
        "verb_top": topk(df["verb"].value_counts()),
        "noun_top": topk(df["noun"].value_counts()),
        "verb_category_dist": topk(df["verb_category"].value_counts(), 30),
        "noun_category_dist": topk(df["noun"].value_counts(), 30),
        "word_top": [[w, c] for w, c in words.most_common(40)],
    }
    with open(os.path.join(HERE, f"{SLUG}_stats.json"), "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False)

    print(f"annotation units         : {len(df):,}")
    print(f"  complex-task targets   : {by_stream.get('complex_task', 0):,}")
    print(f"  primitive descriptions : {by_stream.get('primitive_task', 0):,} ({n_zh:,} with Chinese)")
    print(f"  recipe steps           : {by_stream.get('recipe_step', 0):,}")
    print(f"unique cleaned strings   : {len(uniq):,} ({len(uniq)/len(df):.1%})")
    print(f"sequences                : {n_videos:,}")
    print(f"length tokens mean/med/max: {tok_lens.mean():.1f} / {tok_lens.median():.0f} / {tok_lens.max()}")
    print("wrote: annotations.parquet, sample.csv, stats.json, .cache/unique.parquet")


if __name__ == "__main__":
    main()
