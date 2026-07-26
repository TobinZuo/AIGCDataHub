# Video-text pipeline

Video corpora are expensive to reconstruct and easy to make irreproducible.
This recipe therefore treats source identity, timestamps, codec normalization,
and failure accounting as first-class data.

## Inputs

- source video ID and retrievable location;
- caption, transcript, or other text with provenance;
- optional clip boundaries and upstream quality signals;
- source terms, attribution, and takedown identifier.

## Pipeline

```text
manifest
  -> download and checksum
  -> ffprobe validation
  -> shot detection / semantic clip selection
  -> clip extraction with timestamp ledger
  -> decode sampling and A/V integrity checks
  -> static, low-motion, black-border, subtitle, and watermark signals
  -> captioning or recaptioning with model/version
  -> text-video alignment, visual quality, and temporal consistency
  -> deterministic split and duration/resolution buckets
  -> sharding, index, and audit report
```

Do not transcode repeatedly. Preserve the original asset or checksum and derive
a canonical training encoding once. Capture `ffmpeg`/`ffprobe` versions because
decode behavior can change across builds.

## Minimum output schema

- `sample_id`, `source_video_id`, `start_ms`, `end_ms`;
- original and derived captions with provenance;
- codec, container, FPS, duration, width, height, and audio presence;
- exact/perceptual hashes and source checksum;
- motion, alignment, aesthetic, watermark, subtitle, safety, and temporal scores;
- source terms, attribution, collection time, and takedown identity;
- accepted/rejected state with a stable reason code.

## Required report

Include source and clip counts, total duration, download/decode success, duration
and resolution histograms, motion distribution, caption coverage, duplicate
rate, storage amplification, CPU/GPU hours, throughput, and rejection reasons.

