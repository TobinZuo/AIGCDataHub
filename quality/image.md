# Image data quality

Image quality is multi-dimensional; a single aesthetic or CLIP score cannot
stand in for fitness for use.

| Dimension | Example signals | Typical failure |
|---|---|---|
| Integrity | decode success, MIME, dimensions | corrupt or mislabeled files |
| Visual quality | sharpness, compression, exposure | thumbnails and heavy artifacts |
| Alignment | text-image similarity, object coverage | attractive image with wrong caption |
| Composition | aspect ratio, borders, OCR, watermark | template-heavy or unusable crops |
| Redundancy | exact hash, pHash, embeddings | repeated assets dominating training |
| Safety | content classifiers plus human review | unsafe material or classifier blind spots |
| Provenance | source, collection time, terms | asset cannot be traced or removed |

Thresholds should be selected against a human-reviewed calibration sample and
reported with both acceptance rate and estimated false-positive/negative rates.

