import type { Metadata } from "next";
import changelog from "../changelog-data.json";
import { SiteHeader } from "../site-header";

export const metadata: Metadata = {
  title: "变更记录 | AIGCDataHub",
  description: "从模型、数据集、数据关系、排行榜、监控和未披露六个维度了解 AIGCDataHub 的每次更新。",
  alternates: { canonical: "https://tobinzuo.github.io/AIGCDataHub/changelog/" },
};

type SummaryDimension = {
  id: string;
  label: string;
  text: string;
};

type Entry = {
  date: string;
  title: string;
  summary: SummaryDimension[];
  source_path: string;
};

const entries = changelog.entries as Entry[];
const githubRoot = "https://github.com/TobinZuo/AIGCDataHub/blob/master/";

function formatDate(date: string) {
  return date.replaceAll("-", ".");
}

export default function ChangelogPage() {
  const latest = entries[0];
  const dimensionCount = changelog.dimensions.length;

  return (
    <main className="changelog-page">
      <SiteHeader active="changelog" status={`更新记录 · ${formatDate(latest.date)}`} />

      <section className="changelog-hero">
        <div className="changelog-hero-copy">
          <p className="kicker">每日维护 · 中文摘要</p>
          <h1>今天更新了<br /><span>什么？</span></h1>
          <p>先看模型、数据集和数据关系发生了什么，再看排行榜、监控状态与仍未披露的信息。</p>
        </div>
        <aside className="ledger-summary" aria-label="变更记录概览">
          <div><span>最近更新</span><strong>{formatDate(latest.date)}</strong></div>
          <dl>
            <div><dt>更新批次</dt><dd>{entries.length}</dd></div>
            <div><dt>总结维度</dt><dd>{dimensionCount}</dd></div>
            <div><dt>呈现语言</dt><dd className="ledger-language">中文</dd></div>
          </dl>
          <p>每个批次先给结论，再保留原始核验记录作为证据，方便快速阅读和深入追溯。</p>
        </aside>
      </section>

      <section className="change-ledger" aria-labelledby="ledger-title">
        <header className="change-ledger-heading">
          <div><span>按日期查看</span><h2 id="ledger-title">更新摘要</h2></div>
          <p>每期固定从六个维度总结。没有变化会直接写明，不用从技术日志里寻找结论。</p>
        </header>

        <div className="change-entry-list">
          {entries.map((entry, entryIndex) => (
            <article className="change-entry" key={entry.date}>
              <div className="change-date-rail">
                <span>{String(entries.length - entryIndex).padStart(2, "0")}</span>
                <time dateTime={entry.date}>{formatDate(entry.date)}</time>
                {entryIndex === 0 && <em>最新</em>}
              </div>
              <details open={entryIndex === 0}>
                <summary>
                  <div><span>六个维度</span><h3>{entry.title}</h3></div>
                  <span className="summary-toggle" aria-hidden="true">＋</span>
                </summary>
                <div className="change-entry-body">
                  <div className="change-dimension-grid">
                    {entry.summary.map((dimension, dimensionIndex) => (
                      <section className="change-dimension" key={dimension.id}>
                        <div className="change-dimension-heading">
                          <span>{String(dimensionIndex + 1).padStart(2, "0")}</span>
                          <h4>{dimension.label}</h4>
                        </div>
                        <p>{dimension.text}</p>
                      </section>
                    ))}
                  </div>
                  <a className="change-source-link" href={`${githubRoot}${entry.source_path}`} target="_blank" rel="noreferrer">
                    查看完整核验记录 <span aria-hidden="true">↗</span>
                  </a>
                </div>
              </details>
            </article>
          ))}
        </div>
      </section>

      <footer className="site-footer">
        <div className="footer-brand">AIGC<span>/</span>DATAHUB</div>
        <p>先读中文结论，需要时再追溯完整证据。</p>
        <div><span>最近更新</span><strong>{formatDate(latest.date)}</strong></div>
        <a href="https://github.com/TobinZuo/AIGCDataHub/tree/master/updates" target="_blank" rel="noreferrer">查看全部原始记录 ↗</a>
      </footer>
    </main>
  );
}
