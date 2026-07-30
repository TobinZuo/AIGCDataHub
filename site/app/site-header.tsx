import Link from "next/link";

type SiteHeaderProps = {
  active: "catalog" | "changelog";
  status: string;
};

export function SiteHeader({ active, status }: SiteHeaderProps) {
  return (
    <header className="site-header">
      <Link className="brand" href="/" aria-label="AIGCDataHub 首页">
        <span className="brand-mark" aria-hidden="true">A</span>
        <span>AIGC<span>/</span>DATAHUB</span>
      </Link>
      <div className="header-status">
        <span className="live-dot" aria-hidden="true" />
        {status}
      </div>
      <nav className="header-actions" aria-label="主导航">
        <Link className={active === "changelog" ? "header-link is-active" : "header-link"} href="/changelog">
          变更记录
        </Link>
        <a className="repo-link" href="https://github.com/TobinZuo/AIGCDataHub" target="_blank" rel="noreferrer">
          SOURCE ON GITHUB <span aria-hidden="true">↗</span>
        </a>
      </nav>
    </header>
  );
}
