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
        <Link className={active === "catalog" ? "header-link is-active" : "header-link"} href="/">
          数据目录
        </Link>
        <Link className={active === "changelog" ? "header-link is-active" : "header-link"} href="/changelog">
          变更记录
        </Link>
        <a className="repo-link" href="https://github.com/TobinZuo/AIGCDataHub" target="_blank" rel="noreferrer">
          查看源码 <span aria-hidden="true">↗</span>
        </a>
      </nav>
    </header>
  );
}
