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
  assert.match(html, /应用场景/);
  assert.match(html, /数字人/);
  assert.match(html, /视频翻译/);
  assert.match(html, /Try-On/);
  assert.match(html, /10\/10/);
  assert.match(html, /目录关联/);
  assert.match(html, /模型—数据关系/);
  assert.match(html, /模型 ↔ 数据/);
  assert.match(html, /最新数据集/);
  assert.match(html, /最新模型/);
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
  assert.match(catalog, /"relations"/);
  const parsedCatalog = JSON.parse(catalog);
  assert.equal(parsedCatalog.format_version, 6);
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
  const datasets = Object.fromEntries(parsedCatalog.datasets.map((dataset) => [dataset.id, dataset]));
  assert.equal(datasets["fit-vto-100k"].monitoring.priority, "critical");
  assert.equal(datasets["viton-hd-edit"].monitoring.priority, "critical");
  assert.equal(datasets["tripvvt-10k"].monitoring.priority, "critical");
  assert.equal(datasets.talkverse.monitoring.priority, "critical");
  assert.equal(datasets["openhumanvid-talking"].monitoring.priority, "critical");
  assert.equal(datasets.finevideo.monitoring.priority, "high");
  assert.equal(datasets["graphvid-bench"].monitoring, null);
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
  assert.match(catalogExplorer, /模型和数据，不再是两张孤立清单/);
  assert.match(catalogExplorer, /核心监控/);
  assert.match(catalogExplorer, /同场景数据策略对比/);
  assert.match(catalogExplorer, /不做综合评分/);
  assert.match(catalogExplorer, /打开数据卡/);
  assert.match(catalogExplorer, /目录内反向链接只由模型卡/);
  assert.match(layout, /AIGCDataHub/);
  assert.doesNotMatch(layout, /codex-preview|Starter Project/i);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
  await assert.rejects(access(new URL("app/_sites-preview", templateRoot)));
});
