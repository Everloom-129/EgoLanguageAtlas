#!/usr/bin/env python3
"""STAGE 5: render the EgoVid-5M atlas (EN + CN) using the shared atlas_lib."""
from __future__ import annotations

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import atlas_lib as A  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "egovid-5m"

stats = json.load(open(os.path.join(HERE, f"{SLUG}_stats.json"), encoding="utf-8"))
cdoc = json.load(open(os.path.join(HERE, f"{SLUG}_clusters.json"), encoding="utf-8"))
scatter = json.load(open(os.path.join(HERE, f"{SLUG}_scatter.json"), encoding="utf-8"))
prov = json.load(open(os.path.join(HERE, "download_provenance.json"), encoding="utf-8"))

CLUSTERS = cdoc["clusters"]
CFG = cdoc["config"]
POINTS = scatter["points"]
COMMIT = prov.get("commit_sha", "")
ACCESS = prov.get("access_utc", "")[:10]
BUILD = datetime.date.today().isoformat()

REPO = "https://huggingface.co/datasets/Jeff-Wang/EgoVid-5M"
ARXIV = "https://arxiv.org/abs/2411.08380"
PROJECT = "https://egovid.github.io/"
LICENSE_URL = "https://www.apache.org/licenses/LICENSE-2.0"
EXAMPLE_IMG_URL = "https://egovid.github.io/static/images/abs.png"
EXAMPLE_VIDEO = "https://egovid.github.io/static/videos/egovid.mp4"
EXAMPLE_URI = A.image_to_data_uri(EXAMPLE_IMG_URL, os.path.join(HERE, ".cache", "example.png"))

SAMPLED = stats["counts"].get("sampled_note", "")

META = {
    "name": "EgoVid-5M",
    "usage": ["world-model", "corpus"],
    "downstream": [],
    "annotation_types": ["clip-narration", "verb-noun-action"],
    "source_datasets": ["Ego4D (EgoVid-5M curation)"],
    "links": {"repo": REPO, "paper": ARXIV, "project": PROJECT, "license": LICENSE_URL},
    "license_name": "apache-2.0 (annotations)",
    "citation": "Wang et al., EgoVid-5M: A Large-Scale Video-Action Dataset for "
                "Egocentric Video Generation, NeurIPS 2025 (arXiv:2411.08380).",
    "commit": COMMIT, "access": ACCESS, "build_date": BUILD,
}

WORK_I18N = {
    "en": {
        "page_title": "EgoVid-5M · Ego Language-Annotation Atlas",
        "k_ann": "clips (rows)", "k_unique": "unique descriptions",
        "k_clusters": "clusters", "k_meanlen": "mean length (tokens)",
        "k_clustered": "clustered sample", "k_verbcls": "source verb classes",
        "k_nouncls": "source noun classes", "k_vocab": "vocabulary (tokens)",
        "media_caption": "EgoVid-5M: text-action driven egocentric video generation.",
        "media_credit": "EgoVid-5M, Wang et al., NeurIPS 2025 (annotations apache-2.0).",
        "focus": ("5 million egocentric clips curated from Ego4D, each paired with a "
                  "VLM-authored high-level action description and a long caption, for "
                  "egocentric video generation."),
        "datapath": ("EgoVid-5M curates about 5 million egocentric clips from Ego4D and "
                     "pairs each with kinematic control signals and machine-authored text: "
                     "a high-level action description summarized by a Qwen LLM and a detailed "
                     "caption from the LLaVA-Video model. This atlas clusters the high-level "
                     "action descriptions. Because the descriptions are almost all distinct, "
                     "the cluster view uses a frequency-capped sample (see note below); the "
                     "full text is openly hosted under apache-2.0."),
        "flow": ["Ego4D clips", "Qwen action description + LLaVA caption",
                 "kinematic control + text", "egocentric video generation"],
        "cited_note": ("Per the paper: 5M curated clips with fine-grained kinematic control "
                       "and high-level text. This atlas measures " + SAMPLED + "."),
        "sampled_banner": SAMPLED,
        "sec_src": "Source action classes (Ego4D)",
        "src_help": ("EgoVid-5M also carries Ego4D-style verb and noun class tags per clip. "
                     "The distributions below are counted over the downloaded text file."),
        "src_verbs": "top source verb classes", "src_nouns": "top source noun classes",
    },
    "cn": {
        "page_title": "EgoVid-5M · 第一人称语言标注图谱",
        "k_ann": "片段（行）", "k_unique": "唯一描述",
        "k_clusters": "聚类数", "k_meanlen": "平均长度（token）",
        "k_clustered": "聚类样本", "k_verbcls": "来源动词类别",
        "k_nouncls": "来源名词类别", "k_vocab": "词表（token）",
        "media_caption": "EgoVid-5M：文本动作驱动的第一人称视频生成。",
        "media_credit": "EgoVid-5M，Wang 等，NeurIPS 2025（标注 apache-2.0）。",
        "focus": ("从 Ego4D 精选的 500 万第一人称片段，每段配有由视觉语言模型生成的"
                  "高层动作描述与长描述，用于第一人称视频生成。"),
        "datapath": ("EgoVid-5M 从 Ego4D 精选约 500 万第一人称片段，并为每段配上运动学"
                     "控制信号与机器生成文本：由 Qwen 大模型概括的高层动作描述，以及由 "
                     "LLaVA-Video 模型生成的详细描述。本图谱对高层动作描述进行聚类。由于"
                     "这些描述几乎彼此不同，聚类视图采用按频次截断的样本（见下方说明）；"
                     "完整文本以 apache-2.0 许可公开托管。"),
        "flow": ["Ego4D 片段", "Qwen 动作描述 + LLaVA 描述",
                 "运动学控制 + 文本", "第一人称视频生成"],
        "cited_note": ("论文数据：500 万精选片段，带细粒度运动学控制与高层文本。"
                       "本图谱实测：" + SAMPLED + "。"),
        "sampled_banner": SAMPLED,
        "sec_src": "来源动作类别（Ego4D）",
        "src_help": ("EgoVid-5M 还为每段携带 Ego4D 风格的动词与名词类别标签。"
                     "下方分布基于下载的文本文件统计。"),
        "src_verbs": "高频来源动词类别", "src_nouns": "高频来源名词类别",
    },
}


def kc_list(t):
    c, ln, cl = stats["counts"], stats["length"], stats["clusters"]
    return [
        (f'{c["labelled_segments"]:,}', t["k_ann"]),
        (f'{c["unique_narrations_clean"]:,}', t["k_unique"]),
        (f'{c["clustered_unique"]:,}', t["k_clustered"]),
        (f'{cl["n_clusters"]}', t["k_clusters"]),
        (f'{ln["tokens_mean"]:.1f}', t["k_meanlen"]),
        (f'{c["vocab_size_tokens"]:,}', t["k_vocab"]),
        (f'{c["distinct_verb_cls"]}', t["k_verbcls"]),
        (f'{c["distinct_noun_cls"]}', t["k_nouncls"]),
    ]


def usage_body(t):
    media = (f'<div class="minihead">{A.esc(t["sec_media"])}</div>'
             + A.media_panel(t, image_uri=EXAMPLE_URI, image_url=EXAMPLE_IMG_URL,
                             video_url=EXAMPLE_VIDEO, page_url=PROJECT,
                             caption=t["media_caption"], credit=t["media_credit"]))
    banner = f'<p class="note">{A.esc(t["sampled_banner"])}</p>'
    return media + f'<p class="prose">{A.esc(t["datapath"])}</p>' + A.flow_diagram(t["flow"]) + banner


def gran_body(t):
    ln = stats["length"]
    hist = ln.get("token_hist", [])
    cells = [
        (f'{ln["tokens_median"]:.0f}', t["median_len"]),
        (f'{ln["tokens_p90"]:.0f}', t["p90_len"]),
        (f'{ln["tokens_max"]}', t["max_len"]),
        (f'{ln["chars_mean"]:.0f}', "mean chars" if t is WORK_I18N["en"] else "平均字符"),
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
        f'<div><div class="minihead">{A.esc(t["top_verbs"])}</div>{A.bar_rows(stats["verb_top"][:18], color="var(--accent)")}</div>'
        f'<div><div class="minihead">{A.esc(t["top_nouns"])}</div>{A.bar_rows(stats["noun_top"][:18], color="var(--accent2)")}</div>'
        '</div>'
        f'<div class="minihead">{A.esc(t["top_words"])}</div><div class="wordwrap">{ww}</div>'
    )


def src_body(t):
    return (
        '<div class="twocol">'
        f'<div><div class="minihead">{A.esc(t["src_verbs"])}</div>{A.bar_rows(stats.get("source_verb_cls_top", [])[:18], color="#38a169")}</div>'
        f'<div><div class="minihead">{A.esc(t["src_nouns"])}</div>{A.bar_rows(stats.get("source_noun_cls_top", [])[:18], color="#805ad5")}</div>'
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
        + A.sec("06", t["sec_src"], src_body(t), t["src_help"])
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
