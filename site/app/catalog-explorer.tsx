"use client";

import { useMemo, useState } from "react";

type Mode = "models" | "datasets" | "strategies";

type DataReference = {
  name: string;
  catalog_id: string | null;
  role: string;
  availability: string;
  scale: string | null;
  notes: string;
};

type TrainingStage = {
  name: string;
  modalities: string[];
  source_types: string[];
  operations: string[];
  scale_disclosed: boolean;
  strategy: string;
};

type ModelCard = {
  id: string;
  name: string;
  organization: string;
  released_at: string;
  modalities: string[];
  tasks: string[];
  access: {
    status: string;
    license: string;
    release_url: string;
    weights_url: string | null;
    api_url: string | null;
  };
  architecture: {
    family: string;
    parameters: number | null;
    notes: string;
  };
  data: {
    disclosure_level: string;
    exact_datasets_disclosed: boolean;
    exact_mixture_disclosed: boolean;
    datasets: DataReference[];
    stages: TrainingStage[];
    strategy_summary: string[];
    unknowns: string[];
  };
  evidence: {
    release: string;
    technical_report: string | null;
    repository: string | null;
  };
  status: string;
  last_verified: string;
  source_path: string;
};

type DatasetCard = {
  id: string;
  name: string;
  organization: string;
  released_at: string;
  release_date_source: string;
  modality: string;
  tasks: string[];
  stages: string[];
  description: string;
  access: {
    status: string;
    type: string;
    url: string;
    requires_account: boolean;
    notes: string;
  };
  scale: {
    samples: number | null;
    source_items?: number | null;
    hours?: number | null;
    approximate: boolean;
    notes: string;
  };
  scale_label: string;
  annotations: {
    types: string[];
    source: string;
    languages: string[];
  };
  license: {
    metadata: string;
    media: string;
    commercial_use: string;
    redistribution: string;
    notes: string;
  };
  quality: {
    dimensions: string[];
    known_limitations: string[];
  };
  processing: {
    recipe: string | null;
    recommended_format: string;
    notes: string;
  };
  evidence: {
    homepage: string;
    paper: string | null;
    used_by: string[];
  };
  status: string;
  last_verified: string;
  source_path: string;
};

type Catalog = {
  last_verified: string;
  models: ModelCard[];
  datasets: DatasetCard[];
};

const MODE_LABELS: Record<Mode, string> = {
  models: "最新模型",
  datasets: "最新数据集",
  strategies: "数据策略",
};

const MODALITY_LABELS: Record<string, string> = {
  all: "全部模态",
  image: "图像",
  video: "视频",
  audio: "音频",
  action: "具身 / Action",
  multimodal: "多模态",
  preference: "偏好数据",
  "3d": "3D",
};

const DISCLOSURE_LABELS: Record<string, string> = {
  full: "完整披露",
  partial: "部分披露",
  "high-level": "仅高层策略",
  undisclosed: "未披露",
};

const ACCESS_LABELS: Record<string, string> = {
  open: "公开",
  gated: "需申请",
  "metadata-only": "仅元数据",
  unavailable: "不可用",
  "open-weights": "开放权重",
  "gated-weights": "受限权重",
  "api-only": "仅 API",
  "product-only": "仅产品内",
  "early-access": "早期访问",
  "research-preview": "研究预览",
  announced: "已发布预告",
};

const STATUS_LABELS: Record<string, string> = {
  verified: "已核验",
  partial: "部分核验",
  watch: "持续追踪",
  archived: "已归档",
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(`${value}T00:00:00Z`));
}

function normalize(value: string) {
  return value.toLocaleLowerCase().replaceAll("-", " ");
}

function disclosureScore(level: string) {
  return ({ full: 4, partial: 3, "high-level": 2, undisclosed: 1 }[level] ?? 0);
}

function ExternalLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a className="text-link" href={href} target="_blank" rel="noreferrer">
      {children}<span aria-hidden="true">↗</span>
    </a>
  );
}

function StatusMark({ status }: { status: string }) {
  return (
    <span className={`status-mark status-${status}`}>
      <span aria-hidden="true" />{STATUS_LABELS[status] ?? status}
    </span>
  );
}

function EmptyState({ query }: { query: string }) {
  return (
    <div className="empty-state">
      <span className="empty-symbol" aria-hidden="true">∅</span>
      <h3>没有匹配项</h3>
      <p>试试缩短“{query || "当前条件"}”，或切换到全部模态。</p>
    </div>
  );
}

function ModelResult({ model, expanded, onToggle }: {
  model: ModelCard;
  expanded: boolean;
  onToggle: () => void;
}) {
  const namedDatasets = model.data.datasets.filter((item) => item.catalog_id);

  return (
    <article className={`result-card model-card ${expanded ? "is-expanded" : ""}`}>
      <button className="card-toggle" onClick={onToggle} aria-expanded={expanded}>
        <div className="card-index">M/{model.released_at.slice(2).replaceAll("-", "")}</div>
        <div className="card-primary">
          <div className="eyebrow-row">
            <span>{model.organization}</span>
            <span>{formatDate(model.released_at)}</span>
          </div>
          <h3>{model.name}</h3>
          <p>{model.data.strategy_summary[0]}</p>
          <div className="tag-row">
            {model.modalities.slice(0, 4).map((item) => (
              <span className="tag" key={item}>{MODALITY_LABELS[item] ?? item}</span>
            ))}
          </div>
        </div>
        <div className="card-metrics">
          <div>
            <span className="metric-label">数据披露</span>
            <strong>{DISCLOSURE_LABELS[model.data.disclosure_level]}</strong>
          </div>
          <div>
            <span className="metric-label">目录关联</span>
            <strong>{model.data.datasets.length ? `${namedDatasets.length}/${model.data.datasets.length}` : "—"}</strong>
          </div>
          <StatusMark status={model.status} />
        </div>
        <span className="expand-control" aria-hidden="true">{expanded ? "−" : "+"}</span>
      </button>

      {expanded && (
        <div className="card-detail">
          <section>
            <p className="detail-label">训练数据策略</p>
            <ol className="strategy-list">
              {model.data.strategy_summary.map((item, index) => (
                <li key={item}><span>0{index + 1}</span><p>{item}</p></li>
              ))}
            </ol>
          </section>
          <section>
            <p className="detail-label">阶段与操作</p>
            <div className="stage-list">
              {model.data.stages.map((stage) => (
                <div className="stage" key={`${model.id}-${stage.name}`}>
                  <div className="stage-title">
                    <strong>{stage.name}</strong>
                    <span>{stage.scale_disclosed ? "规模已披露" : "规模未知"}</span>
                  </div>
                  <p>{stage.strategy}</p>
                  <div className="operation-row">
                    {stage.operations.map((item) => <code key={item}>{item}</code>)}
                  </div>
                </div>
              ))}
            </div>
          </section>
          <section>
            <p className="detail-label">数据引用</p>
            {model.data.datasets.length ? (
              <div className="data-reference-list">
                {model.data.datasets.map((item) => (
                  <div key={`${model.id}-${item.name}`}>
                    <strong>{item.name}</strong>
                    <span>{item.role} · {item.scale ?? "规模未披露"}</span>
                    <p>{item.notes}</p>
                  </div>
                ))}
              </div>
            ) : <p className="unknown-copy">官方没有公开任何可识别的数据集名称。</p>}
            {namedDatasets.length > 0 && (
              <p className="linked-note">其中 {namedDatasets.length} 个已与本目录数据卡建立关联。</p>
            )}
          </section>
          <section className="unknown-panel">
            <p className="detail-label">仍然未知</p>
            <ul>
              {model.data.unknowns.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </section>
          <footer className="detail-footer">
            <span>架构：{model.architecture.family}</span>
            <nav aria-label={`${model.name} 来源`}>
              <ExternalLink href={model.evidence.release}>官方发布</ExternalLink>
              {model.evidence.technical_report && <ExternalLink href={model.evidence.technical_report}>技术报告</ExternalLink>}
              {model.evidence.repository && <ExternalLink href={model.evidence.repository}>代码仓库</ExternalLink>}
            </nav>
          </footer>
        </div>
      )}
    </article>
  );
}

function DatasetResult({ dataset, expanded, onToggle }: {
  dataset: DatasetCard;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <article className={`result-card dataset-card ${expanded ? "is-expanded" : ""}`}>
      <button className="card-toggle" onClick={onToggle} aria-expanded={expanded}>
        <div className="card-index">D/{dataset.released_at.slice(2).replaceAll("-", "")}</div>
        <div className="card-primary">
          <div className="eyebrow-row">
            <span>{dataset.organization}</span>
            <span>发布于 {formatDate(dataset.released_at)}</span>
          </div>
          <h3>{dataset.name}</h3>
          <p>{dataset.description}</p>
          <div className="tag-row">
            <span className="tag">{MODALITY_LABELS[dataset.modality] ?? dataset.modality}</span>
            {dataset.tasks.slice(0, 3).map((item) => <span className="tag" key={item}>{item}</span>)}
          </div>
        </div>
        <div className="card-metrics">
          <div>
            <span className="metric-label">样本规模</span>
            <strong>{dataset.scale_label}</strong>
          </div>
          <div>
            <span className="metric-label">访问方式</span>
            <strong>{ACCESS_LABELS[dataset.access.status] ?? dataset.access.status}</strong>
          </div>
          <StatusMark status={dataset.status} />
        </div>
        <span className="expand-control" aria-hidden="true">{expanded ? "−" : "+"}</span>
      </button>

      {expanded && (
        <div className="card-detail dataset-detail">
          <section>
            <p className="detail-label">数据与标注</p>
            <dl className="fact-grid">
              <div><dt>标注来源</dt><dd>{dataset.annotations.source}</dd></div>
              <div><dt>标注类型</dt><dd>{dataset.annotations.types.join(" · ")}</dd></div>
              <div><dt>处理格式</dt><dd>{dataset.processing.recommended_format}</dd></div>
              <div><dt>账号要求</dt><dd>{dataset.access.requires_account ? "需要" : "不需要"}</dd></div>
              <div><dt>首次发布</dt><dd>{formatDate(dataset.released_at)}</dd></div>
              <div><dt>最近核验</dt><dd>{formatDate(dataset.last_verified)}</dd></div>
            </dl>
          </section>
          <section>
            <p className="detail-label">许可边界</p>
            <dl className="fact-grid">
              <div><dt>元数据</dt><dd>{dataset.license.metadata}</dd></div>
              <div><dt>媒体内容</dt><dd>{dataset.license.media}</dd></div>
              <div><dt>商用</dt><dd>{dataset.license.commercial_use}</dd></div>
              <div><dt>再分发</dt><dd>{dataset.license.redistribution}</dd></div>
            </dl>
            <p className="license-note">{dataset.license.notes}</p>
          </section>
          <section className="unknown-panel">
            <p className="detail-label">已知限制</p>
            <ul>
              {dataset.quality.known_limitations.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </section>
          <footer className="detail-footer">
            <span>{dataset.access.notes}</span>
            <nav aria-label={`${dataset.name} 来源`}>
              <ExternalLink href={dataset.evidence.homepage}>项目主页</ExternalLink>
              {dataset.release_date_source !== dataset.evidence.homepage && (
                <ExternalLink href={dataset.release_date_source}>发布日期证据</ExternalLink>
              )}
              {dataset.evidence.paper && dataset.evidence.paper !== dataset.release_date_source && (
                <ExternalLink href={dataset.evidence.paper}>论文</ExternalLink>
              )}
            </nav>
          </footer>
        </div>
      )}
    </article>
  );
}

function StrategyResult({ model }: { model: ModelCard }) {
  const disclosed = disclosureScore(model.data.disclosure_level);
  const linkedDatasets = model.data.datasets.filter((item) => item.catalog_id).length;

  return (
    <article className="strategy-card">
      <header>
        <div>
          <span className="strategy-org">{model.organization}</span>
          <h3>{model.name}</h3>
        </div>
        <div className="disclosure-meter" aria-label={`披露程度：${DISCLOSURE_LABELS[model.data.disclosure_level]}`}>
          {[1, 2, 3, 4].map((level) => <span className={level <= disclosed ? "is-on" : ""} key={level} />)}
        </div>
      </header>
      <p className="strategy-lead">{model.data.strategy_summary[0]}</p>
      <div className="pipeline" aria-label="训练阶段">
        {model.data.stages.map((stage, index) => (
          <div className="pipeline-stage" key={`${model.id}-${stage.name}`}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <strong>{stage.name}</strong>
            <small>{stage.source_types.join(" + ")}</small>
          </div>
        ))}
      </div>
      <div className="strategy-columns">
        <div>
          <p className="detail-label">关键操作</p>
          <div className="operation-row">
            {[...new Set(model.data.stages.flatMap((stage) => stage.operations))].map((item) => <code key={item}>{item}</code>)}
          </div>
        </div>
        <div>
          <p className="detail-label">证据边界</p>
          <p>{model.data.exact_datasets_disclosed ? "公开了具体数据集名称。" : "未公开完整数据集清单。"} {model.data.exact_mixture_disclosed ? "混合比例可核验。" : "混合比例仍未知。"}</p>
        </div>
      </div>
      <footer>
        <span>{DISCLOSURE_LABELS[model.data.disclosure_level]} · {linkedDatasets}/{model.data.datasets.length || "—"} 数据卡关联 · {model.data.unknowns.length} 项未知</span>
        <ExternalLink href={model.evidence.technical_report ?? model.evidence.release}>查看一手证据</ExternalLink>
      </footer>
    </article>
  );
}

export function CatalogExplorer({ catalog }: { catalog: Catalog }) {
  const [mode, setMode] = useState<Mode>("models");
  const [query, setQuery] = useState("");
  const [modality, setModality] = useState("all");
  const [expanded, setExpanded] = useState<string | null>("flux-3");

  const modelResults = useMemo(() => {
    const search = normalize(query.trim());
    return catalog.models.filter((model) => {
      const inModality = modality === "all" || model.modalities.includes(modality);
      const haystack = normalize([
        model.name,
        model.organization,
        ...model.tasks,
        ...model.modalities,
        ...model.data.strategy_summary,
        ...model.data.datasets.map((item) => item.name),
        ...model.data.stages.flatMap((stage) => stage.operations),
      ].join(" "));
      return inModality && (!search || haystack.includes(search));
    });
  }, [catalog.models, modality, query]);

  const datasetResults = useMemo(() => {
    const search = normalize(query.trim());
    return catalog.datasets.filter((dataset) => {
      const inModality = modality === "all" || dataset.modality === modality;
      const haystack = normalize([
        dataset.name,
        dataset.organization,
        dataset.description,
        dataset.modality,
        ...dataset.tasks,
        ...dataset.annotations.types,
        ...dataset.evidence.used_by,
      ].join(" "));
      return inModality && (!search || haystack.includes(search));
    });
  }, [catalog.datasets, modality, query]);

  const visibleModalities = mode === "datasets"
    ? ["all", "image", "video", "audio", "3d", "preference"]
    : ["all", "image", "video", "audio", "3d", "multimodal", "action"];
  const visibleCount = mode === "datasets" ? datasetResults.length : modelResults.length;
  const exactDatasetModels = catalog.models.filter((item) => item.data.exact_datasets_disclosed).length;
  const openDatasets = catalog.datasets.filter((item) => item.access.status === "open").length;

  function switchMode(nextMode: Mode) {
    setMode(nextMode);
    setModality("all");
    setExpanded(nextMode === "models" ? catalog.models[0]?.id ?? null : null);
  }

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="AIGCDataHub 首页">
          <span className="brand-mark" aria-hidden="true">A</span>
          <span>AIGC<span>/</span>DATAHUB</span>
        </a>
        <div className="header-status">
          <span className="live-dot" aria-hidden="true" />
          LIVING INDEX · {formatDate(catalog.last_verified)}
        </div>
        <a className="repo-link" href="https://github.com/TobinZuo/AIGCDataHub" target="_blank" rel="noreferrer">
          SOURCE ON GITHUB <span aria-hidden="true">↗</span>
        </a>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="kicker"><span>01</span> 生成式 AI 数据情报</p>
          <h1>追踪模型，<br />追到它的<span>数据源头。</span></h1>
          <p className="hero-description">
            不止告诉你“有哪些数据集”。这里持续拆解最新 AIGC 模型用了什么数据、怎样清洗与训练，以及官方仍未披露什么。
          </p>
          <div className="hero-actions">
            <button onClick={() => document.querySelector("#explorer")?.scrollIntoView({ behavior: "smooth" })}>
              开始检索 <span aria-hidden="true">↓</span>
            </button>
            <span>一手来源 · 显式未知项 · 每周复核</span>
          </div>
        </div>
        <aside className="hero-stats" aria-label="目录统计">
          <div className="stats-topline"><span>INDEX / 2026</span><span>CN—EN</span></div>
          <div className="stat-main"><strong>{catalog.models.length}</strong><span>最新模型<br />及数据策略</span></div>
          <div className="stat-grid">
            <div><strong>{catalog.datasets.length}</strong><span>结构化数据集</span></div>
            <div><strong>{openDatasets}</strong><span>公开可访问</span></div>
            <div><strong>{exactDatasetModels}</strong><span>披露具体数据</span></div>
            <div><strong>7D</strong><span>更新节奏</span></div>
          </div>
          <div className="stats-note">每条结论保留发布日期、核验时间和官方证据。未知不是空白，也是结论。</div>
        </aside>
      </section>

      <section className="signal-strip" aria-label="最新追踪信号">
        <span className="signal-label">LATEST SIGNAL</span>
        <span className="signal-date">{formatDate(catalog.models[0].released_at)}</span>
        <strong>{catalog.models[0].name}</strong>
        <p>{catalog.models[0].data.strategy_summary[0]}</p>
        <button onClick={() => { switchMode("models"); setExpanded(catalog.models[0].id); document.querySelector("#explorer")?.scrollIntoView({ behavior: "smooth" }); }}>
          查看拆解 ↘
        </button>
      </section>

      <section className="explorer" id="explorer">
        <div className="explorer-heading">
          <div>
            <p className="kicker"><span>02</span> 可核验目录</p>
            <h2>查模型，也查它背后的数据逻辑。</h2>
          </div>
          <p>目录直接由仓库中的 YAML 数据卡生成；更新事实源，页面随之更新。</p>
        </div>

        <div className="mode-tabs" role="tablist" aria-label="目录类型">
          {(Object.keys(MODE_LABELS) as Mode[]).map((item) => (
            <button
              className={mode === item ? "is-active" : ""}
              key={item}
              onClick={() => switchMode(item)}
              role="tab"
              aria-selected={mode === item}
            >
              <span>{MODE_LABELS[item]}</span>
              <small>{item === "datasets" ? catalog.datasets.length : catalog.models.length}</small>
            </button>
          ))}
        </div>

        <div className="search-panel">
          <label className="search-box">
            <span aria-hidden="true">⌕</span>
            <span className="sr-only">搜索目录</span>
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={mode === "datasets" ? "搜索数据集、任务、标注类型…" : "搜索模型、机构、数据集或训练操作…"}
            />
            {query && <button onClick={() => setQuery("")} aria-label="清空搜索">×</button>}
          </label>
          <div className="filter-row" aria-label="模态筛选">
            {visibleModalities.map((item) => (
              <button className={modality === item ? "is-active" : ""} onClick={() => setModality(item)} key={item}>
                {MODALITY_LABELS[item]}
              </button>
            ))}
          </div>
          <div className="result-count"><strong>{visibleCount}</strong> 条结果</div>
        </div>

        <div className="result-list" role="tabpanel">
          {mode === "models" && modelResults.map((model) => (
            <ModelResult
              key={model.id}
              model={model}
              expanded={expanded === model.id}
              onToggle={() => setExpanded(expanded === model.id ? null : model.id)}
            />
          ))}
          {mode === "datasets" && datasetResults.map((dataset) => (
            <DatasetResult
              key={dataset.id}
              dataset={dataset}
              expanded={expanded === dataset.id}
              onToggle={() => setExpanded(expanded === dataset.id ? null : dataset.id)}
            />
          ))}
          {mode === "strategies" && modelResults.map((model) => <StrategyResult model={model} key={model.id} />)}
          {visibleCount === 0 && <EmptyState query={query} />}
        </div>
      </section>

      <section className="method-section">
        <div className="method-heading">
          <p className="kicker"><span>03</span> 证据方法</p>
          <h2>我们把“没说”也写下来。</h2>
        </div>
        <div className="method-grid">
          <article><span>01</span><h3>一手来源优先</h3><p>官方发布、论文、模型卡和代码仓库交叉核验，不用能力猜训练数据。</p></article>
          <article><span>02</span><h3>数据与策略分层</h3><p>区分可下载数据集、未发布语料、合成数据和人类反馈，以及它们所在的训练阶段。</p></article>
          <article><span>03</span><h3>权利边界显式化</h3><p>元数据许可不等于媒体可商用；访问方式、商用和再分发分别记录。</p></article>
          <article><span>04</span><h3>持续复核</h3><p>活跃模型 14 天、普通模型 45 天、数据集 90 天触发过期检查。</p></article>
        </div>
      </section>

      <footer className="site-footer">
        <div className="footer-brand">AIGC<span>/</span>DATAHUB</div>
        <p>一个持续更新、可复现、对未知诚实的生成式 AI 数据工程索引。</p>
        <div><span>LAST VERIFIED</span><strong>{formatDate(catalog.last_verified)}</strong></div>
        <a href="https://github.com/TobinZuo/AIGCDataHub" target="_blank" rel="noreferrer">CONTRIBUTE ↗</a>
      </footer>
    </main>
  );
}
