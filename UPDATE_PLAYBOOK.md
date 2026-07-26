# Continuous update playbook

AIGCDataHub is maintained as a living evidence base. Each update cycle covers
the previous 14 days and uses `sources/watchlist.yaml` as a starting point, not
as an exhaustive list.

## Weekly cycle

1. Review the candidate Issue produced by `.github/workflows/discovery.yml`.
   The scanner compares official-source links with
   `sources/discovery-state.json`; it prioritizes image and video generation.
   It also compares stable revisions for selected important models and
   datasets. A changed Hugging Face `lastModified` or repository commit SHA
   requires reviewing access, files, scale, terms, and affected relationships.
   Review `entity_type`, `entity_id`, `priority`, `impacted_dataset_ids`, and
   `impacted_model_ids` first. For a dataset, the scanner follows reviewed
   `derived_from` edges and canonical model-side `catalog_id` references. For a
   model, it reports the model itself and its directly linked catalog datasets.
   The scenario layer explicitly covers digital humans, talking avatars, video
   translation/dubbing, lip sync, virtual try-on, and commerce creatives.
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
5. Distinguish facts from analysis:
   - `strategy`: directly supported by primary evidence;
   - `unknowns`: material information the source does not provide;
   - `watch`: recent preview that should be checked again soon.
6. Run `make readme`, `make site-data`, `make check`, and `make check-links`.
7. Add `updates/YYYY-MM-DD.md` with accepted candidates, already-covered or
   rejected candidates, scope decisions, changed disclosures, and direct
   primary-source links.
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
`model_id`. Hugging Face dataset/model APIs and official GitHub commit APIs are
supported. Do not monitor by URL alone: the canonical ID connects a revision to
the site card and its reviewed relationships.

## Automation boundary

The scheduled workflow may discover links and maintain a review Issue. It may
also report revisions to selected important models and datasets, but it must not create
model or dataset cards, infer a training corpus, change a license conclusion,
advance `last_verified`, merge a PR, or deploy unreviewed data.

## Freshness policy

- `watch` model cards: verify at least every 14 days;
- other model cards: verify at least every 45 days;
- dataset cards: verify at least every 90 days;
- re-check immediately when a model moves from preview to API/open weights, a
  technical report appears, a dataset is withdrawn, or licensing changes.

An unchanged source is still a meaningful result: update `last_verified` only
after actually checking it, never merely to make CI green.
