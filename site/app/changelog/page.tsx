import type { Metadata } from "next";
import type { ReactNode } from "react";
import changelog from "../changelog-data.json";
import { SiteHeader } from "../site-header";

export const metadata: Metadata = {
  title: "变更记录 | AIGCDataHub",
  description: "AIGCDataHub 每次核验、入库、关系更新与排行榜变化的可追溯记录。",
  alternates: { canonical: "https://tobinzuo.github.io/AIGCDataHub/changelog/" },
};

type Block =
  | { type: "paragraph"; text: string }
  | { type: "subheading"; text: string }
  | { type: "list"; items: string[] }
  | { type: "table"; rows: string[][] };

type Entry = {
  date: string;
  title: string;
  intro: Block[];
  sections: Array<{ title: string; blocks: Block[] }>;
  source_path: string;
};

const entries = changelog.entries as unknown as Entry[];
const githubRoot = "https://github.com/TobinZuo/AIGCDataHub/blob/master/";

function formatDate(date: string) {
  return date.replaceAll("-", ".");
}

function inlineText(text: string): ReactNode[] {
  const pattern = /(\[[^\]]+\]\(https:\/\/[^)]+\)|`[^`]+`|\*\*[^*]+\*\*)/g;
  const nodes: ReactNode[] = [];
  let cursor = 0;

  for (const match of text.matchAll(pattern)) {
    const index = match.index ?? 0;
    if (index > cursor) nodes.push(text.slice(cursor, index));
    const token = match[0];
    const link = token.match(/^\[([^\]]+)\]\((https:\/\/[^)]+)\)$/);
    if (link) {
      nodes.push(<a href={link[2]} target="_blank" rel="noreferrer" key={`${index}-${link[2]}`}>{link[1]} ↗</a>);
    } else if (token.startsWith("`")) {
      nodes.push(<code key={index}>{token.slice(1, -1)}</code>);
    } else {
      nodes.push(<strong key={index}>{token.slice(2, -2)}</strong>);
    }
    cursor = index + token.length;
  }
  if (cursor < text.length) nodes.push(text.slice(cursor));
  return nodes;
}

function ChangeBlocks({ blocks }: { blocks: Block[] }) {
  return blocks.map((block, index) => {
    if (block.type === "subheading") return <h4 key={index}>{inlineText(block.text)}</h4>;
    if (block.type === "paragraph") return <p key={index}>{inlineText(block.text)}</p>;
    if (block.type === "list") {
      return <ul key={index}>{block.items.map((item, itemIndex) => <li key={itemIndex}>{inlineText(item)}</li>)}</ul>;
    }
    return (
      <div className="change-table-wrap" key={index}>
        <table>
          <thead><tr>{block.rows[0]?.map((cell) => <th key={cell}>{inlineText(cell)}</th>)}</tr></thead>
          <tbody>{block.rows.slice(1).map((row, rowIndex) => (
            <tr key={rowIndex}>{row.map((cell, cellIndex) => <td key={cellIndex}>{inlineText(cell)}</td>)}</tr>
          ))}</tbody>
        </table>
      </div>
    );
  });
}

export default function ChangelogPage() {
  const latest = entries[0];
  const sectionCount = entries.reduce((count, entry) => count + entry.sections.length, 0);
  const evidenceCount = JSON.stringify(entries).match(/https:\/\//g)?.length ?? 0;

  return (
    <main className="changelog-page">
      <SiteHeader active="changelog" status={`CHANGE LEDGER · ${formatDate(latest.date)}`} />

      <section className="changelog-hero">
        <div className="changelog-hero-copy">
          <p className="kicker">维护日志 / EVIDENCE LEDGER</p>
          <h1>每一次变化，<br /><span>都有来路。</span></h1>
          <p>这里记录 AIGCDataHub 每轮扫描后的接受、更新、排除与未披露项，并保留可回到原始证据的链接。</p>
        </div>
        <aside className="ledger-summary" aria-label="变更记录概览">
          <div><span>LATEST REVIEW</span><strong>{formatDate(latest.date)}</strong></div>
          <dl>
            <div><dt>维护批次</dt><dd>{entries.length}</dd></div>
            <div><dt>记录分区</dt><dd>{sectionCount}</dd></div>
            <div><dt>证据链接</dt><dd>{evidenceCount}</dd></div>
          </dl>
          <p>内容由仓库中的日期化更新记录自动生成，与事实卡和验证流程一起进入版本控制。</p>
        </aside>
      </section>

      <section className="change-ledger" aria-labelledby="ledger-title">
        <header className="change-ledger-heading">
          <div><span>01 / HISTORY</span><h2 id="ledger-title">更新批次</h2></div>
          <p>最新记录默认展开；历史批次可按日期查看。条目中的“未披露”与“证据不足”同样是核验结论。</p>
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
                  <div><span>{entry.sections.length} 个核验分区</span><h3>{entry.title}</h3></div>
                  <span className="summary-toggle" aria-hidden="true">＋</span>
                </summary>
                <div className="change-entry-body">
                  {entry.intro.length > 0 && <div className="change-intro"><ChangeBlocks blocks={entry.intro} /></div>}
                  {entry.sections.map((section, sectionIndex) => (
                    <section className="change-section" key={section.title}>
                      <div className="change-section-label"><span>{String(sectionIndex + 1).padStart(2, "0")}</span><h3>{section.title}</h3></div>
                      <div className="change-section-content"><ChangeBlocks blocks={section.blocks} /></div>
                    </section>
                  ))}
                  <a className="change-source-link" href={`${githubRoot}${entry.source_path}`} target="_blank" rel="noreferrer">
                    在 GitHub 查看原始记录 <span aria-hidden="true">↗</span>
                  </a>
                </div>
              </details>
            </article>
          ))}
        </div>
      </section>

      <footer className="site-footer">
        <div className="footer-brand">AIGC<span>/</span>DATAHUB</div>
        <p>变更记录不是发布宣传，而是事实、证据与仍然未知部分的维护账本。</p>
        <div><span>LATEST REVIEW</span><strong>{formatDate(latest.date)}</strong></div>
        <a href="https://github.com/TobinZuo/AIGCDataHub/tree/master/updates" target="_blank" rel="noreferrer">ALL SOURCE LOGS ↗</a>
      </footer>
    </main>
  );
}
