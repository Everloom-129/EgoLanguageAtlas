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
| EPIC-KITCHENS-100 | dataset (corpus + benchmark) | corpus, eval-benchmark | verb-noun-action, clip-narration | 76,885 | 111 | open (CSV on GitHub) | CC BY-NC 4.0 | [EN](epic-kitchens-100/epic-kitchens-100_atlas.html) / [CN](epic-kitchens-100/epic-kitchens-100_atlas_cn.html) |
| [Ego4D](https://arxiv.org/abs/2110.07058) | corpus | corpus, perception-pretrain, eval-benchmark | clip-narration, video-summary, verb-noun-action | n/a | n/a | gated (license sign-up, then CLI) | Ego4D License (gated; redistribution restricted, GAP on verbatim terms) | planned |
| [Ego-Exo4D](https://arxiv.org/abs/2311.18259) | corpus | corpus, perception-pretrain, eval-benchmark | atomic-substep, clip-narration, expert-commentary | n/a | n/a | gated (license form, then CLI) | Ego-Exo4D License (gated; redistribution restricted, GAP on verbatim terms) | planned |
| [EgoVLP (EgoClip / EgoNCE / EgoMCQ)](https://arxiv.org/abs/2206.01670) | corpus | perception-pretrain, corpus, eval-benchmark | clip-narration, verb-noun-action | n/a | n/a | open CSV (Ego4D-derived) via repo Drive links | code MIT; data inherits Ego4D License (GAP, not restated) | planned |
| [HD-EPIC](https://arxiv.org/abs/2502.04144) | corpus | corpus, eval-benchmark | dense-multi-aspect, verb-noun-action, task-instruction, vqa | n/a | n/a | open (GitHub annotations) | CC BY 4.0 (data.bris portal; GAP: live GitHub LICENSE not confirmed) | planned |
| [EgoSchema](https://arxiv.org/abs/2308.09126) | corpus | eval-benchmark | vqa | n/a | n/a | open questions + options; correct-answer key withheld | Ego4D License (questions LLM-generated then human-curated) | planned |
| [EgoVerse](https://arxiv.org/abs/2604.07607) | dataset | corpus, co-train, vla-pretrain | task-instruction, clip-narration, atomic-substep | n/a | n/a | via S3 sync script (AWS creds) | code MIT; dataset/annotation redistribution license not stated (GAP) | planned |
| [EgoDex](https://arxiv.org/abs/2505.11709) | dataset | corpus, hand-pose, vla-pretrain, eval-benchmark | task-instruction | n/a | n/a | open download (Apple CDN); redistribution barred | CC BY-NC-ND: annotation-text redistribution NOT permitted | planned |
| [EgoVid-5M](https://arxiv.org/abs/2411.08380) | dataset | world-model, corpus | clip-narration, verb-noun-action | n/a | n/a | open (HF: Jeff-Wang/EgoVid-5M) | apache-2.0 for hosted annotations (Ego4D License on videos) | planned |
| [OpenEgo](https://arxiv.org/abs/2509.05513) | dataset | corpus, hand-pose, vla-pretrain | task-instruction, atomic-substep, verb-noun-action | n/a | n/a | open-ish (Box); EgoDex-derived subset gated | mixed per-source (MIT code; constituents vary, some CC BY-NC-ND) | planned |
| [OakInk2](https://arxiv.org/abs/2403.19417) | dataset | corpus, hand-pose, affordance | task-instruction, atomic-substep | n/a | n/a | open (HF: kelvin34501/OakInk-v2) | CC BY-SA 4.0: redistribution permitted with attribution + share-alike | planned |
| [DeMiAn (How to Instruct Your Robot)](https://arxiv.org/abs/2605.17077) | dense-annotation | dense-relabel, vla-pretrain, world-model | dense-multi-aspect, task-instruction | n/a | n/a | none (no code/data release found) | paper CC BY 4.0; dense annotations not released (GAP) | planned |
| [PhysBrain](https://arxiv.org/abs/2512.16793) | dense-annotation | dense-relabel, vla-pretrain, perception-pretrain, corpus | vqa, dense-multi-aspect | n/a | n/a | none (E2E-3M not yet released) | not stated (GAP) | planned |
| [R3M](https://arxiv.org/abs/2203.12601) | method | perception-pretrain |  | n/a | n/a | none (consumes Ego4D narrations) | code MIT | planned |
| [VIP](https://arxiv.org/abs/2210.00030) | method | reward-repr, perception-pretrain |  | n/a | n/a | none (trains on unlabeled Ego4D) | code CC BY-NC 4.0 | planned |
| [VRB (Vision-Robotics Bridge)](https://arxiv.org/abs/2304.08488) | method | affordance |  | n/a | n/a | none (visual affordances, no language) | code MIT | planned |
| [EgoMimic](https://arxiv.org/abs/2410.24221) | method | co-train, hand-pose |  | n/a | n/a | HF data is hand-tracking + video (no language corpus) | code MIT; HF dataset license not stated (GAP) | planned |
| [HAT (Humanoid Policy ~ Human Policy)](https://arxiv.org/abs/2503.13441) | method | co-train, corpus, hand-pose | task-instruction | n/a | n/a | open (HF: RogerQi/PH2D, ~27k demos) | HF dataset MIT: redistribution permitted | planned |
| [ZeroMimic](https://arxiv.org/abs/2503.23877) | method | affordance, hand-pose |  | n/a | n/a | none (consumes EPIC; releases policies) | arXiv listing CC BY 4.0; code/checkpoint license not separately verified (GAP) | planned |
| [EgoVLA](https://arxiv.org/abs/2507.12440) | method | vla-pretrain, hand-pose, eval-benchmark | task-instruction | n/a | n/a | derived-only (reuses source labels) | code MIT; reused labels follow each source license (GAP) | planned |
| [Being-H0](https://arxiv.org/abs/2507.15597) | method | vla-pretrain, hand-pose, corpus | task-instruction | n/a | n/a | derived-only (checkpoints; UniHand text not released standalone) | code MIT; full UniHand corpus license not released (GAP) | planned |
| [EMMA](https://arxiv.org/abs/2509.04443) | method | co-train |  | n/a | n/a | none (code coming soon) | code/data license unspecified (GAP) | planned |
| [Phantom](https://arxiv.org/abs/2503.00779) | method | hand-pose |  | n/a | n/a | none (code only, no dataset) | code MIT; paper CC BY 4.0 | planned |
| [EgoZero](https://arxiv.org/abs/2505.20290) | method | hand-pose |  | n/a | n/a | none (self-collected, not public) | code MIT; paper CC BY 4.0 | planned |
| [MotionTrans](https://arxiv.org/abs/2509.17759) | method | co-train, hand-pose, corpus | task-instruction | n/a | n/a | derived-only (HF; NL instructions generated locally) | code MIT; HF dataset has no license tag (GAP) | planned |
| [LAPA (Latent Action Pretraining)](https://arxiv.org/abs/2410.11758) | method | vla-pretrain | task-instruction | n/a | n/a | derived-only (weights; instructions follow source licenses) | code + weights MIT; consumed instruction text follows OXE/SSv2/Bridge (GAP) | planned |
| [MAPLE](https://arxiv.org/abs/2504.06084) | method | perception-pretrain, affordance, hand-pose |  | n/a | n/a | none (visual/kinematic priors, no language) | no license file in repo (GAP, default all-rights-reserved) | planned |

<!-- SURVEY:END -->

Open `index.html` for the landing page and survey dashboard.

## Roadmap (researched, not yet built)

These works are classified into the taxonomy below from primary sources. Each is
a candidate for a future single-work run. Facts here are web-verified where
possible; unverifiable items are marked in the per-run uncertainty notes.

<!-- ROADMAP:START -->

### Corpora with real language annotations

- **[Ego4D](https://arxiv.org/abs/2110.07058)** (CVPR 2022) [corpus, perception-pretrain, eval-benchmark | clip-narration, video-summary, verb-noun-action]  
  Foundational 3,670-hour worldwide egocentric corpus with millions of timestamped free-form narrations and a multi-task benchmark suite.  
  access: gated (license sign-up, then CLI) | license: Ego4D License (gated; redistribution restricted, GAP on verbatim terms) | download+cluster target, gated: real #C/#O narrations behind license
- **[Ego-Exo4D](https://arxiv.org/abs/2311.18259)** (CVPR 2024) [corpus, perception-pretrain, eval-benchmark | atomic-substep, clip-narration, expert-commentary]  
  Time-synchronized ego and exo video of skilled activity with atomic action descriptions, narrate-and-act narrations, and expert commentary.  
  access: gated (license form, then CLI) | license: Ego-Exo4D License (gated; redistribution restricted, GAP on verbatim terms) | download+cluster target, gated: three real annotation streams behind license
- **[EgoVLP (EgoClip / EgoNCE / EgoMCQ)](https://arxiv.org/abs/2206.01670)** (NeurIPS 2022) [perception-pretrain, corpus, eval-benchmark | clip-narration, verb-noun-action]  
  A pre-filtered, cleaned text layer over Ego4D: ~3.8M clip-text pairs (EgoClip) plus the EgoNCE objective and the EgoMCQ choice benchmark.  
  access: open CSV (Ego4D-derived) via repo Drive links | license: code MIT; data inherits Ego4D License (GAP, not restated) | download+cluster target: egoclip.csv gives ~3.8M narration strings (Ego4D-derived)
- **[HD-EPIC](https://arxiv.org/abs/2502.04144)** (CVPR 2025) [corpus, eval-benchmark | dense-multi-aspect, verb-noun-action, task-instruction, vqa]  
  Highly-detailed kitchen understanding: 59,454 fine-grained action segments (81% unique sentences), recipe steps, 3D twins, gaze, and a 26,650-question VQA benchmark.  
  access: open (GitHub annotations) | license: CC BY 4.0 (data.bris portal; GAP: live GitHub LICENSE not confirmed) | download+cluster target: open narrations, recipe steps, and VQA strings
- **[EgoSchema](https://arxiv.org/abs/2308.09126)** (NeurIPS 2023) [eval-benchmark | vqa]  
  Diagnostic long-form video-QA benchmark: 5,031 multiple-choice questions over 3-minute Ego4D clips requiring long temporal certificates.  
  access: open questions + options; correct-answer key withheld | license: Ego4D License (questions LLM-generated then human-curated) | download+cluster target: 5,031 question + option strings open (labels withheld)

### Datasets

- **[EgoVerse](https://arxiv.org/abs/2604.07607)** (arXiv 2026) [corpus, co-train, vla-pretrain | task-instruction, clip-narration, atomic-substep]  
  Worldwide human egocentric platform, 1,362 h / ~80k episodes / 1,965 tasks, split into controlled EgoVerse-A and industry-scale EgoVerse-I with manipulation-relevant language.  
  access: via S3 sync script (AWS creds) | license: code MIT; dataset/annotation redistribution license not stated (GAP) | download+cluster target: dense per-segment language, but redistribution terms unclear
- **[EgoDex](https://arxiv.org/abs/2505.11709)** (ICLR 2026) [corpus, hand-pose, vla-pretrain, eval-benchmark | task-instruction]  
  829 hours of Apple Vision Pro egocentric video with native 3D hand pose over 194 tabletop tasks, each with a GPT-generated task description.  
  access: open download (Apple CDN); redistribution barred | license: CC BY-NC-ND: annotation-text redistribution NOT permitted | analyze locally only: rich task language + 3D hand pose, but ND blocks sharing clustered text
- **[EgoVid-5M](https://arxiv.org/abs/2411.08380)** (NeurIPS 2025) [world-model, corpus | clip-narration, verb-noun-action]  
  5M egocentric clips (from Ego4D) paired with kinematic control and MLLM-plus-LLM action text for video generation. A clear VLM-authored annotation case study.  
  access: open (HF: Jeff-Wang/EgoVid-5M) | license: apache-2.0 for hosted annotations (Ego4D License on videos) | download+cluster target: 5M MLLM/LLM action descriptions + captions, openly hosted
- **[OpenEgo](https://arxiv.org/abs/2509.05513)** (arXiv 2025) [corpus, hand-pose, vla-pretrain | task-instruction, atomic-substep, verb-noun-action]  
  Consolidates six egocentric corpora (1,107 h, 290 tasks) into a unified 21-joint hand-pose format with intention-aligned, timestamped language primitives.  
  access: open-ish (Box); EgoDex-derived subset gated | license: mixed per-source (MIT code; constituents vary, some CC BY-NC-ND) | download+cluster target with caveats: unified timestamped language primitives, mixed licenses
- **[OakInk2](https://arxiv.org/abs/2403.19417)** (CVPR 2024) [corpus, hand-pose, affordance | task-instruction, atomic-substep]  
  Bimanual hand-object manipulation organized as Affordance, Primitive Task, and Complex Task, with LLM-decomposable task programs and per-primitive descriptions.  
  access: open (HF: kelvin34501/OakInk-v2) | license: CC BY-SA 4.0: redistribution permitted with attribution + share-alike | download+cluster target: open task and per-primitive language

### Dense-annotation works

- **[DeMiAn (How to Instruct Your Robot)](https://arxiv.org/abs/2605.17077)** (arXiv 2026) [dense-relabel, vla-pretrain, world-model | dense-multi-aspect, task-instruction]  
  Studies language density as a lever: re-labels segments along four aspects (physical motion, scene, arm pose, reasoning) via Qwen3-VL, with a learned instructor selecting an annotation at deployment.  
  access: none (no code/data release found) | license: paper CC BY 4.0; dense annotations not released (GAP) | descriptive-only: the clearest dense-multi-aspect exemplar, but annotations unreleased
- **[PhysBrain](https://arxiv.org/abs/2512.16793)** (arXiv 2025) [dense-relabel, vla-pretrain, perception-pretrain, corpus | vqa, dense-multi-aspect]  
  An Egocentric2Embodiment pipeline turning raw human egocentric video into schema-driven, evidence-grounded supervision across seven VQA modes, yielding the ~3M-instance E2E-3M dataset.  
  access: none (E2E-3M not yet released) | license: not stated (GAP) | descriptive-only: revisit if E2E-3M is released

### Methods that define how human video is used

- **[R3M](https://arxiv.org/abs/2203.12601)** (CoRL 2022) [perception-pretrain | ]  
  Pretrains a reusable visual representation on Ego4D via time-contrastive learning and video-language alignment for data-efficient manipulation.  
  access: none (consumes Ego4D narrations) | license: code MIT | descriptive-only: publishes a frozen encoder, reuses Ego4D narrations
- **[VIP](https://arxiv.org/abs/2210.00030)** (ICLR 2023) [reward-repr, perception-pretrain | ]  
  Learns a self-supervised goal-conditioned value function from unlabeled Ego4D video, providing dense visual rewards for unseen robot tasks.  
  access: none (trains on unlabeled Ego4D) | license: code CC BY-NC 4.0 | descriptive-only: produces a reward/representation model, no annotation corpus
- **[VRB (Vision-Robotics Bridge)](https://arxiv.org/abs/2304.08488)** (CVPR 2023) [affordance | ]  
  Trains a visual affordance model (contact heatmap plus post-contact wrist trajectory) from human video to drive several robot-learning paradigms.  
  access: none (visual affordances, no language) | license: code MIT | descriptive-only: outputs contact + trajectory affordances, no language corpus
- **[EgoMimic](https://arxiv.org/abs/2410.24221)** (ICRA 2025) [co-train, hand-pose | ]  
  Captures egocentric human data with Aria glasses and co-trains a unified human-plus-robot imitation policy on a kinematically-matched bimanual robot.  
  access: HF data is hand-tracking + video (no language corpus) | license: code MIT; HF dataset license not stated (GAP) | descriptive-only: releases an egocentric hand-tracking dataset, not a language corpus
- **[HAT (Humanoid Policy ~ Human Policy)](https://arxiv.org/abs/2503.13441)** (CoRL 2025) [co-train, corpus, hand-pose | task-instruction]  
  Releases PH2D, ~27k egocentric human demos with language task specifications and 3D hand poses, and co-trains a Human Action Transformer with differentiable retargeting.  
  access: open (HF: RogerQi/PH2D, ~27k demos) | license: HF dataset MIT: redistribution permitted | download+cluster target: a NEW open egocentric corpus with per-task language
- **[ZeroMimic](https://arxiv.org/abs/2503.23877)** (ICRA 2025) [affordance, hand-pose | ]  
  Distills image-goal-conditioned manipulation skills (open, close, pour, pick-place, cut, stir) from EPIC-KITCHENS human video for zero-shot robot deployment.  
  access: none (consumes EPIC; releases policies) | license: arXiv listing CC BY 4.0; code/checkpoint license not separately verified (GAP) | descriptive-only: distills EPIC-KITCHENS video into deployable policies, no language corpus
- **[EgoVLA](https://arxiv.org/abs/2507.12440)** (arXiv 2025) [vla-pretrain, hand-pose, eval-benchmark | task-instruction]  
  Pretrains a VLA on egocentric human videos to predict wrist/hand actions, then retargets via inverse kinematics for a bimanual humanoid, with a new manipulation benchmark.  
  access: derived-only (reuses source labels) | license: code MIT; reused labels follow each source license (GAP) | descriptive-only: VLA reusing existing labels, no standalone corpus
- **[Being-H0](https://arxiv.org/abs/2507.15597)** (arXiv 2025) [vla-pretrain, hand-pose, corpus | task-instruction]  
  A dexterous VLA pretrained from large-scale human hand videos via physical instruction tuning and part-level hand-motion tokenization, building the UniHand corpus.  
  access: derived-only (checkpoints; UniHand text not released standalone) | license: code MIT; full UniHand corpus license not released (GAP) | descriptive-only: signature UniHand instruction corpus not independently downloadable
- **[EMMA](https://arxiv.org/abs/2509.04443)** (RA-L 2026) [co-train | ]  
  Scales mobile manipulation by co-training egocentric human full-body motion with static robot data, avoiding mobile teleoperation.  
  access: none (code coming soon) | license: code/data license unspecified (GAP) | descriptive-only: trajectory/motion data only, no language corpus
- **[Phantom](https://arxiv.org/abs/2503.00779)** (CoRL 2025) [hand-pose | ]  
  Trains manipulation from human-only video by converting demos to robot-compatible pairs via hand-pose estimation and visual editing (inpaint arm, overlay robot).  
  access: none (code only, no dataset) | license: code MIT; paper CC BY 4.0 | descriptive-only: code-only human-to-robot pipeline, no language corpus
- **[EgoZero](https://arxiv.org/abs/2505.20290)** (arXiv 2025) [hand-pose | ]  
  Learns closed-loop manipulation from Project Aria smart-glasses human demos with zero robot data, deployed zero-shot on a Franka gripper.  
  access: none (self-collected, not public) | license: code MIT; paper CC BY 4.0 | descriptive-only: policy method, data not public, no language corpus
- **[MotionTrans](https://arxiv.org/abs/2509.17759)** (arXiv 2025) [co-train, hand-pose, corpus | task-instruction]  
  Transfers motion-level skills from VR-collected human demos to robots via a transformation pipeline and weighted human-robot co-training.  
  access: derived-only (HF; NL instructions generated locally) | license: code MIT; HF dataset has no license tag (GAP) | descriptive-only: ~30-task instruction set with local NL augmentation, not a standalone corpus
- **[LAPA (Latent Action Pretraining)](https://arxiv.org/abs/2410.11758)** (ICLR 2025) [vla-pretrain | task-instruction]  
  Unsupervised VLA pretraining that learns discrete latent actions between frames from actionless and human video, then fine-tunes to robot actions.  
  access: derived-only (weights; instructions follow source licenses) | license: code + weights MIT; consumed instruction text follows OXE/SSv2/Bridge (GAP) | descriptive-only: releases weights/code, no downloadable language corpus
- **[MAPLE](https://arxiv.org/abs/2504.06084)** (arXiv 2025) [perception-pretrain, affordance, hand-pose | ]  
  Learns encoder features predicting contact points and grasping hand poses at contact from egocentric images, reused to train dexterous manipulation policies.  
  access: none (visual/kinematic priors, no language) | license: no license file in repo (GAP, default all-rights-reserved) | descriptive-only: contact + hand-pose priors, nothing clusterable

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
