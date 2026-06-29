#!/usr/bin/env python3
"""STAGE 5: render the EPIC-KITCHENS-100 atlas as two single-file, offline,
dependency-free HTML pages (English + Chinese), blueprint style.

All CSS/JS is inline. Cluster, scatter and stats data are embedded as inline
JSON so each page opens by double-click with no server and no network. House
style: no em-dashes in any visible text.

Reads:  *_stats.json, *_clusters.json, *_scatter.json, download_provenance.json
Writes: epic-kitchens-100_atlas.html, epic-kitchens-100_atlas_cn.html
"""
from __future__ import annotations

import datetime
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "epic-kitchens-100"

# ---------------------------------------------------------------- load data ---
stats = json.load(open(os.path.join(HERE, f"{SLUG}_stats.json"), encoding="utf-8"))
clusters_doc = json.load(open(os.path.join(HERE, f"{SLUG}_clusters.json"), encoding="utf-8"))
scatter = json.load(open(os.path.join(HERE, f"{SLUG}_scatter.json"), encoding="utf-8"))
prov = json.load(open(os.path.join(HERE, "download_provenance.json"), encoding="utf-8"))

CLUSTERS = clusters_doc["clusters"]
CFG = clusters_doc["config"]
POINTS = scatter["points"]
BUILD_DATE = datetime.date.today().isoformat()
ACCESS_DATE = prov.get("access_utc", "")[:10]
COMMIT = prov.get("commit_sha", "")

# ---------------------------------------------------------------- constants ---
REPO = "https://github.com/epic-kitchens/epic-kitchens-100-annotations"
ARXIV = "https://arxiv.org/abs/2006.13256"
PROJECT = "https://epic-kitchens.github.io/"
LICENSE_NAME = "CC BY-NC 4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-nc/4.0/"
CITATION = "Damen et al., Rescaling Egocentric Vision, IJCV 2022 (arXiv:2006.13256)"

# semantic-family colors (EPIC verb categories), restrained palette on light paper
CATCOLORS = {
    "retrieve": "#2b6cb0", "leave": "#dd6b20", "clean": "#38a169",
    "access": "#805ad5", "split": "#d53f8c", "merge": "#d69e2e",
    "manipulate": "#319795", "monitor": "#718096", "block": "#e53e3e",
    "transition": "#4a5568", "sense": "#3182ce", "distribute": "#2c7a7b",
    "order": "#975a16", "_noise": "#c2cad6",
}


def cat_color(cat):
    return CATCOLORS.get(cat, "#64748b")


# ------------------------------------------------------------- translations ---
I18N = {
    "en": {
        "lang_name": "English", "other_name": "中文", "other_file": f"{SLUG}_atlas_cn.html",
        "dir": "ltr",
        "tagline": "Ego Language-Annotation Atlas",
        "focus": ("100 hours of unscripted egocentric kitchen activity, densely "
                  "annotated as verb plus noun action segments parsed from participant "
                  "narrations."),
        "disclaimer": ("Hand-compiled reference over downloaded data, may contain "
                       "errors. Open an issue to fix it."),
        "usage_methods": "usage methods", "downstream": "downstream",
        "source_datasets": "source datasets",
        "k_annotations": "annotations (with text)", "k_total_seg": "segments incl. test",
        "k_unique": "unique narrations", "k_clusters": "clusters",
        "k_density": "annotations / hour", "k_hours": "hours (measured)",
        "k_verbs": "verb classes", "k_nouns": "noun classes",
        "k_vocab": "vocabulary (tokens)", "k_participants": "participants (train+val)",
        "k_videos": "videos (labelled / total)", "k_meanlen": "mean length (tokens)",
        "src_repo": "annotations repo", "src_paper": "paper", "src_project": "project page",
        "src_license": "license",
        "sec_usage": "Data-usage path", "sec_scatter": "Annotation clusters",
        "sec_clusters": "Cluster table", "sec_gran": "Granularity and density",
        "sec_vn": "Verbs and nouns", "sec_drawer": "Sample browser",
        "sec_foot": "Provenance and reproducibility",
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
        "scatter_help": ("Each point is one unique cleaned narration, positioned by "
                         "UMAP over sentence-embeddings and colored by its cluster's verb "
                         "family. Hover for the string, search to highlight, click a "
                         "legend family to toggle it, or click a cluster row below."),
        "search_narr": "search narrations", "reset": "reset",
        "by_family": "color: verb family", "noise": "noise",
        "th_id": "id", "th_label": "label", "th_family": "family",
        "th_ann": "annotations", "th_uniq": "unique", "th_ex": "exemplars",
        "search_clusters": "search clusters", "clear_hl": "clear highlight",
        "hl_prefix": "highlighting cluster:",
        "gran_tier": "granularity tier", "len_hist": "narration length (tokens)",
        "density_lab": "density", "per_hour": "annotations / hour (labelled)",
        "per_video": "annotations / labelled video", "multinoun": "segments naming >1 noun",
        "median_len": "median length", "p90_len": "90th pct length", "max_len": "max length",
        "top_verbs": "top verb classes", "top_nouns": "top noun classes",
        "verb_fam": "verb families", "noun_fam": "noun families", "top_words": "top words",
        "drawer_help": ("Search the real annotation strings (deduplicated, with segment "
                        "frequency). Full text is shown: EPIC-KITCHENS-100 is CC BY-NC "
                        "4.0, which permits redistribution with attribution for "
                        "non-commercial use."),
        "filter_cluster": "filter: cluster", "filter_verb": "filter: verb", "all": "all",
        "th_narr": "narration", "th_count": "segments", "th_verb": "verb", "th_cluster": "cluster",
        "showing": "showing {n} of {m} matching unique narrations",
        "foot_source": "source", "foot_version": "dataset version",
        "foot_access": "access date", "foot_build": "build date",
        "foot_encoder": "encoder", "foot_reducer": "reducer", "foot_cluster": "clustering",
        "foot_license": "license", "foot_attrib": "attribution", "foot_author": "compiled for",
        "foot_note": ("Every statistic traces to the downloaded annotation files or is "
                      "marked as cited from the paper. Cluster labels are auto-derived "
                      "from head verbs and nouns, not hand-written. Unknown values are "
                      "shown as n/a."),
        "commit": "annotations commit", "cited": "cited from paper",
        "cited_note": ("Per the paper: 45 kitchens, about 20M frames, 90k action "
                       "segments. This atlas measures 100.03 hours, 700 videos, 76,885 "
                       "labelled segments, 34 participants in the released train and "
                       "validation splits."),
    },
    "cn": {
        "lang_name": "中文", "other_name": "English", "other_file": f"{SLUG}_atlas.html",
        "dir": "ltr",
        "tagline": "第一人称语言标注图谱",
        "focus": ("100 小时无脚本第一人称厨房活动，由参与者旁白解析为动词加名词的动作"
                  "片段并密集标注。"),
        "disclaimer": ("基于下载数据手工整理的参考资料，可能存在错误。欢迎提交 issue "
                       "修正。"),
        "usage_methods": "使用方式", "downstream": "下游",
        "source_datasets": "来源数据集",
        "k_annotations": "标注数（含文本）", "k_total_seg": "片段数（含测试集）",
        "k_unique": "唯一旁白数", "k_clusters": "聚类数",
        "k_density": "每小时标注数", "k_hours": "时长（实测）",
        "k_verbs": "动词类别", "k_nouns": "名词类别",
        "k_vocab": "词表（token）", "k_participants": "参与者（训练+验证）",
        "k_videos": "视频（标注 / 总数）", "k_meanlen": "平均长度（token）",
        "src_repo": "标注仓库", "src_paper": "论文", "src_project": "项目主页",
        "src_license": "许可",
        "sec_usage": "数据使用路径", "sec_scatter": "注释聚类",
        "sec_clusters": "聚类明细表", "sec_gran": "粒度与密度",
        "sec_vn": "动词与名词", "sec_drawer": "样本浏览器",
        "sec_foot": "来源与可复现性",
        "datapath": ("EPIC-KITCHENS-100 记录了 100 小时无脚本的第一人称厨房活动，本图谱"
                     "依据下载的元数据核实为 700 段视频、共 100.03 小时。录制后，参与者以"
                     "自由文本形式为自己的动作配上旁白，每条旁白被解析为带起止时间的动词"
                     "加名词动作片段。由此得到 89,977 个片段（其中 76,885 个附带公开的"
                     "旁白文本），定义了该数据集的识别、检测、预测与检索基准，并被广泛"
                     "用作第一人称感知预训练的监督来源。"),
        "flow": ["第一人称原始视频", "自由文本旁白", "动词 + 名词 + 时间戳",
                 "识别 / 检测 / 预测 / 检索", "下游：感知预训练"],
        "scatter_help": ("每个点代表一条唯一的清洗后旁白，位置由句向量经 UMAP 降维得到，"
                         "颜色对应其聚类的动词大类。悬停查看字符串，搜索可高亮，点击图例"
                         "大类可切换显隐，或点击下方聚类行。"),
        "search_narr": "搜索旁白", "reset": "重置",
        "by_family": "着色：动词大类", "noise": "噪声",
        "th_id": "编号", "th_label": "标签", "th_family": "大类",
        "th_ann": "标注数", "th_uniq": "唯一数", "th_ex": "示例",
        "search_clusters": "搜索聚类", "clear_hl": "清除高亮",
        "hl_prefix": "高亮聚类：",
        "gran_tier": "粒度层级", "len_hist": "旁白长度（token）",
        "density_lab": "密度", "per_hour": "每小时标注数（已标注）",
        "per_video": "每段已标注视频标注数", "multinoun": "含多个名词的片段",
        "median_len": "长度中位数", "p90_len": "长度 90 分位", "max_len": "最大长度",
        "top_verbs": "高频动词类别", "top_nouns": "高频名词类别",
        "verb_fam": "动词大类", "noun_fam": "名词大类", "top_words": "高频词",
        "drawer_help": ("搜索真实标注字符串（已去重，并标注片段频次）。此处显示完整文本："
                        "EPIC-KITCHENS-100 采用 CC BY-NC 4.0 许可，允许在署名且非商业的"
                        "前提下再分发。"),
        "filter_cluster": "筛选：聚类", "filter_verb": "筛选：动词", "all": "全部",
        "th_narr": "旁白", "th_count": "片段数", "th_verb": "动词", "th_cluster": "聚类",
        "showing": "显示 {m} 条匹配中的前 {n} 条唯一旁白",
        "foot_source": "来源", "foot_version": "数据集版本",
        "foot_access": "获取日期", "foot_build": "构建日期",
        "foot_encoder": "编码器", "foot_reducer": "降维", "foot_cluster": "聚类",
        "foot_license": "许可", "foot_attrib": "署名", "foot_author": "编制于",
        "foot_note": ("每一项统计均可追溯到下载的标注文件，或标明引自论文。聚类标签由头部"
                      "动词与名词自动生成，并非人工撰写。未知值显示为 n/a。"),
        "commit": "标注提交", "cited": "引自论文",
        "cited_note": ("论文数据：45 个厨房、约 2000 万帧、9 万动作片段。本图谱实测：100.03 "
                       "小时、700 段视频、76,885 个已标注片段、训练与验证集中 34 名参与者。"),
    },
}


def esc(s):
    return html.escape(str(s), quote=True)


def chip(text, style=""):
    return f'<span class="chip"{(" style=\"" + style + "\"") if style else ""}>{esc(text)}</span>'


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


def cluster_rows():
    rows = []
    for c in CLUSTERS:
        ex = " &middot; ".join(
            f'{esc(e["text"])} ({e["count"]:,})' for e in c["exemplars"][:4]
        )
        search_blob = esc((c["label"] + " " + " ".join(e["text"] for e in c["exemplars"])).lower())
        rows.append(
            f'<tr data-id="{c["id"]}" data-size="{c["size_total"]}" '
            f'data-unique="{c["size_unique"]}" data-label="{esc(c["label"].lower())}" '
            f'data-search="{search_blob}" data-cluster="{c["id"]}">'
            f'<td class="num">{c["id"]}</td>'
            f'<td class="lab">{esc(c["label"])}</td>'
            f'<td>{cat_legend_chip(c["verb_category"])}</td>'
            f'<td class="num">{c["size_total"]:,}</td>'
            f'<td class="num">{c["size_unique"]:,}</td>'
            f'<td class="ex">{ex}</td></tr>'
        )
    return "\n".join(rows)


def flow_diagram(steps):
    boxes = []
    for i, s in enumerate(steps):
        cls = "flowbox down" if i == len(steps) - 1 else "flowbox"
        boxes.append(f'<div class="{cls}">{esc(s)}</div>')
        if i < len(steps) - 1:
            boxes.append('<div class="flowarrow">&rarr;</div>')
    return '<div class="flow">' + "".join(boxes) + "</div>"


# ---------------------------------------------------------------------- CSS ---
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
.focus{color:var(--ink);max-width:70ch;margin:4px 0 12px}
.tagline-chips{margin:6px 0}
.ck{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-right:4px}
.chip{display:inline-block;border:1px solid var(--accent);color:var(--accent);border-radius:11px;
  padding:1px 9px;font-size:11px;margin:2px 3px}
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
.dtable td.lab{font-weight:600;white-space:nowrap}
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
.foot .footgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:6px 18px;font-size:11.5px}
.foot .fk{display:inline-block;min-width:120px;color:var(--muted);text-transform:uppercase;
  letter-spacing:.05em;font-size:10px}
@media(max-width:720px){.twocol{grid-template-columns:1fr}#scatter{height:420px}.hero h1{font-size:24px}}
"""

# ----------------------------------------------------------------------- JS ---
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
  ctx.setTransform(DPR,0,0,DPR,0,0);
  bctx.setTransform(DPR,0,0,DPR,0,0);
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
  ctx.clearRect(0,0,W,H);
  ctx.drawImage(base,0,0,W,H);
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
// legend
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
// cluster table: highlight, sort, search
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
// sample browser
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
// init
layout();sortRows();drawer();
let rt=null;window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(layout,150);});
"""


# -------------------------------------------------------------------- build ---
def build(lang):
    t = I18N[lang]
    c = stats["counts"]; ln = stats["length"]; hr = stats["hours"]
    den = stats["density"]; cl = stats["clusters"]

    kc = [
        (f'{c["labelled_segments"]:,}', t["k_annotations"]),
        (f'{c["total_segments_incl_test"]:,}', t["k_total_seg"]),
        (f'{c["unique_narrations_clean"]:,}', t["k_unique"]),
        (f'{cl["n_clusters"]}', t["k_clusters"]),
        (f'{den["segments_per_hour_labelled"]:,.0f}', t["k_density"]),
        (f'{hr["total_hours_all_videos"]:.2f}', t["k_hours"]),
        ('97', t["k_verbs"]),
        ('300', t["k_nouns"]),
        (f'{c["vocab_size_tokens"]:,}', t["k_vocab"]),
        (f'{c["participants"]}', t["k_participants"]),
        (f'{c["videos_labelled"]} / {c["videos_total"]}', t["k_videos"]),
        (f'{ln["tokens_mean"]:.2f}', t["k_meanlen"]),
    ]
    kc_html = "".join(
        f'<div class="kc"><div class="kcv">{v}</div><div class="kcl">{esc(l)}</div></div>'
        for v, l in kc
    )

    header = (
        '<header class="card hero">'
        '<div class="toprow">'
        f'<div class="brand">{esc(t["tagline"])}</div>'
        f'<div class="langtoggle"><a href="{t["other_file"]}">{esc(t["other_name"])}</a></div>'
        '</div>'
        '<h1>EPIC-KITCHENS-100</h1>'
        f'<p class="focus">{esc(t["focus"])}</p>'
        f'<div class="tagline-chips"><span class="ck">{esc(t["usage_methods"])}:</span> '
        f'{chip("corpus")} {chip("eval-benchmark")} '
        f'<span class="ck">{esc(t["downstream"])}:</span> {chip("perception-pretrain")}</div>'
        f'<div class="tagline-chips"><span class="ck">{esc(t["source_datasets"])}:</span> '
        f'{chip("EPIC-KITCHENS (55 to 100)")}</div>'
        f'<div class="kcgrid">{kc_html}</div>'
        f'<div class="srcrow"><a href="{REPO}">{esc(t["src_repo"])}</a> &middot; '
        f'<a href="{ARXIV}">{esc(t["src_paper"])}</a> &middot; '
        f'<a href="{PROJECT}">{esc(t["src_project"])}</a> &middot; '
        f'<a href="{LICENSE_URL}">{esc(t["src_license"])}: {LICENSE_NAME}</a></div>'
        f'<p class="note">{esc(t["disclaimer"])}</p>'
        '</header>'
    )

    def section(num, title, body, sub=""):
        s = f'<p class="subhelp">{esc(sub)}</p>' if sub else ""
        return (f'<section class="card"><h2><span class="snum">{num}</span>{esc(title)}</h2>'
                f'{s}{body}</section>')

    usage_body = f'<p class="prose">{esc(t["datapath"])}</p>' + flow_diagram(t["flow"])

    scatter_body = (
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

    cluster_body = (
        f'<div class="controls"><input id="q-clusters" placeholder="{esc(t["search_clusters"])}" /></div>'
        '<div class="tablewrap"><table id="clustertable" class="dtable"><thead><tr>'
        f'<th data-sort="id" class="num">{esc(t["th_id"])}</th>'
        f'<th data-sort="label">{esc(t["th_label"])}</th>'
        f'<th>{esc(t["th_family"])}</th>'
        f'<th data-sort="size" class="num">{esc(t["th_ann"])}</th>'
        f'<th data-sort="unique" class="num">{esc(t["th_uniq"])}</th>'
        f'<th>{esc(t["th_ex"])}</th></tr></thead>'
        f'<tbody>{cluster_rows()}</tbody></table></div>'
    )

    hist = stats["length"]["token_hist"]
    gran_body = (
        '<div class="twocol"><div>'
        f'<div class="minihead">{esc(t["len_hist"])}</div>'
        f'{bar_rows([(str(k), v) for k, v in hist])}'
        '</div><div>'
        '<div class="kcgrid small">'
        f'<div class="kc"><div class="kcv">{den["segments_per_hour_labelled"]:,.0f}</div><div class="kcl">{esc(t["per_hour"])}</div></div>'
        f'<div class="kc"><div class="kcv">{den["segments_per_labelled_video"]:,.0f}</div><div class="kcl">{esc(t["per_video"])}</div></div>'
        f'<div class="kc"><div class="kcv">{ln["tokens_median"]:.0f}</div><div class="kcl">{esc(t["median_len"])}</div></div>'
        f'<div class="kc"><div class="kcv">{ln["tokens_p90"]:.0f}</div><div class="kcl">{esc(t["p90_len"])}</div></div>'
        f'<div class="kc"><div class="kcv">{ln["tokens_max"]}</div><div class="kcl">{esc(t["max_len"])}</div></div>'
        f'<div class="kc"><div class="kcv">{ln["multi_noun_share"]*100:.1f}%</div><div class="kcl">{esc(t["multinoun"])}</div></div>'
        '</div>'
        f'<div class="tierbox"><span class="ck">{esc(t["gran_tier"])}:</span> {esc(stats["granularity_tier"])}</div>'
        '</div></div>'
    )

    words = [(w, cc) for w, cc in stats["word_top"] if w not in {"the", "a", "an", "of", "to"}][:24]
    words_html = " ".join(f'<span class="word">{esc(w)} <i>{cc:,}</i></span>' for w, cc in words)
    vn_body = (
        '<div class="twocol">'
        f'<div><div class="minihead">{esc(t["top_verbs"])}</div>{bar_rows(stats["verb_top"][:18], color="var(--accent)")}</div>'
        f'<div><div class="minihead">{esc(t["top_nouns"])}</div>{bar_rows(stats["noun_top"][:18], color="var(--accent2)")}</div>'
        '</div><div class="twocol">'
        f'<div><div class="minihead">{esc(t["verb_fam"])}</div>{bar_rows(stats["verb_category_dist"], color="#38a169")}</div>'
        f'<div><div class="minihead">{esc(t["noun_fam"])}</div>{bar_rows(stats["noun_category_dist"][:14], color="#805ad5")}</div>'
        '</div>'
        f'<div class="minihead">{esc(t["top_words"])}</div><div class="wordwrap">{words_html}</div>'
    )

    drawer_body = (
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

    foot = (
        '<footer class="card foot">'
        f'<h2><span class="snum">07</span>{esc(t["sec_foot"])}</h2>'
        '<div class="footgrid">'
        f'<div><span class="fk">{esc(t["foot_source"])}</span> <a href="{REPO}">{REPO}</a></div>'
        f'<div><span class="fk">{esc(t["commit"])}</span> {COMMIT}</div>'
        f'<div><span class="fk">{esc(t["foot_version"])}</span> EPIC-KITCHENS-100 @ {COMMIT[:10]}</div>'
        f'<div><span class="fk">{esc(t["foot_access"])}</span> {ACCESS_DATE}</div>'
        f'<div><span class="fk">{esc(t["foot_build"])}</span> {BUILD_DATE}</div>'
        f'<div><span class="fk">{esc(t["foot_encoder"])}</span> {esc(CFG["encoder"])}</div>'
        '<div><span class="fk">' + esc(t["foot_reducer"]) + '</span> UMAP viz(2D, n_neighbors=15, min_dist=0.1, cosine), cluster(5D)</div>'
        f'<div><span class="fk">{esc(t["foot_cluster"])}</span> HDBSCAN(min_cluster_size=50, min_samples=10), {cl["n_clusters"]} clusters, noise {cl["noise_share_weighted"]*100:.1f}%</div>'
        f'<div><span class="fk">{esc(t["foot_license"])}</span> <a href="{LICENSE_URL}">{LICENSE_NAME}</a></div>'
        f'<div><span class="fk">{esc(t["foot_attrib"])}</span> {esc(CITATION)}</div>'
        f'<div><span class="fk">{esc(t["foot_author"])}</span> {esc(t["tagline"])}</div>'
        '</div>'
        f'<p class="note">{esc(t["cited"])}: {esc(t["cited_note"])}</p>'
        f'<p class="note">{esc(t["foot_note"])}</p>'
        '</footer>'
    )

    cmap = {str(c2["id"]): {"l": c2["label"], "c": c2["verb_category"],
                           "n": c2["size_total"], "u": c2["size_unique"]} for c2 in CLUSTERS}
    points_json = json.dumps(POINTS, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    cmap_json = json.dumps(cmap, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    cat_json = json.dumps(CATCOLORS, ensure_ascii=False)
    ljs = {"noise": t["noise"], "count": t["th_count"], "verb": t["th_verb"],
           "cluster": t["th_cluster"], "all": t["all"], "showing": t["showing"]}
    ljs_json = json.dumps(ljs, ensure_ascii=False)

    data = (
        f'<script type="application/json" id="d-points">{points_json}</script>'
        f'<script type="application/json" id="d-cmap">{cmap_json}</script>'
        f'<script type="application/json" id="d-cat">{cat_json}</script>'
        '<script>'
        "const CATCOLORS=JSON.parse(document.getElementById('d-cat').textContent);"
        "const CMAP=JSON.parse(document.getElementById('d-cmap').textContent);"
        "const POINTS=JSON.parse(document.getElementById('d-points').textContent);"
        f'const L={ljs_json};'
        f'{JS_APP}'
        '</script>'
    )

    sections = [
        section("01", t["sec_usage"], usage_body),
        section("02", t["sec_scatter"], scatter_body, t["scatter_help"]),
        section("03", t["sec_clusters"], cluster_body),
        section("04", t["sec_gran"], gran_body),
        section("05", t["sec_vn"], vn_body),
        section("06", t["sec_drawer"], drawer_body, t["drawer_help"]),
    ]
    lang_attr = "zh" if lang == "cn" else "en"
    return (
        f'<!DOCTYPE html>\n<html lang="{lang_attr}" dir="{t["dir"]}">\n<head>'
        '<meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
        f'<title>EPIC-KITCHENS-100 &middot; {esc(t["tagline"])}</title>'
        f'<style>{CSS}</style></head>\n<body><div class="wrap">'
        f'{header}{"".join(sections)}{foot}'
        f'</div>{data}</body></html>'
    )


def main():
    for lang, suffix in (("en", "_atlas"), ("cn", "_atlas_cn")):
        out = os.path.join(HERE, f"{SLUG}{suffix}.html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(build(lang))
        print(f"wrote {out}  ({os.path.getsize(out)/1024:.0f} KB)")


if __name__ == "__main__":
    main()

