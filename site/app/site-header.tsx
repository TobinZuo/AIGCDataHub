import Link from "next/link";
import type { Localized } from "./locale-context";
import { localized, useLocale } from "./locale-context";

type SiteHeaderProps = {
  active: "catalog" | "changelog";
  status: string | Localized;
};

const labels = {
  home: { zh: "AIGCDataHub 首页", en: "AIGCDataHub home" },
  nav: { zh: "主导航", en: "Primary navigation" },
  catalog: { zh: "数据目录", en: "Catalog" },
  changelog: { zh: "变更记录", en: "Changelog" },
  source: { zh: "查看源码", en: "View source" },
  language: { zh: "切换呈现语言", en: "Switch display language" },
};

export function SiteHeader({ active, status }: SiteHeaderProps) {
  const { locale, selectLocale } = useLocale();
  const statusText = typeof status === "string" ? status : localized(status, locale);

  return (
    <header className="site-header">
      <Link className="brand" href="/" aria-label={localized(labels.home, locale)}>
        <span className="brand-mark" aria-hidden="true">A</span>
        <span>AIGC<span>/</span>DATAHUB</span>
      </Link>
      <div className="header-status">
        <span className="live-dot" aria-hidden="true" />
        {statusText}
      </div>
      <nav className="header-actions" aria-label={localized(labels.nav, locale)}>
        <Link className={active === "catalog" ? "header-link is-active" : "header-link"} href="/">
          {localized(labels.catalog, locale)}
        </Link>
        <Link className={active === "changelog" ? "header-link is-active" : "header-link"} href="/changelog">
          {localized(labels.changelog, locale)}
        </Link>
        <div className="site-language-switch" role="group" aria-label={localized(labels.language, locale)}>
          <button type="button" aria-pressed={locale === "zh"} onClick={() => selectLocale("zh")}>中</button>
          <button type="button" aria-pressed={locale === "en"} onClick={() => selectLocale("en")}>EN</button>
        </div>
        <a className="repo-link" href="https://github.com/TobinZuo/AIGCDataHub" target="_blank" rel="noreferrer">
          {localized(labels.source, locale)} <span aria-hidden="true">↗</span>
        </a>
      </nav>
    </header>
  );
}
