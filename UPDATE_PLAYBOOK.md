# Continuous update playbook

AIGCDataHub is maintained as a living evidence base. Each update cycle covers
the previous 14 days and uses `sources/watchlist.yaml` as a starting point, not
as an exhaustive list.

## Weekly cycle

1. Search official organization blogs, repositories, model/dataset cards, and
   new technical reports for image, video, audio, 3D, unified generation, and
   physical-AI releases.
2. Create a candidate list with release date, primary source, modality, access,
   and whether any training-data information is actually disclosed.
   Treat `released_at` as the first public date of the exact named version and
   retain its primary evidence in `release_date_source`.
3. De-duplicate candidates against `catalog/**/*.yaml` and `models/**/*.yaml`.
4. Add or update cards. Connect named datasets through `catalog_id`; keep
   unavailable internal corpora as named model-card entries or standalone
   unavailable dataset cards when the corpus itself is an important result.
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

## Freshness policy

- `watch` model cards: verify at least every 14 days;
- other model cards: verify at least every 45 days;
- dataset cards: verify at least every 90 days;
- re-check immediately when a model moves from preview to API/open weights, a
  technical report appears, a dataset is withdrawn, or licensing changes.

An unchanged source is still a meaningful result: update `last_verified` only
after actually checking it, never merely to make CI green.
