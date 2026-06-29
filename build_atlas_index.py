#!/usr/bin/env python3
"""Regenerate the collection landing page (index.html) and the README survey
table + roadmap from per-entry manifests. Keeps the dashboard from desyncing:
run this whenever an atlas is added or rebuilt.

Inputs:
  */atlas_entry.json   one per work (status: built | planned), counts pulled
                       from each built entry's stats_file
  roadmap.json         optional: researched-but-not-built works (planned)

Outputs:
  index.html           landing page + survey dashboard (blueprint style, offline)
  README.md            SURVEY and ROADMAP blocks rewritten between markers
"""
from __future__ import annotations

import datetime
import glob
import html
import json
import os

import atlas_lib as A

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD_DATE = datetime.date.today().isoformat()

TIER_ORDER = ["corpus", "dataset", "dense-relabel", "world-model", "vla-pretrain",
              "co-train", "affordance", "reward-repr", "perception-pretrain",
              "hand-pose", "eval-benchmark", "annotation-pipeline"]
TIER_LABEL = {
    "corpus": "Corpora (language supervision sources)",
    "dataset": "Datasets",
    "dense-relabel": "Dense relabeling",
    "world-model": "World / video models",
    "vla-pretrain": "VLA / policy pretraining",
    "co-train": "Human + robot co-training",
    "affordance": "Affordance / interaction priors",
    "reward-repr": "Reward / representation learning",
    "perception-pretrain": "Perception pretraining",
    "hand-pose": "Hand-pose supervision",
    "eval-benchmark": "Evaluation benchmarks",
    "annotation-pipeline": "Annotation pipelines",
}
CAT_ORDER = ["corpus", "dataset", "dense-annotation", "method"]
CAT_LABEL = {"corpus": "Corpora with real language annotations",
             "dataset": "Datasets", "dense-annotation": "Dense-annotation works",
             "method": "Methods that define how human video is used"}


def esc(s):
    return html.escape(str(s), quote=True)


def chip(s):
    return f'<span class="chip">{esc(s)}</span>'


def load_entries():
    built = []
    for path in sorted(glob.glob(os.path.join(HERE, "*", "atlas_entry.json"))):
        e = json.load(open(path, encoding="utf-8"))
        if e.get("status") == "built" and e.get("stats_file"):
            sp = os.path.join(HERE, e["stats_file"])
            if os.path.exists(sp):
                st = json.load(open(sp, encoding="utf-8"))
                dens = (st["density"].get("segments_per_hour_labelled")
                        or st["density"].get("segments_per_hour_cited") or 0)
                hrs = (st["hours"].get("total_hours_all_videos")
                       or st["hours"].get("annotated_span_hours") or 0)
                e["_counts"] = {
                    "annotations": st["counts"].get("labelled_segments", "n/a"),
                    "clusters": st.get("clusters", {}).get("n_clusters", "n/a"),
                    "density": round(dens),
                    "hours": hrs,
                    "unique": st["counts"].get("unique_narrations_clean", "n/a"),
                }
                e["_stats"] = st
        built.append(e)
    return built


def load_roadmap():
    p = os.path.join(HERE, "roadmap.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8")).get("planned", [])
    return []


def primary_tier(e):
    for t in TIER_ORDER:
        if t in e.get("usage_methods", []):
            return t
    um = e.get("usage_methods") or ["dataset"]
    return um[0]


# ------------------------------------------------------------------ index.html
CSS = r"""
:root{--paper:#e9edf4;--ink:#15233e;--muted:#5d6c87;--line:#c4d0e2;--accent:#1f4e9b;--accent2:#b45309}
*{box-sizing:border-box}body{margin:0;font-family:"JetBrains Mono",ui-monospace,Consolas,Menlo,monospace;
color:var(--ink);background-color:var(--paper);font-size:13px;line-height:1.5;
background-image:linear-gradient(rgba(110,135,175,.10) 1px,transparent 1px),linear-gradient(90deg,rgba(110,135,175,.10) 1px,transparent 1px),linear-gradient(rgba(110,135,175,.18) 1px,transparent 1px),linear-gradient(90deg,rgba(110,135,175,.18) 1px,transparent 1px);
background-size:24px 24px,24px 24px,120px 120px,120px 120px}
a{color:var(--accent);text-decoration:none;border-bottom:1px dotted var(--accent)}a:hover{border-bottom-style:solid}
.wrap{max-width:1080px;margin:0 auto;padding:18px 16px 64px}
.card{background:rgba(255,255,255,.80);border:1px solid var(--line);padding:16px 18px;margin:14px 0}
h1{font-size:28px;letter-spacing:.04em;margin:2px 0 4px}
.brand{font-size:11px;text-transform:uppercase;letter-spacing:.22em;color:var(--muted)}
.focus{max-width:74ch;color:var(--ink)}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.14em;border-bottom:1px solid var(--line);padding-bottom:7px;margin:0 0 12px}
h3{font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--accent);margin:16px 0 8px}
.snum{color:var(--accent);margin-right:6px}
.chip{display:inline-block;border:1px solid var(--accent);color:var(--accent);border-radius:11px;padding:0 8px;font-size:11px;margin:1px 2px}
.chip.alt{border-color:var(--accent2);color:var(--accent2)}
.chip.plan{border-color:var(--muted);color:var(--muted)}
.note{font-size:11px;color:var(--muted);border-left:2px solid var(--line);padding-left:8px;margin:10px 0 0}
.kc{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin:10px 0}
.kc div{border:1px solid var(--line);background:rgba(255,255,255,.55);padding:6px 8px}
.kcv{font-size:17px;font-weight:700;color:var(--accent)}.kcl{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
.entry{border:1px solid var(--line);background:rgba(255,255,255,.6);padding:12px 14px;display:flex;flex-direction:column;gap:6px}
.entry h4{margin:0;font-size:16px}.entry .ef{font-size:12px;color:var(--ink)}
.entry .em{font-size:11px;color:var(--muted)}
.entry .lk{margin-top:auto;font-size:12px}
table{width:100%;border-collapse:collapse;font-size:11.5px}
th,td{border-bottom:1px solid var(--line);padding:5px 7px;text-align:left;vertical-align:top}
th{font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);background:#eef2f8}
.tablewrap{overflow-x:auto;border:1px solid var(--line)}
.built{color:var(--accent);font-weight:700}.plan{color:var(--muted)}
.rm{font-size:12px;margin:5px 0;padding:7px 9px;border:1px solid var(--line);background:rgba(255,255,255,.5)}
.rm b{font-size:13px}.rm .meta{color:var(--muted);font-size:11px}
@media(max-width:680px){.cards{grid-template-columns:1fr}}
"""


def entry_card(e):
    c = e.get("_counts", {})
    counts = ""
    if c:
        counts = (f'<div class="em">{c["annotations"]:,} annotations &middot; '
                  f'{c["clusters"]} clusters &middot; {c["density"]:,}/hr &middot; '
                  f'{c["hours"]:.1f} h</div>')
    um = " ".join(chip(u) for u in e.get("usage_methods", []))
    at = " ".join(chip(a) for a in e.get("annotation_types", []))
    links = []
    lk = e.get("links", {})
    if lk.get("atlas_en"):
        links.append(f'<a href="{lk["atlas_en"]}">atlas EN</a>')
    if lk.get("atlas_cn"):
        links.append(f'<a href="{lk["atlas_cn"]}">中文</a>')
    if lk.get("paper"):
        links.append(f'<a href="{lk["paper"]}">paper</a>')
    if lk.get("repo"):
        links.append(f'<a href="{lk["repo"]}">data</a>')
    return (
        '<div class="entry">'
        f'<h4>{esc(e["name"])}</h4>'
        f'<div class="ef">{esc(e.get("focus", ""))}</div>'
        f'<div>{um} {at}</div>'
        f'{counts}'
        f'<div class="em">license: {esc(e.get("license", "n/a"))}</div>'
        f'<div class="lk">{" &middot; ".join(links)}</div>'
        '</div>'
    )


def survey_rows_html(built, planned):
    rows = []
    for e in built:
        c = e.get("_counts", {})
        lk = e.get("links", {})
        atlas = (f'<a href="{lk.get("atlas_en", "#")}">EN</a> / '
                 f'<a href="{lk.get("atlas_cn", "#")}">CN</a>')
        rows.append(
            f'<tr><td class="built">{esc(e["name"])}</td>'
            f'<td>{esc(e.get("work_type", ""))}</td>'
            f'<td>{esc(", ".join(e.get("usage_methods", [])))}</td>'
            f'<td>{esc(", ".join(e.get("annotation_types", [])))}</td>'
            f'<td>{c.get("annotations", "n/a"):,}</td>'
            f'<td>{c.get("clusters", "n/a")}</td>'
            f'<td>{esc(e.get("downloadable", e.get("data_access", "")))}</td>'
            f'<td>{esc(e.get("license", "n/a"))}</td>'
            f'<td>{atlas}</td></tr>'
        )
    for p in planned:
        ar = p.get("arxiv", "")
        name = (f'<a href="{ar}">{esc(p["name"])}</a>' if ar.startswith("http") else esc(p["name"]))
        rows.append(
            f'<tr><td class="plan">{name}</td>'
            f'<td>{esc(p.get("category", ""))}</td>'
            f'<td>{esc(", ".join(p.get("usage_methods", [])))}</td>'
            f'<td>{esc(", ".join(p.get("annotation_types", [])))}</td>'
            f'<td>n/a</td><td>n/a</td>'
            f'<td>{esc(p.get("downloadable", p.get("data_access", "")))}</td>'
            f'<td>{esc(p.get("license", "n/a"))}</td>'
            f'<td class="plan">planned</td></tr>'
        )
    return "\n".join(rows)


def roadmap_html(planned):
    if not planned:
        return ('<p class="note">Roadmap is empty. Add researched works to '
                'roadmap.json and re-run build_atlas_index.py.</p>')
    out = []
    by_cat = {}
    for p in planned:
        by_cat.setdefault(p.get("category", "method"), []).append(p)
    for cat in CAT_ORDER:
        items = by_cat.get(cat, [])
        if not items:
            continue
        out.append(f'<h3>{esc(CAT_LABEL.get(cat, cat))}</h3>')
        for p in items:
            ar = p.get("arxiv", "")
            name = (f'<a href="{ar}">{esc(p["name"])}</a>' if ar.startswith("http") else esc(p["name"]))
            chips = " ".join(chip(u) for u in p.get("usage_methods", []))
            chips += " " + " ".join(f'<span class="chip alt">{esc(a)}</span>'
                                    for a in p.get("annotation_types", []))
            suit = p.get("suitability", "")
            out.append(
                f'<div class="rm"><b>{name}</b> {chips}<br>'
                f'<span class="ef">{esc(p.get("focus", ""))}</span><br>'
                f'<span class="meta">access: {esc(p.get("downloadable", p.get("data_access", "n/a")))} '
                f'&middot; license: {esc(p.get("license", "n/a"))} '
                f'&middot; {esc(suit)}</span></div>'
            )
    return "\n".join(out)


def jacc(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def build_crosswork(built):
    works = [e for e in built if e.get("_stats")]
    if len(works) < 2:
        return ('<p class="note">A second built atlas is required for the cross-work '
                'comparison.</p>')
    # work x verb-family coverage matrix (share of annotations per verb category)
    totals = {}
    for e in works:
        for name, cnt in e["_stats"].get("verb_category_dist", []):
            totals[name] = totals.get(name, 0) + cnt
    cats = [c for c, _ in sorted(totals.items(), key=lambda x: -x[1])]
    head = "".join(f'<th class="num">{esc(c)}</th>' for c in cats)
    rows = []
    for e in works:
        d = dict(e["_stats"].get("verb_category_dist", []))
        tot = sum(d.values()) or 1
        cells = []
        for c in cats:
            share = d.get(c, 0) / tot
            alpha = min(0.82, share * 2.6)
            cells.append(f'<td class="num" style="background:rgba(31,78,155,{alpha:.2f})">'
                         f'{share * 100:.0f}</td>')
        rows.append(f'<tr><td class="lab">{esc(e["name"])}</td>{"".join(cells)}</tr>')
    matrix = ('<div class="minihead">work &times; verb-family coverage (% of annotations)</div>'
              '<div class="tablewrap"><table class="dtable"><thead><tr><th>work</th>'
              f'{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    # granularity contrast
    mls = [(e["name"], round(e["_stats"]["length"]["tokens_mean"], 1)) for e in works]
    gran = ('<div class="minihead">granularity contrast (mean narration length, tokens)</div>'
            + A.bar_rows([(n, int(round(v))) for n, v in mls], color="var(--accent2)"))
    # lexical overlap on top-25 class keys
    def keys(e, field):
        return set(k for k, _ in e["_stats"].get(field, [])[:25])
    ov = []
    for i in range(len(works)):
        for j in range(i + 1, len(works)):
            a, b = works[i], works[j]
            ov.append(f'<tr><td class="lab">{esc(a["name"])} vs {esc(b["name"])}</td>'
                      f'<td class="num">{jacc(keys(a, "verb_top"), keys(b, "verb_top")):.2f}</td>'
                      f'<td class="num">{jacc(keys(a, "noun_top"), keys(b, "noun_top")):.2f}</td></tr>')
    overlap = ('<div class="minihead">lexical overlap (Jaccard, top-25 class keys)</div>'
               '<div class="tablewrap"><table class="dtable"><thead><tr><th>pair</th>'
               '<th class="num">verbs</th><th class="num">nouns</th></tr></thead>'
               f'<tbody>{"".join(ov)}</tbody></table></div>')
    # usage-method x annotation-style map
    um = []
    for e in works:
        chips = (" ".join(chip(u) for u in e.get("usage_methods", []))
                 + " " + " ".join(f'<span class="chip alt">{esc(a)}</span>'
                                   for a in e.get("annotation_types", [])))
        um.append(f'<div class="rm"><b>{esc(e["name"])}</b> {chips}</div>')
    umap = '<div class="minihead">usage-method and annotation-style</div>' + "".join(um)
    return (matrix + '<div class="twocol"><div>' + gran + '</div><div>' + overlap
            + '</div></div>' + umap)


def build_index(built, planned):
    n_built = len(built)
    n_plan = len(planned)
    # tier grouping for built cards
    tiers = {}
    for e in built:
        tiers.setdefault(primary_tier(e), []).append(e)
    cards = []
    for t in TIER_ORDER:
        if t in tiers:
            cards.append(f'<h3>{esc(TIER_LABEL.get(t, t))}</h3><div class="cards">'
                         + "".join(entry_card(e) for e in tiers[t]) + '</div>')
    cards_html = "".join(cards) or '<p class="note">No built atlases yet.</p>'

    if n_built >= 2:
        cross = build_crosswork(built)
    else:
        cross = ('<p class="note">The cross-work coverage matrix and vocabulary-overlap '
                 'comparison activate once a second atlas is built. With a single entry, '
                 'the per-work cluster scatter and cluster table inside that atlas are '
                 'the comparison surface.</p>')

    return (
        '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
        '<title>Ego Language-Annotation Atlas</title>'
        f'<style>{CSS}</style></head><body><div class="wrap">'
        '<header class="card">'
        '<div class="brand">Ego Language-Annotation Atlas</div>'
        '<h1>Ego Language-Annotation Atlas</h1>'
        '<p class="focus">A curated, side-by-side survey of egocentric human-video '
        'works: how each uses human data, and what its language supervision actually '
        'looks like once the real annotation strings are downloaded and clustered. '
        'Every statistic traces to downloaded data or a cited source.</p>'
        f'<div class="kc"><div><div class="kcv">{n_built}</div><div class="kcl">built atlases</div></div>'
        f'<div><div class="kcv">{n_plan}</div><div class="kcl">on the roadmap</div></div>'
        f'<div><div class="kcv">{BUILD_DATE}</div><div class="kcl">generated</div></div></div>'
        '<p class="note">Hand-compiled reference over downloaded data, may contain '
        'errors. Open an issue to fix it. No em-dashes, blueprint house style.</p>'
        '</header>'
        f'<section class="card"><h2><span class="snum">01</span>Built atlases</h2>{cards_html}</section>'
        '<section class="card"><h2><span class="snum">02</span>Survey table</h2>'
        '<div class="tablewrap"><table><thead><tr><th>work</th><th>type</th><th>usage</th>'
        '<th>annotation types</th><th>annotations</th><th>clusters</th><th>data</th>'
        '<th>license</th><th>atlas</th></tr></thead><tbody>'
        f'{survey_rows_html(built, planned)}</tbody></table></div></section>'
        f'<section class="card"><h2><span class="snum">03</span>Cross-work comparison</h2>{cross}</section>'
        '<section class="card"><h2><span class="snum">04</span>Roadmap (researched, not yet built)</h2>'
        f'{roadmap_html(planned)}</section>'
        '<footer class="card"><p class="note">Generated by build_atlas_index.py on '
        f'{BUILD_DATE}. Each entry is reproducible from its folder: '
        'pip install -r requirements.txt, then python build_&lt;slug&gt;.py.</p></footer>'
        '</div></body></html>'
    )


# -------------------------------------------------------------------- README
def md_survey(built, planned):
    head = ("| Work | Type | Usage methods | Annotation types | Annotations | Clusters "
            "| Data access | License | Atlas |\n"
            "|---|---|---|---|---|---|---|---|---|\n")
    lines = []
    for e in built:
        c = e.get("_counts", {})
        lk = e.get("links", {})
        atlas = f'[EN]({lk.get("atlas_en","#")}) / [CN]({lk.get("atlas_cn","#")})'
        lines.append("| {n} | {t} | {u} | {a} | {ann:,} | {cl} | {d} | {lic} | {at} |".format(
            n=e["name"], t=e.get("work_type", ""), u=", ".join(e.get("usage_methods", [])),
            a=", ".join(e.get("annotation_types", [])), ann=c.get("annotations", 0),
            cl=c.get("clusters", "n/a"), d=e.get("downloadable", e.get("data_access", "")),
            lic=e.get("license", "n/a"), at=atlas))
    for p in planned:
        ar = p.get("arxiv", "")
        nm = f'[{p["name"]}]({ar})' if ar.startswith("http") else p["name"]
        lines.append("| {n} | {t} | {u} | {a} | n/a | n/a | {d} | {lic} | planned |".format(
            n=nm, t=p.get("category", ""), u=", ".join(p.get("usage_methods", [])),
            a=", ".join(p.get("annotation_types", [])),
            d=p.get("downloadable", p.get("data_access", "")), lic=p.get("license", "n/a")))
    return head + "\n".join(lines) + "\n"


def md_roadmap(planned):
    if not planned:
        return "_Roadmap empty. Populate roadmap.json and re-run build_atlas_index.py._\n"
    by_cat = {}
    for p in planned:
        by_cat.setdefault(p.get("category", "method"), []).append(p)
    out = []
    for cat in CAT_ORDER:
        items = by_cat.get(cat, [])
        if not items:
            continue
        out.append(f"\n### {CAT_LABEL.get(cat, cat)}\n")
        for p in items:
            ar = p.get("arxiv", "")
            nm = f'[{p["name"]}]({ar})' if ar.startswith("http") else p["name"]
            out.append(
                f"- **{nm}** ({p.get('venue','')}) "
                f"[{', '.join(p.get('usage_methods', []))} | "
                f"{', '.join(p.get('annotation_types', []))}]  \n"
                f"  {p.get('focus','')}  \n"
                f"  access: {p.get('downloadable', p.get('data_access','n/a'))} "
                f"| license: {p.get('license','n/a')} | {p.get('suitability','')}")
    return "\n".join(out) + "\n"


def update_readme(built, planned):
    path = os.path.join(HERE, "README.md")
    if not os.path.exists(path):
        print("README.md not found, skipping its update")
        return
    txt = open(path, encoding="utf-8").read()
    for tag, content in (("SURVEY", md_survey(built, planned)),
                         ("ROADMAP", md_roadmap(planned))):
        start, end = f"<!-- {tag}:START -->", f"<!-- {tag}:END -->"
        if start in txt and end in txt:
            pre = txt.split(start)[0] + start + "\n"
            post = "\n" + end + txt.split(end)[1]
            txt = pre + content + post
    open(path, "w", encoding="utf-8").write(txt)


def main():
    built = load_entries()
    planned = load_roadmap()
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_index(built, planned))
    update_readme(built, planned)
    print(f"index.html + README updated: {len(built)} built, {len(planned)} planned")


if __name__ == "__main__":
    main()
