# Video data quality

Video audits extend image checks across time and add motion, editing, and decode
stability. Sample-level metrics should distinguish the source video from each
derived clip.

| Dimension | Example signals | Typical failure |
|---|---|---|
| Integrity | ffprobe/decode success, A/V sync | truncated or unsupported media |
| Spatial quality | resolution, sharpness, compression | upscaled or highly compressed clips |
| Temporal quality | frame freezes, jitter, consistency | duplicated frames and broken motion |
| Motion | optical flow, camera/object motion | static slides or chaotic transitions |
| Alignment | caption coverage across the clip | text describes one brief frame only |
| Editing | shot count, fades, hard cuts | multi-shot clips unsuitable for generation |
| Overlays | subtitles, logos, watermarks, borders | text-dominated or branded footage |
| Provenance | source video and timestamps | clip cannot be attributed or removed |

Duration, FPS, and motion should be reported as distributions. Mean values hide
the long tails that dominate storage and training instability.

