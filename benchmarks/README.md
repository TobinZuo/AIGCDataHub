# Benchmarks

This directory will hold reproducible comparisons of data-engineering choices,
not model leaderboards alone. Each report should compare at least one meaningful
pipeline decision and disclose the complete execution context.

## Report template

- dataset card ID, version, sample selection, and seed;
- hardware, region/network assumptions, and software versions;
- configuration and commands;
- attempted, accepted, rejected, retried, and failed samples;
- throughput, wall time, CPU/GPU hours, network bytes, and storage amplification;
- per-reason failures and quality distributions before/after processing;
- estimated cost with pricing date and excluded costs;
- known sources of nondeterminism.

The first planned benchmarks are URL downloader concurrency, video decode and
clip extraction, perceptual deduplication, and caption/alignment filtering on
fixed 1K–10K sample manifests.

