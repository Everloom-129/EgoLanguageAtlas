#!/usr/bin/env python3
"""STAGE 5: render the HD-EPIC atlas (EN + CN) using the shared atlas_lib.

Adds an HD-EPIC specific panel for the recipe-step (task-instruction) and
VQA-benchmark annotation streams, on top of the shared chrome.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import atlas_lib as A  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "hd-epic"

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

REPO = "https://github.com/hd-epic/hd-epic-annotations"
ARXIV = "https://arxiv.org/abs/2502.04144"
PROJECT = "https://hd-epic.github.io/"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
EXAMPLE_IMG_URL = "https://hd-epic.github.io/static/media/hd_epic_poster.png"
EXAMPLE_VIDEO = "https://hd-epic.github.io/static/media/videos/epic_kitchens_videowall.mp4"
EXAMPLE_URI = A.image_to_data_uri(EXAMPLE_IMG_URL, os.path.join(HERE, ".cache", "example.png"))

META = {
    "name": "HD-EPIC",
    "usage": ["corpus", "eval-benchmark"],
    "downstream": [],
    "annotation_types": ["clip-narration", "verb-noun-action", "task-instruction",
                         "vqa", "dense-multi-aspect"],
    "source_datasets": ["EPIC-KITCHENS protocol (9 kitchens)"],
    "links": {"repo": REPO, "paper": ARXIV, "project": PROJECT, "license": LICENSE_URL},
    "license_name": "CC BY 4.0",
    "citation": "HD-EPIC: A Highly-Detailed Egocentric Video Dataset, CVPR 2025 "
                "(arXiv:2502.04144), University of Bristol EPIC team.",
    "commit": COMMIT, "access": ACCESS, "build_date": BUILD,
}

WORK_I18N = {
    "en": {
        "page_title": "HD-EPIC · Ego Language-Annotation Atlas",
        "k_ann": "annotations", "k_unique": "unique narrations",
        "k_clusters": "clusters", "k_meanlen": "mean length (tokens)",
        "k_hours": "hours (measured)", "k_verbcls": "verb classes",
        "k_nouncls": "noun classes", "k_videos": "videos", "k_participants": "participants",
        "media_caption": "HD-EPIC teaser: egocentric multi-day kitchen recording.",
        "media_credit": "HD-EPIC, University of Bristol (CC BY 4.0).",
        "focus": ("41 hours of unscripted egocentric cooking across 9 kitchens, with "
                  "highly-detailed full-sentence narrations, recipe steps, and a 26,550 "
                  "question VQA benchmark."),
        "datapath": ("HD-EPIC records 41 hours of unscripted egocentric cooking in 9 "
                     "kitchens, verified here at 41.2 hours across 156 videos. Each action "
                     "is narrated as a full descriptive sentence and parsed into multiple "
                     "verbs, nouns, hands, and a salient main action. The 59,454 narration "
                     "segments sit alongside 69 recipes with step instructions and a 26,550 "
                     "question VQA benchmark over 7 categories, giving a dense, multi-aspect "
                     "language layer for fine-grained understanding and evaluation."),
        "flow": ["raw egocentric video", "full-sentence narration",
                 "verbs + nouns + hands + main action",
                 "recipe steps + VQA benchmark", "fine-grained understanding and evaluation"],
        "cited_note": ("Per the paper: 9 kitchens, 41 hours, about 26,650 VQA questions. "
                       "This atlas measures 41.2 hours across 156 videos, 59,454 narration "
                       "segments (52,645 unique), 9 participants, and 26,550 VQA questions "
                       "across 7 categories and 30 tasks from the downloaded files."),
        "multiverb": "segments naming >1 verb",
        "sec_vqa": "VQA benchmark and recipes",
        "vqa_help": ("HD-EPIC ships a VQA benchmark and recipe-step instructions alongside "
                     "the narrations. Counts and example strings below come from the "
                     "downloaded annotation files."),
        "vqa_total": "VQA questions", "vqa_cats": "VQA categories", "vqa_tasks": "VQA tasks",
        "recipes_lbl": "recipes", "steps_lbl": "recipe steps",
        "vqa_by_cat": "questions by category", "vqa_examples": "example VQA questions",
        "recipe_examples": "example recipe steps (task instructions)",
    },
    "cn": {
        "page_title": "HD-EPIC · 第一人称语言标注图谱",
        "k_ann": "标注数", "k_unique": "唯一旁白",
        "k_clusters": "聚类数", "k_meanlen": "平均长度 (token)",
        "k_hours": "时长 (实测)", "k_verbcls": "动词类别",
        "k_nouncls": "名词类别", "k_videos": "视频", "k_participants": "参与者",
        "media_caption": "HD-EPIC 预览：第一人称多日厨房录制。",
        "media_credit": "HD-EPIC，布里斯托大学（CC BY 4.0）。",
        "focus": ("41 小时跨 9 个厨房的无脚本第一人称烹饪视频，"
                  "配有高度详细的整句旁白、食谱步骤，"
                  "以及一个 26,550 题的 VQA 基准。"),
        "datapath": ("HD-EPIC 记录了 9 个厨房、共 41 小时的无脚本"
                     "第一人称烹饪活动，本图谱依据下载的时间戳"
                     "核实为 156 段视频、共 41.2 小时。每个动作以一句"
                     "完整描述性旁白标注，并解析出多个动词、"
                     "名词、手部以及主要动作。这 59,454 个旁白片段"
                     "还伴有 69 个带步骤说明的食谱和一个跨 7 类的 "
                     "26,550 题 VQA 基准，提供了用于细粒度理解与评测的"
                     "稠密多面语言层。"),
        "flow": ["第一人称原始视频", "整句旁白",
                 "动词 + 名词 + 手部 + 主要动作",
                 "食谱步骤 + VQA 基准", "细粒度理解与评测"],
        "cited_note": ("论文数据：9 个厨房、41 小时、约 26,650 题 VQA。"
                       "本图谱实测：41.2 小时、156 段视频、59,454 个旁白"
                       "片段（唯一 52,645）、9 名参与者，以及跨 7 类、"
                       "30 项任务的 26,550 题 VQA。"),
        "multiverb": "含多个动词的片段",
        "sec_vqa": "VQA 基准与食谱",
        "vqa_help": ("HD-EPIC 在旁白之外还提供了 VQA 基准和食谱步骤"
                     "说明。下方的计数与示例字符串均来自下载的"
                     "标注文件。"),
        "vqa_total": "VQA 题数", "vqa_cats": "VQA 类别", "vqa_tasks": "VQA 任务",
        "recipes_lbl": "食谱", "steps_lbl": "食谱步骤",
        "vqa_by_cat": "各类问题数", "vqa_examples": "VQA 示例问题",
        "recipe_examples": "食谱步骤示例（任务指令）",
    },
}


def kc_list(t):
    c, ln, hr, den, cl = (stats["counts"], stats["length"], stats["hours"],
                          stats["density"], stats["clusters"])
    return [
        (f'{c["labelled_segments"]:,}', t["k_ann"]),
        (f'{c["unique_narrations_clean"]:,}', t["k_unique"]),
        (f'{cl["n_clusters"]}', t["k_clusters"]),
        (f'{ln["tokens_mean"]:.1f}', t["k_meanlen"]),
        (f'{c["vqa_questions"]:,}', t["vqa_total"]),
        (f'{c["recipe_steps"]:,}', t["steps_lbl"]),
        (f'{hr["annotated_span_hours"]:.1f}', t["k_hours"]),
        (f'{den["segments_per_hour_cited"]:,.0f}', t["per_hour"]),
        (f'{c["verb_classes"]}', t["k_verbcls"]),
        (f'{c["noun_classes"]}', t["k_nouncls"]),
        (f'{c["videos"]}', t["k_videos"]),
        (f'{c["participants"]}', t["k_participants"]),
    ]


def exlist(items, tag_key, text_key):
    lis = "".join(
        f'<li><span class="tag">{A.esc(it[tag_key])}</span>{A.esc(it[text_key])}</li>'
        for it in items)
    return f'<ul class="exlist">{lis}</ul>'


def usage_body(t):
    media = (f'<div class="minihead">{A.esc(t["sec_media"])}</div>'
             + A.media_panel(t, image_uri=EXAMPLE_URI, image_url=EXAMPLE_IMG_URL,
                             video_url=EXAMPLE_VIDEO, page_url=PROJECT,
                             caption=t["media_caption"], credit=t["media_credit"]))
    return media + f'<p class="prose">{A.esc(t["datapath"])}</p>' + A.flow_diagram(t["flow"])


def gran_body(t):
    ln, den = stats["length"], stats["density"]
    hist = ln["token_hist"]
    cells = [
        (f'{den["segments_per_hour_cited"]:,.0f}', t["per_hour"]),
        (f'{den["segments_per_video"]:,.0f}', t["per_video"]),
        (f'{ln["tokens_median"]:.0f}', t["median_len"]),
        (f'{ln["tokens_p90"]:.0f}', t["p90_len"]),
        (f'{ln["tokens_max"]}', t["max_len"]),
        (f'{ln["multi_verb_share"]*100:.1f}%', t["multiverb"]),
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
        '</div><div class="twocol">'
        f'<div><div class="minihead">{A.esc(t["verb_fam"])}</div>{A.bar_rows(stats["verb_category_dist"], color="#38a169")}</div>'
        f'<div><div class="minihead">{A.esc(t["noun_fam"])}</div>{A.bar_rows(stats["noun_category_dist"][:14], color="#805ad5")}</div>'
        '</div>'
        f'<div class="minihead">{A.esc(t["top_words"])}</div><div class="wordwrap">{ww}</div>'
    )


def vqa_body(t):
    vqa, rec = stats["vqa"], stats["recipes"]
    cells = [
        (f'{vqa["total"]:,}', t["vqa_total"]),
        (f'{vqa["n_categories"]}', t["vqa_cats"]),
        (f'{vqa["n_tasks"]}', t["vqa_tasks"]),
        (f'{rec["n_recipes"]}', t["recipes_lbl"]),
        (f'{rec["n_steps"]:,}', t["steps_lbl"]),
    ]
    kc = "".join(f'<div class="kc"><div class="kcv">{v}</div><div class="kcl">{A.esc(l)}</div></div>'
                 for v, l in cells)
    return (
        f'<div class="kcgrid small">{kc}</div>'
        '<div class="twocol"><div>'
        f'<div class="minihead">{A.esc(t["vqa_by_cat"])}</div>'
        f'{A.bar_rows(vqa["by_category"], color="#319795")}'
        '</div><div>'
        f'<div class="minihead">{A.esc(t["recipe_examples"])}</div>'
        f'{exlist(rec["examples"], "recipe", "step")}'
        '</div></div>'
        f'<div class="minihead">{A.esc(t["vqa_examples"])}</div>'
        f'{exlist(vqa["examples"], "task", "question")}'
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
        + A.sec("06", t["sec_vqa"], vqa_body(t), t["vqa_help"])
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
