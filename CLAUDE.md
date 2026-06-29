# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The Ego Language-Annotation Atlas: a survey that builds one egocentric human-video
work per entry. Each entry downloads real language annotations, normalizes them,
embeds and clusters the cleaned strings, and renders a single-file offline
interactive HTML atlas (English plus Chinese). `epic-kitchens-100/` is the
reference implementation; copy its shape for new entries. See README.md for the
usage-method and annotation-type taxonomies.

## Commands

```bash
pip install -r requirements.txt

# Build one entry end to end (download -> normalize -> cluster -> render).
# Idempotent: raw downloads and embeddings are cached in <slug>/.cache/.
cd <slug> && python build_<slug>.py
cd <slug> && python build_<slug>.py --force-download   # re-fetch raw annotations

# Run a single stage of an entry (same effect, finer control):
python download_<slug>.py        # also: --force, --cache <dir>
python normalize_<slug>.py
python cluster_<slug>.py         # downloads the sentence encoder on first run
python render_<slug>.py          # writes both HTML atlases

# Regenerate the collection roadmap, then the landing page + README tables.
# Run in this order; the second consumes the first.
python build_roadmap.py
python build_atlas_index.py
```

There is no test framework or linter. To sanity-check a rendered atlas: confirm
it has no external auto-load tags (`<script src=`, `<link`, `cdn.`), that the
embedded JSON blocks parse, and that no em-dash or en-dash appears in visible
text.

## Architecture

**Per-entry pipeline.** Inside `<slug>/`, four stage scripts named
`download_<slug>.py`, `normalize_<slug>.py`, `cluster_<slug>.py`,
`render_<slug>.py` are chained by `build_<slug>.py` via `subprocess` (filenames
are hyphenated and run as scripts, not importable modules). Data flows through
files, not function calls:

- download -> `<slug>/.cache/` (raw CSV/JSON, gitignored) + `download_provenance.json`
- normalize -> `<slug>_annotations.parquet` (one row per annotation unit), `_sample.csv`, `_stats.json`, and `.cache/<slug>_unique.parquet` (deduped narrations, the cluster input)
- cluster -> `<slug>_clusters.json`, `<slug>_scatter.json`, patches `_stats.json`, caches `.cache/<slug>_emb.npy`
- render -> `<slug>_atlas.html` (EN) and `<slug>_atlas_cn.html` (CN)

**Two kinds of entry.** A FULL entry (download -> normalize -> cluster -> render)
has `status: built` in its `atlas_entry.json` and a real cluster atlas. A
DESCRIPTIVE entry (`status: descriptive`) is for works whose language cannot be
downloaded and clustered (gated, no-derivatives, unreleased, or methods that
consume others' annotations): write `<slug>/descriptive.json` (schema in any
existing one, e.g. `r3m/`) and run `python make_descriptive.py <slug>/descriptive.json`,
which renders the same blueprint chrome minus the scatter and writes the manifest.
Both kinds are finished rows in the survey table; only unstarted works in
`roadmap.json` show as planned, and `build_atlas_index.py` auto-drops any roadmap
work that has gained an entry.

**Generated dashboard, do not hand-edit.** `index.html` (English) and
`index_cn.html` (Chinese), plus the README survey and roadmap blocks, are
produced by `build_atlas_index.py`. It scans every `*/atlas_entry.json` manifest
(built and descriptive entries, with counts read from each built entry's
`stats_file`) plus `roadmap.json` (planned entries), then rewrites both index
files and the README content between the `<!-- SURVEY:START -->`/`<!-- SURVEY:END -->`
and `<!-- ROADMAP:START -->`/`<!-- ROADMAP:END -->` markers. The two index files
link to each other with a header language toggle. Editing those
regions by hand will be overwritten. To change the roadmap, edit the `PLANNED`
list in `build_roadmap.py` (its single source of truth), run it, then run
`build_atlas_index.py`. Adding or rebuilding any atlas means re-running
`build_atlas_index.py` so the dashboard does not desync. When two or more
atlases are built, `build_atlas_index.py` also computes the cross-work comparison
(verb-family coverage matrix, granularity contrast, lexical Jaccard overlap) from
each entry's `stats.json`.

**Atlas HTML is self-contained and offline.** All CSS and JS are inline. Cluster,
scatter and stats data are embedded as `<script type="application/json">` blocks
and read with `JSON.parse`; the render step replaces `</` with `<\/` in that JSON
so a stray `</script>` cannot break the page. No CDNs, no fonts, no network. The shared chrome (CSS, JS, header, scatter,
cluster table, sample browser, footer, page assembly) lives in `atlas_lib.py` at
the repo root; each `render_<slug>.py` is a thin wrapper that supplies entry
metadata, work-specific i18n, and the work-specific section bodies (usage path,
granularity, verbs and nouns, and any extra panel such as HD-EPIC's VQA panel).
EN and CN come from the same data via merged i18n dicts, and a header toggle
links the two files. The scatter is a hand-rolled canvas (no chart library): an
offscreen base layer is blitted per frame, hover does a linear nearest-point scan.

**Analysis conventions.** Clustering runs on the unique cleaned narrations
(frequency-weighted), not every row. The sentence-encoder name is a constant at
the top of `cluster_<slug>.py` (currently `all-MiniLM-L6-v2`). Reduction is UMAP
(2D for the plot, low-D for clustering) with a PCA fallback; clustering uses
scikit-learn's built-in `HDBSCAN` (chosen over the standalone `hdbscan` package
to avoid native numba builds on Windows + Python 3.13). Cluster labels are
auto-derived from head verbs and nouns, never written by hand or by an LLM; noise
is its own bucket. The encoder, reducer, clustering params, source commit, and
access date are recorded in each atlas footer.

## Project rules (enforced across the collection)

- Accuracy first: every statistic must trace to downloaded data or a cited
  source. Mark unknowns `n/a`, never guess. Counts must match across the download
  log, the parquet, `_stats.json`, and the atlas.
- House style: no em-dashes or en-dashes in any visible text (atlas, index,
  README). Blueprint aesthetic.
- Example media: every entry's atlas includes an "Example egocentric media" panel
  (prepended to the data-usage path) with an example image or video from the
  paper or project website, so a reader can see the actual ego video. Inline a
  representative frame as a data URI via `atlas_lib.image_to_data_uri` (keeps the
  page offline) only where the dataset license permits; for gated or
  no-derivatives datasets, link to the source instead of embedding. Never emit
  `<img src="http...">` (it breaks the offline rule); external media are anchors
  only.
- License policy: raw annotation text stays in `<slug>/.cache/` (gitignored).
  Commit only derived artifacts, except where a dataset license permits
  redistribution with attribution (EPIC-KITCHENS-100 is CC BY-NC 4.0, so its
  derived text is committed, for non-commercial use, with attribution). Some
  roadmap datasets are gated (Ego4D, Ego-Exo4D) or no-derivatives (EgoDex, which
  may be analyzed locally but whose text must not be redistributed); check
  `roadmap.json` before building one.

## Gotchas

- EPIC `verb`/`noun` columns are fine-grained tokens (hundreds each); the
  canonical 97 verb / 300 noun classes come from `verb_class`/`noun_class` ids
  mapped through the class CSVs to `key` (name) and `category` (semantic group).
  Do not treat the `verb` string as the class label.
- `numpy` is pinned to 2.4.x because numba (a umap-learn dependency) requires
  `<2.5`. See requirements.txt.
- Chained `grep` in a shell `&&` pipeline exits non-zero when there are no
  matches, which is the desired result when checking for external auto-loads.
- Per-entry `stats.json` schemas differ (EPIC uses
  `density.segments_per_hour_labelled` and `hours.total_hours_all_videos`;
  HD-EPIC uses `segments_per_hour_cited` and `annotated_span_hours`).
  `build_atlas_index.py` reads both with fallbacks; a new entry should match one
  schema or extend that fallback.
