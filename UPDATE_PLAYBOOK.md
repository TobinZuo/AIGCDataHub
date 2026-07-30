# Continuous update playbook

AIGCDataHub is maintained as a living evidence base. Each daily update cycle
covers the previous 7 days and uses `sources/watchlist.yaml` as a starting
point, not as an exhaustive list.

## Daily cycle

1. Review the candidate Issue produced by `.github/workflows/discovery.yml`.
   The scanner compares official-source links with
   `sources/discovery-state.json`; it prioritizes image and video generation.
   It also compares stable revisions for selected important models and
   datasets. A changed Hugging Face `lastModified`, repository commit SHA, or
   content hash of an official page/PDF requires reviewing access, files,
   scale, terms, and affected relationships.
   Review `entity_type`, `entity_id`, `priority`, `impacted_dataset_ids`, and
   `impacted_model_ids` first. For a dataset, the scanner follows reviewed
   `derived_from` edges and canonical model-side `catalog_id` references. For a
   model, it reports the model itself and its directly linked catalog datasets.
   The scenario layer explicitly covers digital humans, talking avatars, video
   translation/dubbing, lip sync, virtual try-on, and commerce creatives.
   Five Artificial Analysis and five Arena leaderboards are snapshotted to Top
   15; review a ranking alert when membership or ordering changes, regardless of
   whether the model is open-weight or closed. Arena data comes from the
   provider's public `lmarena-ai/leaderboard-dataset` latest splits. Unmapped
   ranked entries remain in the Issue as coverage gaps even when the ranking
   order does not change. Eight Hugging Face dataset API feeds sorted by
   creation time provide a separate new-release queue for the same scenarios.
   Every candidate remains visible and receives a high, standard, or low review
   priority from explicit metadata signals. Treat that value as triage order,
   not dataset-quality evidence.
   Seventeen Hugging Face model API feeds provide the parallel broad-discovery
   queue for image/video generation and editing, digital humans/localization,
   virtual try-on, directly related audio-video models, and 3D generation.
   Standalone releases are prioritized from pipeline, paper, license, weight,
   and adoption signals. LoRA/adapters, quantized mirrors, wrappers, and demos
   remain visible but are explicitly demoted so they are not treated as new
   foundation-model releases.
   GitHub API revision probes use the workflow token rather than the anonymous
   rate limit. A connection reset, TLS error, or other source-level network
   failure is recorded for review without aborting the remaining source scan.
   All entries in `sources/source-platforms.yaml` contribute a monitor for an
   official API, partner portal, licensed-service page, or an availability-only
   endpoint. Review platform alerts for access scope, authorization, license,
   policy, and interface lifecycle changes; never treat an API as training
   permission.
   Search beyond the generated candidates when an official organization uses a
   new domain, publishes only through a feed, or changes an existing model card.
2. Create a candidate list with release date, primary source, modality, access,
   and whether any training-data information is actually disclosed.
   Treat `released_at` as the first public date of the exact named version and
   retain its primary evidence in `release_date_source`.
3. De-duplicate candidates against `catalog/**/*.yaml` and `models/**/*.yaml`.
4. Add or update cards. Connect named datasets through `catalog_id`; keep
   unavailable internal corpora as named model-card entries or standalone
   unavailable dataset cards when the corpus itself is an important result.
   If a task belongs to a maintained application scenario, confirm its mapping
   in `sources/scenarios.yaml` instead of adding front-end-only filter logic.
   Treat model-side `catalog_id` as the canonical relationship record. The site
   generator derives `relations`, `linked_dataset_ids`, and `linked_model_ids`;
   never hand-maintain a second backlink. Dataset `evidence.used_by` is an
   editorial claim from upstream evidence, not a substitute for `catalog_id`.
   For dataset derivation, put `derived_from` only on the child card. The site
   generator derives `dataset_relations`, `upstream_dataset_ids`, and
   `downstream_dataset_ids`; unknown parents, duplicates, self-links, and cycles
   fail validation.
   Candidate website sources belong in `sources/source-platforms.yaml`, not in
   `catalog/`. A homepage is never labeled as a dataset download, and public
   entries must exclude non-public operational assessments. Each platform keeps
   an explicit access profile and monitor plus a required rights-review boundary
   until source-specific permissions are independently established.
5. Distinguish facts from analysis:
   - `strategy`: directly supported by primary evidence;
   - `unknowns`: material information the source does not provide;
   - `watch`: recent preview that should be checked again soon.
6. Run `make readme`, `make model-data-index`, `make site-data`, `make check`,
   and `make check-links`.
7. Add `updates/YYYY-MM-DD.md` with accepted candidates, already-covered or
   rejected candidates, scope decisions, changed disclosures, and direct
   primary-source links. Every meaningful update must begin with a
   paired `## 中文摘要` and `## English Summary` sections, each containing
   exactly six reader-facing dimensions in
   this order: `### 模型`, `### 数据集`, `### 数据关系`, `### 排行榜`,
   `### 监控`, and `### 未披露`, mirrored by `### Models`, `### Datasets`,
   `### Data relations`, `### Rankings`, `### Monitoring`, and
   `### Undisclosed`. Write one concise conclusion per locale and dimension;
   use “无变化” / “No change” when appropriate. Under every Chinese dimension,
   add exactly one `页面定位：` line; under its English counterpart add exactly
   one `Page links:` line. Both must contain the same Pages targets, translated
   labels, and direct links to affected cards or views. The public changelog is
   generated from these summaries, supports Chinese/English switching, and does
   not expose the full technical log by default. Treat language as a shared
   site preference: place the switch in the common header, apply it to both the
   catalog and changelog, and preserve the selection during in-site navigation.
   Generic homepage-only links are not sufficient when a specific card exists.
8. Summarize new models, new datasets, changed disclosures, broken links, and
   stale cards for the reviewer.
9. After every generated candidate is accepted or rejected, run
   `make discovery-accept` and include the reviewed baseline change in the same
   PR. This prevents reviewed links from reappearing without treating them as
   accepted catalog facts.

When adding an important revision probe, use a structured object with an
official HTTPS API `url` and `priority: critical|high|standard`. Dataset probes
belong in `important-dataset-updates` and require an existing `catalog_id`;
model probes belong in `important-model-updates` and require an existing
`model_id`. Hugging Face dataset/model APIs and official GitHub commit APIs
expose stable revision identifiers. For publishers without such an API, the
scanner records a SHA-256 content revision of the official page or PDF. HTML
revisions are derived from normalized visible text and metadata, excluding
scripts, styles, hydration payloads, and markup-only build changes; PDFs and
other binaries retain a byte-level hash. Do not monitor an important model or
dataset by URL alone: the canonical ID connects a revision to the site card and
its reviewed relationships. An access-controlled source that always returns
401 to anonymous CI stays linked from its card but is not presented as a
healthy revision probe.

Source-platform monitors are generated from `sources/source-platforms.yaml`.
Use `content-revision` for stable official documentation or terms and
`availability` only when a public interface is not cataloged or the portal is
consistently access-controlled. Availability accepts 401, 403, 405, and 429 as
proof that the official surface still exists, but a 404 or 410 remains a
failure. Every platform access profile must state that the interface itself
does not grant model-training rights.

Ranking sources belong in `industry-model-rankings` and require a unique
`ranking_id` plus provider, label, modality, parser, score/date labels, coverage
policy, public page URL, and `ranking_limit`. Use `required` only when every
tracked seat already resolves to a verified model card; use `monitor` to retain
unmapped ranked models in the review queue. A leaderboard is authoritative only
for its own observed ranking; model release, access, and data-strategy facts
still need first-party evidence. Dataset discovery feeds belong in
`dataset-release-feeds`; their candidates are never accepted as catalog facts
without primary-source review. Candidate priority may use API metadata but must
never be presented as a quality or licensing conclusion.
Model discovery feeds belong in `model-release-feeds` and follow the same
review boundary. A Hugging Face repository is a discovery signal, not proof of
the publisher, release date, architecture, license, or training-data strategy.

## Automation boundary

The scheduled GitHub workflow may discover links and maintain a review Issue.
It may also report revisions to selected important models, datasets, and source
platform access surfaces, but it must not create cards, infer a training
corpus, change a license conclusion, advance `last_verified`, merge a PR, or
deploy unreviewed data.

The user-controlled Codex automation runs separately at 10:00 Asia/Shanghai in
an isolated worktree. It may edit cards and push `master` only after it has
reviewed primary evidence, recorded every candidate disposition, rebuilt the
generated indexes, accepted a failure-free discovery baseline, and passed the
repository, link, lint, server-render, and GitHub Pages export checks. It never
force-pushes. No material change means no empty commit and no synthetic
`last_verified` update.

## Freshness policy

- The default review date is calculated in `Asia/Shanghai`, independent of the
  CI host timezone. Use `--today YYYY-MM-DD` for deterministic historical audits.
- `watch` model cards: verify at least every 14 days;
- other model cards: verify at least every 45 days;
- dataset cards: verify at least every 90 days;
- re-check immediately when a model moves from preview to API/open weights, a
  technical report appears, a dataset is withdrawn, or licensing changes.

An unchanged source is still a meaningful result: update `last_verified` only
after actually checking it, never merely to make CI green.
