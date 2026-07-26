# Dataset audit

The audit recipe inspects a deterministic sample—or a complete small dataset—
without rewriting the source. Its output is a versioned report plus row-level
signals that can be reproduced by another operator.

## Audit dimensions

1. **Access:** retrieval rate, latency, bytes, status codes, and URL decay.
2. **Integrity:** MIME/container validation, decode failures, truncation, and A/V sync.
3. **Distribution:** language, resolution, aspect ratio, duration, FPS, and source domains.
4. **Semantics:** caption length, language confidence, text-media alignment, and OCR overlap.
5. **Visual quality:** sharpness, compression, aesthetics, borders, watermark, and motion.
6. **Redundancy:** exact, perceptual, and near-semantic duplicate rates.
7. **Safety and governance:** NSFW signals, faces/PII indicators, provenance coverage,
   license unknowns, takedown support, and redistribution risk.
8. **Cost:** storage, network traffic, CPU/GPU time, and projected full-corpus cost.

## Reproducibility contract

The report must record dataset version, sample selection seed and algorithm,
tool/model versions, thresholds, hardware, execution time, and failures. Never
report a score without the model/version and decision threshold that produced it.

## Executable manifest audit

The first executable layer audits JSONL or dotted-column CSV manifests without
fetching media. Rows follow
[`schemas/sample-manifest.schema.json`](../../schemas/sample-manifest.schema.json),
and reports follow
[`schemas/audit-report.schema.json`](../../schemas/audit-report.schema.json).

```bash
python3 scripts/audit_manifest.py manifest.jsonl \
  --sample-size 1000 \
  --seed 20260726 \
  --json-out report.json \
  --markdown-out report.md \
  --fail-on-invalid \
  --min-provenance-coverage 0.95
```

Sampling uses a stable SHA-256 bottom-k algorithm, so the selected identities do
not depend on manifest order and memory remains bounded by the requested sample
size. The report covers schema validity, field coverage, duplicate identities,
caption and media distributions, provenance, geometry/duration, and arbitrary
numeric quality fields.

This layer deliberately does not claim that media is reachable, decodable,
safe, aligned, or legally usable. Network, decode, and learned-score probes will
attach to the same report contract in later iterations.
