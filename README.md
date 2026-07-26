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
- candidate video, stock-media, studio, and e-commerce source platforms, kept
  separate from downloadable dataset releases;
- scenario-first coverage for image/video generation, digital humans, video
  localization, and virtual try-on;
- data engineering: acquisition, validation, filtering, deduplication,
  recaptioning, sharding, and loading;
- quality and governance: alignment, visual quality, motion, safety, privacy,
  provenance, licensing, and redistribution constraints.

Text-only LLM corpora are intentionally out of scope.

## Latest models and data strategies

Model cards link architecture and release information to the disclosed training
stages, named datasets, source types, curation operations, and material unknowns.
“Undisclosed” is a result: the catalog never invents a training dataset from a
model's capabilities or outputs. The table is sorted by model release date,
newest first.

<!-- BEGIN MODEL CATALOG -->
| Model | Organization | Modalities | Released | Access | Data disclosure | Named datasets | Status |
|---|---|---|---|---|---|---|:---:|
| [Midjourney V8.2](models/image/midjourney-v8-2.yaml) | Midjourney | image | 2026-07-24 | product only | high level | V8.2 personalization ratings and image-selection pool | 👀 |
| [SANA-Video 2.0](models/video/sana-video-2-0.yaml) | NVIDIA | video | 2026-07-23 | research preview | partial | Curated in-house image and video training pool, Gemini-ranked generated video preference pairs | 👀 |
| [GraphVid](models/video/graphvid.yaml) | University of Illinois Urbana-Champaign and Sony Research India | video | 2026-07-23 | announced | partial | LTX-Video base-model training mixture, [GraphVid-Bench](catalog/video/graphvid-bench.yaml) | 👀 |
| [FLUX 3](models/multimodal/flux-3.yaml) | Black Forest Labs | image, video, audio, action | 2026-07-23 | early access | partial | General video training corpus, Human and robot manipulation video corpus, Robot action demonstrations | 👀 |
| [Mage-Flow](models/image/mage-flow.yaml) | Microsoft Mage Team | image | 2026-07-21 | announced | partial | Mage-Flow curated image-text corpus, Mage-Flow-Edit training triples, Mage-Flow capability-routed RL prompt pools | 👀 |
| [Seedream 5.0 Pro](models/image/seedream-5-0-pro.yaml) | ByteDance Seed | image | 2026-07-17 | api only | undisclosed | not disclosed | 👀 |
| [CtrlVTON](models/image/ctrlvton.yaml) | NXN Labs and KAIST | image | 2026-07-10 | announced | partial | FLUX.2 Klein inherited pretraining mixture, VIP-Seg fashion segmentation dataset, CtrlVTON training corpus, [VITON-HD-edit](catalog/image/viton-hd-edit.yaml) | 👀 |
| [Reve 2.1](models/image/reve-2-1.yaml) | Reve | image | 2026-07-09 | api only | undisclosed | not disclosed | 👀 |
| [Muse Video](models/video/muse-video.yaml) | Meta Superintelligence Labs | video, audio | 2026-07-07 | announced | high level | not disclosed | 👀 |
| [Muse Image](models/multimodal/muse-image.yaml) | Meta Superintelligence Labs | image | 2026-07-07 | product only | high level | not disclosed | 👀 |
| [Gemini Omni Flash](models/video/gemini-omni-flash.yaml) | Google DeepMind | video, audio | 2026-06-30 | api only | high level | Undisclosed multimodal training mixture | ✅ |
| [Gemini 3.1 Flash-Lite Image](models/image/gemini-3-1-flash-lite-image.yaml) | Google DeepMind | image | 2026-06-30 | api only | high level | Gemini 3 family multimodal training mixture | ✅ |
| [HappyHorse 1.1](models/video/happyhorse-1-1.yaml) | Alibaba ATH | video, audio | 2026-06-22 | api only | undisclosed | not disclosed | 👀 |
| [Grok Imagine Video 1.5](models/video/grok-imagine-video-1-5.yaml) | xAI | video, audio | 2026-06-16 | api only | undisclosed | not disclosed | 👀 |
| [HiDream-O1-Image-1.5](models/image/hidream-o1-image-1-5.yaml) | HiDream.ai | image | 2026-06-09 | product only | high level | HiDream O1 heterogeneous visual corpus | 🟡 |
| [Reve 2.0](models/image/reve-2.yaml) | Reve | image | 2026-06-03 | api only | undisclosed | not disclosed | 👀 |
| [Ideogram 4.0](models/image/ideogram-4.yaml) | Ideogram | image | 2026-06-03 | gated weights | high level | not disclosed | ✅ |
| [MAI-Image-2.5](models/image/mai-image-2-5.yaml) | Microsoft AI | image | 2026-06-02 | api only | undisclosed | not disclosed | 👀 |
| [Cosmos3-Super-Text2Image](models/image/cosmos3-super-text2image.yaml) | NVIDIA | image | 2026-05-31 | open weights | high level | Cosmos 3 multimodal generator corpus | ✅ |
| [GPIC Baseline Models](models/image/gpic-baselines.yaml) | Stanford Vision Lab and collaborators | image | 2026-05-28 | open weights | partial | [GPIC](catalog/image/gpic.yaml) | 🟡 |
| [FLUX VTO](models/image/flux-vto.yaml) | Black Forest Labs | image | 2026-05-28 | api only | undisclosed | not disclosed | 👀 |
| [Runway Aleph 2.0](models/video/runway-aleph-2.yaml) | Runway | video | 2026-05-21 | product only | undisclosed | not disclosed | 👀 |
| [Lens](models/image/lens.yaml) | Microsoft Research | image | 2026-05-20 | open weights | partial | [Lens-800M](catalog/image/lens-800m.yaml), [Lens-RL-8K](catalog/preference/lens-rl-8k.yaml) | ✅ |
| [Lance](models/multimodal/lance.yaml) | ByteDance | image, video | 2026-05-18 | open weights | high level | not disclosed | ✅ |
| [Recraft V4.1](models/image/recraft-v4-1.yaml) | Recraft | image | 2026-05-14 | api only | undisclosed | not disclosed | 👀 |
| [HiDream-O1-Image](models/image/hidream-o1-image.yaml) | HiDream.ai | image | 2026-05-08 | open weights | partial | HiDream O1 heterogeneous visual corpus | ✅ |
| [Grok Imagine Image Quality](models/image/grok-imagine-image-quality.yaml) | xAI | image | 2026-05-06 | api only | undisclosed | not disclosed | 👀 |
| [Luma UNI 1 Max](models/image/luma-uni-1-max.yaml) | Luma AI | image | 2026-05-05 | api only | high level | Luma UNI creative training corpus | 👀 |
| [TripVVT](models/video/tripvvt.yaml) | Nanjing University, JIUTIAN Research (CMCC), Jilin University, and ByteDance | video | 2026-04-30 | announced | partial | Wan2.1-Fun-14B-control inherited pretraining mixture, TripVVT supplementary training set, [TripVVT-10K](catalog/video/tripvvt-10k.yaml) | ✅ |
| [HappyHorse 1.0](models/video/happyhorse-1-0.yaml) | Alibaba ATH | video, audio | 2026-04-27 | api only | undisclosed | not disclosed | 👀 |
| [GPT Image 2](models/image/gpt-image-2.yaml) | OpenAI | image | 2026-04-21 | api only | undisclosed | not disclosed | 👀 |
| [ERNIE-Image](models/image/ernie-image.yaml) | Baidu | image | 2026-04-15 | open weights | partial | Internal large-scale image pool, [ERIA-1K](catalog/evaluation/eria-1k.yaml) | ✅ |
| [Fit-VTO](models/image/fit-vto.yaml) | University of Washington and Google Research | image | 2026-04-09 | research preview | partial | FLUX.1-dev inherited pretraining mixture, Full FIT training collection, [FIT-VTO-100K](catalog/image/fit-vto-100k.yaml) | ✅ |
| [Avatar V](models/video/avatar-v.yaml) | HeyGen Research | video, audio | 2026-04-08 | product only | partial | Avatar V general video pretraining corpus, Avatar V audio-to-video fine-tuning corpus, Avatar V human preference data | ✅ |
| [Wan 2.7](models/video/wan-2-7.yaml) | Alibaba Cloud | video, audio | 2026-04-03 | api only | undisclosed | not disclosed | 👀 |
| [Veo 3.1 Lite](models/video/veo-3-1-lite.yaml) | Google DeepMind | video | 2026-03-31 | api only | undisclosed | not disclosed | 👀 |
| [PixVerse V6](models/video/pixverse-v6.yaml) | PixVerse | video, audio | 2026-03-30 | api only | undisclosed | not disclosed | 👀 |
| [Gemini 3.1 Flash Image (Nano Banana 2)](models/image/gemini-3-1-flash-image.yaml) | Google DeepMind | image | 2026-02-26 | api only | undisclosed | not disclosed | 👀 |
| [SkyReels V4](models/video/skyreels-v4.yaml) | Skywork AI | video, audio | 2026-02-25 | api only | partial | [LAION (version not specified)](catalog/image/re-laion-5b.yaml), [Flickr](catalog/image/flickr-5b.yaml), [WebVid-10M](catalog/video/webvid-10m.yaml), [Koala-36M](catalog/video/koala-36m.yaml), [OpenHumanVid](catalog/video/openhumanvid.yaml), [Emilia](catalog/audio/emilia.yaml), [AudioSet](catalog/audio/audioset.yaml), [VGGSound](catalog/audio/vggsound.yaml), [SoundNet](catalog/audio/soundnet.yaml), Licensed SkyReels film and web-video corpus, Synthetic multilingual and editing corpora | ✅ |
| [LTX-2.3](models/multimodal/ltx-2-3.yaml) | Lightricks | video, audio | 2026-02-23 | open weights | partial | Audio-informative subset of the LTX-Video training corpus, Higher-quality VAE training subset | ✅ |
| [Seedance 2.0](models/video/seedance-2-0.yaml) | ByteDance Seed | video, audio | 2026-02-12 | api only | undisclosed | not disclosed | 👀 |
| [Qwen-Image 2.0](models/image/qwen-image-2.yaml) | Qwen Team | image | 2026-02-10 | api only | undisclosed | not disclosed | 👀 |
| [JUST-DUB-IT](models/video/just-dub-it.yaml) | Lightricks and Tel Aviv University | video, audio | 2026-02-10 | gated weights | partial | LTX-2 base-model training mixture, [Audiovisual Translation Dubbing Dataset](catalog/video/audiovisual-translation-dub.yaml) | ✅ |
| [Kling AI 3.0](models/video/kling-3.yaml) | Kuaishou Technology | video, audio, image | 2026-02-05 | product only | undisclosed | not disclosed | 👀 |
| [Grok Imagine Video](models/video/grok-imagine-video.yaml) | xAI | video, audio | 2026-01-28 | api only | undisclosed | not disclosed | 👀 |
| [Grok Imagine Image](models/image/grok-imagine-image.yaml) | xAI | image | 2026-01-28 | api only | undisclosed | not disclosed | 👀 |
| [Vidu Q3 Pro](models/video/vidu-q3-pro.yaml) | ShengShu Technology | video, audio | 2026-01-27 | api only | undisclosed | not disclosed | 👀 |
| [HunyuanImage 3.0 Instruct](models/image/hunyuanimage-3-instruct.yaml) | Tencent Hunyuan | image | 2026-01-26 | open weights | partial | Filtered Hunyuan image corpus, Hunyuan interleaved image-pair corpus, Hunyuan reasoning and editing corpora | ✅ |
| [FASHN VTON v1.5](models/image/fashn-vton-1-5.yaml) | FASHN AI | image | 2026-01-19 | open weights | partial | FASHN masked try-on pair pool, FASHN synthetic same-person alternative-garment triplets | ✅ |
| [Veo 3.1](models/video/veo-3-1.yaml) | Google DeepMind | video, audio | 2026-01-13 | api only | high level | Veo 3 multimodal training corpus | ✅ |
| [Omni2Sound](models/multimodal/omni2sound.yaml) | Tsinghua University, Monash University, and Shengshu AI | audio, video | 2026-01-06 | open weights | partial | [AudioCaps](catalog/audio/audiocaps-2-0.yaml), [WavCaps](catalog/audio/wavcaps.yaml), [Clotho](catalog/audio/clotho-2-1.yaml), [AudioSet](catalog/audio/audioset.yaml), [VGGSound](catalog/audio/vggsound.yaml), [FSD50K](catalog/audio/fsd50k.yaml), [Million Song Dataset](catalog/audio/million-song-dataset.yaml), [FMA](catalog/audio/fma.yaml), [SoundAtlas](catalog/audio/soundatlas.yaml), [VGGSound-Omni](catalog/evaluation/vggsound-omni.yaml) | ✅ |
| [TalkVerse-5B](models/video/talkverse-5b.yaml) | CUHK MMLab and Snap Research | video, audio | 2025-12-24 | open weights | partial | Wan2.2-TI2V-5B inherited training mixture, [TalkVerse](catalog/video/talkverse.yaml) | ✅ |
| [Wan 2.6](models/video/wan-2-6.yaml) | Alibaba Cloud | video, audio, image | 2025-12-16 | api only | undisclosed | not disclosed | 👀 |
| [GPT Image 1.5](models/image/gpt-image-1-5.yaml) | OpenAI | image | 2025-12-16 | api only | undisclosed | not disclosed | 👀 |
| [FLUX.2 [max]](models/image/flux-2-max.yaml) | Black Forest Labs | image | 2025-12-16 | api only | undisclosed | not disclosed | 👀 |
| [VideoCoF](models/video/videocof.yaml) | University of Technology Sydney and Zhejiang University | video | 2025-12-08 | open weights | partial | [VideoCoF-50K](catalog/video/videocof-50k.yaml) | ✅ |
| [OpenVE-Edit](models/video/openve-edit.yaml) | Zhejiang University and ByteDance | video | 2025-12-08 | announced | partial | [OpenVE-3M](catalog/video/openve-3m.yaml), [OpenVE-Bench](catalog/evaluation/openve-bench.yaml) | 👀 |
| [Kling O1](models/image/kling-o1.yaml) | Kuaishou Technology | image, video | 2025-12-01 | product only | undisclosed | not disclosed | 👀 |
| [HunyuanVideo 1.5](models/video/hunyuanvideo-1-5.yaml) | Tencent Hunyuan | video | 2025-11-24 | open weights | high level | not disclosed | 🟡 |
| [Gemini 3 Pro Image (Nano Banana Pro)](models/image/gemini-3-pro-image.yaml) | Google DeepMind | image | 2025-11-20 | api only | undisclosed | not disclosed | 👀 |
| [Sora 2](models/video/sora-2.yaml) | OpenAI | video, audio | 2025-09-30 | api only | high level | not disclosed | 🟡 |
| [HuMo-17B](models/multimodal/humo-17b.yaml) | Tsinghua University and ByteDance Intelligent Creation Team | video, audio, image | 2025-09-10 | open weights | partial | [Phantom-Data (Koala-36M release)](catalog/video/phantom-data.yaml), [HuMoSet](catalog/video/humoset.yaml) | ✅ |
| [Runway Aleph](models/video/runway-aleph.yaml) | Runway | video | 2025-07-25 | product only | undisclosed | not disclosed | 👀 |
| [Seedance 1.0 Pro](models/video/seedance-1-0-pro.yaml) | ByteDance Seed | video | 2025-06-11 | api only | high level | Large-scale multi-source video corpus, High-quality video-text SFT mixture, [Seedance 1 Pro Human Preferences](catalog/preference/seedance-1-pro-human-preference.yaml) | 🟡 |
| [HunyuanVideo-Avatar](models/video/hunyuanvideo-avatar.yaml) | Tencent Hunyuan | video, audio | 2025-05-28 | open weights | partial | HunyuanVideo-I2V inherited training mixture, HunyuanVideo-Avatar character-audio training corpus, [HDTF](catalog/video/hdtf.yaml), [CelebV-HQ](catalog/video/celebv-hq.yaml) | ✅ |
| [Phantom-Wan-14B](models/video/phantom-wan-14b.yaml) | ByteDance Intelligent Creation Team | video, image | 2025-05-27 | open weights | partial | [Panda-70M](catalog/video/panda-70m.yaml), In-house video sources, Subject200K, OmniGen paired image data | 🟡 |
| [MuseTalk 1.5](models/video/musetalk-1-5.yaml) | Tencent Music Entertainment Lyra Lab | video, audio | 2025-03-28 | open weights | partial | Stable Diffusion 1.4 inherited training mixture, [HDTF](catalog/video/hdtf.yaml), MuseTalk private talking-face dataset | ✅ |
| [CommonCanvas-XL-C](models/image/commoncanvas-xl-c.yaml) | CommonCanvas collaborators | image | 2024-05-16 | open weights | partial | [CommonCatalog commercial subset](catalog/image/commoncatalog.yaml) | ✅ |
<!-- END MODEL CATALOG -->

Legend: ✅ strategy checked against primary technical sources; 🟡 only part of
the strategy can be verified; 👀 active release to watch for new technical or
data disclosures.

The repository-level [model ↔ dataset audit](MODEL_DATASET_INDEX.md) lists every
named data reference. Public or gated references are required to resolve to a
catalog card; unreleased and undisclosed references explain why no card exists.

## Ranking and release monitoring

The weekly discovery workflow watches ten generated-media boards from two
independent providers. Artificial Analysis contributes five Top 15 snapshots;
Arena contributes the same five tasks through its official public leaderboard
dataset on Hugging Face. Open-weight and closed/API models are treated equally.
Membership or ordering changes trigger review; score-only fluctuations do not.
The generated site maps provider-specific aliases back to canonical model cards
and shows unmatched ranked entries as a persistent review queue. The five
Artificial Analysis boards and five Arena boards all require full Top-15 card
coverage. Any future unmatched entry remains visible in the review queue and
fails the repository coverage check until first-party evidence is verified.

New dataset discovery is not limited to existing cards. Eight Hugging Face API
feeds are sorted by `createdAt` for image generation, video generation,
image-to-video, talking heads, video dubbing, and virtual try-on, alongside the
recent arXiv CS.CV and CS.MM feeds and official project sources. These are
triage signals only: a dataset enters the catalog after its primary source,
release date, access, license, scale, and evidence boundaries are verified.
Hugging Face candidates are retained rather than filtered out, then ordered by
a transparent review-priority score using generative-media relevance, modality,
paper linkage, dataset-card metadata, declared license/scale, and adoption
signals. A high priority is not a quality certification.

## Dataset catalog

The table below is generated from `catalog/**/*.yaml` and sorted by the first
public release date of the exact named version. Edit the data card, not the
generated table. The Access column now links directly to the publisher's data
distribution, URL/downloader, metadata tooling, request form, or availability
notice. For a download-first view of every card, use the
[dataset access and download index](DATASET_ACCESS_INDEX.md).

<!-- BEGIN DATASET CATALOG -->
| Dataset | Organization | Modality | Released | Tasks | Scale | Access | Commercial use | Status |
|---|---|---|---|---|---:|---|---|:---:|
| [GraphVid-Bench](catalog/video/graphvid-bench.yaml) | University of Illinois Urbana-Champaign and Sony Research India | video | 2026-07-23 | graph conditioned video generation, image to video, object interaction generation, video generation evaluation | ~27.5K | [availability notice (unavailable)](https://arxiv.org/abs/2607.21580) | unknown | 🟡 |
| [OpenHumanVid-Talking](catalog/video/openhumanvid-talking.yaml) | Haoson Zhang | video | 2026-07-15 | audio driven avatar, talking head generation, text to video | ~32.2K | [download / browse (open)](https://huggingface.co/datasets/Haosonnn/OpenHumanVid-Talking) | noncommercial | ✅ |
| [VITON-HD-edit](catalog/image/viton-hd-edit.yaml) | NXN Labs and KAIST | image | 2026-07-10 | virtual try on, controllable virtual try on, garment instance segmentation, image editing, virtual try on evaluation | 2K | [download / browse (open)](https://huggingface.co/datasets/NXN-Labs/VITON-HD-edit) | noncommercial | ✅ |
| [GenSyn10](catalog/evaluation/gensyn10.yaml) | University of Western Australia | evaluation | 2026-07-10 | synthetic image detection, image classification, out of distribution evaluation | 60K | [availability notice (unavailable)](https://arxiv.org/abs/2607.16283) | review required | 🟡 |
| [MV-Fashion](catalog/3d/mv-fashion.yaml) | Max Planck Institute for Intelligent Systems and collaborators | 3d | 2026-06-02 | virtual try on, video virtual try on, garment conditioned generation, garment instance segmentation, multi view human reconstruction | 52M | [request access (gated)](https://huggingface.co/datasets/MV-Fashion/MV-Fashion) | noncommercial | 🟡 |
| [MAVEN Multicultural Multiagent Videos](catalog/evaluation/maven-multicultural-video.yaml) | Sichuan University and University of Washington | evaluation | 2026-05-29 | text to video evaluation, multicultural generation evaluation, prompt refinement evaluation | 972 | [download / browse (open)](https://huggingface.co/datasets/AIM-SCU/MAVEN_Multicultura_Text-to-Video_Generation) | allowed | ✅ |
| [GPIC](catalog/image/gpic.yaml) | Stanford Vision Lab and collaborators | image | 2026-05-28 | text to image, image text pretraining, generative model evaluation | 101.2M | [download / browse (gated)](https://huggingface.co/datasets/stanford-vision-lab/gpic) | allowed | ✅ |
| [ERIA-1K](catalog/evaluation/eria-1k.yaml) | Baidu | evaluation | 2026-05-25 | image aesthetic assessment, aesthetic model evaluation | 1K | [availability notice (unavailable)](https://huggingface.co/baidu/ERNIE-Image-Aes) | unknown | 🟡 |
| [Lens-RL-8K](catalog/preference/lens-rl-8k.yaml) | Microsoft Research | preference | 2026-05-20 | text to image reinforcement learning, rubric based reward modeling | ~8K | [availability notice (unavailable)](https://arxiv.org/abs/2605.21573) | unknown | 🟡 |
| [Lens-800M](catalog/image/lens-800m.yaml) | Microsoft Research | image | 2026-05-20 | text to image, image text pretraining | 800M | [availability notice (unavailable)](https://www.microsoft.com/en-us/research/publication/lens-rethinking-training-efficiency-for-foundational-text-to-image-models/) | unknown | 🟡 |
| [FIT-VTO-100K](catalog/image/fit-vto-100k.yaml) | University of Washington and Google Research | image | 2026-05-08 | virtual try on, fit aware generation, garment conditioned generation, virtual try on evaluation | 105K | [download / browse (open)](https://huggingface.co/datasets/Yuanhao-Harry-Wang/fitvto-100k) | noncommercial | ✅ |
| [TripVVT-10K](catalog/video/tripvvt-10k.yaml) | Nanjing University, JIUTIAN Research (CMCC), Jilin University, and ByteDance | video | 2026-04-30 | video virtual try on, virtual try on, garment conditioned generation, video to video, virtual try on evaluation | 10K | [download / browse (gated)](https://huggingface.co/datasets/TripVVT/TripVVT-10K) | noncommercial | ✅ |
| [Fine-T2I](catalog/image/fine-t2i.yaml) | Northeastern University | image | 2026-02-10 | text to image, image text fine tuning, instruction following generation | 6.3M | [download / browse (open)](https://huggingface.co/datasets/ma-xu/fine-t2i) | review required | 🟡 |
| [Audiovisual Translation Dubbing Dataset](catalog/video/audiovisual-translation-dub.yaml) | Lightricks and Tel Aviv University | video | 2026-02-08 | video dubbing, audiovisual translation, lip sync training | 288 | [download / browse (open)](https://huggingface.co/datasets/justdubit/audiovisual_translation_dub) | noncommercial | ✅ |
| [VGGSound-Omni](catalog/evaluation/vggsound-omni.yaml) | Tsinghua University, Monash University, and Shengshu AI | evaluation | 2026-01-06 | text to audio evaluation, video to audio evaluation, video text to audio evaluation, off screen audio evaluation | ~14K | [download / browse (gated)](https://huggingface.co/datasets/Dalision/Omni2Sound_Benchmark) | noncommercial | ✅ |
| [SoundAtlas](catalog/audio/soundatlas.yaml) | Tsinghua University, Monash University, and Shengshu AI | audio | 2026-01-06 | text to audio, video to audio, video text to audio, audio captioning | ~470K | [download / browse (gated)](https://huggingface.co/datasets/Dalision/Omni2Sound_Benchmark) | noncommercial | ✅ |
| [VideoCoF-50K](catalog/video/videocof-50k.yaml) | University of Technology Sydney and Zhejiang University | video | 2026-01-02 | instruction guided video editing, video to video, object removal, object addition, object swap, local style transfer | 49.2K | [download / browse (open)](https://huggingface.co/datasets/XiangpengYang/VideoCoF-50k) | noncommercial | ✅ |
| [TalkVerse](catalog/video/talkverse.yaml) | CUHK MMLab and Snap Research | video | 2026-01-02 | audio driven avatar, talking head generation, image to video | ~2.1M | [metadata / tooling (gated)](https://huggingface.co/datasets/zhenzhiwang/TalkVerse) | noncommercial | 🟡 |
| [HuMoSet](catalog/video/humoset.yaml) | Tsinghua University and ByteDance Intelligent Creation Team | video | 2025-12-23 | multimodal human video generation, audio driven avatar, talking head generation, subject consistent video generation, text image audio to video | ~670K | [download / browse (open)](https://modelscope.cn/datasets/leoniuschen/HuMoSet) | noncommercial | 🟡 |
| [OpenVE-Bench](catalog/evaluation/openve-bench.yaml) | Zhejiang University and ByteDance | evaluation | 2025-12-08 | instruction guided video editing, video editing evaluation | 431 | [download / browse (open)](https://huggingface.co/datasets/Lewandofski/OpenVE-Bench) | noncommercial | ✅ |
| [OpenVE-3M](catalog/video/openve-3m.yaml) | Zhejiang University and ByteDance | video | 2025-12-08 | instruction guided video editing, video to video, text guided video editing | ~3M | [download / browse (open)](https://huggingface.co/datasets/Lewandofski/OpenVE-3M) | noncommercial | ✅ |
| [Phantom-Data (Koala-36M release)](catalog/video/phantom-data.yaml) | ByteDance Intelligent Creation Lab | video | 2025-09-30 | subject consistent video generation, reference image conditioned video, identity preservation | ~1M | [metadata / tooling (metadata only)](https://huggingface.co/datasets/ZhuoweiChen/Phantom-data-Koala36M) | noncommercial | 🟡 |
| [SpatialVID](catalog/video/spatialvid.yaml) | Nanjing University and Institute of Automation, Chinese Academy of Sciences | video | 2025-09-18 | camera controlled video generation, world modeling, video to 3d, camera pose estimation, novel view synthesis | ~2.7M | [request access (gated)](https://huggingface.co/datasets/SpatialVID/SpatialVID) | noncommercial | 🟡 |
| [TalkVid](catalog/video/talkvid.yaml) | FreedomIntelligence | video | 2025-08-19 | talking head generation, audio driven avatar, multilingual avatar video, lip sync training, talking head evaluation | 500 | [metadata / tooling (metadata only)](https://huggingface.co/datasets/FreedomIntelligence/TalkVid) | noncommercial | 🟡 |
| [Seedance 1 Pro Human Preferences](catalog/preference/seedance-1-pro-human-preference.yaml) | Rapidata | preference | 2025-08-08 | image to video evaluation, video generation preference, pairwise model comparison | 198 | [download / browse (open)](https://huggingface.co/datasets/Rapidata/image-to-video-human-preference-seedance-1-pro) | review required | ✅ |
| [TalkingHeadBench](catalog/evaluation/talkingheadbench.yaml) | University of North Carolina at Chapel Hill and Michigan State University | evaluation | 2025-05-15 | talking head deepfake detection, audio visual deepfake detection, cross generator generalization | 5.3K | [download / browse (open)](https://huggingface.co/datasets/luchaoqi/TalkingHeadBench) | review required | 🟡 |
| [MVHumanNet++](catalog/3d/mvhumannet-plus-plus.yaml) | GAP-Lab, CUHK-Shenzhen | 3d | 2025-05-03 | digital human, 3d avatar generation, human digitization, multi view human reconstruction | ~645M | [request access (gated)](https://github.com/GAP-LAB-CUHK-SZ/MVHumanNet_plusplus) | noncommercial | 🟡 |
| [AudioCaps 2.0](catalog/audio/audiocaps-2-0.yaml) | Seoul National University | audio | 2025-02-24 | audio captioning, text to audio, audio language pretraining, text to audio evaluation | 98.6K | [request access (gated)](https://github.com/cdjkim/audiocaps/tree/master/dataset2.0) | noncommercial | 🟡 |
| [VideoUFO](catalog/video/videoufo.yaml) | ReLER Lab, University of Technology Sydney | video | 2025-02-18 | text to video, video text pretraining, user focused video generation | 1.1M | [download / browse (open)](https://huggingface.co/datasets/WenhaoWang/VideoUFO) | allowed | ✅ |
| [Señorita-2M](catalog/video/senorita-2m.yaml) | CUHK, PolyU, Tsinghua University, IntelliFusion, HKU, and UESTC | video | 2025-02-10 | instruction guided video editing, video to video, local video editing, global video editing | ~2M | [download / browse (open)](https://huggingface.co/datasets/SENORITADATASET/Senorita) | noncommercial | 🟡 |
| [OpenHumanVid](catalog/video/openhumanvid.yaml) | Fudan University and collaborators | video | 2024-11-28 | text to video, video text pretraining, human centric video generation, pose conditioned generation | ~13.2M | [request access (gated)](https://forms.gle/moqec5Qod7mz9pfD6) | noncommercial | 🟡 |
| [Koala-36M](catalog/video/koala-36m.yaml) | Kling AI Research | video | 2024-10-10 | text to video, video text pretraining | ~36M | [URLs / downloader (metadata only)](https://huggingface.co/datasets/Koala-36M/Koala-36M-v1) | unknown | 🟡 |
| [FineVideo](catalog/video/finevideo.yaml) | Hugging Face | video | 2024-09-23 | video understanding, text to video | ~43K | [download / browse (gated)](https://huggingface.co/datasets/HuggingFaceFV/finevideo) | review required | ✅ |
| [Re-LAION-5B](catalog/image/re-laion-5b.yaml) | LAION | image | 2024-08-30 | image text pretraining, text to image | ~5.8B | [URLs / downloader (open)](https://laion.ai/blog/relaion-5b/) | review required | 🟡 |
| [Emilia](catalog/audio/emilia.yaml) | Amphion / OpenMMLab | audio | 2024-08-27 | text to speech, speech generation pretraining, automatic speech recognition, audio language pretraining | unknown | [download / browse (open)](https://huggingface.co/datasets/amphion/Emilia-Dataset) | noncommercial | 🟡 |
| [Flickr 5B metadata](catalog/image/flickr-5b.yaml) | hlky / bigdata-pw | image | 2024-08-15 | image text pretraining, text to image, image retrieval, geospatial image analysis | ~5B | [URLs / downloader (metadata only)](https://huggingface.co/datasets/bigdata-pw/Flickr) | review required | 🟡 |
| [OpenVid-1M](catalog/video/openvid-1m.yaml) | Nanjing University PCALab | video | 2024-07-02 | text to video, image to video | ~1M | [download / browse (open)](https://huggingface.co/datasets/nkp37/OpenVid-1M) | noncommercial | ✅ |
| [MVHumanNet](catalog/3d/mvhumannet.yaml) | GAP-Lab, CUHK-Shenzhen | 3d | 2024-05-07 | digital human, 3d avatar generation, text driven human image generation, human nerf reconstruction | ~645M | [request access (gated)](https://github.com/GAP-LAB-CUHK-SZ/MVHumanNet) | noncommercial | 🟡 |
| [Panda-70M](catalog/video/panda-70m.yaml) | Snap Research | video | 2024-02-29 | text to video, video text pretraining | 70.7M | [metadata / tooling (open)](https://github.com/snap-research/Panda-70M) | review required | ✅ |
| [CommonCatalog](catalog/image/commoncatalog.yaml) | CommonCanvas collaborators | image | 2023-10-25 | text to image, image text pretraining | 67M | [download / browse (open)](https://huggingface.co/common-canvas) | review required | ✅ |
| [Pick-a-Pic v2](catalog/preference/pick-a-pic-v2.yaml) | Tel Aviv University and Meta AI | preference | 2023-09-25 | text to image preference, reward modeling | ~1M | [download / browse (gated)](https://huggingface.co/datasets/yuvalkirstain/pickapic_v2) | review required | 🟡 |
| [FreeMan](catalog/3d/freeman.yaml) | CUHK-Shenzhen, Tencent, and IDEA | 3d | 2023-09-10 | 3d human pose estimation, human motion reconstruction, digital human | ~11.3M | [request access (gated)](https://wangjiongw.github.io/freeman/download.html) | noncommercial | 🟡 |
| [InternVid](catalog/video/internvid.yaml) | OpenGVLab | video | 2023-07-13 | video text pretraining, text to video | ~234M | [metadata / tooling (open)](https://huggingface.co/datasets/OpenGVLab/InternVid) | review required | 🟡 |
| [Objaverse-XL](catalog/3d/objaverse-xl.yaml) | Allen Institute for AI | 3d | 2023-07-11 | 3d pretraining, image to 3d, text to 3d, novel view synthesis | ~10M | [URLs / downloader (open)](https://github.com/allenai/objaverse-xl) | review required | 🟡 |
| [JourneyDB](catalog/image/journeydb.yaml) | CUHK MMLab and Shanghai AI Laboratory | image | 2023-07-03 | text to image, generative image understanding, evaluation | 4.4M | [request access (gated)](https://journeydb.github.io/) | review required | 🟡 |
| [Cap3D](catalog/3d/cap3d.yaml) | University of Michigan | 3d | 2023-06-12 | text to 3d, image to 3d, 3d text pretraining, novel view synthesis | 1.6M | [download / browse (open)](https://huggingface.co/datasets/tiange/Cap3D) | review required | ✅ |
| [DataComp-1B](catalog/image/datacomp-1b.yaml) | DataComp research consortium | image | 2023-04-27 | image text pretraining | ~1B | [URLs / downloader (open)](https://github.com/mlfoundations/datacomp) | review required | 🟡 |
| [WavCaps](catalog/audio/wavcaps.yaml) | Centre for Vision, Speech and Signal Processing, University of Surrey | audio | 2023-03-30 | audio captioning, audio text retrieval, text to audio, audio language pretraining | ~403.1K | [download / browse (open)](https://huggingface.co/datasets/cvssp/WavCaps) | noncommercial | 🟡 |
| [COYO-700M](catalog/image/coyo-700m.yaml) | Kakao Brain | image | 2022-08-30 | image text pretraining, text to image | ~700M | [URLs / downloader (open)](https://huggingface.co/datasets/kakaobrain/coyo-700m) | review required | 🟡 |
| [CelebV-HQ](catalog/video/celebv-hq.yaml) | CUHK MMLab and SenseTime Research | video | 2022-07-25 | talking head generation, audio driven avatar, face video generation, talking head evaluation | 35.7K | [URLs / downloader (metadata only)](https://github.com/CelebV-HQ/CelebV-HQ) | noncommercial | 🟡 |
| [WebVid-10M](catalog/video/webvid-10m.yaml) | University of Oxford VGG | video | 2022-05-13 | video text pretraining, text to video | ~10M | [availability notice (unavailable)](https://github.com/m-bain/webvid) | noncommercial | 🗄️ |
| [Clotho 2.1](catalog/audio/clotho-2-1.yaml) | Tampere University | audio | 2021-05-26 | audio captioning, audio text retrieval, text to audio, audio language pretraining | 7K | [download / browse (open)](https://zenodo.org/records/4783391) | noncommercial | 🟡 |
| [HDTF](catalog/video/hdtf.yaml) | University of Science and Technology of China and Microsoft Research Asia | video | 2021-03-28 | talking head generation, audio driven avatar, lip sync training, talking head evaluation | ~362 | [URLs / downloader (metadata only)](https://github.com/MRzzm/HDTF) | review required | 🟡 |
| [FSD50K](catalog/audio/fsd50k.yaml) | Music Technology Group, Universitat Pompeu Fabra | audio | 2020-10-02 | audio event classification, audio language pretraining, audio representation learning, text to audio | 51.2K | [download / browse (open)](https://zenodo.org/records/4060432) | review required | ✅ |
| [VGGSound](catalog/audio/vggsound.yaml) | Visual Geometry Group, University of Oxford | audio | 2020-04-29 | audio event classification, audio visual learning, video to audio, audio language pretraining | ~210K | [URLs / downloader (metadata only)](https://github.com/hche11/VGGSound) | review required | 🟡 |
| [FMA](catalog/audio/fma.yaml) | École Polytechnique Fédérale de Lausanne | audio | 2017-05-09 | music generation pretraining, music information retrieval, music tagging, genre classification | ~106.6K | [download / browse (open)](https://github.com/mdeff/fma) | review required | ✅ |
| [AudioSet](catalog/audio/audioset.yaml) | Google Research | audio | 2017-03-30 | audio event classification, audio language pretraining, audio representation learning, text to audio | ~2.1M | [URLs / downloader (metadata only)](https://research.google.com/audioset/download.html) | review required | 🟡 |
| [SoundNet Flickr video dataset](catalog/audio/soundnet.yaml) | Massachusetts Institute of Technology | audio | 2016-10-28 | audio visual learning, audio representation learning, audio event classification, video to audio | ~2M | [download / browse (open)](https://projects.csail.mit.edu/soundnet/) | review required | 🟡 |
| [YFCC100M](catalog/image/yfcc100m.yaml) | Yahoo Labs and collaborators | image | 2015-03-05 | image text pretraining, video text pretraining, multimedia retrieval | ~100M | [metadata / tooling (metadata only)](https://multimediacommons.wordpress.com/yfcc100m-core-dataset/) | review required | 🟡 |
| [Million Song Dataset](catalog/audio/million-song-dataset.yaml) | The Echo Nest and LabROSA, Columbia University | audio | 2011-02-08 | music information retrieval, music representation learning, music metadata modeling, music recommendation | 1M | [availability notice (unavailable)](https://github.com/tbertinmahieux/MSongsDB) | review required | 🗄️ |
<!-- END DATASET CATALOG -->

Legend: ✅ verified against primary sources; 🟡 partially verified or contains
material unknowns; 🗄️ archived or unavailable from the original distributor.

## Candidate content-source platforms

The [source-platform index](SOURCE_PLATFORM_INDEX.md) tracks 16 candidate
content surfaces referenced for image/video data planning. Each entry separates
the public content scope from the documented API, partner portal, or licensed
delivery path, and records access requirements plus a monitored official
interface. An interface is not a dataset download action and does not grant
permission to crawl, train, commercialize, or redistribute its content.
Non-public operational assessments are intentionally excluded from this public
repository.

## What is in this repository?

| Layer | Content | Question answered |
|---|---|---|
| Catalog | Machine-readable dataset cards | What data exists and is it accessible? |
| Models | Model cards linked to datasets and training stages | What data strategy produced each model? |
| Scenarios | Task-derived application taxonomy shared by the generated site | Which models and datasets support a concrete workflow? |
| Source platforms | Candidate acquisition surfaces with explicit access and rights boundaries | Which websites may be relevant without pretending they are datasets? |
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
make dataset-access-index # regenerate every dataset access/download link
make source-platform-index # regenerate the candidate website/source index
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
updates one GitHub Issue when it finds new candidates, source failures, or an
important model or dataset revision. For selected Hugging Face repositories it
records both `lastModified` and the commit SHA, so changed weights or data are
surfaced even when the URL stays the same. Selected official GitHub repositories
are tracked by commit date and SHA through the same contract. Every important
revision probe declares either a dataset `catalog_id` or model `model_id` plus a
monitoring priority. Dataset changes propagate through derived datasets into
affected models; model changes list the model's directly linked catalog
datasets. It closes the Issue when the queue is clear.
Refreshing the reviewed baseline fails closed when any watched source is
unreachable, so a transient outage cannot be accepted as the new normal. An
explicit `--allow-failures` override exists only for reviewed, intentional
exceptions.
Fifty-four of the 55 cataloged datasets now have an independent revision probe. The
only exception is Flickr 5B metadata: its current Hugging Face repository
requires authentication, so the catalog preserves the access boundary instead
of reporting an unauthenticated failure as a working monitor. Every other
dataset referenced by a model has a dedicated official probe.
Ranking entries that do not yet resolve to a verified model card also keep the
Issue open, so newly ranked closed or open models cannot disappear between
weekly scans. Arena snapshots use its official Hugging Face leaderboard dataset
rather than a bot-protected web page.
All 40 distinct model cards represented by the current 133 leaderboard seats
have their own official revision probe, regardless of whether the model is open
weight, API-only, product-only, or only announced. Revision-only model and
dataset probes do not emit navigation links as discovery candidates; broader
provider feeds remain responsible for finding new releases.

The same workflow checks all 16 candidate source platforms through their
official API documentation, partner portal, licensed-service terms, or a
conservative availability probe when no public data interface is cataloged.
HTML content revisions hash normalized visible text rather than scripts,
styles, hydration payloads, or build attributes, preventing dynamic page noise
from opening false review items.
This is triage rather than automatic fact generation: a card, license
conclusion, or `last_verified` date changes only through a reviewed PR.

The application taxonomy in [sources/scenarios.yaml](sources/scenarios.yaml)
maps card tasks to stable scenario IDs. The generated site uses those IDs for
the same filters across model, dataset, and data-strategy views. Each generated
model record also includes a source-bound `strategy_profile` derived directly
from its stages, source types, data references, scale disclosures, and recorded
unknowns. Selecting one scenario in the strategy view exposes those fields in a
cross-model matrix without adding an inferred score.

Model-to-dataset relationships have one canonical source: a model data
reference with a non-null `catalog_id`. Site generation converts those reviewed
references into a relation index plus model and dataset backlinks, so users can
use the dedicated **关系图谱** view or navigate in either direction without
maintaining two editable copies. Dataset derivation is separate and equally
explicit: a child card's `derived_from` entries identify its reviewed upstream
`catalog_id`, relationship type, contribution, and evidence boundary. Site
generation creates the dataset-to-dataset relation index and symmetric upstream
and downstream backlinks. Model and dataset cards covered by the revision
scanner also expose their monitoring tier and probe source. A dataset card's
`evidence.used_by` remains an upstream claim and is never silently promoted to
a canonical model relationship.

The latest evidence review is recorded in
[updates/2026-07-27.md](updates/2026-07-27.md), including accepted releases,
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
