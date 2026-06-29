#!/usr/bin/env python3
"""STAGE 5: render the EgoVLP / EgoClip atlas (EN + CN) using the shared atlas_lib.

EgoClip is the canonical Ego4D narration corpus (manually written, #C camera-wearer
and #O other-person tags). Adds a panel for the subject split and narration source,
and discloses the frequency-capped clustering sample.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import atlas_lib as A  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "egovlp"

stats = json.load(open(os.path.join(HERE, f"{SLUG}_stats.json"), encoding="utf-8"))
cdoc = json.load(open(os.path.join(HERE, f"{SLUG}_clusters.json"), encoding="utf-8"))
scatter = json.load(open(os.path.join(HERE, f"{SLUG}_scatter.json"), encoding="utf-8"))
prov = json.load(open(os.path.join(HERE, "download_provenance.json"), encoding="utf-8"))

CLUSTERS = cdoc["clusters"]
CFG = cdoc["config"]
POINTS = scatter["points"]
ACCESS = prov.get("access_utc", "")[:10]
BUILD = datetime.date.today().isoformat()
SAMPLED = stats["counts"].get("sampled_note", "")

REPO = "https://github.com/showlab/EgoVLP"
ARXIV = "https://arxiv.org/abs/2206.01670"
PROJECT = "https://qinghonglin.github.io/EgoVLP/"
EGO4D = "https://ego4d-data.org/"
LICENSE_URL = "https://ego4ddataset.com/"

META = {
    "name": "EgoVLP (EgoClip / EgoNCE / EgoMCQ)",
    "usage": ["perception-pretrain", "corpus", "eval-benchmark"],
    "downstream": [],
    "annotation_types": ["clip-narration", "verb-noun-action"],
    "source_datasets": ["Ego4D (filtered by EgoVLP)"],
    "links": {"repo": REPO, "paper": ARXIV, "project": PROJECT, "license": LICENSE_URL},
    "license_name": "Ego4D License (internal use)",
    "citation": "Lin et al., Egocentric Video-Language Pretraining (EgoVLP), NeurIPS 2022 "
                "(arXiv:2206.01670); EgoClip narrations derived from Ego4D.",
    "commit": "egoclip.csv", "access": ACCESS, "build_date": BUILD,
}

WORK_I18N = {
    "en": {
        "page_title": "EgoVLP (EgoClip) · Ego Language-Annotation Atlas",
        "k_ann": "clip-text pairs", "k_unique": "unique narrations",
        "k_clusters": "clusters", "k_meanlen": "mean length (tokens)",
        "k_clustered": "clustered sample", "k_vocab": "vocabulary (tokens)",
        "k_cw": "camera-wearer share", "k_other": "other-person share",
        "media_caption": "EgoClip narrations are filtered from Ego4D egocentric video.",
        "media_credit": "EgoVLP / EgoClip, Lin et al., NeurIPS 2022; narrations from Ego4D.",
        "focus": ("The canonical Ego4D narration corpus: about 3.8 million timestamped "
                  "clip-text pairs filtered for video-language pretraining, with camera-wearer "
                  "and other-person tags."),
        "datapath": ("EgoVLP builds EgoClip by filtering about 3.8 million clip-text pairs from "
                     "the manually written Ego4D narrations, then pretrains a video-language "
                     "model with the EgoNCE objective and evaluates on the EgoMCQ choice "
                     "benchmark. The narrations use Ego4D markup, a camera-wearer tag (#C) or "
                     "other-person tag (#O) followed by a subject pronoun and the action. This "
                     "atlas strips the tags, records the subject, and clusters the cleaned "
                     "narrations. Because they are almost all distinct, the cluster view uses a "
                     "frequency-capped sample (see note below)."),
        "flow": ["Ego4D manual narrations", "filter to ~3.8M clip-text pairs (EgoClip)",
                 "strip #C / #O tags, record subject", "EgoNCE pretraining + EgoMCQ benchmark"],
        "cited_note": ("Per the paper: about 3.8M clip-text pairs (EgoClip) and the EgoMCQ "
                       "benchmark, from Ego4D. This atlas measures " + SAMPLED + "."),
        "sampled_banner": SAMPLED,
        "sec_subj": "Subject and narration source",
        "subj_help": ("Ego4D narrations describe the camera wearer (#C) or another person (#O). "
                      "Counts below are over all clip-text pairs in the downloaded file."),
        "subj_dist": "subject (camera-wearer vs other)", "src_dist": "narration source",
    },
    "cn": {
        "page_title": "EgoVLP (EgoClip) · 第一人称语言标注图谱",
        "k_ann": "片段-文本对", "k_unique": "唯一旁白",
        "k_clusters": "聚类数", "k_meanlen": "平均长度（token）",
        "k_clustered": "聚类样本", "k_vocab": "词表（token）",
        "k_cw": "相机佩戴者占比", "k_other": "他人占比",
        "media_caption": "EgoClip 旁白筛选自 Ego4D 第一人称视频。",
        "media_credit": "EgoVLP / EgoClip，Lin 等，NeurIPS 2022；旁白来自 Ego4D。",
        "focus": ("典型的 Ego4D 旁白语料：约 380 万条带时间戳的片段-文本对，"
                  "为视频-语言预训练筛选，并带有相机佩戴者与他人标记。"),
        "datapath": ("EgoVLP 通过从人工撰写的 Ego4D 旁白中筛选约 380 万条片段-文本对构建 "
                     "EgoClip，随后用 EgoNCE 目标预训练视频-语言模型，并在 EgoMCQ 选择基准上"
                     "评测。旁白采用 Ego4D 标记：相机佩戴者标记（#C）或他人标记（#O），其后"
                     "是主语代词与动作。本图谱去除标记、记录主语，并对清洗后的旁白聚类。由于"
                     "它们几乎彼此不同，聚类视图采用按频次截断的样本（见下方说明）。"),
        "flow": ["Ego4D 人工旁白", "筛选为约 380 万片段-文本对（EgoClip）",
                 "去除 #C / #O 标记并记录主语", "EgoNCE 预训练 + EgoMCQ 基准"],
        "cited_note": ("论文数据：约 380 万片段-文本对（EgoClip）与 EgoMCQ 基准，来自 Ego4D。"
                       "本图谱实测：" + SAMPLED + "。"),
        "sampled_banner": SAMPLED,
        "sec_subj": "主语与旁白来源",
        "subj_help": ("Ego4D 旁白描述相机佩戴者（#C）或他人（#O）。下方计数基于下载文件中"
                      "所有片段-文本对。"),
        "subj_dist": "主语（相机佩戴者 vs 他人）", "src_dist": "旁白来源",
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
        (f'{c["camera_wearer_share"]*100:.0f}%', t["k_cw"]),
        (f'{c["other_person_share"]*100:.0f}%', t["k_other"]),
    ]


def usage_body(t):
    media = (f'<div class="minihead">{A.esc(t["sec_media"])}</div>'
             + A.media_panel(t, image_uri=None, video_url=EGO4D, page_url=PROJECT,
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


def subj_body(t):
    sd = [[("camera wearer" if k == "camera_wearer" else "other person" if k == "other_person" else k), v]
          for k, v in stats.get("subject_dist", [])]
    return (
        '<div class="twocol">'
        f'<div><div class="minihead">{A.esc(t["subj_dist"])}</div>{A.bar_rows(sd, color="#319795")}</div>'
        f'<div><div class="minihead">{A.esc(t["src_dist"])}</div>{A.bar_rows(stats.get("narration_source_dist", [])[:8], color="#805ad5")}</div>'
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
        + A.sec("06", t["sec_subj"], subj_body(t), t["subj_help"])
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
