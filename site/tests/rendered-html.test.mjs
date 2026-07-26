import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const templateRoot = new URL("../", import.meta.url);

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the AIGCDataHub catalog", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>AIGCDataHub \| 模型背后的数据策略<\/title>/i);
  assert.match(html, /追踪模型/);
  assert.match(html, /Midjourney V8\.2/);
  assert.match(html, /Muse Image/);
  assert.match(html, /FLUX 3/);
  assert.match(html, /SANA-Video 2\.0/);
  assert.match(html, /GraphVid/);
  assert.match(html, /GraphVid-Bench/);
  assert.match(html, /Mage-Flow/);
  assert.match(html, /Omni2Sound/);
  assert.match(html, /SoundAtlas/);
  assert.match(html, /Cap3D/);
  assert.match(html, /AudioCaps 2\.0/);
  assert.match(html, /WavCaps/);
  assert.match(html, /VGGSound-Omni/);
  assert.match(html, /Clotho 2\.1/);
  assert.match(html, /AudioSet/);
  assert.match(html, /VGGSound/);
  assert.match(html, /FSD50K/);
  assert.match(html, /Million Song Dataset/);
  assert.match(html, /FMA/);
  assert.match(html, /Lens-RL-8K/);
  assert.match(html, /ERIA-1K/);
  assert.match(html, /GenSyn10/);
  assert.match(html, /Gemini Omni Flash/);
  assert.match(html, /Gemini 3\.1 Flash-Lite Image/);
  assert.match(html, /GPT Image 2/);
  assert.match(html, /Reve 2\.1/);
  assert.match(html, /MAI-Image-2\.5/);
  assert.match(html, /HappyHorse 1\.1/);
  assert.match(html, /Wan 2\.7/);
  assert.match(html, /Kling AI 3\.0/);
  assert.match(html, /Kling O1/);
  assert.match(html, /Grok Imagine Image/);
  assert.match(html, /HiDream-O1-Image/);
  assert.match(html, /PixVerse V6/);
  assert.match(html, /Vidu Q3 Pro/);
  assert.match(html, /Recraft V4\.1/);
  assert.match(html, /FLUX\.2 \[max\]/);
  assert.match(html, /Veo 3\.1 Lite/);
  assert.match(html, /Avatar V/);
  assert.match(html, /JUST-DUB-IT/);
  assert.match(html, /Audiovisual Translation Dubbing Dataset/);
  assert.match(html, /FIT-VTO-100K/);
  assert.match(html, /Fit-VTO/);
  assert.match(html, /FLUX VTO/);
  assert.match(html, /CtrlVTON/);
  assert.match(html, /VITON-HD-edit/);
  assert.match(html, /TripVVT/);
  assert.match(html, /TripVVT-10K/);
  assert.match(html, /TalkVerse-5B/);
  assert.match(html, /OpenHumanVid-Talking/);
  assert.match(html, /OpenHumanVid/);
  assert.match(html, /Koala-36M/);
  assert.match(html, /FreeMan/);
  assert.match(html, /MVHumanNet\+\+/);
  assert.match(html, /CommonCatalog/);
  assert.match(html, /Fine-T2I/);
  assert.match(html, /GPIC/);
  assert.match(html, /OpenVE-3M/);
  assert.match(html, /OpenVE-Bench/);
  assert.match(html, /CommonCanvas-XL-C/);
  assert.match(html, /OpenVE-Edit/);
  assert.match(html, /HunyuanVideo-Avatar/);
  assert.match(html, /MuseTalk 1\.5/);
  assert.match(html, /FASHN VTON v1\.5/);
  assert.match(html, /HDTF/);
  assert.match(html, /CelebV-HQ/);
  assert.match(html, /TalkVid/);
  assert.match(html, /MV-Fashion/);
  assert.match(html, /应用场景/);
  assert.match(html, /数字人/);
  assert.match(html, /视频翻译/);
  assert.match(html, /Try-On/);
  assert.match(html, /10\/10/);
  assert.match(html, /目录关联/);
  assert.match(html, /模型与数据血缘/);
  assert.match(html, /关系图谱/);
  assert.match(html, /最新数据集/);
  assert.match(html, /模型 · 发布时间/);
  assert.match(html, /行业排行榜/);
  assert.match(html, /来源平台/);
  assert.match(html, /结构化数据集/);
  assert.match(html, /https:\/\/tobinzuo\.github\.io\/AIGCDataHub\/og\.png/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Your site is taking shape/i);
});

test("uses generated catalog data and removes starter preview assets", async () => {
  const [catalog, page, catalogExplorer, layout, packageJson] = await Promise.all([
    readFile(new URL("../app/catalog-data.json", import.meta.url), "utf8"),
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/catalog-explorer.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
  ]);

  assert.match(catalog, /"models"/);
  assert.match(catalog, /"datasets"/);
  assert.match(catalog, /"soundatlas"/);
  assert.match(catalog, /"objaverse-xl"/);
  assert.match(catalog, /"released_at": "2026-05-20"/);
  assert.match(catalog, /"release_date_source"/);
  assert.match(catalog, /"audiocaps-2-0"/);
  assert.match(catalog, /"vggsound-omni"/);
  assert.match(catalog, /"lens-rl-8k"/);
  assert.match(catalog, /"eria-1k"/);
  assert.match(catalog, /"gensyn10"/);
  assert.match(catalog, /"gemini-omni-flash"/);
  assert.match(catalog, /"gemini-3-1-flash-lite-image"/);
  assert.match(catalog, /"gpt-image-2"/);
  assert.match(catalog, /"happyhorse-1-1"/);
  assert.match(catalog, /"rankings"/);
  assert.match(catalog, /"source_platforms"/);
  assert.match(catalog, /"source-platform-not-dataset"/);
  assert.match(catalog, /"name": "YouTube"/);
  assert.match(catalog, /"name": "Shutterstock"/);
  assert.match(catalog, /"name": "SHEIN"/);
  assert.match(catalogExplorer, /把网站来源和可下载数据集分开管理/);
  assert.match(catalog, /"avatar-v"/);
  assert.match(catalog, /"just-dub-it"/);
  assert.match(catalog, /"audiovisual-translation-dub"/);
  assert.match(catalog, /"fit-vto-100k"/);
  assert.match(catalog, /"ctrlvton"/);
  assert.match(catalog, /"viton-hd-edit"/);
  assert.match(catalog, /"tripvvt"/);
  assert.match(catalog, /"tripvvt-10k"/);
  assert.match(catalog, /"talkverse-5b"/);
  assert.match(catalog, /"talkverse"/);
  assert.match(catalog, /"openhumanvid"/);
  assert.match(catalog, /"openhumanvid-talking"/);
  assert.match(catalog, /"clotho-2-1"/);
  assert.match(catalog, /"audioset"/);
  assert.match(catalog, /"vggsound"/);
  assert.match(catalog, /"fsd50k"/);
  assert.match(catalog, /"million-song-dataset"/);
  assert.match(catalog, /"fma"/);
  assert.match(catalog, /"graphvid-bench"/);
  assert.match(catalog, /"sana-video-2-0"/);
  assert.match(catalog, /"mage-flow"/);
  assert.match(catalog, /"koala-36m"/);
  assert.match(catalog, /"mvhumannet-plus-plus"/);
  assert.match(catalog, /"commoncatalog"/);
  assert.match(catalog, /"fine-t2i"/);
  assert.match(catalog, /"gpic"/);
  assert.match(catalog, /"openve-3m"/);
  assert.match(catalog, /"openve-bench"/);
  assert.match(catalog, /"commoncanvas-xl-c"/);
  assert.match(catalog, /"gpic-baselines"/);
  assert.match(catalog, /"openve-edit"/);
  assert.match(catalog, /"hunyuanvideo-avatar"/);
  assert.match(catalog, /"musetalk-1-5"/);
  assert.match(catalog, /"fashn-vton-1-5"/);
  assert.match(catalog, /"hdtf"/);
  assert.match(catalog, /"celebv-hq"/);
  assert.match(catalog, /"talkvid"/);
  assert.match(catalog, /"mv-fashion"/);
  assert.match(catalog, /"relations"/);
  assert.match(catalog, /"dataset_relations"/);
  const parsedCatalog = JSON.parse(catalog);
  assert.equal(parsedCatalog.format_version, 10);
  assert.equal(parsedCatalog.rankings.length, 5);
  assert.equal(parsedCatalog.source_platforms.length, 16);
  assert.equal(
    parsedCatalog.rankings.find((board) => board.id === "text-to-image").entries[0].model_id,
    "gpt-image-2",
  );
  assert.deepEqual(
    parsedCatalog.scenarios.map((scenario) => scenario.id),
    ["image-generation", "video-generation", "digital-human", "video-localization", "virtual-try-on"],
  );
  assert.equal(parsedCatalog.datasets[0].id, "graphvid-bench");
  const models = Object.fromEntries(parsedCatalog.models.map((model) => [model.id, model]));
  assert.deepEqual(
    models.lens.data.datasets.map((dataset) => dataset.catalog_id),
    ["lens-800m", "lens-rl-8k"],
  );
  assert.deepEqual(
    models["ernie-image"].data.datasets.map((dataset) => dataset.catalog_id),
    [null, "eria-1k"],
  );
  assert.deepEqual(
    models["just-dub-it"].data.datasets.map((dataset) => dataset.catalog_id),
    [null, "audiovisual-translation-dub"],
  );
  assert.deepEqual(models.graphvid.linked_dataset_ids, ["graphvid-bench"]);
  assert.deepEqual(models.ctrlvton.linked_dataset_ids, ["viton-hd-edit"]);
  assert.deepEqual(models.tripvvt.linked_dataset_ids, ["tripvvt-10k"]);
  assert.deepEqual(models["talkverse-5b"].linked_dataset_ids, ["talkverse"]);
  assert.deepEqual(models["commoncanvas-xl-c"].linked_dataset_ids, ["commoncatalog"]);
  assert.deepEqual(models["gpic-baselines"].linked_dataset_ids, ["gpic"]);
  assert.deepEqual(models["openve-edit"].linked_dataset_ids, ["openve-3m", "openve-bench"]);
  assert.deepEqual(models["hunyuanvideo-avatar"].linked_dataset_ids, ["hdtf", "celebv-hq"]);
  assert.deepEqual(models["musetalk-1-5"].linked_dataset_ids, ["hdtf"]);
  assert.equal(models["hunyuanvideo-avatar"].monitoring.priority, "critical");
  assert.equal(models["musetalk-1-5"].monitoring.priority, "critical");
  assert.equal(models["fashn-vton-1-5"].monitoring.priority, "critical");
  assert.ok(parsedCatalog.relations.some(
    (relation) => relation.model_id === "graphvid" && relation.dataset_id === "graphvid-bench",
  ));
  assert.ok(parsedCatalog.relations.some(
    (relation) => relation.model_id === "ctrlvton" && relation.dataset_id === "viton-hd-edit",
  ));
  assert.ok(parsedCatalog.relations.some(
    (relation) => relation.model_id === "tripvvt" && relation.dataset_id === "tripvvt-10k",
  ));
  assert.ok(parsedCatalog.relations.some(
    (relation) => relation.model_id === "talkverse-5b" && relation.dataset_id === "talkverse",
  ));
  assert.ok(parsedCatalog.dataset_relations.some(
    (relation) => relation.source_dataset_id === "openhumanvid" && relation.derived_dataset_id === "talkverse",
  ));
  assert.ok(parsedCatalog.dataset_relations.some(
    (relation) => relation.source_dataset_id === "panda-70m" && relation.derived_dataset_id === "talkverse",
  ));
  assert.ok(parsedCatalog.dataset_relations.some(
    (relation) => relation.source_dataset_id === "openhumanvid" && relation.derived_dataset_id === "openhumanvid-talking",
  ));
  assert.ok(parsedCatalog.dataset_relations.some(
    (relation) => relation.source_dataset_id === "yfcc100m" && relation.derived_dataset_id === "commoncatalog",
  ));
  assert.ok(parsedCatalog.dataset_relations.some(
    (relation) => relation.source_dataset_id === "mvhumannet" && relation.derived_dataset_id === "mvhumannet-plus-plus",
  ));
  assert.ok(parsedCatalog.dataset_relations.some(
    (relation) => relation.source_dataset_id === "openve-3m" && relation.derived_dataset_id === "openve-bench",
  ));
  const datasets = Object.fromEntries(parsedCatalog.datasets.map((dataset) => [dataset.id, dataset]));
  assert.equal(datasets["fit-vto-100k"].monitoring.priority, "critical");
  assert.equal(datasets["viton-hd-edit"].monitoring.priority, "critical");
  assert.equal(datasets["tripvvt-10k"].monitoring.priority, "critical");
  assert.equal(datasets.talkverse.monitoring.priority, "critical");
  assert.equal(datasets["openhumanvid-talking"].monitoring.priority, "critical");
  assert.equal(datasets["koala-36m"].monitoring.priority, "critical");
  assert.equal(datasets.freeman.monitoring.priority, "critical");
  assert.equal(datasets.commoncatalog.monitoring.priority, "critical");
  assert.equal(datasets["fine-t2i"].monitoring.priority, "critical");
  assert.equal(datasets.gpic.monitoring.priority, "critical");
  assert.equal(datasets["openve-3m"].monitoring.priority, "critical");
  assert.equal(datasets["openve-bench"].monitoring.priority, "critical");
  assert.equal(datasets.finevideo.monitoring.priority, "high");
  assert.equal(datasets["graphvid-bench"].monitoring, null);
  assert.equal(datasets.hdtf.monitoring.priority, "critical");
  assert.equal(datasets["celebv-hq"].monitoring.priority, "critical");
  assert.equal(datasets.talkvid.monitoring.priority, "critical");
  assert.equal(datasets["mv-fashion"].monitoring.priority, "critical");
  assert.equal(
    datasets.openhumanvid.access.url,
    "https://forms.gle/moqec5Qod7mz9pfD6",
  );
  assert.ok(parsedCatalog.datasets.every((dataset) => /^https?:\/\//.test(dataset.access.url)));
  assert.deepEqual(datasets.talkverse.upstream_dataset_ids, ["openhumanvid", "panda-70m"]);
  assert.deepEqual(
    datasets.openhumanvid.downstream_dataset_ids,
    ["openhumanvid-talking", "talkverse"],
  );
  assert.deepEqual(datasets.yfcc100m.downstream_dataset_ids, ["commoncatalog"]);
  assert.deepEqual(datasets.mvhumannet.downstream_dataset_ids, ["mvhumannet-plus-plus"]);
  assert.deepEqual(datasets["openve-3m"].downstream_dataset_ids, ["openve-bench"]);
  assert.deepEqual(models["fit-vto"].scenario_ids, ["virtual-try-on"]);
  assert.deepEqual(models["flux-vto"].scenario_ids, ["virtual-try-on"]);
  assert.deepEqual(models.ctrlvton.scenario_ids, ["image-generation", "virtual-try-on"]);
  assert.deepEqual(models.tripvvt.scenario_ids, ["video-generation", "virtual-try-on"]);
  assert.deepEqual(
    models["talkverse-5b"].scenario_ids,
    ["video-generation", "digital-human", "video-localization"],
  );
  assert.deepEqual(models["fit-vto"].strategy_profile.stage_names, ["pretraining", "fine-tuning"]);
  assert.equal(models["fit-vto"].strategy_profile.data_reference_count, 3);
  assert.equal(models["fit-vto"].strategy_profile.linked_dataset_count, 1);
  assert.equal(models["flux-vto"].strategy_profile.scale_disclosed_stage_count, 0);
  assert.match(page, /CatalogExplorer/);
  assert.match(catalogExplorer, /StrategyMatrix/);
  assert.match(catalogExplorer, /LineageOverview/);
  assert.match(catalogExplorer, /RankingOverview/);
  assert.match(catalogExplorer, /头部模型不是凭印象补录/);
  assert.match(catalogExplorer, /从上游数据，一路追到衍生集和模型/);
  assert.match(catalogExplorer, /核心监控/);
  assert.match(catalogExplorer, /同场景数据策略对比/);
  assert.match(catalogExplorer, /不做综合评分/);
  assert.match(catalogExplorer, /打开数据卡/);
  assert.match(catalogExplorer, /数据获取入口/);
  assert.match(catalogExplorer, /datasetAccessAction\(dataset\)/);
  assert.match(catalogExplorer, /目录内反向链接只由模型卡/);
  assert.match(catalogExplorer, /DATASET → DATASET/);
  assert.match(catalogExplorer, /上游数据如何形成衍生集/);
  assert.match(layout, /AIGCDataHub/);
  assert.doesNotMatch(layout, /codex-preview|Starter Project/i);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
  await assert.rejects(access(new URL("app/_sites-preview", templateRoot)));
});
