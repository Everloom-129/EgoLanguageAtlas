#!/usr/bin/env python3
"""STAGE 5: render the OakInk2 atlas (EN + CN) using the shared atlas_lib.

OakInk2-specific panel covers the task hierarchy (complex tasks, primitive
substeps, recipe-style steps) and the bilingual primitive descriptions.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import atlas_lib as A  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "oakink2"

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

REPO = "https://huggingface.co/datasets/kelvin34501/OakInk-v2"
ARXIV = "https://arxiv.org/abs/2403.19417"
PROJECT = "https://oakink.net/v2/"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
EXAMPLE_IMG_URL = "https://oakink.net/img/v2/teaser.png"
EXAMPLE_VIDEO = "https://www.youtube.com/watch?v=u8fV1TWUvdQ"
EXAMPLE_URI = A.image_to_data_uri(EXAMPLE_IMG_URL, os.path.join(HERE, ".cache", "example.png"))

META = {
    "name": "OakInk2",
    "usage": ["corpus", "hand-pose", "affordance"],
    "downstream": [],
    "annotation_types": ["task-instruction", "atomic-substep"],
    "source_datasets": ["OakInk2 (multi-view bimanual capture)"],
    "links": {"repo": REPO, "paper": ARXIV, "project": PROJECT, "license": LICENSE_URL},
    "license_name": "CC BY-SA 4.0",
    "citation": "Zhan et al., OakInk2: A Dataset of Bimanual Hands-Object Manipulation "
                "in Complex Task Completion, CVPR 2024 (arXiv:2403.19417).",
    "commit": COMMIT, "access": ACCESS, "build_date": BUILD,
}

WORK_I18N = {
    "en": {
        "page_title": "OakInk2 · Ego Language-Annotation Atlas",
        "k_ann": "annotations", "k_unique": "unique descriptions",
        "k_clusters": "clusters", "k_meanlen": "mean length (tokens)",
        "k_prim": "primitive substeps", "k_complex": "complex tasks",
        "k_steps": "recipe steps", "k_seq": "sequences",
        "k_verbs": "head verbs", "k_nouns": "head nouns",
        "media_caption": "OakInk2 teaser: bimanual hand-object manipulation in complex tasks.",
        "media_credit": "OakInk2, Zhan et al., CVPR 2024 (CC BY-SA 4.0).",
        "focus": ("Bimanual hand-object manipulation organized as a task hierarchy, with "
                  "complex-task and primitive-substep language descriptions in English and "
                  "Chinese."),
        "datapath": ("OakInk2 captures bimanual hand-object manipulation with a multi-view "
                     "rig and organizes it as a three-level hierarchy: affordance, primitive "
                     "task, and complex task. Each primitive substep carries a natural-language "
                     "description (verified here at 2,841 primitive segments, all with a paired "
                     "Chinese description), and complex tasks add higher-level task instructions. "
                     "This atlas clusters the cleaned primitive plus complex-task descriptions, "
                     "giving a view of the manipulation-program language."),
        "flow": ["multi-view bimanual capture", "affordance / primitive / complex hierarchy",
                 "primitive + complex-task descriptions (EN + ZH)",
                 "hand-object manipulation learning"],
        "cited_note": ("Per the paper: bimanual hand-object manipulation organized as "
                       "affordance, primitive task, and complex task. This atlas measures "
                       "3,833 language segments (1,122 unique cleaned), 2,841 primitive "
                       "substeps, 627 complex tasks, and 1,254 sequences from the downloaded "
                       "HuggingFace release."),
        "sec_hier": "Task hierarchy and bilingual descriptions",
        "hier_help": ("OakInk2 organizes manipulation as a hierarchy. Counts and example "
                      "strings below come from the downloaded annotation files."),
        "by_type": "segments by annotation type", "examples_lbl": "example descriptions",
    },
    "cn": {
        "page_title": "OakInk2 · 第一人称语言标注图谱",
        "k_ann": "标注数", "k_unique": "唯一描述",
        "k_clusters": "聚类数", "k_meanlen": "平均长度（token）",
        "k_prim": "基元子步骤", "k_complex": "复杂任务",
        "k_steps": "食谱步骤", "k_seq": "序列",
        "k_verbs": "头部动词", "k_nouns": "头部名词",
        "media_caption": "OakInk2 预览：复杂任务中的双手手物操作。",
        "media_credit": "OakInk2，Zhan 等，CVPR 2024（CC BY-SA 4.0）。",
        "focus": ("以任务层级组织的双手手物操作数据集，"
                  "提供复杂任务与基元子步骤的中英文语言描述。"),
        "datapath": ("OakInk2 通过多视角采集双手手物操作，并以三级层次组织："
                     "可供性、基元任务与复杂任务。每个基元子步骤都配有自然语言"
                     "描述（本图谱实测为 2,841 个基元片段，且均带有对应的中文描述），"
                     "复杂任务则补充更高层的任务指令。本图谱对清洗后的基元与复杂"
                     "任务描述进行聚类，呈现其操作程序语言。"),
        "flow": ["多视角双手采集", "可供性 / 基元 / 复杂层级",
                 "基元 + 复杂任务描述（中英）", "手物操作学习"],
        "cited_note": ("论文数据：以可供性、基元任务、复杂任务组织的双手手物操作。"
                       "本图谱实测：3,833 条语言片段（唯一清洗后 1,122）、2,841 个基元"
                       "子步骤、627 个复杂任务、1,254 个序列，来自下载的 HuggingFace 发布。"),
        "sec_hier": "任务层级与中英描述",
        "hier_help": ("OakInk2 以层级组织操作。下方计数与示例字符串均来自下载的标注文件。"),
        "by_type": "各标注类型片段数", "examples_lbl": "示例描述",
    },
}


def kc_list(t):
    c, ln, cl = stats["counts"], stats["length"], stats["clusters"]
    return [
        (f'{c["labelled_segments"]:,}', t["k_ann"]),
        (f'{c["unique_narrations_clean"]:,}', t["k_unique"]),
        (f'{cl["n_clusters"]}', t["k_clusters"]),
        (f'{ln["tokens_mean"]:.1f}', t["k_meanlen"]),
        (f'{c["primitive_segments"]:,}', t["k_prim"]),
        (f'{c["complex_tasks"]:,}', t["k_complex"]),
        (f'{c["recipe_steps"]:,}', t["k_steps"]),
        (f'{c["sequences"]:,}', t["k_seq"]),
        (f'{c["distinct_head_verbs"]}', t["k_verbs"]),
        (f'{c["distinct_head_nouns"]}', t["k_nouns"]),
    ]


def usage_body(t):
    media = (f'<div class="minihead">{A.esc(t["sec_media"])}</div>'
             + A.media_panel(t, image_uri=EXAMPLE_URI, image_url=EXAMPLE_IMG_URL,
                             video_url=EXAMPLE_VIDEO, page_url=PROJECT,
                             caption=t["media_caption"], credit=t["media_credit"]))
    return media + f'<p class="prose">{A.esc(t["datapath"])}</p>' + A.flow_diagram(t["flow"])


def gran_body(t):
    ln = stats["length"]
    den = stats.get("density", {})
    hist = ln.get("token_hist", [])
    cells = [
        (f'{den.get("segments_per_video", 0):.1f}', t["per_video"]),
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
    words = [(w, c) for w, c in stats["word_top"]
             if w.lower() not in {"the", "a", "an", "of", "to", "and", "with", "in", "on", "position.", "position"}][:24]
    ww = " ".join(f'<span class="word">{A.esc(w)} <i>{c:,}</i></span>' for w, c in words)
    return (
        '<div class="twocol">'
        f'<div><div class="minihead">{A.esc(t["top_verbs"])}</div>{A.bar_rows([x for x in stats["verb_top"] if x[0] not in ("the","to","a")][:18], color="var(--accent)")}</div>'
        f'<div><div class="minihead">{A.esc(t["top_nouns"])}</div>{A.bar_rows(stats["noun_top"][:18], color="var(--accent2)")}</div>'
        '</div>'
        f'<div><div class="minihead">{A.esc(t["verb_fam"])}</div>{A.bar_rows(stats["verb_category_dist"], color="#38a169")}</div>'
        f'<div class="minihead">{A.esc(t["top_words"])}</div><div class="wordwrap">{ww}</div>'
    )


def hier_body(t):
    c = stats["counts"]
    atd = stats.get("annotation_type_dist", [])
    cells = [
        (f'{c["complex_tasks"]:,}', t["k_complex"]),
        (f'{c["primitive_segments"]:,}', t["k_prim"]),
        (f'{c["recipes"]:,}', "recipes" if t is WORK_I18N["en"] else "食谱"),
        (f'{c["recipe_steps"]:,}', t["k_steps"]),
        (f'{c["primitive_with_chinese"]:,}', "primitives with Chinese" if t is WORK_I18N["en"] else "含中文的基元"),
    ]
    kc = "".join(f'<div class="kc"><div class="kcv">{v}</div><div class="kcl">{A.esc(l)}</div></div>'
                 for v, l in cells)
    # exemplars: medoid texts from a few clusters as example descriptions
    ex = "".join(f'<li><span class="tag">cluster {cl["id"]}</span>{A.esc(cl["medoid_text"])}</li>'
                 for cl in CLUSTERS[:8])
    return (
        f'<div class="kcgrid small">{kc}</div>'
        '<div class="twocol"><div>'
        f'<div class="minihead">{A.esc(t["by_type"])}</div>'
        f'{A.bar_rows(atd, color="#319795")}'
        '</div><div>'
        f'<div class="minihead">{A.esc(t["examples_lbl"])}</div>'
        f'<ul class="exlist">{ex}</ul>'
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
        + A.sec("06", t["sec_hier"], hier_body(t), t["hier_help"])
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
