# AIGCDataHub site

This directory contains the optional interactive view for the
[AIGCDataHub GitHub repository](https://github.com/TobinZuo/AIGCDataHub). The
repository indexes remain the source of truth:

- [dataset downloads](../DATASET_ACCESS_INDEX.md)
- [model ↔ dataset relationships](../MODEL_DATASET_INDEX.md)
- [model cards](../models/)
- [dataset cards](../catalog/)

The public static export is deployed only through the repository's
[`pages.yml`](../.github/workflows/pages.yml) workflow to
`https://tobinzuo.github.io/AIGCDataHub/`. The retired
`aigc-datahub-index.zuotongbin.chatgpt.site` preview is not part of the deploy
pipeline and must not be used as a canonical link.

## Prerequisites

- Node.js `>=22.13.0`

## Quick Start

```bash
npm ci
npm run dev
```

## Project shape

- `app/catalog-data.json` is generated from the repository cards by
  `python scripts/build_site_data.py` at the repository root.
- `app/catalog-explorer.tsx` renders the model, dataset, source, ranking, and
  lineage views.
- `next.config.ts` enables a static export with the `/AIGCDataHub` base path
  when `GITHUB_PAGES=true`.
- `tests/pages-export.test.mjs` verifies the exported GitHub Pages artifact.

## Useful Commands

- `npm run dev`: start local development
- `npm run build`: build the vinext server-rendered variant
- `npm test`: build and run rendered-output tests
- `npm run lint`: lint the site
- `GITHUB_PAGES=true npm run pages:build`: create the static export in `out/`
- `npm run pages:test`: build and verify the static export

From the repository root, `make check` validates all generated indexes and
catalog invariants before the site is deployed.
