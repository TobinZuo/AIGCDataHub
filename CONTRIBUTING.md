# Contributing to AIGCDataHub

Contributions should make dataset selection or data engineering more
reproducible. A smaller verified contribution is preferred to a large list of
unreviewed links.

## Dataset card requirements

- Use the canonical project or dataset name for `name` and a stable kebab-case
  identifier for `id`.
- Record the maintaining `organization`, the first public `released_at` date,
  and a primary `release_date_source`. For a named version, use that version's
  release rather than the original dataset family's paper date.
- Link to a maintainer-owned repository, project page, paper, or dataset card.
- Record the date on which access and terms were checked.
- Treat repository code licenses, metadata licenses, and underlying media rights
  as separate claims.
- Use `unknown` or `review_required` where a primary source is silent.
- Put important caveats in `license.notes` or `quality.known_limitations`.
- When a primary source explicitly identifies an upstream catalog dataset, add
  one `derived_from` entry with its `catalog_id`, relationship type,
  contribution, and evidence-bounded notes. Do not infer lineage from similar
  tasks, overlapping names, or an `evidence.used_by` claim.
- Keep dataset lineage acyclic. Generated upstream/downstream backlinks and the
  top-level dataset relation index must not be hand-edited.
- Do not copy marketing claims into a `verified` card without evidence.

## Model and data-strategy card requirements

- Prefer a technical report, official model card, repository, and release post;
  a third-party summary is not primary evidence.
- Record each disclosed training stage separately. Do not collapse pretraining,
  SFT, preference optimization, and distillation into one vague paragraph.
- Link named datasets to `catalog_id` when a catalog card exists. A named but
  unreleased corpus should still be recorded with `availability: not-released`.
  Public or gated references without a catalog card fail validation. Regenerate
  `MODEL_DATASET_INDEX.md` so every unresolved reference states its evidence
  boundary.
- Use model-side `catalog_id` as the only editable model-to-dataset relation.
  Generated dataset backlinks and the top-level site relation index must not be
  hand-edited. `evidence.used_by` records an upstream statement, not a canonical
  backlink.
- Set `exact_datasets_disclosed` and `exact_mixture_disclosed` independently.
  A paper can describe a strong strategy while withholding source identities.
- Put every material gap in `data.unknowns`; never infer a source from model
  behavior, a benchmark table, or a similar model from the same organization.
- Use `watch` for a recent preview whose technical details are still changing.

## Application scenario taxonomy

- Keep card `tasks` factual and specific; do not add a task solely to make a
  model appear under a desired filter.
- Map supported tasks to stable scenario IDs in `sources/scenarios.yaml`.
- A scenario shown on the site must match at least one model and one dataset so
  users can compare capability, training strategy, and reusable data together.
- Add a new scenario only when it has durable meaning across organizations, not
  for a single product name or marketing phrase.

## Status definitions

- `verified`: scale, access, and licensing fields were checked against primary
  sources and material caveats are documented.
- `partial`: the entry is useful, but one or more important fields remain
  uncertain or source-dependent.
- `archived`: the original source is withdrawn, unavailable, or intentionally
  preserved only as historical context.

## Development workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
make readme
make model-data-index
make site-data
make check
```

The generated catalogs in `README.md` and `site/app/catalog-data.json` must be
committed with changed dataset, model, or scenario sources. Link checks run
separately because remote sites can be transient.

Important revision probes live under `important-dataset-updates` or
`important-model-updates` in `sources/watchlist.yaml`. Each probe must use an
official HTTPS `url`, a `priority` of `critical`, `high`, or `standard`, and
exactly one existing canonical ID: dataset `catalog_id` or model `model_id`.
The scanner derives downstream or linked impacts from reviewed card
relationships; do not maintain impact lists in the watchlist.

## Recipes and benchmarks

A recipe should declare its inputs, outputs, configurable decisions, quality
checks, and observable metrics. Benchmark submissions should include hardware,
software versions, sample selection, failure policy, and enough commands or
configuration to reproduce the result.
