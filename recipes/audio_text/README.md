# Audio–text and audiovisual data recipe

This recipe turns public audio or video references into a traceable corpus for
text-to-audio, video-to-audio, or joint video-text-to-audio training. The order
follows the failure boundaries exposed by SoundAtlas while remaining
implementation-neutral.

## 1. Snapshot provenance and rights

- Store the upstream dataset, object ID, source URL, fetch time, and media hash.
- Keep dataset-level terms separate from the underlying clip's rights.
- Record tombstones instead of silently replacing unavailable clips.

## 2. Decode and normalize

- Validate container duration, audio stream presence, channel count, and sample rate.
- Decode to one canonical training rate without discarding the original metadata.
- Reject silence, clipping, corrupt streams, and implausible duration mismatches.

## 3. Route by audiovisual consistency

- Score whether the audible events are supported by the visual stream.
- Route high-consistency clips to audiovisual captioning and audio-only clips to
  an audio-first path; retain the routing score as metadata.
- Do not treat off-screen sound as an automatic error.

## 4. Generate grounded captions

- Compress useful visual evidence into a short intermediate description.
- Generate an initial caption that identifies sound events, sources, ambience,
  speech or music, and temporal order.
- Escalate low-confidence or conflicting cases to a stronger reviewer model.
- Version prompts, models, and decoding settings for every generated annotation.

## 5. Filter and audit

- Combine audio-text similarity with audiovisual-text consistency checks.
- Audit temporal claims separately from semantic nouns and scene descriptions.
- Deduplicate by media hash and near-duplicate embeddings before splitting.
- Keep a rejected-sample ledger with reason codes and threshold versions.

## 6. Package for training

- Store queryable metadata and scores in Parquet; use WebDataset shards when
  sequential media throughput matters.
- Preserve stable sample IDs across re-captioning runs.
- Split by source item before producing clips to avoid near-duplicate leakage.
- Publish counts at every stage: discovered, fetched, decoded, captioned,
  filtered, deduplicated, and admitted.

The recipe is not a license grant. Re-run the rights and availability audit for
the exact upstream snapshot used by a training run.

