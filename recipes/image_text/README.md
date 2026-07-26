# Image-text pipeline

This recipe defines the minimum reproducible path from URL-backed or hosted
image metadata to training-ready shards. It is tool-agnostic by design: an
implementation may use img2dataset, NeMo Curator, Ray Data, Spark, or a local
runner as long as it preserves the same observable contract.

## Inputs

- stable sample ID;
- image URL or object-store reference;
- original text and its source;
- dataset version, source page, and license/provenance fields;
- optional hashes and upstream quality signals.

## Pipeline

```text
manifest
  -> fetch with bounded retries
  -> decode and MIME verification
  -> resolution/aspect-ratio filtering
  -> exact and perceptual deduplication
  -> safety/OCR/watermark signals
  -> caption normalization or recaptioning
  -> text-image alignment and visual-quality scores
  -> deterministic split and sharding
  -> manifest, statistics, and rejection ledger
```

Every filter should emit a reason code instead of silently dropping samples.
Keep original metadata immutable; derived captions and scores belong in new,
versioned columns.

## Minimum output schema

| Field | Purpose |
|---|---|
| `sample_id` | Stable identity independent of shard placement |
| `media` | Encoded bytes or durable object reference |
| `caption_original` | Unmodified upstream text |
| `caption_derived` | Optional recaptioned text with model/version |
| `sha256` / `phash` | Integrity and deduplication signals |
| `width`, `height`, `mime` | Decode and bucketing metadata |
| `quality.*` | Named, versioned scores rather than one opaque score |
| `provenance.*` | Source URL, crawl time, terms, and takedown identity |

## Required report

Report attempted, fetched, decoded, accepted, and rejected counts; bytes and
wall time; retry distribution; rejection reasons; duplicate rate; and score
distributions before and after filtering. A dataset count without a failure
ledger is not reproducible for URL-backed corpora.

