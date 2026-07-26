# Manifest audit report

- Input: `examples/manifests/tiny-multimodal.jsonl`
- SHA-256: `482332b8919c0ca21cc67a6f86cfc780cfbfca30bccccfebb97d3b3f597f459d`
- Rows parsed: 8 / 8
- Rows selected: 8
- Sampling: `sha256-bottom-k-v1` with seed `20260726`
- Schema-valid rows: 100.0%

## Field coverage

| Field | Present | Coverage |
|---|---:|---:|
| `sample_id` | 8 | 100.0% |
| `media.uri` | 8 | 100.0% |
| `media.sha256` | 8 | 100.0% |
| `media.mime_type` | 8 | 100.0% |
| `caption.text` | 8 | 100.0% |
| `caption.source` | 8 | 100.0% |
| `caption.language` | 8 | 100.0% |
| `provenance.dataset_id` | 8 | 100.0% |
| `provenance.source_url` | 8 | 100.0% |
| `provenance.license` | 8 | 100.0% |
| `provenance.takedown_id` | 8 | 100.0% |
| `provenance.collected_at` | 8 | 100.0% |
| `properties.width` | 8 | 100.0% |
| `properties.height` | 8 | 100.0% |
| `properties.duration_seconds` | 4 | 50.0% |
| `properties.fps` | 4 | 50.0% |
| `provenance.core` | 8 | 100.0% |

## Duplicates

| Identity | Duplicate values | Excess rows |
|---|---:|---:|
| `sample_id` | 0 | 0 |
| `media.uri` | 0 | 0 |
| `media.sha256` | 0 | 0 |

## Key distributions

- **Modality:** image=4, video=4
- **Caption Source:** human=3, model-generated=3, web-metadata=2
- **Caption Language:** en=6, zh=2
- **Media Scheme:** https=4, local=2, s3=2
- **License:** CC-BY-4.0=4, CC-BY-SA-4.0=2, CC0-1.0=2

## Recommendations

- No manifest-level issues triggered; proceed to media access and decode probes.

This report covers manifest metadata only. It does not prove media availability,
decode integrity, safety, semantic alignment, or legal fitness for use.
