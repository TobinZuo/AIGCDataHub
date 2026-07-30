"use client";

import Link from "next/link";
import { useState } from "react";
import { SiteHeader } from "../site-header";

type Locale = "zh" | "en";
type Localized = Record<Locale, string>;
type SummaryDimension = {
  id: string;
  label: Localized;
  text: Localized;
  links: Array<{ label: Localized; href: string }>;
};
type Entry = {
  date: string;
  title: Localized;
  summary: SummaryDimension[];
  source_path: string;
};
type Changelog = {
  dimensions: Array<{ id: string; label: Localized }>;
  entries: Entry[];
};

const githubRoot = "https://github.com/TobinZuo/AIGCDataHub/blob/master/";
const copy = {
  zh: {
    status: "更新记录",
    kicker: "每日维护",
    headlineTop: "今天更新了",
    headlineAccent: "什么？",
    description: "先看模型、数据集和数据关系发生了什么，再看排行榜、监控状态与仍未披露的信息。",
    back: "返回数据目录",
    overview: "变更记录概览",
    latestUpdate: "最近更新",
    batches: "更新批次",
    dimensions: "总结维度",
    evidenceNote: "每个批次先给结论，再保留原始核验记录作为证据，方便快速阅读和深入追溯。",
    browse: "按日期查看",
    summary: "更新摘要",
    summaryNote: "每期固定从六个维度总结。没有变化会直接写明，不用从技术日志里寻找结论。",
    sixDimensions: "六个维度",
    latest: "最新",
    pageLinks: "页面定位",
    fullRecord: "查看完整核验记录",
    footer: "先读中文结论，需要时再追溯完整证据。",
    allRecords: "查看全部原始记录",
    language: "切换呈现语言",
    header: { home: "AIGCDataHub 首页", nav: "主导航", catalog: "数据目录", changelog: "变更记录", source: "查看源码" },
  },
  en: {
    status: "CHANGELOG",
    kicker: "DAILY MAINTENANCE",
    headlineTop: "What changed",
    headlineAccent: "today?",
    description: "Start with changes to models, datasets, and data relations, then review rankings, monitoring status, and what remains undisclosed.",
    back: "Back to catalog",
    overview: "Changelog overview",
    latestUpdate: "LATEST UPDATE",
    batches: "UPDATE BATCHES",
    dimensions: "SUMMARY DIMENSIONS",
    evidenceNote: "Each batch leads with conclusions and preserves the original verification record for deeper review.",
    browse: "BROWSE BY DATE",
    summary: "Update summary",
    summaryNote: "Every update is summarized across six fixed dimensions. No-change results are stated directly, without making readers search technical logs.",
    sixDimensions: "SIX DIMENSIONS",
    latest: "LATEST",
    pageLinks: "page links",
    fullRecord: "View full verification record",
    footer: "Read the conclusions first, then follow the evidence when needed.",
    allRecords: "View all source records",
    language: "Switch display language",
    header: { home: "AIGCDataHub home", nav: "Primary navigation", catalog: "Catalog", changelog: "Changelog", source: "View source" },
  },
} as const;

function formatDate(date: string) {
  return date.replaceAll("-", ".");
}

export function ChangelogView({ changelog }: { changelog: Changelog }) {
  const [locale, setLocale] = useState<Locale>("zh");
  const entries = changelog.entries;
  const latest = entries[0];
  const text = copy[locale];

  function selectLocale(nextLocale: Locale) {
    setLocale(nextLocale);
    document.documentElement.lang = nextLocale === "zh" ? "zh-CN" : "en";
  }

  return (
    <main className="changelog-page" lang={locale === "zh" ? "zh-CN" : "en"}>
      <SiteHeader active="changelog" status={`${text.status} · ${formatDate(latest.date)}`} labels={text.header} />

      <section className="changelog-hero">
        <div className="changelog-hero-copy">
          <div className="changelog-kicker-row">
            <p className="kicker">{text.kicker}</p>
            <div className="language-switch" role="group" aria-label={text.language}>
              <button type="button" aria-pressed={locale === "zh"} onClick={() => selectLocale("zh")}>中文</button>
              <button type="button" aria-pressed={locale === "en"} onClick={() => selectLocale("en")}>EN</button>
            </div>
          </div>
          <h1>{text.headlineTop}<br /><span>{text.headlineAccent}</span></h1>
          <p className="changelog-description">{text.description}</p>
          <div className="changelog-actions">
            <Link href="/">{text.back} <span aria-hidden="true">←</span></Link>
          </div>
        </div>
        <aside className="ledger-summary" aria-label={text.overview}>
          <div><span>{text.latestUpdate}</span><strong>{formatDate(latest.date)}</strong></div>
          <dl>
            <div><dt>{text.batches}</dt><dd>{entries.length}</dd></div>
            <div><dt>{text.dimensions}</dt><dd>{changelog.dimensions.length}</dd></div>
          </dl>
          <p>{text.evidenceNote}</p>
        </aside>
      </section>

      <section className="change-ledger" aria-labelledby="ledger-title">
        <header className="change-ledger-heading">
          <div><span>{text.browse}</span><h2 id="ledger-title">{text.summary}</h2></div>
          <p>{text.summaryNote}</p>
        </header>

        <div className="change-entry-list">
          {entries.map((entry, entryIndex) => (
            <article className="change-entry" key={entry.date}>
              <div className="change-date-rail">
                <span>{String(entries.length - entryIndex).padStart(2, "0")}</span>
                <time dateTime={entry.date}>{formatDate(entry.date)}</time>
                {entryIndex === 0 && <em>{text.latest}</em>}
              </div>
              <details open={entryIndex === 0}>
                <summary>
                  <div><span>{text.sixDimensions}</span><h3>{entry.title[locale]}</h3></div>
                  <span className="summary-toggle" aria-hidden="true">＋</span>
                </summary>
                <div className="change-entry-body">
                  <div className="change-dimension-grid">
                    {entry.summary.map((dimension, dimensionIndex) => (
                      <section className="change-dimension" key={dimension.id}>
                        <div className="change-dimension-heading">
                          <span>{String(dimensionIndex + 1).padStart(2, "0")}</span>
                          <h4>{dimension.label[locale]}</h4>
                        </div>
                        <p>{dimension.text[locale]}</p>
                        <div className="change-dimension-links" aria-label={`${dimension.label[locale]} ${text.pageLinks}`}>
                          {dimension.links.map((link) => (
                            <Link href={link.href} key={link.href}>{link.label[locale]} <span aria-hidden="true">↘</span></Link>
                          ))}
                        </div>
                      </section>
                    ))}
                  </div>
                  <a className="change-source-link" href={`${githubRoot}${entry.source_path}`} target="_blank" rel="noreferrer">
                    {text.fullRecord} <span aria-hidden="true">↗</span>
                  </a>
                  <Link className="change-catalog-link" href="/">
                    {text.back} <span aria-hidden="true">←</span>
                  </Link>
                </div>
              </details>
            </article>
          ))}
        </div>
      </section>

      <footer className="site-footer">
        <div className="footer-brand">AIGC<span>/</span>DATAHUB</div>
        <p>{text.footer}</p>
        <div><span>{text.latestUpdate}</span><strong>{formatDate(latest.date)}</strong></div>
        <a href="https://github.com/TobinZuo/AIGCDataHub/tree/master/updates" target="_blank" rel="noreferrer">{text.allRecords} ↗</a>
      </footer>
    </main>
  );
}
