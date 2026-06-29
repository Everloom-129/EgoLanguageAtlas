#!/usr/bin/env python3
"""Shared rendering library for atlas entries (blueprint style, offline, bilingual).

Each entry's render_<slug>.py imports this, supplies entry metadata, work-specific
i18n, and the work-specific section bodies (usage path, granularity, verbs/nouns,
and any extra panels), and calls the builders here for the parts that are
identical across the collection: header, the annotation-cluster scatter, the
cluster table, the sample browser (drawer), the footer, the inline data scripts,
and the page wrapper.

House style: no em-dashes in any visible text. All CSS/JS is inline; cluster and
scatter data are embedded as JSON and parsed with JSON.parse so each page is a
single offline file.
"""
from __future__ import annotations

import html
import json

# Semantic-family colors (verb categories), restrained palette on light paper.
CATCOLORS = {
    "retrieve": "#2b6cb0", "leave": "#dd6b20", "clean": "#38a169",
    "access": "#805ad5", "split": "#d53f8c", "merge": "#d69e2e",
    "manipulate": "#319795", "monitor": "#718096", "block": "#e53e3e",
    "transition": "#4a5568", "sense": "#3182ce", "distribute": "#2c7a7b",
    "order": "#975a16", "_noise": "#c2cad6",
}


def cat_color(cat):
    return CATCOLORS.get(cat, "#64748b")


def esc(s):
    return html.escape(str(s), quote=True)


def chip(text, cls=""):
    c = f" {cls}" if cls else ""
    return f'<span class="chip{c}">{esc(text)}</span>'


def bar_rows(items, color="var(--accent)", maxn=None):
    if not items:
        return ""
    mx = maxn or max(v for _, v in items) or 1
    out = []
    for name, v in items:
        w = max(1.2, v / mx * 100.0)
        out.append(
            f'<div class="bar"><span class="bk">{esc(name)}</span>'
            f'<span class="bt"><span class="bf" style="width:{w:.1f}%;background:{color}"></span></span>'
            f'<span class="bv">{v:,}</span></div>'
        )
    return "\n".join(out)


def cat_legend_chip(cat):
    return (f'<span class="famchip" style="border-color:{cat_color(cat)};color:{cat_color(cat)}">'
            f'{esc(cat)}</span>')


def flow_diagram(steps):
    boxes = []
    for i, s in enumerate(steps):
        cls = "flowbox down" if i == len(steps) - 1 else "flowbox"
        boxes.append(f'<div class="{cls}">{esc(s)}</div>')
        if i < len(steps) - 1:
            boxes.append('<div class="flowarrow">&rarr;</div>')
    return '<div class="flow">' + "".join(boxes) + "</div>"


def image_to_data_uri(url, cache_path, max_bytes=4_000_000):
    """Download an image once (cache it) and return a data: URI, or None.

    Embedding as a data URI keeps the page offline (no external request at view
    time). Used only where the dataset license permits showing a teaser frame.
    """
    import base64
    import mimetypes
    import os
    import urllib.request
    try:
        if not os.path.exists(cache_path):
            req = urllib.request.Request(url, headers={"User-Agent": "ego-atlas/1.0"})
            data = urllib.request.urlopen(req, timeout=30).read()
            if len(data) > max_bytes:
                return None
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "wb") as fh:
                fh.write(data)
        with open(cache_path, "rb") as fh:
            data = fh.read()
        if not data or len(data) > max_bytes:
            return None
        mime = mimetypes.guess_type(cache_path)[0] or "image/jpeg"
        return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")
    except Exception:
        return None


def media_panel(t, image_uri=None, image_url="", video_url="", page_url="",
                caption="", credit=""):
    """Example egocentric media. Inline image is a data URI (offline). External
    URLs appear only as clickable links, never as auto-loaded <img src=http>."""
    if image_uri:
        img = f'<img class="egomedia" src="{image_uri}" alt="example egocentric frame"/>'
    else:
        img = f'<div class="egomedia ph">{esc(t.get("m_frame", "example"))}</div>'
    links = []
    if image_url:
        links.append(f'<a href="{esc(image_url)}">{esc(t["m_frame"])}</a>')
    if video_url:
        links.append(f'<a href="{esc(video_url)}">{esc(t["m_video"])}</a>')
    if page_url:
        links.append(f'<a href="{esc(page_url)}">{esc(t["m_page"])}</a>')
    cap = f'<div class="mediacap">{esc(caption)}</div>' if caption else ""
    cr = f'<div class="mediacredit">{esc(credit)}</div>' if credit else ""
    return (f'<div class="mediawrap">{img}<div class="mediameta">{cap}'
            f'<div class="medialinks">{" &middot; ".join(links)}</div>{cr}</div></div>')


def sec(num, title, body, sub=""):
    s = f'<p class="subhelp">{esc(sub)}</p>' if sub else ""
    return (f'<section class="card"><h2><span class="snum">{num}</span>{esc(title)}</h2>'
            f'{s}{body}</section>')


def cluster_rows(clusters):
    rows = []
    for c in clusters:
        ex = " &middot; ".join(
            f'{esc(e["text"])} ({e["count"]:,})' for e in c["exemplars"][:4])
        blob = esc((c["label"] + " " + " ".join(e["text"] for e in c["exemplars"])).lower())
        rows.append(
            f'<tr data-id="{c["id"]}" data-size="{c["size_total"]}" '
            f'data-unique="{c["size_unique"]}" data-label="{esc(c["label"].lower())}" '
            f'data-search="{blob}" data-cluster="{c["id"]}">'
            f'<td class="num">{c["id"]}</td><td class="lab">{esc(c["label"])}</td>'
            f'<td>{cat_legend_chip(c["verb_category"])}</td>'
            f'<td class="num">{c["size_total"]:,}</td>'
            f'<td class="num">{c["size_unique"]:,}</td><td class="ex">{ex}</td></tr>'
        )
    return "\n".join(rows)


# ----- shared chrome strings (work-specific strings live in each render) -----
CHROME = {
    "en": {
        "lang_name": "English", "other_name": "中文", "dir": "ltr",
        "tagline": "Ego Language-Annotation Atlas",
        "disclaimer": ("Hand-compiled reference over downloaded data, may contain "
                       "errors. Open an issue to fix it."),
        "usage_methods": "usage methods", "downstream": "downstream",
        "annotation_kinds": "annotation types", "source_datasets": "source datasets",
        "src_repo": "annotations repo", "src_paper": "paper", "src_project": "project page",
        "src_license": "license",
        "sec_usage": "Data-usage path", "sec_scatter": "Annotation clusters",
        "sec_clusters": "Cluster table", "sec_gran": "Granularity and density",
        "sec_vn": "Verbs and nouns", "sec_drawer": "Sample browser",
        "sec_foot": "Provenance and reproducibility",
        "sec_media": "Example egocentric media",
        "m_frame": "example frame", "m_video": "example video", "m_page": "project page",
        "media_help": ("A representative example from the source so you can see the "
                       "egocentric video. Inline frames appear only where the dataset "
                       "license permits; otherwise follow the source links."),
        "scatter_help": ("Each point is one unique cleaned annotation, positioned by "
                         "UMAP over sentence-embeddings and colored by its cluster's verb "
                         "family. Hover for the string, search to highlight, click a "
                         "legend family to toggle it, or click a cluster row below."),
        "search_narr": "search annotations", "reset": "reset",
        "by_family": "color: verb family", "noise": "noise",
        "th_id": "id", "th_label": "label", "th_family": "family",
        "th_ann": "annotations", "th_uniq": "unique", "th_ex": "exemplars",
        "search_clusters": "search clusters", "clear_hl": "clear highlight",
        "hl_prefix": "highlighting cluster:",
        "gran_tier": "granularity tier", "len_hist": "narration length (tokens)",
        "per_hour": "annotations / hour", "per_video": "annotations / video",
        "median_len": "median length", "p90_len": "90th pct length", "max_len": "max length",
        "top_verbs": "top verb classes", "top_nouns": "top noun classes",
        "verb_fam": "verb families", "noun_fam": "noun families", "top_words": "top words",
        "drawer_help": ("Search the real annotation strings (deduplicated, with segment "
                        "frequency). Full text is shown where the dataset license permits "
                        "redistribution with attribution; otherwise short snippets only."),
        "filter_cluster": "filter: cluster", "filter_verb": "filter: verb", "all": "all",
        "th_narr": "annotation", "th_count": "segments", "th_verb": "verb", "th_cluster": "cluster",
        "showing": "showing {n} of {m} matching unique annotations",
        "foot_source": "source", "foot_version": "dataset version",
        "foot_access": "access date", "foot_build": "build date",
        "foot_encoder": "encoder", "foot_reducer": "reducer", "foot_cluster": "clustering",
        "foot_license": "license", "foot_attrib": "attribution", "foot_author": "compiled for",
        "foot_note": ("Every statistic traces to the downloaded annotation files or is "
                      "marked as cited. Cluster labels are auto-derived from head verbs "
                      "and nouns, not hand-written. Unknown values are shown as n/a."),
        "commit": "annotations commit", "cited": "cited",
    },
    "cn": {
        "lang_name": "中文", "other_name": "English", "dir": "ltr",
        "tagline": "第一人称语言标注图谱",
        "disclaimer": ("基于下载数据手工整理的参考资料，可能存在错误。欢迎提交 issue "
                       "修正。"),
        "usage_methods": "使用方式", "downstream": "下游",
        "annotation_kinds": "标注类型", "source_datasets": "来源数据集",
        "src_repo": "标注仓库", "src_paper": "论文", "src_project": "项目主页",
        "src_license": "许可",
        "sec_usage": "数据使用路径", "sec_scatter": "注释聚类",
        "sec_clusters": "聚类明细表", "sec_gran": "粒度与密度",
        "sec_vn": "动词与名词", "sec_drawer": "样本浏览器",
        "sec_foot": "来源与可复现性",
        "sec_media": "第一人称示例媒体",
        "m_frame": "示例帧", "m_video": "示例视频", "m_page": "项目主页",
        "media_help": ("来自来源的代表性示例，便于直观了解第一人称视频。仅在数据集"
                       "许可允许时内嵌帧，否则请点击来源链接。"),
        "scatter_help": ("每个点代表一条唯一的清洗后标注，位置由句向量经 UMAP 降维得到，"
                         "颜色对应其聚类的动词大类。悬停查看字符串，搜索可高亮，点击图例"
                         "大类可切换显隐，或点击下方聚类行。"),
        "search_narr": "搜索标注", "reset": "重置",
        "by_family": "着色：动词大类", "noise": "噪声",
        "th_id": "编号", "th_label": "标签", "th_family": "大类",
        "th_ann": "标注数", "th_uniq": "唯一数", "th_ex": "示例",
        "search_clusters": "搜索聚类", "clear_hl": "清除高亮",
        "hl_prefix": "高亮聚类：",
        "gran_tier": "粒度层级", "len_hist": "标注长度（token）",
        "per_hour": "每小时标注数", "per_video": "每视频标注数",
        "median_len": "长度中位数", "p90_len": "长度 90 分位", "max_len": "最大长度",
        "top_verbs": "高频动词类别", "top_nouns": "高频名词类别",
        "verb_fam": "动词大类", "noun_fam": "名词大类", "top_words": "高频词",
        "drawer_help": ("搜索真实标注字符串（已去重，并标注片段频次）。在数据集许可允许"
                        "署名再分发时显示完整文本，否则仅显示短片段。"),
        "filter_cluster": "筛选：聚类", "filter_verb": "筛选：动词", "all": "全部",
        "th_narr": "标注", "th_count": "片段数", "th_verb": "动词", "th_cluster": "聚类",
        "showing": "显示 {m} 条匹配中的前 {n} 条唯一标注",
        "foot_source": "来源", "foot_version": "数据集版本",
        "foot_access": "获取日期", "foot_build": "构建日期",
        "foot_encoder": "编码器", "foot_reducer": "降维", "foot_cluster": "聚类",
        "foot_license": "许可", "foot_attrib": "署名", "foot_author": "编制于",
        "foot_note": ("每一项统计均可追溯到下载的标注文件或标明引用来源。聚类标签由头部"
                      "动词与名词自动生成，并非人工撰写。未知值显示为 n/a。"),
        "commit": "标注提交", "cited": "引用",
    },
}


def header(meta, t, kc):
    kc_html = "".join(
        f'<div class="kc"><div class="kcv">{v}</div><div class="kcl">{esc(l)}</div></div>'
        for v, l in kc)
    usage = " ".join(chip(u) for u in meta.get("usage", []))
    down = meta.get("downstream", [])
    down_html = (f'<span class="ck">{esc(t["downstream"])}:</span> '
                 + " ".join(chip(u) for u in down)) if down else ""
    at = " ".join(chip(a, "alt") for a in meta.get("annotation_types", []))
    src = " ".join(chip(s) for s in meta.get("source_datasets", []))
    lk = meta.get("links", {})
    links = []
    if lk.get("repo"):
        links.append(f'<a href="{lk["repo"]}">{esc(t["src_repo"])}</a>')
    if lk.get("paper"):
        links.append(f'<a href="{lk["paper"]}">{esc(t["src_paper"])}</a>')
    if lk.get("project"):
        links.append(f'<a href="{lk["project"]}">{esc(t["src_project"])}</a>')
    if lk.get("license"):
        links.append(f'<a href="{lk["license"]}">{esc(t["src_license"])}: {esc(meta.get("license_name",""))}</a>')
    return (
        '<header class="card hero">'
        '<div class="toprow">'
        f'<div class="brand">{esc(t["tagline"])}</div>'
        f'<div class="langtoggle"><a href="{t["other_file"]}">{esc(t["other_name"])}</a></div>'
        '</div>'
        f'<h1>{esc(meta["name"])}</h1>'
        f'<p class="focus">{esc(t["focus"])}</p>'
        f'<div class="tagline-chips"><span class="ck">{esc(t["usage_methods"])}:</span> {usage} {down_html}</div>'
        f'<div class="tagline-chips"><span class="ck">{esc(t["annotation_kinds"])}:</span> {at}</div>'
        f'<div class="tagline-chips"><span class="ck">{esc(t["source_datasets"])}:</span> {src}</div>'
        f'<div class="kcgrid">{kc_html}</div>'
        f'<div class="srcrow">{" &middot; ".join(links)}</div>'
        f'<p class="note">{esc(t["disclaimer"])}</p>'
        '</header>'
    )


def scatter_body(t):
    return (
        '<div class="controls">'
        f'<input id="q-scatter" placeholder="{esc(t["search_narr"])}" />'
        f'<button id="reset-scatter">{esc(t["reset"])}</button>'
        f'<span class="cinfo">{esc(t["by_family"])}</span></div>'
        '<div id="legend" class="legend"></div>'
        '<div class="scatterwrap"><canvas id="scatter"></canvas><div id="tip" class="tip"></div></div>'
        '<div id="hlbar" class="hlbar" style="display:none">'
        f'<span>{esc(t["hl_prefix"])} <b id="hlname"></b></span>'
        f'<button id="hlclear">{esc(t["clear_hl"])}</button></div>'
    )


def cluster_body(t, clusters):
    return (
        f'<div class="controls"><input id="q-clusters" placeholder="{esc(t["search_clusters"])}" /></div>'
        '<div class="tablewrap"><table id="clustertable" class="dtable"><thead><tr>'
        f'<th data-sort="id" class="num">{esc(t["th_id"])}</th>'
        f'<th data-sort="label">{esc(t["th_label"])}</th><th>{esc(t["th_family"])}</th>'
        f'<th data-sort="size" class="num">{esc(t["th_ann"])}</th>'
        f'<th data-sort="unique" class="num">{esc(t["th_uniq"])}</th>'
        f'<th>{esc(t["th_ex"])}</th></tr></thead>'
        f'<tbody>{cluster_rows(clusters)}</tbody></table></div>'
    )


def drawer_body(t):
    return (
        '<div class="controls">'
        f'<input id="q-drawer" placeholder="{esc(t["search_narr"])}" />'
        f'<label>{esc(t["filter_cluster"])} <select id="f-cluster"></select></label>'
        f'<label>{esc(t["filter_verb"])} <select id="f-verb"></select></label></div>'
        '<div id="drawercount" class="cinfo"></div>'
        '<div class="tablewrap tall"><table class="dtable"><thead><tr>'
        f'<th>{esc(t["th_narr"])}</th><th class="num">{esc(t["th_count"])}</th>'
        f'<th>{esc(t["th_verb"])}</th><th>{esc(t["th_cluster"])}</th></tr></thead>'
        '<tbody id="drawerbody"></tbody></table></div>'
    )


def footer(num, meta, t, cfg):
    lk = meta.get("links", {})
    return (
        '<footer class="card foot">'
        f'<h2><span class="snum">{num}</span>{esc(t["sec_foot"])}</h2>'
        '<div class="footgrid">'
        f'<div><span class="fk">{esc(t["foot_source"])}</span> <a href="{lk.get("repo","#")}">{esc(lk.get("repo",""))}</a></div>'
        f'<div><span class="fk">{esc(t["commit"])}</span> {esc(meta.get("commit",""))}</div>'
        f'<div><span class="fk">{esc(t["foot_version"])}</span> {esc(meta["name"])} @ {esc(str(meta.get("commit",""))[:10])}</div>'
        f'<div><span class="fk">{esc(t["foot_access"])}</span> {esc(meta.get("access",""))}</div>'
        f'<div><span class="fk">{esc(t["foot_build"])}</span> {esc(meta.get("build_date",""))}</div>'
        f'<div><span class="fk">{esc(t["foot_encoder"])}</span> {esc(cfg["encoder"])}</div>'
        f'<div><span class="fk">{esc(t["foot_reducer"])}</span> {esc(cfg["reducer_desc"])}</div>'
        f'<div><span class="fk">{esc(t["foot_cluster"])}</span> {esc(cfg["cluster_desc"])}</div>'
        f'<div><span class="fk">{esc(t["foot_license"])}</span> <a href="{lk.get("license","#")}">{esc(meta.get("license_name",""))}</a></div>'
        f'<div><span class="fk">{esc(t["foot_attrib"])}</span> {esc(meta.get("citation",""))}</div>'
        f'<div><span class="fk">{esc(t["foot_author"])}</span> {esc(t["tagline"])}</div>'
        '</div>'
        + (f'<p class="note">{esc(t["cited"])}: {esc(t["cited_note"])}</p>' if t.get("cited_note") else "")
        + f'<p class="note">{esc(t["foot_note"])}</p>'
        '</footer>'
    )


def data_scripts(points, clusters, ljs):
    cmap = {str(c["id"]): {"l": c["label"], "c": c["verb_category"],
                          "n": c["size_total"], "u": c["size_unique"]} for c in clusters}
    pj = json.dumps(points, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    cj = json.dumps(cmap, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    catj = json.dumps(CATCOLORS, ensure_ascii=False)
    lj = json.dumps(ljs, ensure_ascii=False)
    return (
        f'<script type="application/json" id="d-points">{pj}</script>'
        f'<script type="application/json" id="d-cmap">{cj}</script>'
        f'<script type="application/json" id="d-cat">{catj}</script>'
        '<script>'
        "const CATCOLORS=JSON.parse(document.getElementById('d-cat').textContent);"
        "const CMAP=JSON.parse(document.getElementById('d-cmap').textContent);"
        "const POINTS=JSON.parse(document.getElementById('d-points').textContent);"
        f'const L={lj};'
        f'{JS_APP}'
        '</script>'
    )


def ljs_from(t):
    return {"noise": t["noise"], "count": t["th_count"], "verb": t["th_verb"],
            "cluster": t["th_cluster"], "all": t["all"], "showing": t["showing"]}


def page(lang, t, body_html, data_html):
    lang_attr = "zh" if lang == "cn" else "en"
    return (
        f'<!DOCTYPE html>\n<html lang="{lang_attr}" dir="{t["dir"]}">\n<head>'
        '<meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
        f'<title>{esc(t.get("page_title", t["tagline"]))}</title>'
        f'<style>{CSS}</style></head>\n<body><div class="wrap">'
        f'{body_html}</div>{data_html}</body></html>'
    )


CSS = r"""
:root{
  --paper:#e9edf4; --ink:#15233e; --muted:#5d6c87; --line:#c4d0e2;
  --accent:#1f4e9b; --accent2:#b45309; --card:rgba(255,255,255,.80);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  font-family:"JetBrains Mono",ui-monospace,"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
  color:var(--ink); background-color:var(--paper);
  background-image:
    linear-gradient(rgba(110,135,175,.10) 1px,transparent 1px),
    linear-gradient(90deg,rgba(110,135,175,.10) 1px,transparent 1px),
    linear-gradient(rgba(110,135,175,.18) 1px,transparent 1px),
    linear-gradient(90deg,rgba(110,135,175,.18) 1px,transparent 1px);
  background-size:24px 24px,24px 24px,120px 120px,120px 120px;
  font-size:13px; line-height:1.5; -webkit-font-smoothing:antialiased;
}
a{color:var(--accent);text-decoration:none;border-bottom:1px dotted var(--accent)}
a:hover{border-bottom-style:solid}
.wrap{max-width:1080px;margin:0 auto;padding:18px 16px 64px}
.card{background:var(--card);border:1px solid var(--line);padding:16px 18px;margin:14px 0;
  box-shadow:0 1px 0 rgba(21,35,62,.04)}
.hero h1{font-size:30px;letter-spacing:.04em;margin:6px 0 4px}
.toprow{display:flex;justify-content:space-between;align-items:center}
.brand{font-size:11px;text-transform:uppercase;letter-spacing:.22em;color:var(--muted)}
.langtoggle a{font-size:12px}
.focus{color:var(--ink);max-width:74ch;margin:4px 0 12px}
.tagline-chips{margin:6px 0}
.ck{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-right:4px}
.chip{display:inline-block;border:1px solid var(--accent);color:var(--accent);border-radius:11px;
  padding:1px 9px;font-size:11px;margin:2px 3px}
.chip.alt{border-color:var(--accent2);color:var(--accent2)}
.famchip{display:inline-block;border:1px solid;border-radius:9px;padding:0 7px;font-size:11px;white-space:nowrap}
.kcgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:14px 0}
.kcgrid.small{margin:0 0 10px}
.kc{border:1px solid var(--line);background:rgba(255,255,255,.55);padding:8px 10px}
.kcv{font-size:18px;font-weight:700;color:var(--accent);letter-spacing:.02em}
.kcl{font-size:10.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.srcrow{font-size:12px;color:var(--muted);margin-top:6px}
.note{font-size:11px;color:var(--muted);border-left:2px solid var(--line);padding-left:8px;margin:10px 0 0}
section h2,.foot h2{font-size:13px;text-transform:uppercase;letter-spacing:.14em;color:var(--ink);
  border-bottom:1px solid var(--line);padding-bottom:7px;margin:0 0 12px;font-weight:700}
.snum{color:var(--accent);font-weight:700;margin-right:6px}
.subhelp{font-size:12px;color:var(--muted);margin:-4px 0 12px;max-width:78ch}
.prose{max-width:80ch}
.flow{display:flex;flex-wrap:wrap;align-items:stretch;gap:6px;margin:8px 0 2px}
.flowbox{border:1px solid var(--accent);background:rgba(31,78,155,.06);padding:8px 10px;font-size:11.5px;
  display:flex;align-items:center;text-align:center;max-width:200px}
.flowbox.down{border-color:var(--accent2);background:rgba(180,83,9,.07);color:var(--accent2)}
.flowarrow{display:flex;align-items:center;color:var(--muted);font-size:16px}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:6px 0 10px}
input,select,button{font-family:inherit;font-size:12px;color:var(--ink);background:#fff;
  border:1px solid var(--line);padding:5px 8px;border-radius:2px}
input{min-width:200px;flex:0 1 260px}
button{cursor:pointer;background:#f3f6fb}
button:hover{border-color:var(--accent);color:var(--accent)}
label{font-size:11px;color:var(--muted);display:inline-flex;gap:5px;align-items:center}
.cinfo{font-size:11px;color:var(--muted)}
.legend{display:flex;flex-wrap:wrap;gap:4px 12px;margin:2px 0 10px}
.legitem{font-size:11px;cursor:pointer;user-select:none;display:inline-flex;align-items:center;gap:5px}
.legitem.off{opacity:.32;text-decoration:line-through}
.sw{width:10px;height:10px;border-radius:50%;display:inline-block;border:1px solid rgba(0,0,0,.15)}
.scatterwrap{position:relative}
#scatter{width:100%;height:520px;display:block;background:#fbfcfe;border:1px solid var(--line);cursor:crosshair}
.tip{position:fixed;z-index:30;pointer-events:none;display:none;background:var(--ink);color:#eef3fb;
  padding:6px 9px;font-size:11px;max-width:260px;border:1px solid #0c1626;box-shadow:0 3px 10px rgba(0,0,0,.25)}
.hlbar{display:flex;justify-content:space-between;align-items:center;margin-top:8px;font-size:12px;
  background:rgba(31,78,155,.07);border:1px solid var(--line);padding:6px 10px}
.tablewrap{overflow-x:auto;border:1px solid var(--line)}
.tablewrap.tall{max-height:520px;overflow-y:auto}
.dtable{width:100%;border-collapse:collapse;font-size:12px}
.dtable th,.dtable td{border-bottom:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}
.dtable thead th{position:sticky;top:0;background:#eef2f8;cursor:pointer;white-space:nowrap;
  font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.dtable th.num,.dtable td.num{text-align:right;font-variant-numeric:tabular-nums}
.dtable td.lab{font-weight:600}
.dtable td.ex{color:var(--muted);font-size:11px}
#clustertable tbody tr{cursor:pointer}
#clustertable tbody tr:hover{background:rgba(31,78,155,.06)}
#clustertable tbody tr.sel{background:rgba(180,83,9,.12);outline:1px solid var(--accent2)}
.twocol{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.minihead{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin:6px 0 6px}
.bar{display:grid;grid-template-columns:120px 1fr 56px;gap:8px;align-items:center;margin:3px 0}
.bk{font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bt{background:#dde6f2;height:12px;border:1px solid var(--line);position:relative}
.bf{display:block;height:100%}
.bv{font-size:11px;text-align:right;color:var(--muted);font-variant-numeric:tabular-nums}
.tierbox{font-size:12px;margin-top:8px;border:1px dashed var(--line);padding:8px}
.wordwrap{display:flex;flex-wrap:wrap;gap:5px 9px;margin-top:4px}
.word{font-size:12px;border:1px solid var(--line);padding:1px 7px;background:rgba(255,255,255,.5)}
.word i{color:var(--muted);font-style:normal;font-size:10px}
.exlist{margin:6px 0 0;padding:0;list-style:none}
.exlist li{font-size:12px;border-left:2px solid var(--line);padding:3px 0 3px 8px;margin:4px 0}
.exlist .tag{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.05em;margin-right:6px}
.foot .footgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:6px 18px;font-size:11.5px}
.foot .fk{display:inline-block;min-width:120px;color:var(--muted);text-transform:uppercase;
  letter-spacing:.05em;font-size:10px}
.mediawrap{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start;margin:2px 0 6px}
.egomedia{max-width:360px;width:100%;border:1px solid var(--line);background:#fff;display:block}
.egomedia.ph{display:flex;align-items:center;justify-content:center;height:120px;color:var(--muted);font-size:11px}
.mediameta{flex:1;min-width:200px;font-size:12px}
.medialinks{margin:6px 0}
.mediacap{color:var(--ink)}
.mediacredit{color:var(--muted);font-size:11px;margin-top:6px}
.kvpanel .bar{grid-template-columns:170px 1fr;align-items:start}
.kvpanel .bk{width:auto;white-space:normal;color:var(--muted);text-transform:uppercase;font-size:10px;letter-spacing:.05em}
.kvpanel .bv{text-align:left}
@media(max-width:720px){.twocol{grid-template-columns:1fr}#scatter{height:420px}.hero h1{font-size:24px}}
"""

JS_APP = r"""
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function catOf(cid){if(cid<0)return '_noise';const m=CMAP[cid];return m?m.c:'_noise';}
function colorOf(cid){return CATCOLORS[catOf(cid)]||'#64748b';}
let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
for(const p of POINTS){if(p[0]<minX)minX=p[0];if(p[0]>maxX)maxX=p[0];if(p[1]<minY)minY=p[1];if(p[1]>maxY)maxY=p[1];}
{const dx=(maxX-minX)*0.04||1,dy=(maxY-minY)*0.04||1;minX-=dx;maxX+=dx;minY-=dy;maxY+=dy;}
const cv=document.getElementById('scatter');
const ctx=cv.getContext('2d');
const base=document.createElement('canvas');
const bctx=base.getContext('2d');
const px=new Float32Array(POINTS.length), py=new Float32Array(POINTS.length);
let W=0,H=0,DPR=1;
const state={query:'',offCats:new Set(),hlCluster:null};
function layout(){
  DPR=window.devicePixelRatio||1;
  W=cv.clientWidth;H=cv.clientHeight;
  for(const c of [cv,base]){c.width=Math.round(W*DPR);c.height=Math.round(H*DPR);}
  ctx.setTransform(DPR,0,0,DPR,0,0);bctx.setTransform(DPR,0,0,DPR,0,0);
  const m=14;
  for(let i=0;i<POINTS.length;i++){
    px[i]=m+(POINTS[i][0]-minX)/(maxX-minX)*(W-2*m);
    py[i]=H-m-(POINTS[i][1]-minY)/(maxY-minY)*(H-2*m);
  }
  renderBase();blit();
}
function matches(i){
  const p=POINTS[i];
  if(state.query && !p[4].toLowerCase().includes(state.query))return false;
  if(state.offCats.has(catOf(p[2])))return false;
  return true;
}
function renderBase(){
  bctx.clearRect(0,0,W,H);
  const hl=state.hlCluster!==null;
  for(let i=0;i<POINTS.length;i++){
    const ok=matches(i)&&(!hl||POINTS[i][2]===state.hlCluster);
    if(ok)continue;
    bctx.fillStyle='rgba(150,162,182,0.15)';
    bctx.beginPath();bctx.arc(px[i],py[i],1.1,0,6.283);bctx.fill();
  }
  for(let i=0;i<POINTS.length;i++){
    const ok=matches(i)&&(!hl||POINTS[i][2]===state.hlCluster);
    if(!ok)continue;
    bctx.fillStyle=colorOf(POINTS[i][2]);
    bctx.beginPath();bctx.arc(px[i],py[i],hl?2.4:1.7,0,6.283);bctx.fill();
  }
}
function blit(h){
  ctx.clearRect(0,0,W,H);ctx.drawImage(base,0,0,W,H);
  if(h!=null){
    ctx.beginPath();ctx.arc(px[h],py[h],4.5,0,6.283);
    ctx.fillStyle=colorOf(POINTS[h][2]);ctx.fill();
    ctx.lineWidth=1.5;ctx.strokeStyle='#15233e';ctx.stroke();
  }
}
const tip=document.getElementById('tip');
let raf=null,last=null;
cv.addEventListener('mousemove',e=>{const r=cv.getBoundingClientRect();last=[e.clientX-r.left,e.clientY-r.top,e.clientX,e.clientY];if(!raf)raf=requestAnimationFrame(hover);});
cv.addEventListener('mouseleave',()=>{tip.style.display='none';blit();});
function hover(){
  raf=null;if(!last)return;
  const mx=last[0],my=last[1],cx=last[2],cy=last[3];
  const hl=state.hlCluster!==null;let best=-1,bd=64;
  for(let i=0;i<POINTS.length;i++){
    if(hl&&POINTS[i][2]!==state.hlCluster)continue;
    if(!matches(i))continue;
    const dx=px[i]-mx,dy=py[i]-my,d=dx*dx+dy*dy;
    if(d<bd){bd=d;best=i;}
  }
  if(best<0){tip.style.display='none';blit();return;}
  const p=POINTS[best],m=CMAP[p[2]];
  const clab=p[2]<0?L.noise:(m?m.l:'#'+p[2]);
  tip.innerHTML='<b>'+escapeHtml(p[4])+'</b><br>'+escapeHtml(L.count)+': '+p[3].toLocaleString()+
    ' &middot; '+escapeHtml(L.verb)+': '+escapeHtml(p[5])+'<br>'+escapeHtml(L.cluster)+': '+escapeHtml(clab);
  tip.style.display='block';
  let lx=cx+13,ly=cy+13;
  if(lx>window.innerWidth-270)lx=cx-260;
  if(ly>window.innerHeight-70)ly=cy-60;
  tip.style.left=lx+'px';tip.style.top=ly+'px';
  blit(best);
}
(function(){
  const tot={};for(const k in CMAP){const c=CMAP[k];tot[c.c]=(tot[c.c]||0)+c.n;}
  const cats=Object.keys(tot).sort((a,b)=>tot[b]-tot[a]);cats.push('_noise');
  const leg=document.getElementById('legend');
  for(const cat of cats){
    const el=document.createElement('span');el.className='legitem';
    const nm=cat==='_noise'?L.noise:cat;
    el.innerHTML='<span class="sw" style="background:'+(CATCOLORS[cat]||'#64748b')+'"></span>'+escapeHtml(nm);
    el.onclick=()=>{if(state.offCats.has(cat)){state.offCats.delete(cat);el.classList.remove('off');}else{state.offCats.add(cat);el.classList.add('off');}renderBase();blit();};
    leg.appendChild(el);
  }
})();
document.getElementById('q-scatter').addEventListener('input',e=>{state.query=e.target.value.trim().toLowerCase();renderBase();blit();});
document.getElementById('reset-scatter').onclick=()=>{
  state.query='';state.offCats.clear();state.hlCluster=null;
  document.getElementById('q-scatter').value='';
  document.querySelectorAll('.legitem.off').forEach(x=>x.classList.remove('off'));
  document.querySelectorAll('#clustertable tbody tr.sel').forEach(x=>x.classList.remove('sel'));
  document.getElementById('hlbar').style.display='none';
  renderBase();blit();
};
const tbody=document.querySelector('#clustertable tbody');
function highlightCluster(cid,label,tr){
  state.hlCluster=cid;
  document.getElementById('hlname').textContent=label;
  document.getElementById('hlbar').style.display='flex';
  document.querySelectorAll('#clustertable tbody tr.sel').forEach(x=>x.classList.remove('sel'));
  if(tr)tr.classList.add('sel');
  renderBase();blit();
  cv.scrollIntoView({behavior:'smooth',block:'center'});
}
tbody.querySelectorAll('tr').forEach(tr=>{
  tr.addEventListener('click',()=>highlightCluster(parseInt(tr.dataset.cluster,10),tr.querySelector('.lab').textContent,tr));
});
document.getElementById('hlclear').onclick=()=>{
  state.hlCluster=null;document.getElementById('hlbar').style.display='none';
  document.querySelectorAll('#clustertable tbody tr.sel').forEach(x=>x.classList.remove('sel'));
  renderBase();blit();
};
let sortKey='size',sortDir=-1;
document.querySelectorAll('#clustertable th[data-sort]').forEach(th=>{
  th.addEventListener('click',()=>{const k=th.dataset.sort;if(k===sortKey)sortDir=-sortDir;else{sortKey=k;sortDir=(k==='label'?1:-1);}sortRows();});
});
function sortRows(){
  const rows=[...tbody.querySelectorAll('tr')];
  rows.sort((a,b)=>{
    if(sortKey==='label'){const x=a.dataset.label,y=b.dataset.label;return x<y?-sortDir:x>y?sortDir:0;}
    return (parseFloat(a.dataset[sortKey])-parseFloat(b.dataset[sortKey]))*sortDir;
  });
  rows.forEach(r=>tbody.appendChild(r));
}
document.getElementById('q-clusters').addEventListener('input',e=>{
  const q=e.target.value.trim().toLowerCase();
  tbody.querySelectorAll('tr').forEach(tr=>{tr.style.display=(!q||tr.dataset.search.includes(q))?'':'none';});
});
const CAP=400;
const dq=document.getElementById('q-drawer'),dcl=document.getElementById('f-cluster'),dvb=document.getElementById('f-verb');
const dbody=document.getElementById('drawerbody'),dcount=document.getElementById('drawercount');
(function(){
  const arr=Object.keys(CMAP).map(k=>[k,CMAP[k]]).sort((a,b)=>b[1].n-a[1].n);
  let h='<option value="all">'+escapeHtml(L.all)+'</option>';
  for(const kv of arr)h+='<option value="'+kv[0]+'">'+escapeHtml(kv[1].l+' ('+kv[1].n.toLocaleString()+')')+'</option>';
  h+='<option value="noise">'+escapeHtml(L.noise)+'</option>';
  dcl.innerHTML=h;
  const s=new Set();for(const p of POINTS)s.add(p[5]);
  dvb.innerHTML='<option value="all">'+escapeHtml(L.all)+'</option>'+[...s].sort().map(v=>'<option value="'+escapeHtml(v)+'">'+escapeHtml(v)+'</option>').join('');
  dcl.value='all';dvb.value='all';
})();
function drawer(){
  const q=(dq.value||'').trim().toLowerCase(),fc=dcl.value,fv=dvb.value,out=[];
  for(const p of POINTS){
    if(q&&!p[4].toLowerCase().includes(q))continue;
    if(fv!=='all'&&p[5]!==fv)continue;
    if(fc!=='all'){if(fc==='noise'){if(p[2]>=0)continue;}else if(String(p[2])!==fc)continue;}
    out.push(p);
  }
  out.sort((a,b)=>b[3]-a[3]);
  const shown=out.slice(0,CAP);let h='';
  for(const p of shown){const m=CMAP[p[2]],cl=p[2]<0?L.noise:(m?m.l:'#'+p[2]);
    h+='<tr><td class="lab">'+escapeHtml(p[4])+'</td><td class="num">'+p[3].toLocaleString()+'</td><td>'+escapeHtml(p[5])+'</td><td class="ex">'+escapeHtml(cl)+'</td></tr>';}
  dbody.innerHTML=h;
  dcount.textContent=L.showing.replace('{n}',shown.length.toLocaleString()).replace('{m}',out.length.toLocaleString());
}
[dq,dcl,dvb].forEach(el=>el.addEventListener('input',drawer));
layout();sortRows();drawer();
let rt=null;window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(layout,150);});
"""
