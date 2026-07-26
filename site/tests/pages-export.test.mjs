import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const siteRoot = new URL("../", import.meta.url);

test("exports a self-contained GitHub Pages site under the repository base path", async () => {
  const html = await readFile(new URL("out/index.html", siteRoot), "utf8");

  assert.match(html, /AIGCDataHub/);
  assert.match(html, /AudioSet/);
  assert.match(html, /Million Song Dataset/);
  assert.match(html, /Lens-RL-8K/);
  assert.match(html, /ERIA-1K/);
  assert.match(html, /10\/10/);
  assert.match(html, /\/AIGCDataHub\/_next\/static\//);
  assert.match(html, /https:\/\/tobinzuo\.github\.io\/AIGCDataHub\/og\.png/);

  await access(new URL("out/og.png", siteRoot));
  await access(new URL("out/favicon.svg", siteRoot));
});
