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
  assert.match(html, /<title>AIGCDataHub — 模型背后的数据策略<\/title>/i);
  assert.match(html, /追踪模型/);
  assert.match(html, /Midjourney V8\.2/);
  assert.match(html, /Muse Image/);
  assert.match(html, /FLUX 3/);
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
  assert.match(html, /10\/10/);
  assert.match(html, /目录关联/);
  assert.match(html, /最新数据集/);
  assert.match(html, /最新模型/);
  assert.match(html, /结构化数据集/);
  assert.match(html, /https:\/\/aigc-datahub-index\.zuotongbin\.chatgpt\.site\/og\.png/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Your site is taking shape/i);
});

test("uses generated catalog data and removes starter preview assets", async () => {
  const [catalog, page, layout, packageJson] = await Promise.all([
    readFile(new URL("../app/catalog-data.json", import.meta.url), "utf8"),
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
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
  assert.match(catalog, /"clotho-2-1"/);
  assert.match(catalog, /"audioset"/);
  assert.match(catalog, /"vggsound"/);
  assert.match(catalog, /"fsd50k"/);
  assert.match(catalog, /"million-song-dataset"/);
  assert.match(catalog, /"fma"/);
  const parsedCatalog = JSON.parse(catalog);
  assert.equal(parsedCatalog.format_version, 2);
  assert.equal(parsedCatalog.datasets[0].id, "lens-800m");
  assert.match(page, /CatalogExplorer/);
  assert.match(layout, /AIGCDataHub/);
  assert.doesNotMatch(layout, /codex-preview|Starter Project/i);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
  await assert.rejects(access(new URL("app/_sites-preview", templateRoot)));
});
