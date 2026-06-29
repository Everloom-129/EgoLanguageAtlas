#!/usr/bin/env python3
"""STAGE 5: render the PH2D / HAT atlas (EN + CN) using the shared atlas_lib.

PH2D's language is a small, coarse set of session-level task descriptions; the
distinctive feature is the human plus humanoid embodiment split, which gets its
own panel. The atlas is honest about the small instruction vocabulary.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import atlas_lib as A  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "ph2d"

stats = json.load(open(os.path.join(HERE, f"{SLUG}_stats.json"), encoding="utf-8"))
cdoc = json.load(open(os.path.join(HERE, f"{SLUG}_clusters.json"), encoding="utf-8"))
scatter = json.load(open(os.path.join(HERE, f"{SLUG}_scatter.json"), encoding="utf-8"))
prov = json.load(open(os.path.join(HERE, "download_provenance.json"), encoding="utf-8"))

CLUSTERS = cdoc["clusters"]
CFG = cdoc["config"]
POINTS = scatter["points"]
ACCESS = prov.get("access_utc", "")[:10]
BUILD = datetime.date.today().isoformat()

REPO = "https://huggingface.co/datasets/RogerQi/PH2D"
ARXIV = "https://arxiv.org/abs/2503.13441"
PROJECT = "https://human-as-robot.github.io/"
LICENSE_URL = "https://opensource.org/license/mit"
EXAMPLE_IMG_URL = "https://human-as-robot.github.io/resources/hat_overview.jpg"
EXAMPLE_URI = A.image_to_data_uri(EXAMPLE_IMG_URL, os.path.join(HERE, ".cache", "example.jpg"))

META = {
    "name": "HAT (Humanoid Policy ~ Human Policy)",
    "usage": ["co-train", "corpus", "hand-pose"],
    "downstream": [],
    "annotation_types": ["task-instruction"],
    "source_datasets": ["PH2D (own egocentric capture)"],
    "links": {"repo": REPO, "paper": ARXIV, "project": PROJECT, "license": LICENSE_URL},
    "license_name": "MIT",
    "citation": "Qiu et al., Humanoid Policy ~ Human Policy, CoRL 2025 (arXiv:2503.13441); "
                "PH2D dataset (RogerQi/PH2D, MIT).",
    "commit": "PH2D main", "access": ACCESS, "build_date": BUILD,
}

WORK_I18N = {
    "en": {
        "page_title": "HAT / PH2D · Ego Language-Annotation Atlas",
        "k_eps": "episodes", "k_sessions": "sessions", "k_unique": "unique descriptions",
        "k_clusters": "clusters", "k_meanlen": "mean length (tokens)",
        "k_human": "human episodes", "k_humanoid": "humanoid episodes", "k_verbs": "verbs",
        "media_caption": "PH2D pairs egocentric human demos with humanoid-robot demos for co-training.",
        "media_credit": "HAT / PH2D, Qiu et al., CoRL 2025 (MIT).",
        "focus": ("An egocentric human plus humanoid demonstration corpus with per-session "
                  "task instructions and 3D hand poses, used to co-train a Human Action "
                  "Transformer."),
        "datapath": ("PH2D records egocentric human demonstrations (Apple Vision Pro and a ZED "
                     "rig) alongside matched humanoid-robot demonstrations, each episode tagged "
                     "with a task description, an embodiment, and 3D hand poses. The task "
                     "description is shared across a session, so the corpus has many episodes "
                     "but a small, coarse instruction vocabulary. This atlas reads the "
                     "description attributes (no video downloaded), clusters the unique "
                     "instructions weighted by episode count, and breaks the corpus down by "
                     "human versus humanoid embodiment."),
        "flow": ["egocentric human + humanoid capture", "per-session task instruction + 3D hand pose",
                 "differentiable human-to-robot retargeting", "co-trained Human Action Transformer"],
        "cited_note": ("PH2D as released here: " + f"{stats['counts']['labelled_segments']:,} "
                       "episodes across " + f"{stats['counts']['sessions']} sessions, "
                       f"{stats['counts']['unique_narrations_clean']} unique task descriptions "
                       f"({stats['counts']['human_episodes']} human, "
                       f"{stats['counts']['humanoid_episodes']} humanoid episodes). The paper "
                       "reports a larger PH2D collection; this atlas measures the public "
                       "HuggingFace release."),
        "small_note": ("Note: PH2D task descriptions are session-level and coarse, so the "
                       "unique instruction set is small (a few dozen). The scatter is "
                       "correspondingly sparse; the embodiment panel below is the more "
                       "informative view."),
        "sec_emb": "Human and humanoid embodiment",
        "emb_help": ("PH2D is Physical Human-Humanoid Data: the same tasks are demonstrated by "
                     "a human and by a humanoid robot, for co-training. Episode counts below "
                     "come from the downloaded session attributes."),
        "emb_dist": "episodes by embodiment class", "emb_raw": "episodes by capture rig",
    },
    "cn": {
        "page_title": "HAT / PH2D · 第一人称语言标注图谱",
        "k_eps": "片段数", "k_sessions": "会话数", "k_unique": "唯一描述",
        "k_clusters": "聚类数", "k_meanlen": "平均长度（token）",
        "k_human": "人类片段", "k_humanoid": "人形机器人片段", "k_verbs": "动词",
        "media_caption": "PH2D 将第一人称人类演示与人形机器人演示配对以协同训练。",
        "media_credit": "HAT / PH2D，Qiu 等，CoRL 2025（MIT）。",
        "focus": ("一个第一人称人类加人形机器人演示语料库，带逐会话任务指令与三维手部"
                  "姿态，用于协同训练人类动作 Transformer。"),
        "datapath": ("PH2D 同时记录第一人称人类演示（Apple Vision Pro 与 ZED 装置）以及配套的"
                     "人形机器人演示，每个片段都带有任务描述、具身类型与三维手部姿态。任务"
                     "描述在一个会话内共享，因此语料片段众多但指令词表小而粗。本图谱读取"
                     "描述属性（不下载视频），对按片段数加权的唯一指令聚类，并按人类与人形"
                     "具身拆分语料。"),
        "flow": ["第一人称人类 + 人形采集", "逐会话任务指令 + 三维手部姿态",
                 "可微的人到机器人重定向", "协同训练的人类动作 Transformer"],
        "cited_note": ("此处发布的 PH2D：" + f"{stats['counts']['labelled_segments']:,} 个片段、"
                       f"{stats['counts']['sessions']} 个会话、"
                       f"{stats['counts']['unique_narrations_clean']} 条唯一任务描述"
                       f"（人类 {stats['counts']['human_episodes']}，"
                       f"人形 {stats['counts']['humanoid_episodes']} 片段）。论文报告了更大的 "
                       "PH2D 合集；本图谱实测公开的 HuggingFace 发布。"),
        "small_note": ("注：PH2D 任务描述是会话级且较粗，唯一指令集较小（数十条）。散点图"
                       "因此较稀疏；下方的具身面板是更有信息量的视图。"),
        "sec_emb": "人类与人形具身",
        "emb_help": ("PH2D 即 Physical Human-Humanoid Data：同一任务由人类和人形机器人分别"
                     "演示，用于协同训练。下方片段数来自下载的会话属性。"),
        "emb_dist": "按具身类别的片段数", "emb_raw": "按采集装置的片段数",
    },
}


def kc_list(t):
    c, ln, cl = stats["counts"], stats["length"], stats["clusters"]
    return [
        (f'{c["labelled_segments"]:,}', t["k_eps"]),
        (f'{c["sessions"]}', t["k_sessions"]),
        (f'{c["unique_narrations_clean"]}', t["k_unique"]),
        (f'{cl["n_clusters"]}', t["k_clusters"]),
        (f'{ln["tokens_mean"]:.1f}', t["k_meanlen"]),
        (f'{c["human_episodes"]:,}', t["k_human"]),
        (f'{c["humanoid_episodes"]:,}', t["k_humanoid"]),
        (f'{c["distinct_verbs"]}', t["k_verbs"]),
    ]


def usage_body(t):
    media = (f'<div class="minihead">{A.esc(t["sec_media"])}</div>'
             + A.media_panel(t, image_uri=EXAMPLE_URI, image_url=EXAMPLE_IMG_URL,
                             page_url=PROJECT, caption=t["media_caption"], credit=t["media_credit"]))
    return (media + f'<p class="prose">{A.esc(t["datapath"])}</p>' + A.flow_diagram(t["flow"])
            + f'<p class="note">{A.esc(t["small_note"])}</p>')


def gran_body(t):
    ln = stats["length"]
    den = stats.get("density", {})
    hist = ln.get("token_hist", [])
    cells = [
        (f'{den.get("episodes_per_session", 0):.0f}', "episodes / session" if t is WORK_I18N["en"] else "每会话片段"),
        (f'{ln["tokens_median"]:.0f}', t["median_len"]),
        (f'{ln["tokens_p90"]:.0f}', t["p90_len"]),
        (f'{ln["tokens_max"]}', t["max_len"]),
    ]
    kc = "".join(f'<div class="kc"><div class="kcv">{v}</div><div class="kcl">{A.esc(l)}</div></div>'
                 for v, l in cells)
    return (
        '<div class="twocol"><div>'
        f'<div class="minihead">{A.esc(t["len_hist"])}</div>'
        f'{A.bar_rows([(str(k), v) for k, v in hist])}'
        '</div><div>'
        f'<div class="kcgrid small">{kc}</div>'
        f'<div class="tierbox"><span class="ck">{A.esc(t["gran_tier"])}:</span> {A.esc(stats["granularity_tier"])}</div>'
        '</div></div>'
    )


def vn_body(t):
    words = [(w, c) for w, c in stats["word_top"]][:24]
    ww = " ".join(f'<span class="word">{A.esc(w)} <i>{c:,}</i></span>' for w, c in words)
    return (
        '<div class="twocol">'
        f'<div><div class="minihead">{A.esc(t["top_verbs"])}</div>{A.bar_rows(stats["verb_top"][:12], color="var(--accent)")}</div>'
        f'<div><div class="minihead">{A.esc(t["top_nouns"])}</div>{A.bar_rows(stats["noun_top"][:14], color="var(--accent2)")}</div>'
        '</div>'
        f'<div class="minihead">{A.esc(t["top_words"])}</div><div class="wordwrap">{ww}</div>'
    )


def emb_body(t):
    ed = [[("human" if k == "human" else "humanoid" if k == "humanoid" else k), v]
          for k, v in stats.get("embodiment_dist", [])]
    return (
        '<div class="twocol">'
        f'<div><div class="minihead">{A.esc(t["emb_dist"])}</div>{A.bar_rows(ed, color="#319795")}</div>'
        f'<div><div class="minihead">{A.esc(t["emb_raw"])}</div>{A.bar_rows(stats.get("embodiment_raw_dist", [])[:8], color="#805ad5")}</div>'
        '</div>'
    )


def cfg_desc():
    uv, uc, hp = CFG["umap_viz"], CFG["umap_cluster"], CFG["hdbscan"]
    return {
        "encoder": CFG["encoder"],
        "reducer_desc": (f'{CFG["reducer"].upper()} viz(2D, n_neighbors={uv["n_neighbors"]}, '
                         f'min_dist={uv["min_dist"]}, {uv["metric"]}), cluster({uc["n_components"]}D)'),
        "cluster_desc": (f'HDBSCAN(min_cluster_size={hp["min_cluster_size"]}, '
                         f'min_samples={hp["min_samples"]}), {cdoc["n_clusters"]} clusters, '
                         f'noise {cdoc["noise_share_weighted"]*100:.1f}%'),
    }


def build(lang):
    t = dict(A.CHROME[lang])
    t.update(WORK_I18N[lang])
    t["other_file"] = f"{SLUG}_atlas{'_cn' if lang == 'en' else ''}.html"
    body = (
        A.header(META, t, kc_list(t))
        + A.sec("01", t["sec_usage"], usage_body(t))
        + A.sec("02", t["sec_scatter"], A.scatter_body(t), t["scatter_help"])
        + A.sec("03", t["sec_clusters"], A.cluster_body(t, CLUSTERS))
        + A.sec("04", t["sec_gran"], gran_body(t))
        + A.sec("05", t["sec_vn"], vn_body(t))
        + A.sec("06", t["sec_emb"], emb_body(t), t["emb_help"])
        + A.sec("07", t["sec_drawer"], A.drawer_body(t), t["drawer_help"])
        + A.footer("08", META, t, cfg_desc())
    )
    data = A.data_scripts(POINTS, CLUSTERS, A.ljs_from(t))
    return A.page(lang, t, body, data)


def main():
    for lang, suffix in (("en", "_atlas"), ("cn", "_atlas_cn")):
        out = os.path.join(HERE, f"{SLUG}{suffix}.html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(build(lang))
        print(f"wrote {out}  ({os.path.getsize(out)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
