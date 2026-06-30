#!/usr/bin/env python3
"""STAGE 5: render the EgoSchema atlas (EN + CN) using the shared atlas_lib.

EgoSchema is a long-form VQA benchmark; the clustered unit is the question, the
scatter colors by question type, and a VQA panel shows the type distribution and
example questions with their five options. Example media is link-only.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import atlas_lib as A  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "egoschema"

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

REPO = "https://github.com/egoschema/EgoSchema"
ARXIV = "https://arxiv.org/abs/2308.09126"
PROJECT = "https://egoschema.github.io/"
EGO4D = "https://ego4d-data.org/"
LICENSE_URL = "https://ego4ddataset.com/"
EXAMPLE_VIDEO = "https://www.youtube.com/watch?v=_VVoiSzb5E4"
EXAMPLE_IMG_URL = "https://img.youtube.com/vi/_VVoiSzb5E4/hqdefault.jpg"
EXAMPLE_URI = A.image_to_data_uri(EXAMPLE_IMG_URL, os.path.join(HERE, ".cache", "example.jpg"))

# a few example questions with options, from the parquet
EXAMPLES = []
try:
    import pandas as pd
    _df = pd.read_parquet(os.path.join(HERE, f"{SLUG}_annotations.parquet"),
                          columns=["text", "options", "verb_category"])
    for _, r in _df.head(60).iterrows():
        opts = [o for o in str(r["options"]).split(" ||| ") if o][:5]
        if len(opts) == 5 and len(str(r["text"])) > 40:
            EXAMPLES.append({"q": str(r["text"]), "opts": opts, "type": str(r["verb_category"])})
        if len(EXAMPLES) >= 4:
            break
except Exception:
    EXAMPLES = []

META = {
    "name": "EgoSchema",
    "usage": ["eval-benchmark"],
    "downstream": [],
    "annotation_types": ["vqa"],
    "source_datasets": ["Ego4D (EgoSchema)"],
    "links": {"repo": REPO, "paper": ARXIV, "project": PROJECT, "license": LICENSE_URL},
    "license_name": "Ego4D License (internal use)",
    "citation": "Mangalam et al., EgoSchema: A Diagnostic Benchmark for Very Long-form "
                "Video Language Understanding, NeurIPS 2023 (arXiv:2308.09126).",
    "commit": (COMMIT or "")[:10], "access": ACCESS, "build_date": BUILD,
}

WORK_I18N = {
    "en": {
        "page_title": "EgoSchema · Ego Language-Annotation Atlas",
        "k_q": "questions", "k_unique": "unique questions", "k_clusters": "clusters",
        "k_meanlen": "mean question length", "k_opts": "options total",
        "k_ans": "public answers", "k_types": "question types", "k_vocab": "vocabulary (tokens)",
        "media_caption": "EgoSchema questions are long-form QA over 3-minute Ego4D clips.",
        "media_credit": "EgoSchema, Mangalam et al., NeurIPS 2023; clips from Ego4D.",
        "focus": ("A diagnostic long-form video-QA benchmark: 5,031 multiple-choice questions "
                  "over three-minute Ego4D clips, each requiring a long temporal certificate."),
        "datapath": ("EgoSchema samples three-minute clips from Ego4D and, with an LLM over the "
                     "dense Ego4D narrations followed by human curation, writes 5,031 difficult "
                     "multiple-choice questions with five options each. The questions are "
                     "long-form: answering needs a long temporal certificate, not a single "
                     "frame. This atlas clusters the questions and colors them by question type. "
                     "Correct answers are public for only 500 questions (the rest are held out "
                     "for the leaderboard)."),
        "flow": ["Ego4D 3-minute clips", "LLM over dense narrations + human curation",
                 "5,031 questions, 5 options each", "long-form video-language evaluation"],
        "cited_note": ("Per the paper: 5,031 questions over about 250 hours of 3-minute Ego4D "
                       "clips, answers held out except a 500-question subset. This atlas measures "
                       f"{stats['counts']['questions']:,} questions, "
                       f"{stats['counts']['unique_narrations_clean']:,} unique, "
                       f"{stats['counts']['public_answers']} public answers, "
                       f"{stats['counts']['question_types']} question types."),
        "sec_vqa": "Question types and examples",
        "vqa_help": ("EgoSchema questions are abstract and holistic. Below: the question-type "
                     "mix and a few example questions with their five options, from the "
                     "downloaded benchmark."),
        "qtypes_lbl": "question types", "examples_lbl": "example questions (with options)",
        "vn_verbs": "question types", "vn_nouns": "key terms",
    },
    "cn": {
        "page_title": "EgoSchema · 第一人称语言标注图谱",
        "k_q": "问题数", "k_unique": "唯一问题", "k_clusters": "聚类数",
        "k_meanlen": "问题平均长度", "k_opts": "选项总数",
        "k_ans": "公开答案", "k_types": "问题类型", "k_vocab": "词表（token）",
        "media_caption": "EgoSchema 问题是针对 3 分钟 Ego4D 片段的长程问答。",
        "media_credit": "EgoSchema，Mangalam 等，NeurIPS 2023；片段来自 Ego4D。",
        "focus": ("一个诊断性的长程视频问答基准：针对 3 分钟 Ego4D 片段的 5,031 道"
                  "多项选择题，每题都需要较长的时间凭证才能作答。"),
        "datapath": ("EgoSchema 从 Ego4D 采样 3 分钟片段，借助大模型处理密集的 Ego4D 旁白"
                     "并经人工校订，撰写出 5,031 道高难度多项选择题，每题五个选项。问题是"
                     "长程的：作答需要较长的时间凭证，而非单帧。本图谱对问题进行聚类，并按"
                     "问题类型着色。正确答案仅对 500 题公开（其余用于排行榜）。"),
        "flow": ["Ego4D 3 分钟片段", "大模型处理密集旁白 + 人工校订",
                 "5,031 道题，每题 5 个选项", "长程视频-语言评测"],
        "cited_note": ("论文数据：约 250 小时 3 分钟 Ego4D 片段上的 5,031 道题，除 500 题子集"
                       "外答案保留。本图谱实测："
                       f"{stats['counts']['questions']:,} 道题、"
                       f"{stats['counts']['unique_narrations_clean']:,} 道唯一、"
                       f"{stats['counts']['public_answers']} 个公开答案、"
                       f"{stats['counts']['question_types']} 种问题类型。"),
        "sec_vqa": "问题类型与示例",
        "vqa_help": ("EgoSchema 问题抽象而整体。下方为问题类型分布，以及若干带五个选项的"
                     "示例问题，均来自下载的基准。"),
        "qtypes_lbl": "问题类型", "examples_lbl": "示例问题（含选项）",
        "vn_verbs": "问题类型", "vn_nouns": "关键词",
    },
}


def kc_list(t):
    c, ln, cl = stats["counts"], stats["length"], stats["clusters"]
    return [
        (f'{c["questions"]:,}', t["k_q"]),
        (f'{c["unique_narrations_clean"]:,}', t["k_unique"]),
        (f'{cl["n_clusters"]}', t["k_clusters"]),
        (f'{ln["tokens_mean"]:.0f}', t["k_meanlen"]),
        (f'{c["options_total"]:,}', t["k_opts"]),
        (f'{c["public_answers"]}', t["k_ans"]),
        (f'{c["question_types"]}', t["k_types"]),
        (f'{c["vocab_size_tokens"]:,}', t["k_vocab"]),
    ]


def usage_body(t):
    media = (f'<div class="minihead">{A.esc(t["sec_media"])}</div>'
             + A.media_panel(t, image_uri=EXAMPLE_URI, image_url=EXAMPLE_IMG_URL,
                             video_url=EXAMPLE_VIDEO, page_url=PROJECT,
                             caption=t["media_caption"], credit=t["media_credit"]))
    return media + f'<p class="prose">{A.esc(t["datapath"])}</p>' + A.flow_diagram(t["flow"])


def gran_body(t):
    ln = stats["length"]
    hist = ln.get("token_hist", [])
    cells = [
        (f'{ln["tokens_median"]:.0f}', t["median_len"]),
        (f'{ln["tokens_p90"]:.0f}', t["p90_len"]),
        (f'{ln["tokens_max"]}', t["max_len"]),
        (f'{ln.get("option_tokens_mean", 0):.0f}', "mean option len" if t is WORK_I18N["en"] else "选项平均长度"),
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
        f'<div><div class="minihead">{A.esc(t["vn_verbs"])}</div>{A.bar_rows(stats["verb_top"][:10], color="var(--accent)")}</div>'
        f'<div><div class="minihead">{A.esc(t["vn_nouns"])}</div>{A.bar_rows(stats["noun_top"][:14], color="var(--accent2)")}</div>'
        '</div>'
        f'<div class="minihead">{A.esc(t["top_words"])}</div><div class="wordwrap">{ww}</div>'
    )


def vqa_body(t):
    ex = ""
    for e in EXAMPLES:
        opts = "".join(f'<li>{A.esc(o)}</li>' for o in e["opts"])
        ex += (f'<div class="rmq"><div class="qtag">{A.esc(e["type"])}</div>'
               f'<div class="qtext">{A.esc(e["q"])}</div>'
               f'<ol class="qopts">{opts}</ol></div>')
    return (
        '<div class="twocol"><div>'
        f'<div class="minihead">{A.esc(t["qtypes_lbl"])}</div>'
        f'{A.bar_rows(stats.get("qtype_dist", []), color="#319795")}'
        '</div><div>'
        f'<div class="minihead">{A.esc(t["examples_lbl"])}</div>{ex}'
        '</div></div>'
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


EXTRA_CSS = ("<style>.rmq{border-left:2px solid var(--line);padding:4px 0 4px 9px;margin:7px 0}"
             ".qtag{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--accent)}"
             ".qtext{font-size:12px;margin:2px 0}"
             ".qopts{margin:3px 0 0 16px;padding:0;font-size:11px;color:var(--muted)}"
             ".qopts li{margin:1px 0}</style>")


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
        + A.sec("06", t["sec_vqa"], vqa_body(t), t["vqa_help"])
        + A.sec("07", t["sec_drawer"], A.drawer_body(t), t["drawer_help"])
        + A.footer("08", META, t, cfg_desc())
    )
    data = A.data_scripts(POINTS, CLUSTERS, A.ljs_from(t))
    page = A.page(lang, t, body, data)
    return page.replace("</style>", "</style>" + EXTRA_CSS, 1)


def main():
    for lang, suffix in (("en", "_atlas"), ("cn", "_atlas_cn")):
        out = os.path.join(HERE, f"{SLUG}{suffix}.html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(build(lang))
        print(f"wrote {out}  ({os.path.getsize(out)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
