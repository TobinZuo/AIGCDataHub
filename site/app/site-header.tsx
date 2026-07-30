import Link from "next/link";

type SiteHeaderProps = {
  active: "catalog" | "changelog";
  status: string;
  labels?: {
    home: string;
    nav: string;
    catalog: string;
    changelog: string;
    source: string;
  };
};

const defaultLabels = {
  home: "AIGCDataHub 首页",
  nav: "主导航",
  catalog: "数据目录",
  changelog: "变更记录",
  source: "查看源码",
};

export function SiteHeader({ active, status, labels = defaultLabels }: SiteHeaderProps) {
  return (
    <header className="site-header">
      <Link className="brand" href="/" aria-label={labels.home}>
        <span className="brand-mark" aria-hidden="true">A</span>
        <span>AIGC<span>/</span>DATAHUB</span>
      </Link>
      <div className="header-status">
        <span className="live-dot" aria-hidden="true" />
        {status}
      </div>
      <nav className="header-actions" aria-label={labels.nav}>
        <Link className={active === "catalog" ? "header-link is-active" : "header-link"} href="/">
          {labels.catalog}
        </Link>
        <Link className={active === "changelog" ? "header-link is-active" : "header-link"} href="/changelog">
          {labels.changelog}
        </Link>
        <a className="repo-link" href="https://github.com/TobinZuo/AIGCDataHub" target="_blank" rel="noreferrer">
          {labels.source} <span aria-hidden="true">↗</span>
        </a>
      </nav>
    </header>
  );
}
