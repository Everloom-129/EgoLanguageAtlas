#!/usr/bin/env python3
"""STAGE 4 (embed + cluster) for HD-EPIC.

Embeds the unique cleaned narrations with a sentence encoder, reduces with UMAP
(2D for plotting, low-D for clustering), clusters with HDBSCAN, labels each
cluster from its head verb + nouns (no LLM), and writes plotting + cluster
artifacts. Exemplars carry full text: HD-EPIC is CC BY-NC 4.0, which
permits redistribution with attribution for non-commercial use.

Reproducibility constants live at the top of the file.

Outputs:
  epic-kitchens-100_clusters.json   cluster id, label, sizes, exemplars, config
  epic-kitchens-100_scatter.json    2D coords + cluster + count + text per point
  epic-kitchens-100_stats.json      (patched) adds cluster summary
  .cache/epic-kitchens-100_emb.npy  embeddings (gitignored)
"""
from __future__ import annotations

import json
import os
import warnings
from collections import Counter

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
SLUG = "hd-epic"

# ---- reproducibility constants (recorded in the atlas footer) ----
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
UMAP_VIZ = dict(n_components=2, n_neighbors=15, min_dist=0.10, metric="cosine", random_state=42)
UMAP_CLU = dict(n_components=5, n_neighbors=15, min_dist=0.00, metric="cosine", random_state=42)
HDBSCAN_PARAMS = dict(min_cluster_size=50, min_samples=10, metric="euclidean",
                      cluster_selection_method="eom")
MAX_EXEMPLARS = 8


def embed(texts):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBED_MODEL)
    emb = model.encode(list(texts), batch_size=256, convert_to_numpy=True,
                       normalize_embeddings=True, show_progress_bar=True)
    return emb.astype(np.float32)


def reduce_umap(emb):
    import umap
    viz = umap.UMAP(**UMAP_VIZ).fit_transform(emb)
    clu = umap.UMAP(**UMAP_CLU).fit_transform(emb)
    return np.asarray(viz, np.float32), np.asarray(clu, np.float32), "umap"


def reduce_pca(emb):
    from sklearn.decomposition import PCA
    viz = PCA(n_components=2, random_state=42).fit_transform(emb)
    clu = PCA(n_components=min(15, emb.shape[1]), random_state=42).fit_transform(emb)
    return np.asarray(viz, np.float32), np.asarray(clu, np.float32), "pca"


def cluster(low):
    from sklearn.cluster import HDBSCAN
    labels = HDBSCAN(**HDBSCAN_PARAMS).fit_predict(low)
    return labels


def label_from_heads(verbs, nouns, weights):
    vc, nc = Counter(), Counter()
    for v, n, w in zip(verbs, nouns, weights):
        vc[v] += w
        nc[n] += w
    top_verbs = [v for v, _ in vc.most_common(2)]
    top_nouns = [n for n, _ in nc.most_common(3)]
    verb_part = " / ".join(top_verbs) if top_verbs else "?"
    noun_part = ", ".join(top_nouns) if top_nouns else "?"
    return f"{verb_part}: {noun_part}", vc, nc


def main():
    uniq = pd.read_parquet(os.path.join(CACHE, f"{SLUG}_unique.parquet"))
    texts = uniq["text_clean"].tolist()
    counts = uniq["count"].to_numpy()
    verbs = uniq["verb"].tolist()
    nouns = uniq["noun"].tolist()
    vcats = uniq["verb_category"].tolist()
    examples = uniq["example"].tolist()
    print(f"unique narrations to embed: {len(texts):,}")

    emb_path = os.path.join(CACHE, f"{SLUG}_emb.npy")
    if os.path.exists(emb_path) and np.load(emb_path, mmap_mode="r").shape[0] == len(texts):
        emb = np.load(emb_path)
        print(f"loaded cached embeddings: {emb.shape}")
    else:
        emb = embed(texts)
        np.save(emb_path, emb)
        print(f"embeddings: {emb.shape}")

    try:
        viz, low, reducer = reduce_umap(emb)
    except Exception as exc:  # pragma: no cover - fallback path
        print(f"UMAP unavailable ({exc}); falling back to PCA")
        viz, low, reducer = reduce_pca(emb)
    print(f"reduced with {reducer}: viz={viz.shape} cluster={low.shape}")

    labels = cluster(low)
    uniq["cluster"] = labels
    uniq.to_parquet(os.path.join(CACHE, f"{SLUG}_unique.parquet"), index=False)

    ids = sorted(set(int(x) for x in labels if x >= 0))
    n_noise = int((labels < 0).sum())
    noise_share_unique = round(n_noise / len(labels), 4)
    noise_total = int(counts[labels < 0].sum())
    noise_share_total = round(noise_total / int(counts.sum()), 4)
    print(f"clusters: {len(ids)}  noise(unique): {n_noise:,} ({noise_share_unique:.1%})"
          f"  noise(weighted): {noise_share_total:.1%}")

    # centroids / medoids in embedding space
    clusters = []
    for cid in ids:
        idx = np.where(labels == cid)[0]
        sub = emb[idx]
        centroid = sub.mean(axis=0)
        centroid /= (np.linalg.norm(centroid) + 1e-9)
        cos = sub @ centroid
        medoid_local = int(idx[int(np.argmax(cos))])

        sub_counts = counts[idx]
        order = idx[np.argsort(-sub_counts)]  # highest-frequency members first
        label, vc, nc = label_from_heads(
            [verbs[i] for i in idx], [nouns[i] for i in idx], sub_counts.tolist()
        )

        exemplar_idx = []
        seen = set()
        for i in [medoid_local, *order.tolist()]:
            t = examples[i]
            if t in seen:
                continue
            seen.add(t)
            exemplar_idx.append(i)
            if len(exemplar_idx) >= MAX_EXEMPLARS:
                break
        exemplars = [{"text": examples[i], "count": int(counts[i])} for i in exemplar_idx]

        cat_counter = Counter()
        for i in idx:
            cat_counter[vcats[i]] += int(counts[i])
        dom_cat = cat_counter.most_common(1)[0][0] if cat_counter else ""

        clusters.append({
            "id": cid,
            "label": label,
            "auto_named": True,
            "naming": "head verb(s) + top nouns, count-weighted",
            "verb_category": dom_cat,
            "size_unique": int(len(idx)),
            "size_total": int(sub_counts.sum()),
            "verb_top": [[v, int(w)] for v, w in vc.most_common(5)],
            "noun_top": [[n, int(w)] for n, w in nc.most_common(6)],
            "medoid_text": examples[medoid_local],
            "exemplars": exemplars,
        })

    clusters.sort(key=lambda c: -c["size_total"])

    config = {
        "encoder": EMBED_MODEL,
        "reducer": reducer,
        "umap_viz": UMAP_VIZ,
        "umap_cluster": UMAP_CLU,
        "hdbscan": HDBSCAN_PARAMS,
        "n_points": int(len(texts)),
    }
    out = {
        "work": "HD-EPIC",
        "config": config,
        "n_clusters": len(ids),
        "noise_unique": n_noise,
        "noise_share_unique": noise_share_unique,
        "noise_share_weighted": noise_share_total,
        "clusters": clusters,
    }
    with open(os.path.join(HERE, f"{SLUG}_clusters.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)

    # compact scatter: [x, y, cluster, count, text, verb_key]
    points = [[round(float(viz[i, 0]), 3), round(float(viz[i, 1]), 3),
               int(labels[i]), int(counts[i]), examples[i], verbs[i]]
              for i in range(len(texts))]
    with open(os.path.join(HERE, f"{SLUG}_scatter.json"), "w", encoding="utf-8") as fh:
        json.dump({"reducer": reducer, "points": points}, fh,
                  ensure_ascii=False, separators=(",", ":"))

    # patch stats.json with the cluster summary
    stats_path = os.path.join(HERE, f"{SLUG}_stats.json")
    with open(stats_path, "r", encoding="utf-8") as fh:
        stats = json.load(fh)
    sizes = sorted([c["size_total"] for c in clusters], reverse=True)
    stats["clusters"] = {
        "encoder": EMBED_MODEL,
        "reducer": reducer,
        "n_clusters": len(ids),
        "noise_share_unique": noise_share_unique,
        "noise_share_weighted": noise_share_total,
        "largest_total": sizes[0] if sizes else 0,
        "median_total": int(np.median(sizes)) if sizes else 0,
    }
    with open(stats_path, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, indent=2)

    print("top clusters by volume:")
    for c in clusters[:12]:
        print(f"  [{c['id']:>3}] {c['size_total']:>6,}  {c['label']}")
    print("wrote: clusters.json, scatter.json, patched stats.json")


if __name__ == "__main__":
    main()
