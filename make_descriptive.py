#!/usr/bin/env python3
"""Render a DESCRIPTIVE atlas entry (no downloadable clusterable corpus).

Used for roadmap works that cannot be a full download+cluster atlas: gated
datasets, no-derivatives licenses, unreleased data, or methods that consume
others' annotations rather than publishing a new one. Produces the same
blueprint, offline, bilingual chrome as a full atlas, minus the cluster scatter,
and an atlas_entry.json (status: descriptive) so the dashboard lists it as a
finished row rather than a planned one.

Usage:
    python make_descriptive.py <slug>/descriptive.json

Spec schema (all strings unless noted); *_cn fields are the Chinese counterparts:
    name, slug, work_type, venue, arxiv, repo, project,
    usage_methods [list], annotation_types [list], source_datasets,
    data_access, downloadable, license, redistribution, suitability,
    focus_en, focus_cn, datapath_en, datapath_cn, flow_en [list], flow_cn [list],
    no_corpus_en, no_corpus_cn, provenance, citation
"""
from __future__ import annotations

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atlas_lib as A  # noqa: E402

BUILD = datetime.date.today().isoformat()

DESC_I18N = {
    "en": {
        "sec_class": "Classification", "sec_access": "Access and license",
        "sec_why": "Why this is a descriptive entry",
        "l_usage": "usage methods", "l_annot": "annotation types",
        "l_source": "source datasets", "l_access": "data access",
        "l_down": "annotations downloadable", "l_redist": "redistribution",
        "l_suit": "atlas suitability", "l_venue": "venue", "l_type": "entry type",
        "descriptive": "descriptive",
    },
    "cn": {
        "sec_class": "分类", "sec_access": "获取与许可",
        "sec_why": "为何为描述性条目",
        "l_usage": "使用方式", "l_annot": "标注类型",
        "l_source": "来源数据集", "l_access": "数据获取",
        "l_down": "标注可下载性", "l_redist": "再分发",
        "l_suit": "图谱适配性", "l_venue": "发表", "l_type": "条目类型",
        "descriptive": "描述性",
    },
}


def kv_panel(pairs):
    rows = "".join(
        f'<div class="bar"><span class="bk" style="width:auto">{A.esc(k)}</span>'
        f'<span class="bv" style="text-align:left;flex:1">{v}</span></div>'
        for k, v in pairs)
    return f'<div class="kvpanel">{rows}</div>'


def build(lang, spec, img_uri=None):
    d = DESC_I18N[lang]
    t = dict(A.CHROME[lang])
    t["focus"] = spec.get(f"focus_{lang}", spec.get("focus_en", ""))
    t["page_title"] = f'{spec["name"]} · {t["tagline"]}'
    t["other_file"] = f'{spec["slug"]}_atlas{"_cn" if lang == "en" else ""}.html'
    t["cited_note"] = ""

    meta = {
        "name": spec["name"],
        "usage": spec.get("usage_methods", []),
        "downstream": [],
        "annotation_types": spec.get("annotation_types", []),
        "source_datasets": [spec.get("source_datasets", "")] if spec.get("source_datasets") else [],
        "links": {"repo": spec.get("repo", ""), "paper": spec.get("arxiv", ""),
                  "project": spec.get("project", ""), "license": spec.get("license_url", "")},
        "license_name": spec.get("license", "n/a"),
        "citation": spec.get("citation", f'{spec["name"]}, {spec.get("venue","")} ({spec.get("arxiv","")})'),
        "commit": "n/a", "access": spec.get("access_date", "2026-06-28"), "build_date": BUILD,
    }
    kc = [
        (A.esc(spec.get("venue", "n/a")), d["l_venue"]),
        (d["descriptive"], d["l_type"]),
        (A.esc(spec.get("downloadable", "n/a")), d["l_down"]),
        (A.esc(spec.get("license", "n/a")), t["src_license"]),
    ]

    flow = spec.get(f"flow_{lang}", spec.get("flow_en", []))
    media = (f'<div class="minihead">{A.esc(t["sec_media"])}</div>'
             + A.media_panel(t, image_uri=img_uri,
                             image_url=spec.get("example_image_url", ""),
                             video_url=spec.get("example_video_url", ""),
                             page_url=spec.get("project", spec.get("example_page_url", "")),
                             caption=spec.get(f"example_caption_{lang}", spec.get("example_caption_en", "")),
                             credit=spec.get("example_credit", "")))
    usage = media + f'<p class="prose">{A.esc(spec.get(f"datapath_{lang}", spec.get("datapath_en","")))}</p>'
    if flow:
        usage += A.flow_diagram(flow)

    classification = kv_panel([
        (d["l_usage"], " ".join(A.chip(u) for u in spec.get("usage_methods", [])) or "n/a"),
        (d["l_annot"], " ".join(A.chip(a, "alt") for a in spec.get("annotation_types", [])) or "n/a"),
        (d["l_source"], A.esc(spec.get("source_datasets", "n/a"))),
        (d["l_suit"], A.esc(spec.get("suitability", "n/a"))),
    ])
    access = kv_panel([
        (d["l_access"], A.esc(spec.get("data_access", "n/a"))),
        (d["l_down"], A.esc(spec.get("downloadable", "n/a"))),
        (t["src_license"], A.esc(spec.get("license", "n/a"))),
        (d["l_redist"], A.esc(spec.get("redistribution", "n/a"))),
    ])
    why = f'<p class="prose">{A.esc(spec.get(f"no_corpus_{lang}", spec.get("no_corpus_en","")))}</p>'

    cfg = {"encoder": "n/a", "reducer_desc": "n/a (descriptive entry)",
           "cluster_desc": "no downloadable clusterable corpus; see access and license"}
    body = (
        A.header(meta, t, kc)
        + A.sec("01", t["sec_usage"], usage)
        + A.sec("02", d["sec_class"], classification)
        + A.sec("03", d["sec_access"], access)
        + A.sec("04", d["sec_why"], why, spec.get("provenance", ""))
        + A.footer("05", meta, t, cfg)
    )
    return A.page(lang, t, body, "")


def main():
    if len(sys.argv) < 2:
        print("usage: python make_descriptive.py <slug>/descriptive.json", file=sys.stderr)
        sys.exit(2)
    spec_path = sys.argv[1]
    spec = json.load(open(spec_path, encoding="utf-8"))
    folder = os.path.dirname(os.path.abspath(spec_path))
    slug = spec["slug"]

    img_uri = None
    if spec.get("example_inline") and spec.get("example_image_url"):
        ext = os.path.splitext(spec["example_image_url"].split("?")[0])[1] or ".img"
        img_uri = A.image_to_data_uri(spec["example_image_url"],
                                      os.path.join(folder, ".cache", "example" + ext))
    for lang, suffix in (("en", "_atlas"), ("cn", "_atlas_cn")):
        out = os.path.join(folder, f"{slug}{suffix}.html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(build(lang, spec, img_uri))

    entry = {
        "name": spec["name"], "slug": slug, "status": "descriptive",
        "work_type": spec.get("work_type", ""),
        "focus": spec.get("focus_en", ""),
        "usage_methods": spec.get("usage_methods", []),
        "annotation_types": spec.get("annotation_types", []),
        "source_datasets": [spec.get("source_datasets", "")] if spec.get("source_datasets") else [],
        "downloadable": spec.get("downloadable", "n/a"),
        "license": spec.get("license", "n/a"),
        "links": {"paper": spec.get("arxiv", ""), "repo": spec.get("repo", ""),
                  "project": spec.get("project", ""),
                  "atlas_en": f"{slug}/{slug}_atlas.html",
                  "atlas_cn": f"{slug}/{slug}_atlas_cn.html"},
    }
    with open(os.path.join(folder, "atlas_entry.json"), "w", encoding="utf-8") as fh:
        json.dump(entry, fh, indent=2, ensure_ascii=False)
    print(f"descriptive entry written: {slug} ({spec['name']})")


if __name__ == "__main__":
    main()
