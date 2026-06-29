#!/usr/bin/env python3
"""STAGE 5: render the EPIC-KITCHENS-100 atlas (EN + CN) using shared atlas_lib.

Produces two single-file, offline, blueprint-style pages. Work-specific bodies
(usage path, granularity, verbs/nouns) are built here; the shared chrome (header,
scatter, cluster table, sample browser, footer, CSS/JS) comes from atlas_lib.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import atlas_lib as A  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "epic-kitchens-100"

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

REPO = "https://github.com/epic-kitchens/epic-kitchens-100-annotations"
ARXIV = "https://arxiv.org/abs/2006.13256"
PROJECT = "https://epic-kitchens.github.io/"
LICENSE_URL = "https://creativecommons.org/licenses/by-nc/4.0/"
EXAMPLE_VIDEO = "https://www.youtube.com/watch?v=8IzkrWAfAGg"
EXAMPLE_IMG_URL = "https://img.youtube.com/vi/8IzkrWAfAGg/hqdefault.jpg"
EXAMPLE_URI = A.image_to_data_uri(EXAMPLE_IMG_URL, os.path.join(HERE, ".cache", "example.jpg"))

META = {
    "name": "EPIC-KITCHENS-100",
    "usage": ["corpus", "eval-benchmark"],
    "downstream": ["perception-pretrain"],
    "annotation_types": ["verb-noun-action", "clip-narration"],
    "source_datasets": ["EPIC-KITCHENS (55 to 100)"],
    "links": {"repo": REPO, "paper": ARXIV, "project": PROJECT, "license": LICENSE_URL},
    "license_name": "CC BY-NC 4.0",
    "citation": "Damen et al., Rescaling Egocentric Vision, IJCV 2022 (arXiv:2006.13256).",
    "commit": COMMIT, "access": ACCESS, "build_date": BUILD,
}

WORK_I18N = {
    "en": {
        "page_title": "EPIC-KITCHENS-100 · Ego Language-Annotation Atlas",
        "k_ann": "annotations (with text)", "k_total": "segments incl. test",
        "k_unique": "unique narrations", "k_clusters": "clusters",
        "k_hours": "hours (measured)", "k_verbs": "verb classes", "k_nouns": "noun classes",
        "k_vocab": "vocabulary (tokens)", "k_participants": "participants (train+val)",
        "k_videos": "videos (labelled / total)", "k_meanlen": "mean length (tokens)",
        "media_caption": "EPIC-KITCHENS-100 trailer frame: unscripted egocentric cooking.",
        "media_credit": "EPIC-KITCHENS, University of Bristol (CC BY-NC 4.0).",
        "multinoun": "segments naming >1 noun",
        "focus": ("100 hours of unscripted egocentric kitchen activity, densely "
                  "annotated as verb plus noun action segments parsed from participant "
                  "narrations."),
        "datapath": ("EPIC-KITCHENS-100 records 100 hours of unscripted egocentric "
                     "kitchen activity, verified here at 100.03 hours across 700 videos. "
                     "After recording, participants narrate their own actions in free "
                     "form, and each narration is parsed into a verb plus noun action "
                     "segment with start and stop times. The 89,977 resulting segments, "
                     "76,885 of them carrying released narration text, define the "
                     "dataset's recognition, detection, anticipation and retrieval "
                     "benchmarks, and the corpus is widely reused as supervision for "
                     "egocentric perception pretraining."),
        "flow": ["raw egocentric video", "free-form narration",
                 "verb + noun + timestamps",
                 "recognition / detection / anticipation / retrieval",
                 "downstream: perception pretraining"],
        "cited_note": ("Per the paper: 45 kitchens, about 20M frames, 90k action "
                       "segments. This atlas measures 100.03 hours, 700 videos, 76,885 "
                       "labelled segments, 34 participants in the released train and "
                       "validation splits."),
    },
    "cn": {
        "page_title": "EPIC-KITCHENS-100 · 第一人称语言标注图谱",
        "k_ann": "标注数（含文本）", "k_total": "片段数（含测试集）",
        "k_unique": "唯一旁白数", "k_clusters": "聚类数",
        "k_hours": "时长（实测）", "k_verbs": "动词类别", "k_nouns": "名词类别",
        "k_vocab": "词表（token）", "k_participants": "参与者（训练+验证）",
        "k_videos": "视频（标注 / 总数）", "k_meanlen": "平均长度（token）",
        "media_caption": "EPIC-KITCHENS-100 预告片画面：无脚本第一人称烹饪。",
        "media_credit": "EPIC-KITCHENS，布里斯托大学（CC BY-NC 4.0）。",
        "multinoun": "含多个名词的片段",
        "focus": ("100 小时无脚本第一人称厨房活动，由参与者旁白解析为动词加名词的动作"
                  "片段并密集标注。"),
        "datapath": ("EPIC-KITCHENS-100 记录了 100 小时无脚本的第一人称厨房活动，本图谱"
                     "依据下载的元数据核实为 700 段视频、共 100.03 小时。录制后，参与者以"
                     "自由文本形式为自己的动作配上旁白，每条旁白被解析为带起止时间的动词"
                     "加名词动作片段。由此得到 89,977 个片段（其中 76,885 个附带公开的"
                     "旁白文本），定义了该数据集的识别、检测、预测与检索基准，并被广泛"
                     "用作第一人称感知预训练的监督来源。"),
        "flow": ["第一人称原始视频", "自由文本旁白", "动词 + 名词 + 时间戳",
                 "识别 / 检测 / 预测 / 检索", "下游：感知预训练"],
        "cited_note": ("论文数据：45 个厨房、约 2000 万帧、9 万动作片段。本图谱实测："
                       "100.03 小时、700 段视频、76,885 个已标注片段、训练与验证集中 "
                       "34 名参与者。"),
    },
}


def kc_list(t):
    c, ln, hr, den, cl = (stats["counts"], stats["length"], stats["hours"],
                          stats["density"], stats["clusters"])
    return [
        (f'{c["labelled_segments"]:,}', t["k_ann"]),
        (f'{c["total_segments_incl_test"]:,}', t["k_total"]),
        (f'{c["unique_narrations_clean"]:,}', t["k_unique"]),
        (f'{cl["n_clusters"]}', t["k_clusters"]),
        (f'{den["segments_per_hour_labelled"]:,.0f}', t["per_hour"]),
        (f'{hr["total_hours_all_videos"]:.2f}', t["k_hours"]),
        ('97', t["k_verbs"]),
        ('300', t["k_nouns"]),
        (f'{c["vocab_size_tokens"]:,}', t["k_vocab"]),
        (f'{c["participants"]}', t["k_participants"]),
        (f'{c["videos_labelled"]} / {c["videos_total"]}', t["k_videos"]),
        (f'{ln["tokens_mean"]:.2f}', t["k_meanlen"]),
    ]


def usage_body(t):
    media = (f'<div class="minihead">{A.esc(t["sec_media"])}</div>'
             + A.media_panel(t, image_uri=EXAMPLE_URI, video_url=EXAMPLE_VIDEO,
                             page_url=PROJECT, caption=t["media_caption"], credit=t["media_credit"]))
    return media + f'<p class="prose">{A.esc(t["datapath"])}</p>' + A.flow_diagram(t["flow"])


def gran_body(t):
    ln, den = stats["length"], stats["density"]
    hist = ln["token_hist"]
    cells = [
        (f'{den["segments_per_hour_labelled"]:,.0f}', t["per_hour"]),
        (f'{den["segments_per_labelled_video"]:,.0f}', t["per_video"]),
        (f'{ln["tokens_median"]:.0f}', t["median_len"]),
        (f'{ln["tokens_p90"]:.0f}', t["p90_len"]),
        (f'{ln["tokens_max"]}', t["max_len"]),
        (f'{ln["multi_noun_share"]*100:.1f}%', t["multinoun"]),
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
    words = [(w, c) for w, c in stats["word_top"] if w not in {"the", "a", "an", "of", "to"}][:24]
    ww = " ".join(f'<span class="word">{A.esc(w)} <i>{c:,}</i></span>' for w, c in words)
    return (
        '<div class="twocol">'
        f'<div><div class="minihead">{A.esc(t["top_verbs"])}</div>{A.bar_rows(stats["verb_top"][:18], color="var(--accent)")}</div>'
        f'<div><div class="minihead">{A.esc(t["top_nouns"])}</div>{A.bar_rows(stats["noun_top"][:18], color="var(--accent2)")}</div>'
        '</div><div class="twocol">'
        f'<div><div class="minihead">{A.esc(t["verb_fam"])}</div>{A.bar_rows(stats["verb_category_dist"], color="#38a169")}</div>'
        f'<div><div class="minihead">{A.esc(t["noun_fam"])}</div>{A.bar_rows(stats["noun_category_dist"][:14], color="#805ad5")}</div>'
        '</div>'
        f'<div class="minihead">{A.esc(t["top_words"])}</div><div class="wordwrap">{ww}</div>'
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
        + A.sec("06", t["sec_drawer"], A.drawer_body(t), t["drawer_help"])
        + A.footer("07", META, t, cfg_desc())
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
