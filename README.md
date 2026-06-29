# Ego Language-Annotation Atlas

A curated, side-by-side survey of egocentric human-video works, focused on how
each one uses human data and what its language supervision actually looks like
once you pull the real annotation strings and cluster them.

Each entry is built from primary sources: a download script fetches the real
language annotations, a normalize step produces one row per annotation unit, a
cluster step embeds and groups the cleaned strings, and a render step emits a
single-file, dependency-free, offline interactive atlas (English plus Chinese).

Principles: accuracy and reproducibility first. Every statistic traces to
downloaded data or a cited source. Every cluster is backed by real exemplar
strings, never an invented paraphrase. Every gap is marked, never guessed. Each
dataset license is respected: gated raw text is never redistributed, only derived
artifacts and, where the license allows, short exemplars or full strings with
attribution. House style: blueprint aesthetic, no em-dashes in visible text.

## Built atlases

<!-- SURVEY:START -->
| Work | Type | Usage methods | Annotation types | Annotations | Clusters | Data access | License | Atlas |
|---|---|---|---|---|---|---|---|---|
| Being-H0 | method | vla-pretrain, hand-pose, corpus | task-instruction | n/a | n/a | derived-only (checkpoints; UniHand text not released standalone) | code MIT; full UniHand corpus license not released | [EN](being-h0/being-h0_atlas.html) / [CN](being-h0/being-h0_atlas_cn.html) (descriptive) |
| DeMiAn (How to Instruct Your Robot) | method (dense annotation) | dense-relabel, vla-pretrain, world-model | dense-multi-aspect, task-instruction | n/a | n/a | none (no code/data release found) | paper CC BY 4.0; dense annotations not released | [EN](demian/demian_atlas.html) / [CN](demian/demian_atlas_cn.html) (descriptive) |
| Ego-Exo4D | dataset (corpus + benchmark) | corpus, perception-pretrain, eval-benchmark | atomic-substep, clip-narration, expert-commentary | n/a | n/a | gated (license form, then CLI) | Ego-Exo4D License (gated; redistribution restricted) | [EN](ego-exo4d/ego-exo4d_atlas.html) / [CN](ego-exo4d/ego-exo4d_atlas_cn.html) (descriptive) |
| Ego4D | dataset (corpus + benchmark) | corpus, perception-pretrain, eval-benchmark | clip-narration, video-summary, verb-noun-action | n/a | n/a | gated (license sign-up, then CLI) | Ego4D License (gated; redistribution restricted) | [EN](ego4d/ego4d_atlas.html) / [CN](ego4d/ego4d_atlas_cn.html) (descriptive) |
| EgoDex | dataset (corpus) | corpus, hand-pose, vla-pretrain | task-instruction | 3,243 | 50 | open download (Apple CDN); CC BY-NC-ND, internal use | CC BY-NC-ND 4.0 (internal analysis) | [EN](egodex/egodex_atlas.html) / [CN](egodex/egodex_atlas_cn.html) |
| EgoMimic | method | co-train, hand-pose |  | n/a | n/a | HF data is hand-tracking + video (no language corpus) | code MIT; HuggingFace dataset license not stated | [EN](egomimic/egomimic_atlas.html) / [CN](egomimic/egomimic_atlas_cn.html) (descriptive) |
| EgoScale | method | vla-pretrain, hand-pose |  | n/a | n/a | none (no dataset or annotations released) | not stated (code coming soon) | [EN](egoscale/egoscale_atlas.html) / [CN](egoscale/egoscale_atlas_cn.html) (descriptive) |
| EgoSchema | benchmark | eval-benchmark | vqa | 5,031 | 67 | open (questions.json on GitHub); answers held out except 500 | Ego4D License (questions LLM-generated then human-curated) | [EN](egoschema/egoschema_atlas.html) / [CN](egoschema/egoschema_atlas_cn.html) |
| EgoVerse | dataset (corpus) | corpus, co-train, vla-pretrain | task-instruction, clip-narration, atomic-substep | n/a | n/a | via S3 sync script (AWS creds) | code MIT; dataset/annotation redistribution license not stated | [EN](egoverse/egoverse_atlas.html) / [CN](egoverse/egoverse_atlas_cn.html) (descriptive) |
| EgoVid-5M | dataset (corpus) | world-model, corpus | clip-narration, verb-noun-action | 4,873,088 | 357 | open (HF: Jeff-Wang/EgoVid-5M, apache-2.0) | apache-2.0 (annotations; videos under Ego4D License) | [EN](egovid-5m/egovid-5m_atlas.html) / [CN](egovid-5m/egovid-5m_atlas_cn.html) |
| EgoVLA | method | vla-pretrain, hand-pose, eval-benchmark | task-instruction | n/a | n/a | derived-only (reuses source labels) | code MIT; reused labels follow each source dataset license | [EN](egovla/egovla_atlas.html) / [CN](egovla/egovla_atlas_cn.html) (descriptive) |
| EgoVLP (EgoClip / EgoNCE / EgoMCQ) | method + derived corpus | perception-pretrain, corpus, eval-benchmark | clip-narration, verb-noun-action | 3,847,727 | 394 | open CSV (egoclip.csv); Ego4D-derived, internal use | Ego4D License (EgoClip text is Ego4D-derived) | [EN](egovlp/egovlp_atlas.html) / [CN](egovlp/egovlp_atlas_cn.html) |
| EgoZero | method | hand-pose |  | n/a | n/a | none (self-collected demos, not released) | code MIT; paper CC BY 4.0 | [EN](egozero/egozero_atlas.html) / [CN](egozero/egozero_atlas_cn.html) (descriptive) |
| EMMA | method | co-train |  | n/a | n/a | none (code coming soon) | code and data license unspecified | [EN](emma/emma_atlas.html) / [CN](emma/emma_atlas_cn.html) (descriptive) |
| EPIC-KITCHENS-100 | dataset (corpus + benchmark) | corpus, eval-benchmark | verb-noun-action, clip-narration | 76,885 | 111 | open (CSV on GitHub) | CC BY-NC 4.0 | [EN](epic-kitchens-100/epic-kitchens-100_atlas.html) / [CN](epic-kitchens-100/epic-kitchens-100_atlas_cn.html) |
| HD-EPIC | dataset (corpus + benchmark) | corpus, eval-benchmark | clip-narration, verb-noun-action, task-instruction, vqa, dense-multi-aspect | 59,454 | 314 | open (GitHub) | CC BY 4.0 | [EN](hd-epic/hd-epic_atlas.html) / [CN](hd-epic/hd-epic_atlas_cn.html) |
| LAPA (Latent Action Pretraining) | method | vla-pretrain | task-instruction | n/a | n/a | derived-only (releases weights and code; no language corpus) | code and weights MIT | [EN](lapa/lapa_atlas.html) / [CN](lapa/lapa_atlas_cn.html) (descriptive) |
| MAPLE | method | perception-pretrain, affordance, hand-pose |  | n/a | n/a | none (releases a checkpoint and code, not annotations) | no license file in repo (default all rights reserved) | [EN](maple/maple_atlas.html) / [CN](maple/maple_atlas_cn.html) (descriptive) |
| MotionTrans | method | co-train, hand-pose, corpus | task-instruction | n/a | n/a | derived-only (HF dataset; NL instructions generated locally) | code MIT; HF dataset has no license tag | [EN](motiontrans/motiontrans_atlas.html) / [CN](motiontrans/motiontrans_atlas_cn.html) (descriptive) |
| OakInk2 | dataset (corpus) | corpus, hand-pose, affordance | task-instruction, atomic-substep | 3,833 | 64 | open (HF: kelvin34501/OakInk-v2) | CC BY-SA 4.0 | [EN](oakink2/oakink2_atlas.html) / [CN](oakink2/oakink2_atlas_cn.html) |
| OpenEgo | dataset (unified corpus) | corpus, hand-pose, vla-pretrain | task-instruction, atomic-substep, verb-noun-action | n/a | n/a | open-ish (Box); EgoDex-derived subset gated | mixed per-source (MIT code; constituents vary, some CC BY-NC-ND) | [EN](openego/openego_atlas.html) / [CN](openego/openego_atlas_cn.html) (descriptive) |
| HAT (Humanoid Policy ~ Human Policy) | method + corpus | co-train, corpus, hand-pose | task-instruction | 1,848 | 3 | open (HF: RogerQi/PH2D, MIT; HDF5 attributes) | MIT | [EN](ph2d/ph2d_atlas.html) / [CN](ph2d/ph2d_atlas_cn.html) |
| Phantom | method | hand-pose |  | n/a | n/a | none (releases code and policies, not annotations) | code MIT; paper CC BY 4.0 | [EN](phantom/phantom_atlas.html) / [CN](phantom/phantom_atlas_cn.html) (descriptive) |
| PhysBrain | method + dataset (VQA) | dense-relabel, vla-pretrain, perception-pretrain, corpus | vqa, dense-multi-aspect | n/a | n/a | none (E2E-3M not yet released) | not stated | [EN](physbrain/physbrain_atlas.html) / [CN](physbrain/physbrain_atlas_cn.html) (descriptive) |
| R3M | method | perception-pretrain |  | n/a | n/a | none (releases encoder weights, not annotations) | code MIT | [EN](r3m/r3m_atlas.html) / [CN](r3m/r3m_atlas_cn.html) (descriptive) |
| VIP | method | reward-repr, perception-pretrain |  | n/a | n/a | none (trains on unlabeled Ego4D; releases encoder weights) | code CC BY-NC 4.0 | [EN](vip/vip_atlas.html) / [CN](vip/vip_atlas_cn.html) (descriptive) |
| VRB (Vision-Robotics Bridge) | method | affordance |  | n/a | n/a | none (visual affordances, no language) | code MIT | [EN](vrb/vrb_atlas.html) / [CN](vrb/vrb_atlas_cn.html) (descriptive) |
| ZeroMimic | method | affordance, hand-pose |  | n/a | n/a | none (consumes EPIC; releases policies) | arXiv listing CC BY 4.0; code/checkpoint license not separately stated | [EN](zeromimic/zeromimic_atlas.html) / [CN](zeromimic/zeromimic_atlas_cn.html) (descriptive) |

<!-- SURVEY:END -->

Open `index.html` for the landing page and survey dashboard.

## Roadmap (researched, not yet built)

These works are classified into the taxonomy below from primary sources. Each is
a candidate for a future single-work run. Facts here are web-verified where
possible; unverifiable items are marked in the per-run uncertainty notes.

<!-- ROADMAP:START -->
_Roadmap empty. Populate roadmap.json and re-run build_atlas_index.py._

<!-- ROADMAP:END -->

## Reproduce an entry

```bash
pip install -r requirements.txt
cd <slug>                       # e.g. epic-kitchens-100
python build_<slug>.py          # download -> normalize -> cluster -> render
```

The build chain is idempotent: raw downloads and sentence embeddings are cached
under `<slug>/.cache/` (gitignored), so re-runs are cheap. After adding or
rebuilding an entry, regenerate the dashboard so it does not desync:

```bash
python build_atlas_index.py     # rewrites index.html + the tables above
```

Per entry the folder holds: `download_<slug>.py`, `normalize_<slug>.py`,
`cluster_<slug>.py`, `render_<slug>.py`, `build_<slug>.py`, the normalized
`*_annotations.parquet` plus a CSV sample, the `*_clusters.json` / `*_stats.json`
/ `*_scatter.json` artifacts, `atlas_entry.json` (the dashboard manifest), and
the two HTML atlases.

## Taxonomies

How human data is used (`usage-method`): `perception-pretrain`, `vla-pretrain`,
`co-train`, `affordance`, `reward-repr`, `world-model`, `dense-relabel`,
`hand-pose`, `eval-benchmark`, `corpus`.

What the language looks like (`annotation-type`): `video-summary`,
`clip-narration`, `verb-noun-action`, `atomic-substep`, `expert-commentary`,
`dense-multi-aspect`, `task-instruction`, `vqa`.

## Method

- Encoder: a sentence-transformers model (constant at the top of each
  `cluster_<slug>.py`, currently `sentence-transformers/all-MiniLM-L6-v2`).
- Reduction: UMAP (2D for plotting, low-D for clustering), PCA fallback.
- Clustering: HDBSCAN (scikit-learn implementation). Noise points are their own
  bucket. Cluster labels are auto-derived from head verbs and nouns, not written
  by hand.
- Each atlas footer records the encoder, reducer and clustering parameters, the
  dataset version (source commit), and the access date.

## License and attribution

Code in this repository is provided for non-commercial research use. Each
dataset keeps its own license, recorded per entry and in each atlas footer. Raw
gated annotation text is never committed; it stays in the local cache. Where a
license permits redistribution (for example CC BY-NC 4.0), derived artifacts and
exemplar strings are included with attribution.

- EPIC-KITCHENS-100 annotations: CC BY-NC 4.0, Damen et al., Rescaling
  Egocentric Vision, IJCV 2022 (arXiv:2006.13256).
