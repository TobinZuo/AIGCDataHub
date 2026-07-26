# AIGCDataHub

> A reproducible data engineering hub for multimodal generative AI.

AIGCDataHub is a living, structured catalog of AIGC datasets, models, training
data strategies, processing recipes, governance notes, and engineering
benchmarks. It is built for practitioners who need to answer not only “what is
new?”, but also “what data did the model use, how was it processed, what remains
undisclosed, and can the strategy be reproduced?”.

**[Open the searchable AIGCDataHub index on GitHub Pages](https://tobinzuo.github.io/AIGCDataHub/)**

> [!IMPORTANT]
> A dataset being publicly downloadable does not imply that every underlying
> media asset can be used for training, commercial purposes, or redistribution.
> Each data card separates metadata terms from media rights and records unknowns
> explicitly. This repository is an engineering reference, not legal advice.

## Scope

The current scope covers:

- current image, video, audio-video, unified multimodal, and physical-AI models;
- the public, gated, internal, synthetic, and undisclosed data behind each model;
- image, video, audio, 3D, and preference datasets;
- data engineering: acquisition, validation, filtering, deduplication,
  recaptioning, sharding, and loading;
- quality and governance: alignment, visual quality, motion, safety, privacy,
  provenance, licensing, and redistribution constraints.

Digital-human coverage will expand as verified cards are added. Text-only LLM
corpora are intentionally out of scope.

## Latest models and data strategies

Model cards link architecture and release information to the disclosed training
stages, named datasets, source types, curation operations, and material unknowns.
“Undisclosed” is a result: the catalog never invents a training dataset from a
model's capabilities or outputs.

<!-- BEGIN MODEL CATALOG -->
| Model | Organization | Modalities | Released | Access | Data disclosure | Named datasets | Status |
|---|---|---|---|---|---|---|:---:|
| [Midjourney V8.2](models/image/midjourney-v8-2.yaml) | Midjourney | image | 2026-07-24 | product only | high level | V8.2 personalization ratings and image-selection pool | 👀 |
| [FLUX 3](models/multimodal/flux-3.yaml) | Black Forest Labs | image, video, audio, action | 2026-07-23 | early access | partial | General video training corpus, Human and robot manipulation video corpus, Robot action demonstrations | 👀 |
| [Muse Video](models/video/muse-video.yaml) | Meta Superintelligence Labs | video, audio | 2026-07-07 | announced | high level | not disclosed | 👀 |
| [Muse Image](models/multimodal/muse-image.yaml) | Meta Superintelligence Labs | image | 2026-07-07 | product only | high level | not disclosed | 👀 |
| [Gemini Omni Flash](models/video/gemini-omni-flash.yaml) | Google DeepMind | video, audio | 2026-06-30 | api only | high level | Undisclosed multimodal training mixture | ✅ |
| [Gemini 3.1 Flash-Lite Image](models/image/gemini-3-1-flash-lite-image.yaml) | Google DeepMind | image | 2026-06-30 | api only | high level | Gemini 3 family multimodal training mixture | ✅ |
| [Lens](models/image/lens.yaml) | Microsoft Research | image | 2026-05-20 | open weights | partial | [Lens-800M](catalog/image/lens-800m.yaml), [Lens-RL-8K](catalog/preference/lens-rl-8k.yaml) | ✅ |
| [Lance](models/multimodal/lance.yaml) | ByteDance | image, video | 2026-05-18 | open weights | high level | not disclosed | ✅ |
| [ERNIE-Image](models/image/ernie-image.yaml) | Baidu | image | 2026-04-15 | open weights | partial | Internal large-scale image pool, [ERIA-1K](catalog/evaluation/eria-1k.yaml) | ✅ |
| [Avatar V](models/video/avatar-v.yaml) | HeyGen Research | video, audio | 2026-04-08 | product only | partial | Avatar V general video pretraining corpus, Avatar V audio-to-video fine-tuning corpus, Avatar V human preference data | ✅ |
| [LTX-2.3](models/multimodal/ltx-2-3.yaml) | Lightricks | video, audio | 2026-02-23 | open weights | partial | Audio-informative subset of the LTX-Video training corpus, Higher-quality VAE training subset | ✅ |
| [Seedance 2.0](models/video/seedance-2-0.yaml) | ByteDance Seed | video, audio | 2026-02-12 | api only | undisclosed | not disclosed | 👀 |
| [JUST-DUB-IT](models/video/just-dub-it.yaml) | Lightricks and Tel Aviv University | video, audio | 2026-02-10 | gated weights | partial | LTX-2 base-model training mixture, [Audiovisual Translation Dubbing Dataset](catalog/video/audiovisual-translation-dub.yaml) | ✅ |
| [Omni2Sound](models/multimodal/omni2sound.yaml) | Tsinghua University, Monash University, and Shengshu AI | audio, video | 2026-01-06 | open weights | partial | [AudioCaps](catalog/audio/audiocaps-2-0.yaml), [WavCaps](catalog/audio/wavcaps.yaml), [Clotho](catalog/audio/clotho-2-1.yaml), [AudioSet](catalog/audio/audioset.yaml), [VGGSound](catalog/audio/vggsound.yaml), [FSD50K](catalog/audio/fsd50k.yaml), [Million Song Dataset](catalog/audio/million-song-dataset.yaml), [FMA](catalog/audio/fma.yaml), [SoundAtlas](catalog/audio/soundatlas.yaml), [VGGSound-Omni](catalog/evaluation/vggsound-omni.yaml) | ✅ |
| [HunyuanVideo 1.5](models/video/hunyuanvideo-1-5.yaml) | Tencent Hunyuan | video | 2025-11-24 | open weights | high level | not disclosed | 🟡 |
<!-- END MODEL CATALOG -->

Legend: ✅ strategy checked against primary technical sources; 🟡 only part of
the strategy can be verified; 👀 active release to watch for new technical or
data disclosures.

## Dataset catalog

The table below is generated from `catalog/**/*.yaml` and sorted by the first
public release date of the exact named version. Edit the data card, not the
generated table.

<!-- BEGIN DATASET CATALOG -->
| Dataset | Organization | Modality | Released | Tasks | Scale | Access | Commercial use | Status |
|---|---|---|---|---|---:|---|---|:---:|
| [GenSyn10](catalog/evaluation/gensyn10.yaml) | University of Western Australia | evaluation | 2026-07-10 | synthetic image detection, image classification, out of distribution evaluation | 60K | unavailable | review required | 🟡 |
| [ERIA-1K](catalog/evaluation/eria-1k.yaml) | Baidu | evaluation | 2026-05-25 | image aesthetic assessment, aesthetic model evaluation | 1K | unavailable | unknown | 🟡 |
| [Lens-RL-8K](catalog/preference/lens-rl-8k.yaml) | Microsoft Research | preference | 2026-05-20 | text to image reinforcement learning, rubric based reward modeling | ~8K | unavailable | unknown | 🟡 |
| [Lens-800M](catalog/image/lens-800m.yaml) | Microsoft Research | image | 2026-05-20 | text to image, image text pretraining | 800M | unavailable | unknown | 🟡 |
| [FIT-VTO-100K](catalog/image/fit-vto-100k.yaml) | University of Washington and Google Research | image | 2026-05-08 | virtual try on, fit aware generation, garment conditioned generation, virtual try on evaluation | 105K | open | noncommercial | ✅ |
| [Audiovisual Translation Dubbing Dataset](catalog/video/audiovisual-translation-dub.yaml) | Lightricks and Tel Aviv University | video | 2026-02-08 | video dubbing, audiovisual translation, lip sync training | 288 | open | noncommercial | ✅ |
| [VGGSound-Omni](catalog/evaluation/vggsound-omni.yaml) | Tsinghua University, Monash University, and Shengshu AI | evaluation | 2026-01-06 | text to audio evaluation, video to audio evaluation, video text to audio evaluation, off screen audio evaluation | ~14K | gated | noncommercial | ✅ |
| [SoundAtlas](catalog/audio/soundatlas.yaml) | Tsinghua University, Monash University, and Shengshu AI | audio | 2026-01-06 | text to audio, video to audio, video text to audio, audio captioning | ~470K | gated | noncommercial | ✅ |
| [AudioCaps 2.0](catalog/audio/audiocaps-2-0.yaml) | Seoul National University | audio | 2025-02-24 | audio captioning, text to audio, audio language pretraining, text to audio evaluation | 98.6K | gated | noncommercial | 🟡 |
| [FineVideo](catalog/video/finevideo.yaml) | Hugging Face | video | 2024-09-23 | video understanding, text to video | ~43K | gated | review required | ✅ |
| [Re-LAION-5B](catalog/image/re-laion-5b.yaml) | LAION | image | 2024-08-30 | image text pretraining, text to image | ~5.8B | open | review required | 🟡 |
| [OpenVid-1M](catalog/video/openvid-1m.yaml) | Nanjing University PCALab | video | 2024-07-02 | text to video, image to video | ~1M | open | noncommercial | ✅ |
| [Panda-70M](catalog/video/panda-70m.yaml) | Snap Research | video | 2024-02-29 | text to video, video text pretraining | 70.7M | open | review required | ✅ |
| [Pick-a-Pic v2](catalog/preference/pick-a-pic-v2.yaml) | Tel Aviv University and Meta AI | preference | 2023-09-25 | text to image preference, reward modeling | ~1M | gated | review required | 🟡 |
| [InternVid](catalog/video/internvid.yaml) | OpenGVLab | video | 2023-07-13 | video text pretraining, text to video | ~234M | open | review required | 🟡 |
| [Objaverse-XL](catalog/3d/objaverse-xl.yaml) | Allen Institute for AI | 3d | 2023-07-11 | 3d pretraining, image to 3d, text to 3d, novel view synthesis | ~10M | open | review required | 🟡 |
| [JourneyDB](catalog/image/journeydb.yaml) | CUHK MMLab and Shanghai AI Laboratory | image | 2023-07-03 | text to image, generative image understanding, evaluation | 4.4M | gated | review required | 🟡 |
| [Cap3D](catalog/3d/cap3d.yaml) | University of Michigan | 3d | 2023-06-12 | text to 3d, image to 3d, 3d text pretraining, novel view synthesis | 1.6M | open | review required | ✅ |
| [DataComp-1B](catalog/image/datacomp-1b.yaml) | DataComp research consortium | image | 2023-04-27 | image text pretraining | ~1B | open | review required | 🟡 |
| [WavCaps](catalog/audio/wavcaps.yaml) | Centre for Vision, Speech and Signal Processing, University of Surrey | audio | 2023-03-30 | audio captioning, audio text retrieval, text to audio, audio language pretraining | ~403.1K | open | noncommercial | 🟡 |
| [COYO-700M](catalog/image/coyo-700m.yaml) | Kakao Brain | image | 2022-08-30 | image text pretraining, text to image | ~700M | open | review required | 🟡 |
| [WebVid-10M](catalog/video/webvid-10m.yaml) | University of Oxford VGG | video | 2022-05-13 | video text pretraining, text to video | ~10M | unavailable | noncommercial | 🗄️ |
| [Clotho 2.1](catalog/audio/clotho-2-1.yaml) | Tampere University | audio | 2021-05-26 | audio captioning, audio text retrieval, text to audio, audio language pretraining | 7K | open | noncommercial | 🟡 |
| [FSD50K](catalog/audio/fsd50k.yaml) | Music Technology Group, Universitat Pompeu Fabra | audio | 2020-10-02 | audio event classification, audio language pretraining, audio representation learning, text to audio | 51.2K | open | review required | ✅ |
| [VGGSound](catalog/audio/vggsound.yaml) | Visual Geometry Group, University of Oxford | audio | 2020-04-29 | audio event classification, audio visual learning, video to audio, audio language pretraining | ~210K | metadata only | review required | 🟡 |
| [FMA](catalog/audio/fma.yaml) | École Polytechnique Fédérale de Lausanne | audio | 2017-05-09 | music generation pretraining, music information retrieval, music tagging, genre classification | ~106.6K | open | review required | ✅ |
| [AudioSet](catalog/audio/audioset.yaml) | Google Research | audio | 2017-03-30 | audio event classification, audio language pretraining, audio representation learning, text to audio | ~2.1M | metadata only | review required | 🟡 |
| [Million Song Dataset](catalog/audio/million-song-dataset.yaml) | The Echo Nest and LabROSA, Columbia University | audio | 2011-02-08 | music information retrieval, music representation learning, music metadata modeling, music recommendation | 1M | unavailable | review required | 🗄️ |
<!-- END DATASET CATALOG -->

Legend: ✅ verified against primary sources; 🟡 partially verified or contains
material unknowns; 🗄️ archived or unavailable from the original distributor.

## What is in this repository?

| Layer | Content | Question answered |
|---|---|---|
| Catalog | Machine-readable dataset cards | What data exists and is it accessible? |
| Models | Model cards linked to datasets and training stages | What data strategy produced each model? |
| Recipes | Reproducible processing blueprints | How does raw media become training data? |
| Quality | Metrics, filters, and audit guidance | Is the data good enough? |
| Governance | License, privacy, safety, and provenance | May the data be used or redistributed? |
| Benchmarks | Throughput, failure rate, cost, and quality deltas | Which pipeline is worth running? |

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
make check
```

Useful commands:

```bash
make validate      # schema, duplicate ID, and file-name checks
make readme        # regenerate this catalog table
make site-data     # regenerate the searchable site's catalog payload
make check-links   # verify primary-source links (network required)
make audit-example # regenerate the manifest audit example
```

## Add a dataset or model

1. Copy a nearby card from `catalog/<modality>/`.
2. For a model, copy a card from `models/<primary-modality>/` and record every
   disclosed training stage plus the unknowns.
3. Use primary sources for scale, access, strategy, and license claims.
4. Separate metadata licensing from underlying media rights.
5. Run `make readme site-data && make check`.
6. Open a pull request and describe what was verified.

See [CONTRIBUTING.md](CONTRIBUTING.md), the
[dataset schema](schemas/dataset.schema.json), and the
[model/data-strategy schema](schemas/model.schema.json) for the complete
contract.

## Continuous updates

The [watchlist](sources/watchlist.yaml) defines modalities, topics, and official
sources to review each week. The [update playbook](UPDATE_PLAYBOOK.md) defines
the evidence and freshness policy. `make freshness` fails when a `watch` model
has not been rechecked for 14 days, another model for 45 days, or a dataset for
90 days.

The weekly discovery workflow compares image/video-related links from those
watched sources with a reviewed baseline. Its application tracks include
digital humans, talking avatars, video translation and dubbing, lip sync,
virtual try-on, and commerce-oriented conditional generation. It opens or
updates one GitHub Issue when it finds new candidates or source failures, and
closes the Issue when the queue is clear. This is triage rather than automatic
fact generation: a card, license conclusion, or `last_verified` date changes
only through a reviewed PR.

The latest evidence review is recorded in
[updates/2026-07-26.md](updates/2026-07-26.md), including accepted releases,
scope decisions, and disclosures that remain unknown.

Freshness dates are evidence, not bookkeeping: update `last_verified` only after
checking the primary source.

## Roadmap

- **v0.1:** structured dataset catalog, validation, generated README, core recipes;
- **v0.2:** living model/data-strategy tracker, freshness monitoring, and executable manifest audits;
- **v0.3:** searchable model, dataset, and data-strategy site generated from the same YAML cards;
- **v0.4:** audio and 3D dataset coverage plus richer model-to-dataset lineage;
- **v0.5:** digital-human, video-localization, and virtual-try-on coverage plus reproducible cross-model data-strategy comparisons;
- **later:** organization-specific adapters and pipeline benchmarks on shared snapshots.

## License

Repository code and original documentation are licensed under Apache-2.0.
Individual datasets retain their own terms; inclusion here does not relicense
them.
