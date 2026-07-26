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
- Do not copy marketing claims into a `verified` card without evidence.

## Model and data-strategy card requirements

- Prefer a technical report, official model card, repository, and release post;
  a third-party summary is not primary evidence.
- Record each disclosed training stage separately. Do not collapse pretraining,
  SFT, preference optimization, and distillation into one vague paragraph.
- Link named datasets to `catalog_id` when a catalog card exists. A named but
  unreleased corpus should still be recorded with `availability: not-released`.
- Set `exact_datasets_disclosed` and `exact_mixture_disclosed` independently.
  A paper can describe a strong strategy while withholding source identities.
- Put every material gap in `data.unknowns`; never infer a source from model
  behavior, a benchmark table, or a similar model from the same organization.
- Use `watch` for a recent preview whose technical details are still changing.

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
make site-data
make check
```

The generated catalogs in `README.md` and `site/app/catalog-data.json` must be
committed with changed dataset or model cards. Link checks run separately because
remote sites can be transient.

## Recipes and benchmarks

A recipe should declare its inputs, outputs, configurable decisions, quality
checks, and observable metrics. Benchmark submissions should include hardware,
software versions, sample selection, failure policy, and enough commands or
configuration to reproduce the result.
