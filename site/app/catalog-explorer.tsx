"use client";

import { useEffect, useMemo, useState } from "react";
import { SiteHeader } from "./site-header";
import type { Locale, Localized } from "./locale-context";
import { localized, useLocale } from "./locale-context";

type Mode = "models" | "datasets" | "sources" | "rankings" | "lineage" | "strategies";

type CatalogHashTarget = {
  mode: Mode;
  id: string | null;
  elementId: string;
};

const CATALOG_VIEW_HASHES: Record<string, Mode> = {
  models: "models",
  datasets: "datasets",
  sources: "sources",
  rankings: "rankings",
  lineage: "lineage",
  strategies: "strategies",
};

function parseCatalogHash(hash: string): CatalogHashTarget | null {
  const value = decodeURIComponent(hash.replace(/^#/, ""));
  const viewMode = CATALOG_VIEW_HASHES[value];
  if (viewMode) return { mode: viewMode, id: null, elementId: "explorer" };

  const prefixes: Array<[string, CatalogHashTarget["mode"]]> = [
    ["strategy-datasets-", "strategies"],
    ["strategy-", "strategies"],
    ["dataset-", "datasets"],
    ["model-", "models"],
  ];

  for (const [prefix, mode] of prefixes) {
    if (value.startsWith(prefix) && value.length > prefix.length) {
      return { mode, id: value.slice(prefix.length), elementId: value };
    }
  }
  return null;
}

function scrollToCatalogTarget(elementId: string) {
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      document.getElementById(elementId)?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  });
}

type ScenarioDefinition = {
  id: string;
  label: string;
  short_label: string;
  description: string;
};

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

type StrategyProfile = {
  stage_names: string[];
  source_types: string[];
  operations: string[];
  data_reference_count: number;
  linked_dataset_count: number;
  scale_disclosed_stage_count: number;
  stage_count: number;
  unknown_count: number;
};

type ModelDatasetRelation = {
  model_id: string;
  dataset_id: string;
  role: string;
  availability: string;
  scale: string | null;
  reference_name: string;
};

type EnrichedRelation = ModelDatasetRelation & {
  model: ModelCard;
  dataset: DatasetCard;
};

type DatasetLineageRelation = {
  source_dataset_id: string;
  derived_dataset_id: string;
  relationship: string;
  contribution: string;
  notes: string;
};

type EnrichedDatasetLineage = DatasetLineageRelation & {
  sourceDataset: DatasetCard;
  derivedDataset: DatasetCard;
};

type Monitoring = {
  priority: string;
  source_url: string;
  mode?: string;
};

type RankingPosition = {
  ranking_id: string;
  provider: string;
  rank: number;
  score: number;
  score_label: string;
  entry_model: string;
  component_count: number;
};

type RankingComponent = {
  name: string;
  model_id: string | null;
};

type RankingEntry = {
  rank: number;
  creator: string;
  model: string;
  score: number;
  confidence_interval: string;
  samples: number | null;
  released: string;
  open_weights: boolean;
  license: string | null;
  model_id: string | null;
  model_ids: string[];
  components: RankingComponent[];
};

type RankingBoard = {
  id: string;
  provider: string;
  label: string;
  modality: string;
  score_label: string;
  date_label: string;
  coverage_policy: string;
  source_url: string;
  fetch_url: string;
  entries: RankingEntry[];
};

type SourcePlatform = {
  id: string;
  name: string;
  homepage: string;
  category: string;
  modalities: string[];
  relevant_scenarios: string[];
  content_scope: string;
  data_access: {
    status: string;
    interface_name: string | null;
    interface_url: string | null;
    scope: string;
    requirements: string;
    training_rights: string;
  };
  monitoring: {
    url: string;
    mode: string;
    focus: string;
    priority: string;
  };
  source_status: string;
  access_boundary: string;
  rights_review: string;
  last_reviewed: string;
};

type ModelCard = {
  id: string;
  name: string;
  organization: string;
  released_at: string;
  ranking_names?: string[];
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
  scenario_ids: string[];
  strategy_profile: StrategyProfile;
  linked_dataset_ids: string[];
  monitoring: Monitoring | null;
  ranking_positions: RankingPosition[];
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
  derived_from?: {
    catalog_id: string;
    relationship: string;
    contribution: string;
    notes: string;
  }[];
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
  scenario_ids: string[];
  linked_model_ids: string[];
  upstream_dataset_ids: string[];
  downstream_dataset_ids: string[];
  monitoring: Monitoring | null;
};

type Catalog = {
  last_verified: string;
  scenarios: ScenarioDefinition[];
  source_platforms: SourcePlatform[];
  models: ModelCard[];
  datasets: DatasetCard[];
  relations: ModelDatasetRelation[];
  dataset_relations: DatasetLineageRelation[];
  rankings: RankingBoard[];
};

const MODE_LABELS: Record<Mode, Localized> = {
  models: { zh: "模型 · 发布时间↓", en: "Models · release date↓" },
  datasets: { zh: "最新数据集", en: "Latest datasets" },
  sources: { zh: "来源平台", en: "Source platforms" },
  rankings: { zh: "行业排行榜", en: "Leaderboards" },
  lineage: { zh: "关系图谱", en: "Data lineage" },
  strategies: { zh: "数据策略", en: "Data strategies" },
};

const SCENARIO_LABELS: Record<string, Localized> = {
  "image-generation": { zh: "生图", en: "Image generation" },
  "video-generation": { zh: "生视频", en: "Video generation" },
  "digital-human": { zh: "数字人", en: "Digital humans" },
  "video-localization": { zh: "视频翻译", en: "Video localization" },
  "virtual-try-on": { zh: "Try-On", en: "Try-on" },
};

const SCENARIO_DESCRIPTIONS_EN: Record<string, string> = {
  "image-generation": "Text-to-image, image editing, personalization, and their image-text or preference data.",
  "video-generation": "Text-to-video, image-to-video, reference generation, joint audiovisual generation, and video editing.",
  "digital-human": "Identity preservation, audio-driven avatars, talking heads, lip sync, and cross-scene consistency.",
  "video-localization": "Cross-language dubbing, voice preservation, audiovisual translation, and facial-motion localization.",
  "virtual-try-on": "Person- and garment-conditioned generation, size-aware try-on, multi-item composition, and garment transfer.",
};

const RANKING_LABELS: Record<string, Localized> = {
  "text-to-image": { zh: "文生图", en: "Text to image" },
  "image-editing": { zh: "图片编辑", en: "Image editing" },
  "text-to-video": { zh: "文生视频", en: "Text to video" },
  "image-to-video": { zh: "图生视频", en: "Image to video" },
  "video-editing": { zh: "视频编辑", en: "Video editing" },
  "arena-text-to-image": { zh: "Arena 文生图", en: "Arena text to image" },
  "arena-image-edit": { zh: "Arena 图片编辑", en: "Arena image editing" },
  "arena-text-to-video": { zh: "Arena 文生视频", en: "Arena text to video" },
  "arena-image-to-video": { zh: "Arena 图生视频", en: "Arena image to video" },
  "arena-video-edit": { zh: "Arena 视频编辑", en: "Arena video editing" },
};

const MODALITY_LABELS: Record<string, Localized> = {
  all: { zh: "全部模态", en: "All modalities" },
  image: { zh: "图像", en: "Image" }, video: { zh: "视频", en: "Video" },
  audio: { zh: "音频", en: "Audio" }, text: { zh: "文本 / 元数据", en: "Text / metadata" },
  action: { zh: "具身 / Action", en: "Embodied / action" }, multimodal: { zh: "多模态", en: "Multimodal" },
  preference: { zh: "偏好数据", en: "Preference data" }, "3d": { zh: "3D", en: "3D" },
};

const SOURCE_PLATFORM_CATEGORY_LABELS: Record<string, Localized> = {
  "video-platform": { zh: "视频平台", en: "Video platform" },
  "streaming-and-studio": { zh: "流媒体与影视", en: "Streaming and studio" },
  "stock-media": { zh: "素材平台", en: "Stock media" }, ecommerce: { zh: "电商平台", en: "E-commerce" },
};

const SOURCE_PLATFORM_ACCESS_LABELS: Record<string, Localized> = {
  "documented-api": { zh: "公开文档 API", en: "Documented API" },
  "partner-api": { zh: "合作方 API", en: "Partner API" }, "partner-portal": { zh: "合作方门户", en: "Partner portal" },
  "licensed-service": { zh: "授权服务", en: "Licensed service" }, "not-cataloged": { zh: "尚未确认接口", en: "Interface unconfirmed" },
};

const DISCLOSURE_LABELS: Record<string, Localized> = {
  full: { zh: "完整披露", en: "Full" }, partial: { zh: "部分披露", en: "Partial" },
  "high-level": { zh: "仅高层策略", en: "High-level only" }, undisclosed: { zh: "未披露", en: "Undisclosed" },
};

const MONITORING_LABELS: Record<string, Localized> = {
  critical: { zh: "核心监控", en: "Critical watch" }, high: { zh: "重点监控", en: "Priority watch" }, standard: { zh: "常规监控", en: "Standard watch" },
};

const MONITORING_MODE_LABELS: Record<string, Localized> = {
  "content-revision": { zh: "内容版本监控", en: "Content revision" }, availability: { zh: "可用性监控", en: "Availability" },
};

const STAGE_LABELS: Record<string, Localized> = {
  pretraining: { zh: "预训练", en: "Pretraining" }, midtraining: { zh: "持续训练", en: "Mid-training" },
  "fine-tuning": { zh: "微调", en: "Fine-tuning" }, preference: { zh: "偏好对齐", en: "Preference" },
  distillation: { zh: "蒸馏", en: "Distillation" }, "action-adaptation": { zh: "动作适配", en: "Action adaptation" },
};

const SOURCE_TYPE_LABELS: Record<string, Localized> = {
  undisclosed: { zh: "未披露", en: "Undisclosed" }, "public-web": { zh: "公开网络", en: "Public web" },
  "public-dataset": { zh: "公开数据集", en: "Public dataset" }, licensed: { zh: "授权数据", en: "Licensed" },
  proprietary: { zh: "自有数据", en: "Proprietary" }, synthetic: { zh: "合成数据", en: "Synthetic" },
  "human-feedback": { zh: "人类反馈", en: "Human feedback" }, "robot-demonstration": { zh: "机器人示范", en: "Robot demonstrations" },
  "user-provided": { zh: "用户运行时输入", en: "Runtime user input" },
};

const ACCESS_LABELS: Record<string, Localized> = {
  open: { zh: "公开", en: "Open" }, gated: { zh: "需申请", en: "Gated" }, "metadata-only": { zh: "仅元数据", en: "Metadata only" },
  unavailable: { zh: "不可用", en: "Unavailable" }, "open-weights": { zh: "开放权重", en: "Open weights" },
  "gated-weights": { zh: "受限权重", en: "Gated weights" }, "api-only": { zh: "仅 API", en: "API only" },
  "product-only": { zh: "仅产品内", en: "Product only" }, "early-access": { zh: "早期访问", en: "Early access" },
  "research-preview": { zh: "研究预览", en: "Research preview" }, announced: { zh: "已发布预告", en: "Announced" },
};

const RELATION_ROLE_LABELS: Record<string, Localized> = {
  pretraining: { zh: "预训练", en: "Pretraining" }, "fine-tuning": { zh: "微调", en: "Fine-tuning" },
  preference: { zh: "偏好对齐", en: "Preference" }, evaluation: { zh: "评测", en: "Evaluation" }, distillation: { zh: "蒸馏", en: "Distillation" },
};

const DATA_AVAILABILITY_LABELS: Record<string, Localized> = {
  public: { zh: "公开数据", en: "Public" }, gated: { zh: "受限访问", en: "Gated" },
  "not-released": { zh: "尚未发布", en: "Not released" }, "runtime-input": { zh: "每次运行输入", en: "Runtime input" },
  undisclosed: { zh: "未披露", en: "Undisclosed" },
};

const DATASET_LINEAGE_LABELS: Record<string, Localized> = {
  "source-component": { zh: "来源组成", en: "Source component" }, "filtered-subset": { zh: "筛选子集", en: "Filtered subset" },
  "annotation-derivative": { zh: "标注衍生", en: "Annotation derivative" }, "benchmark-derivative": { zh: "评测衍生", en: "Benchmark derivative" },
  "transformed-derivative": { zh: "转换衍生", en: "Transformed derivative" },
};

const STATUS_LABELS: Record<string, Localized> = {
  verified: { zh: "已核验", en: "Verified" }, partial: { zh: "部分核验", en: "Partial" },
  watch: { zh: "持续追踪", en: "Watch" }, archived: { zh: "已归档", en: "Archived" },
};

function formatDate(value: string, locale: Locale = "zh") {
  return new Intl.DateTimeFormat(locale === "zh" ? "zh-CN" : "en-CA", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(`${value}T00:00:00Z`));
}

function normalize(value: string) {
  return value.toLocaleLowerCase().replaceAll("-", " ");
}

function mostRecentlyVerifiedModel(models: ModelCard[]) {
  return [...models].sort((left, right) =>
    right.last_verified.localeCompare(left.last_verified)
    || right.released_at.localeCompare(left.released_at)
    || left.name.localeCompare(right.name),
  )[0];
}

function uiLabel(labels: Record<string, Localized>, value: string, locale: Locale) {
  return labels[value] ? localized(labels[value], locale) : value.replaceAll("-", " ");
}

function datasetAccessAction(dataset: DatasetCard, locale: Locale) {
  const labels: Record<string, Localized> = {
    hosted: { zh: dataset.access.status === "gated" ? "登录并获取数据" : "下载 / 浏览数据文件", en: dataset.access.status === "gated" ? "Sign in to access data" : "Download / browse files" },
    urls: { zh: "获取源 URL 与下载工具", en: "Get source URLs and tools" }, metadata: { zh: "获取元数据与工具", en: "Get metadata and tools" },
    request: { zh: "申请数据访问", en: "Request data access" }, none: { zh: "查看不可用说明", en: "View availability note" },
  };
  return labels[dataset.access.type] ? localized(labels[dataset.access.type], locale) : locale === "zh" ? "查看数据访问入口" : "View data access";
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
  const { locale } = useLocale();
  return (
    <span className={`status-mark status-${status}`}>
      <span aria-hidden="true" />{uiLabel(STATUS_LABELS, status, locale)}
    </span>
  );
}

function EmptyState({ query }: { query: string }) {
  const { locale } = useLocale();
  return (
    <div className="empty-state">
      <span className="empty-symbol" aria-hidden="true">∅</span>
      <h3>{locale === "zh" ? "没有匹配项" : "No matches"}</h3>
      <p>{locale === "zh" ? <>试试缩短“{query || "当前条件"}”，或切换到全部场景和全部模态。</> : <>Shorten “{query || "the current query"}”, or switch to all scenarios and modalities.</>}</p>
    </div>
  );
}

function ModelResult({ model, scenarioLabels, expanded, onToggle, onOpenDataset }: {
  model: ModelCard;
  scenarioLabels: string[];
  expanded: boolean;
  onToggle: () => void;
  onOpenDataset: (datasetId: string) => void;
}) {
  const { locale } = useLocale();
  const namedDatasets = model.data.datasets.filter((item) => item.catalog_id);

  return (
    <article id={`model-${model.id}`} className={`result-card model-card ${expanded ? "is-expanded" : ""}`}>
      <button className="card-toggle" onClick={onToggle} aria-expanded={expanded}>
        <div className="card-index">M/{model.released_at.slice(2).replaceAll("-", "")}</div>
        <div className="card-primary">
          <div className="eyebrow-row">
            <span>{model.organization}</span>
              <span>{formatDate(model.released_at, locale)}</span>
          </div>
          <h3>{model.name}</h3>
          <p>{model.data.strategy_summary[0]}</p>
          <div className="tag-row">
            {scenarioLabels.slice(0, 2).map((item) => (
              <span className="tag tag-scenario" key={item}>{item}</span>
            ))}
            {model.modalities.slice(0, 4).map((item) => (
              <span className="tag" key={item}>{uiLabel(MODALITY_LABELS, item, locale)}</span>
            ))}
            {model.ranking_positions.slice(0, 2).map((item) => (
              <span className="tag tag-ranking" key={`${item.ranking_id}-${item.rank}`}>
                {uiLabel(RANKING_LABELS, item.ranking_id, locale)} #{item.rank}{item.component_count > 1 ? locale === "zh" ? " · 组合" : " · pipeline" : ""}
              </span>
            ))}
            {model.monitoring && <span className="tag tag-monitor">{uiLabel(MONITORING_LABELS, model.monitoring.priority, locale)}</span>}
          </div>
        </div>
        <div className="card-metrics">
          <div>
            <span className="metric-label">{locale === "zh" ? "数据披露" : "Data disclosure"}</span>
            <strong>{uiLabel(DISCLOSURE_LABELS, model.data.disclosure_level, locale)}</strong>
          </div>
          <div>
            <span className="metric-label">{locale === "zh" ? "目录关联" : "Catalog links"}</span>
            <strong>{model.data.datasets.length ? `${namedDatasets.length}/${model.data.datasets.length}` : locale === "zh" ? "无" : "None"}</strong>
          </div>
          <StatusMark status={model.status} />
        </div>
        <span className="expand-control" aria-hidden="true">{expanded ? "−" : "+"}</span>
      </button>

      {expanded && (
        <div className="card-detail">
          <section>
            <p className="detail-label">{locale === "zh" ? "训练数据策略" : "Training-data strategy"}</p>
            <ol className="strategy-list">
              {model.data.strategy_summary.map((item, index) => (
                <li key={item}><span>0{index + 1}</span><p>{item}</p></li>
              ))}
            </ol>
          </section>
          <section>
            <p className="detail-label">{locale === "zh" ? "阶段与操作" : "Stages and operations"}</p>
            <div className="stage-list">
              {model.data.stages.map((stage, index) => (
                <div className="stage" key={`${model.id}-${index}-${stage.name}`}>
                  <div className="stage-title">
                    <strong>{stage.name}</strong>
                    <span>{stage.scale_disclosed ? locale === "zh" ? "规模已披露" : "Scale disclosed" : locale === "zh" ? "规模未知" : "Scale unknown"}</span>
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
            <p className="detail-label">{locale === "zh" ? "数据引用" : "Data references"}</p>
            {model.data.datasets.length ? (
              <div className="data-reference-list">
                {model.data.datasets.map((item) => (
                  <div key={`${model.id}-${item.name}`}>
                    <strong>{item.name}</strong>
                    <span>{item.role} · {uiLabel(DATA_AVAILABILITY_LABELS, item.availability, locale)} · {item.scale ?? (locale === "zh" ? "规模未披露" : "Scale undisclosed")}</span>
                    <p>{item.notes}</p>
                    {item.catalog_id && (
                      <button className="relation-link" onClick={() => onOpenDataset(item.catalog_id!)}>
                        {locale === "zh" ? "打开数据卡" : "Open dataset card"} <span aria-hidden="true">→</span>
                      </button>
                    )}
                    {!item.catalog_id && (
                      <small className="reference-resolution">
                        {item.availability === "not-released"
                          ? locale === "zh" ? "没有数据卡：发布方尚未发布该语料。" : "No dataset card: the publisher has not released this corpus."
                          : item.availability === "runtime-input"
                            ? locale === "zh" ? "没有数据卡：这是每次运行的用户输入，不是固定发布语料。" : "No dataset card: this is per-run user input, not a released corpus."
                            : locale === "zh" ? "没有数据卡：一手资料没有披露可识别的数据集。" : "No dataset card: primary sources disclose no identifiable dataset."}
                      </small>
                    )}
                  </div>
                ))}
              </div>
            ) : <p className="unknown-copy">{locale === "zh" ? "官方没有公开任何可识别的数据集名称。" : "Official sources disclose no identifiable dataset names."}</p>}
            {namedDatasets.length > 0 && (
              <p className="linked-note">{locale === "zh" ? `其中 ${namedDatasets.length} 个已与本目录数据卡建立关联。` : `${namedDatasets.length} references resolve to catalog dataset cards.`}</p>
            )}
            {model.monitoring && (
              <p className="linked-note">{locale === "zh" ? "模型更新：" : "Model monitoring: "}{uiLabel(MONITORING_MODE_LABELS, model.monitoring.mode ?? "content-revision", locale)} / {uiLabel(MONITORING_LABELS, model.monitoring.priority, locale)}{locale === "zh" ? "。监控源变化时进入每周复核队列。" : ". Source changes enter the weekly review queue."}</p>
            )}
          </section>
          <section className="unknown-panel">
            <p className="detail-label">{locale === "zh" ? "仍然未知" : "Still unknown"}</p>
            <ul>
              {model.data.unknowns.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </section>
          <footer className="detail-footer">
            <span>{locale === "zh" ? "架构" : "Architecture"}：{model.architecture.family}</span>
            <nav aria-label={`${model.name} ${locale === "zh" ? "来源" : "sources"}`}>
              <ExternalLink href={model.evidence.release}>{locale === "zh" ? "官方发布" : "Official release"}</ExternalLink>
              {model.evidence.technical_report && <ExternalLink href={model.evidence.technical_report}>{locale === "zh" ? "技术报告" : "Technical report"}</ExternalLink>}
              {model.evidence.repository && <ExternalLink href={model.evidence.repository}>{locale === "zh" ? "代码仓库" : "Repository"}</ExternalLink>}
              {model.monitoring && <ExternalLink href={model.monitoring.source_url}>{locale === "zh" ? "版本监控源" : "Revision source"}</ExternalLink>}
            </nav>
          </footer>
        </div>
      )}
    </article>
  );
}

function DatasetResult({
  dataset,
  scenarioLabels,
  linkedModels,
  upstreamDatasets,
  downstreamDatasets,
  expanded,
  onToggle,
  onOpenModel,
  onOpenDataset,
}: {
  dataset: DatasetCard;
  scenarioLabels: string[];
  linkedModels: ModelCard[];
  upstreamDatasets: DatasetCard[];
  downstreamDatasets: DatasetCard[];
  expanded: boolean;
  onToggle: () => void;
  onOpenModel: (modelId: string) => void;
  onOpenDataset: (datasetId: string) => void;
}) {
  const { locale } = useLocale();
  const datasetLineageCount = upstreamDatasets.length + downstreamDatasets.length;
  return (
    <article id={`dataset-${dataset.id}`} className={`result-card dataset-card ${expanded ? "is-expanded" : ""}`}>
      <button className="card-toggle" onClick={onToggle} aria-expanded={expanded}>
        <div className="card-index">D/{dataset.released_at.slice(2).replaceAll("-", "")}</div>
        <div className="card-primary">
          <div className="eyebrow-row">
            <span>{dataset.organization}</span>
            <span>{locale === "zh" ? "发布于" : "Released"} {formatDate(dataset.released_at, locale)}</span>
          </div>
          <h3>{dataset.name}</h3>
          <p>{dataset.description}</p>
          <div className="tag-row">
            {scenarioLabels.slice(0, 2).map((item) => (
              <span className="tag tag-scenario" key={item}>{item}</span>
            ))}
            <span className="tag">{uiLabel(MODALITY_LABELS, dataset.modality, locale)}</span>
            {dataset.tasks.slice(0, 2).map((item) => <span className="tag" key={item}>{item}</span>)}
            {dataset.monitoring && <span className="tag tag-monitor">{uiLabel(MONITORING_LABELS, dataset.monitoring.priority, locale)}</span>}
            {linkedModels.length > 0 && <span className="tag tag-relation">{linkedModels.length} {locale === "zh" ? "个模型关联" : "model links"}</span>}
            {datasetLineageCount > 0 && <span className="tag tag-lineage">{datasetLineageCount} {locale === "zh" ? "条数据血缘" : "lineage links"}</span>}
          </div>
        </div>
        <div className="card-metrics">
          <div>
            <span className="metric-label">{locale === "zh" ? "样本规模" : "Scale"}</span>
            <strong>{dataset.scale_label}</strong>
          </div>
          <div>
            <span className="metric-label">{locale === "zh" ? "访问方式" : "Access"}</span>
            <strong>{uiLabel(ACCESS_LABELS, dataset.access.status, locale)}</strong>
          </div>
          <StatusMark status={dataset.status} />
        </div>
        <span className="expand-control" aria-hidden="true">{expanded ? "−" : "+"}</span>
      </button>

      {expanded && (
        <div className="card-detail dataset-detail">
          <section className="access-panel">
            <p className="detail-label">{locale === "zh" ? "数据获取入口" : "Data access"}</p>
            <ExternalLink href={dataset.access.url}>{datasetAccessAction(dataset, locale)}</ExternalLink>
            <p>{dataset.access.notes}</p>
          </section>
          <section>
            <p className="detail-label">{locale === "zh" ? "数据与标注" : "Data and annotations"}</p>
            <dl className="fact-grid">
              <div><dt>{locale === "zh" ? "标注来源" : "Annotation source"}</dt><dd>{dataset.annotations.source}</dd></div>
              <div><dt>{locale === "zh" ? "标注类型" : "Annotation types"}</dt><dd>{dataset.annotations.types.join(" · ")}</dd></div>
              <div><dt>{locale === "zh" ? "处理格式" : "Format"}</dt><dd>{dataset.processing.recommended_format}</dd></div>
              <div><dt>{locale === "zh" ? "账号要求" : "Account required"}</dt><dd>{dataset.access.requires_account ? locale === "zh" ? "需要" : "Yes" : locale === "zh" ? "不需要" : "No"}</dd></div>
              <div><dt>{locale === "zh" ? "首次发布" : "First released"}</dt><dd>{formatDate(dataset.released_at, locale)}</dd></div>
              <div><dt>{locale === "zh" ? "最近核验" : "Last verified"}</dt><dd>{formatDate(dataset.last_verified, locale)}</dd></div>
              {dataset.monitoring && (
                <div>
                  <dt>{locale === "zh" ? "更新监控" : "Monitoring"}</dt>
                  <dd>{uiLabel(MONITORING_MODE_LABELS, dataset.monitoring.mode ?? "content-revision", locale)} / {uiLabel(MONITORING_LABELS, dataset.monitoring.priority, locale)}</dd>
                </div>
              )}
            </dl>
          </section>
          <section>
            <p className="detail-label">{locale === "zh" ? "许可边界" : "License boundaries"}</p>
            <dl className="fact-grid">
              <div><dt>{locale === "zh" ? "元数据" : "Metadata"}</dt><dd>{dataset.license.metadata}</dd></div>
              <div><dt>{locale === "zh" ? "媒体内容" : "Media"}</dt><dd>{dataset.license.media}</dd></div>
              <div><dt>{locale === "zh" ? "商用" : "Commercial use"}</dt><dd>{dataset.license.commercial_use}</dd></div>
              <div><dt>{locale === "zh" ? "再分发" : "Redistribution"}</dt><dd>{dataset.license.redistribution}</dd></div>
            </dl>
            <p className="license-note">{dataset.license.notes}</p>
          </section>
          {(linkedModels.length > 0
            || upstreamDatasets.length > 0
            || downstreamDatasets.length > 0
            || dataset.evidence.used_by.length > 0) && (
            <section className="relation-panel">
              <p className="detail-label">{locale === "zh" ? "模型关系与数据血缘" : "Model relations and data lineage"}</p>
              {linkedModels.length > 0 && (
                <div className="relation-list relation-group">
                  <span className="relation-group-label">{locale === "zh" ? "关联模型" : "Linked models"}</span>
                  {linkedModels.map((model) => (
                    <button className="relation-link" onClick={() => onOpenModel(model.id)} key={model.id}>
                      <span>{model.name}</span><small>{model.data.datasets.find((item) => item.catalog_id === dataset.id)?.role ?? (locale === "zh" ? "关联" : "Linked")}</small><b aria-hidden="true">→</b>
                    </button>
                  ))}
                </div>
              )}
              {upstreamDatasets.length > 0 && (
                <div className="relation-list relation-group">
                  <span className="relation-group-label">{locale === "zh" ? "上游数据集" : "Upstream datasets"}</span>
                  {upstreamDatasets.map((source) => {
                    const lineage = dataset.derived_from?.find((item) => item.catalog_id === source.id);
                    return (
                      <button className="relation-link" onClick={() => onOpenDataset(source.id)} key={source.id}>
                        <span>{source.name}</span>
                        <small>{uiLabel(DATASET_LINEAGE_LABELS, lineage?.relationship ?? "", locale)}</small>
                        <b aria-hidden="true">↑</b>
                      </button>
                    );
                  })}
                </div>
              )}
              {downstreamDatasets.length > 0 && (
                <div className="relation-list relation-group">
                  <span className="relation-group-label">{locale === "zh" ? "下游衍生数据集" : "Derived datasets"}</span>
                  {downstreamDatasets.map((derived) => (
                    <button className="relation-link" onClick={() => onOpenDataset(derived.id)} key={derived.id}>
                      <span>{derived.name}</span>
                      <small>{uiLabel(DATASET_LINEAGE_LABELS, derived.derived_from?.find((item) => item.catalog_id === dataset.id)?.relationship ?? "", locale)}</small>
                      <b aria-hidden="true">↓</b>
                    </button>
                  ))}
                </div>
              )}
              {dataset.evidence.used_by.length > 0 && (
                <p className="editorial-relation">
                  {locale === "zh" ? "上游资料提及" : "Mentioned upstream"}：{dataset.evidence.used_by.join(locale === "zh" ? "、" : ", ")}。{locale === "zh" ? <>目录内反向链接只由模型卡的 <code>catalog_id</code> 自动生成。</> : <>Catalog backlinks are generated only from model-card <code>catalog_id</code> values.</>}
                </p>
              )}
            </section>
          )}
          <section className="unknown-panel">
            <p className="detail-label">{locale === "zh" ? "已知限制" : "Known limitations"}</p>
            <ul>
              {dataset.quality.known_limitations.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </section>
          <footer className="detail-footer">
            <span>{dataset.access.notes}</span>
            <nav aria-label={`${dataset.name} ${locale === "zh" ? "来源" : "sources"}`}>
              <ExternalLink href={dataset.access.url}>{datasetAccessAction(dataset, locale)}</ExternalLink>
              <ExternalLink href={dataset.evidence.homepage}>{locale === "zh" ? "项目主页" : "Project page"}</ExternalLink>
              {dataset.release_date_source !== dataset.evidence.homepage && (
                <ExternalLink href={dataset.release_date_source}>{locale === "zh" ? "发布日期证据" : "Release-date evidence"}</ExternalLink>
              )}
              {dataset.evidence.paper && dataset.evidence.paper !== dataset.release_date_source && (
                <ExternalLink href={dataset.evidence.paper}>{locale === "zh" ? "论文" : "Paper"}</ExternalLink>
              )}
              {dataset.monitoring && <ExternalLink href={dataset.monitoring.source_url}>{locale === "zh" ? "版本监控源" : "Revision source"}</ExternalLink>}
            </nav>
          </footer>
        </div>
      )}
    </article>
  );
}

function LineageOverview({ modelRelations, datasetRelations, onOpenModel, onOpenDataset }: {
  modelRelations: EnrichedRelation[];
  datasetRelations: EnrichedDatasetLineage[];
  onOpenModel: (modelId: string) => void;
  onOpenDataset: (datasetId: string) => void;
}) {
  const { locale } = useLocale();
  const modelCount = new Set(modelRelations.map((item) => item.model_id)).size;
  const datasetCount = new Set([
    ...modelRelations.map((item) => item.dataset_id),
    ...datasetRelations.flatMap((item) => [item.source_dataset_id, item.derived_dataset_id]),
  ]).size;
  const relationCount = modelRelations.length + datasetRelations.length;

  return (
    <section className="lineage-overview" aria-labelledby="lineage-title">
      <header className="lineage-summary">
        <div>
          <p className="comparison-kicker">LINEAGE / CANONICAL</p>
          <h3 id="lineage-title">{locale === "zh" ? "从上游数据，一路追到衍生集和模型。" : "Trace upstream data into derivatives and models."}</h3>
          <p>{locale === "zh" ? <>模型关系来自模型卡的 <code>catalog_id</code>；数据血缘来自子数据集的 <code>derived_from</code>。两类边都保留原始证据边界。</> : <>Model relations come from model-card <code>catalog_id</code> values; dataset lineage comes from <code>derived_from</code>. Both preserve their evidence boundaries.</>}</p>
        </div>
        <dl>
          <div><dt>{locale === "zh" ? "当前关系" : "Relations"}</dt><dd>{relationCount}</dd></div>
          <div><dt>{locale === "zh" ? "关联模型" : "Models"}</dt><dd>{modelCount}</dd></div>
          <div><dt>{locale === "zh" ? "关联数据集" : "Datasets"}</dt><dd>{datasetCount}</dd></div>
        </dl>
      </header>
      {modelRelations.length > 0 && (
        <section className="lineage-section">
          <div className="lineage-section-heading"><span>MODEL → DATASET</span><strong>{locale === "zh" ? "模型使用了哪些数据" : "Data used by models"}</strong></div>
          <div className="lineage-grid">
            {modelRelations.map((relation) => (
              <article className="lineage-row" key={`${relation.model_id}-${relation.dataset_id}-${relation.role}`}>
                <button
                  className="lineage-entity lineage-model"
                  onClick={() => onOpenModel(relation.model_id)}
                  aria-label={`${locale === "zh" ? "打开模型" : "Open model"} ${relation.model.name}`}
                >
                  <span>M</span>
                  <strong>{relation.model.name}</strong>
                  <small>{relation.model.organization}</small>
                  {relation.model.monitoring && <small>{uiLabel(MONITORING_LABELS, relation.model.monitoring.priority, locale)}</small>}
                </button>
                <div className="lineage-edge">
                  <strong>{uiLabel(RELATION_ROLE_LABELS, relation.role, locale)}</strong>
                  <span>{uiLabel(DATA_AVAILABILITY_LABELS, relation.availability, locale)}</span>
                  <small>{relation.scale ?? (locale === "zh" ? "规模未披露" : "Scale undisclosed")}</small>
                </div>
                <button
                  className="lineage-entity lineage-dataset"
                  onClick={() => onOpenDataset(relation.dataset_id)}
                  aria-label={`${locale === "zh" ? "打开数据集" : "Open dataset"} ${relation.dataset.name}`}
                >
                  <span>D</span>
                  <strong>{relation.dataset.name}</strong>
                  <small>
                    {uiLabel(MODALITY_LABELS, relation.dataset.modality, locale)} · {uiLabel(ACCESS_LABELS, relation.dataset.access.status, locale)}
                    {relation.dataset.monitoring ? ` · ${uiLabel(MONITORING_LABELS, relation.dataset.monitoring.priority, locale)}` : ""}
                  </small>
                </button>
              </article>
            ))}
          </div>
        </section>
      )}
      {datasetRelations.length > 0 && (
        <section className="lineage-section">
          <div className="lineage-section-heading"><span>DATASET → DATASET</span><strong>{locale === "zh" ? "上游数据如何形成衍生集" : "How upstream data forms derivatives"}</strong></div>
          <div className="lineage-grid">
            {datasetRelations.map((relation) => (
              <article className="lineage-row" key={`${relation.source_dataset_id}-${relation.derived_dataset_id}`}>
                <button
                  className="lineage-entity lineage-dataset"
                  onClick={() => onOpenDataset(relation.source_dataset_id)}
                  aria-label={`${locale === "zh" ? "打开上游数据集" : "Open upstream dataset"} ${relation.sourceDataset.name}`}
                >
                  <span>D</span>
                  <strong>{relation.sourceDataset.name}</strong>
                  <small>{locale === "zh" ? "上游" : "Upstream"} · {uiLabel(MODALITY_LABELS, relation.sourceDataset.modality, locale)}</small>
                </button>
                <div className="lineage-edge lineage-edge-dataset">
                  <strong>{uiLabel(DATASET_LINEAGE_LABELS, relation.relationship, locale)}</strong>
                  <span>{relation.contribution}</span>
                  <small>{locale === "zh" ? "已核验派生关系" : "Verified derivative"}</small>
                </div>
                <button
                  className="lineage-entity lineage-derived"
                  onClick={() => onOpenDataset(relation.derived_dataset_id)}
                  aria-label={`${locale === "zh" ? "打开衍生数据集" : "Open derived dataset"} ${relation.derivedDataset.name}`}
                >
                  <span>D′</span>
                  <strong>{relation.derivedDataset.name}</strong>
                  <small>
                    {locale === "zh" ? "衍生" : "Derived"} · {uiLabel(ACCESS_LABELS, relation.derivedDataset.access.status, locale)}
                    {relation.derivedDataset.monitoring ? ` · ${uiLabel(MONITORING_LABELS, relation.derivedDataset.monitoring.priority, locale)}` : ""}
                  </small>
                </button>
              </article>
            ))}
          </div>
        </section>
      )}
    </section>
  );
}

function RankingOverview({ boards, modelById, onOpenModel }: {
  boards: RankingBoard[];
  modelById: Map<string, ModelCard>;
  onOpenModel: (modelId: string) => void;
}) {
  const { locale } = useLocale();
  const monitored = boards.reduce((count, board) => count + board.entries.length, 0);
  const cataloged = boards.reduce(
    (count, board) => count + board.entries.filter((entry) => entry.model_id).length,
    0,
  );
  const componentCount = boards.reduce(
    (count, board) => count + board.entries.reduce((total, entry) => total + entry.components.length, 0),
    0,
  );
  const catalogedComponents = boards.reduce(
    (count, board) => count + board.entries.reduce(
      (total, entry) => total + entry.components.filter((component) => component.model_id).length,
      0,
    ),
    0,
  );
  return (
    <section className="ranking-overview" aria-labelledby="ranking-title">
      <header className="ranking-summary">
        <div>
          <p className="comparison-kicker">RANKING / TOP 15 / OPEN + CLOSED</p>
          <h3 id="ranking-title">{locale === "zh" ? "头部模型不是凭印象补录，而是跟着榜单持续复核。" : "Leading models are tracked from live leaderboards, not memory."}</h3>
          <p>{locale === "zh" ? "每周同步 Artificial Analysis、Arena 与 AVGen-Bench 的生成媒体榜单。成员或名次变化进入复核队列，分数的小幅波动不单独提醒。" : "Artificial Analysis, Arena, and AVGen-Bench are synchronized weekly. Membership and rank changes enter review; minor score noise does not."}</p>
        </div>
        <dl>
          <div><dt>{locale === "zh" ? "榜单" : "Boards"}</dt><dd>{boards.length}</dd></div>
          <div><dt>{locale === "zh" ? "监控席位" : "Tracked entries"}</dt><dd>{monitored}</dd></div>
          <div><dt>{locale === "zh" ? "席位映射" : "Mapped entries"}</dt><dd>{cataloged}/{monitored}</dd></div>
          <div><dt>{locale === "zh" ? "组件关系" : "Components"}</dt><dd>{catalogedComponents}/{componentCount}</dd></div>
        </dl>
      </header>
      <div className="ranking-boards">
        {boards.map((board) => (
          <article className="ranking-board" key={board.id}>
            <header>
              <div><span>{board.provider.toUpperCase()}</span><h4>{board.label}</h4></div>
              <ExternalLink href={board.source_url}>{locale === "zh" ? "榜单原页" : "Source leaderboard"}</ExternalLink>
            </header>
            <ol>
              {board.entries.map((entry) => (
                <li key={`${board.id}-${entry.rank}-${entry.model}`}>
                  <strong className="ranking-rank">{String(entry.rank).padStart(2, "0")}</strong>
                  <div>
                    <b>{entry.model}</b>
                    <span>{entry.creator} · {entry.released ? `${locale === "zh" ? board.date_label : "Released"} ${entry.released}` : locale === "zh" ? "发布日期未列" : "Release date not listed"}</span>
                    {entry.components.length > 1 && <small>{locale === "zh" ? "组合管线" : "Pipeline"}: {entry.components.length} {locale === "zh" ? "个组件模型" : "components"}</small>}
                  </div>
                  <div className="ranking-score"><strong>{Number.isInteger(entry.score) ? entry.score : entry.score.toFixed(1)}</strong><span>{board.score_label}</span></div>
                  <span className={`ranking-access ${entry.open_weights ? "is-open" : ""}`}>
                    {entry.open_weights ? entry.license || (locale === "zh" ? "开放权重" : "Open weights") : entry.license || (locale === "zh" ? "闭源 / 服务" : "Closed / service")}
                  </span>
                  <div className="ranking-model-links" aria-label={`${entry.model} ${locale === "zh" ? "组件模型" : "component models"}`}>
                    {entry.components.map((component) => {
                      const model = component.model_id ? modelById.get(component.model_id) : undefined;
                      return model ? (
                        <button
                          type="button"
                          title={`${locale === "zh" ? "打开" : "Open"} ${model.name} ${locale === "zh" ? "模型卡" : "model card"}`}
                          onClick={() => onOpenModel(model.id)}
                          key={`${entry.rank}-${component.name}`}
                        >
                          <strong>{entry.components.length > 1 ? component.name : locale === "zh" ? "模型卡" : "Model card"}</strong>
                          <small>{model.strategy_profile.linked_dataset_count} {locale === "zh" ? "卡" : "cards"} / {model.strategy_profile.data_reference_count} {locale === "zh" ? "引用" : "references"}</small>
                        </button>
                      ) : (
                        <small key={`${entry.rank}-${component.name}`}>{component.name}: {locale === "zh" ? "待建卡" : "card pending"}</small>
                      );
                    })}
                  </div>
                </li>
              ))}
            </ol>
          </article>
        ))}
      </div>
    </section>
  );
}

function SourcePlatformOverview({
  platforms,
  scenarioLabels,
}: {
  platforms: SourcePlatform[];
  scenarioLabels: Map<string, string>;
}) {
  const { locale } = useLocale();
  const categories = [
    "video-platform",
    "streaming-and-studio",
    "stock-media",
    "ecommerce",
  ];
  const interfaceCount = platforms.filter((item) => item.data_access.interface_url).length;
  const highPriorityCount = platforms.filter((item) => item.monitoring.priority === "high").length;

  return (
    <section className="source-platform-overview" aria-labelledby="source-platform-title">
      <header className="source-platform-summary">
        <div>
          <h3 id="source-platform-title">{locale === "zh" ? "把网站来源和可下载数据集分开管理。" : "Manage source platforms separately from downloadable datasets."}</h3>
          <p>{locale === "zh" ? "这些条目是候选内容来源，不是数据集下载入口，也不代表已经获得抓取、训练、商用或再分发许可。" : "These are candidate content sources, not dataset downloads, and do not imply permission to collect, train, commercialize, or redistribute."}</p>
        </div>
        <dl>
          <div><dt>{locale === "zh" ? "候选平台" : "Platforms"}</dt><dd>{platforms.length}</dd></div>
          <div><dt>{locale === "zh" ? "已登记接口" : "Interfaces"}</dt><dd>{interfaceCount}</dd></div>
          <div><dt>{locale === "zh" ? "重点监控" : "Priority watch"}</dt><dd>{highPriorityCount}</dd></div>
        </dl>
      </header>
      <div className="source-platform-groups">
        {categories.map((category) => {
          const entries = platforms.filter((item) => item.category === category);
          if (entries.length === 0) return null;
          return (
            <article className="source-platform-group" key={category}>
              <header>
                <h4>{uiLabel(SOURCE_PLATFORM_CATEGORY_LABELS, category, locale)}</h4>
                <span>{entries.length}</span>
              </header>
              <div className="source-platform-list">
                {entries.map((platform) => (
                  <section className="source-platform-item" key={platform.id}>
                    <div className="source-platform-name">
                      <ExternalLink href={platform.homepage}>{platform.name}</ExternalLink>
                      <span>{formatDate(platform.last_reviewed, locale)} {locale === "zh" ? "复核" : "reviewed"}</span>
                    </div>
                    <p>{platform.content_scope}</p>
                    <div className="source-platform-access">
                      <span>{uiLabel(SOURCE_PLATFORM_ACCESS_LABELS, platform.data_access.status, locale)}</span>
                      {platform.data_access.interface_url && platform.data_access.interface_name ? (
                        <ExternalLink href={platform.data_access.interface_url}>
                          {platform.data_access.interface_name}
                        </ExternalLink>
                      ) : (
                        <strong>{locale === "zh" ? "仅登记官方站点" : "Official site only"}</strong>
                      )}
                    </div>
                    <p className="source-platform-scope">{locale === "zh" ? "可访问范围" : "Access scope"}：{platform.data_access.scope}</p>
                    <p className="source-platform-requirements">{locale === "zh" ? "准入条件" : "Requirements"}：{platform.data_access.requirements}</p>
                    <div className="tag-row">
                      {platform.modalities.map((item) => (
                        <span className="tag" key={item}>{uiLabel(MODALITY_LABELS, item, locale)}</span>
                      ))}
                      {platform.relevant_scenarios.map((item) => (
                        <span className="tag tag-scenario" key={item}>{scenarioLabels.get(item) ?? item}</span>
                      ))}
                    </div>
                    <footer>
                      <span>{locale === "zh" ? "来源平台，不是数据集" : "Source platform, not a dataset"}</span>
                      <strong>{platform.monitoring.priority === "high" ? locale === "zh" ? "重点监控" : "Priority watch" : locale === "zh" ? "标准监控" : "Standard watch"} · {locale === "zh" ? "权利需逐源审核" : "rights require source-level review"}</strong>
                    </footer>
                  </section>
                ))}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function StrategyMatrix({
  models,
  scenario,
  datasetById,
  onOpenDataset,
}: {
  models: ModelCard[];
  scenario: ScenarioDefinition | null;
  datasetById: Map<string, DatasetCard>;
  onOpenDataset: (datasetId: string) => void;
}) {
  const { locale } = useLocale();
  const title = scenario
    ? locale === "zh" ? `${scenario.short_label}：同场景数据策略对比` : `${scenario.short_label}: data-strategy comparison`
    : locale === "zh" ? "同场景数据策略对比" : "Compare data strategies within a scenario";

  return (
    <section className="strategy-comparison" aria-labelledby="strategy-comparison-title">
      <header>
        <div>
          <p className="comparison-kicker">COMPARE / SOURCE-BOUND</p>
          <h3 id="strategy-comparison-title">{title}</h3>
        </div>
        <p>{locale === "zh" ? "只比较一手资料明确披露的字段，不补全未知项，也不做综合评分。" : "Compare only fields disclosed by primary sources. Unknowns are not filled in, and no composite score is assigned."}</p>
      </header>
      {!scenario && (
        <div className="comparison-prompt">
          <strong>{locale === "zh" ? "先选择一个应用场景" : "Choose an application scenario"}</strong>
          <span>{locale === "zh" ? "生图、生视频、数字人、视频翻译与 Try-On 将在各自场景内比较。" : "Image, video, digital-human, localization, and try-on models are compared within their own scenarios."}</span>
        </div>
      )}
      {scenario && models.length === 0 && (
        <div className="comparison-prompt">
          <strong>{locale === "zh" ? "当前条件下没有可比较模型" : "No comparable models under these filters"}</strong>
          <span>{locale === "zh" ? "可清空搜索词或切换模态后重试。" : "Clear the search or switch modality to try again."}</span>
        </div>
      )}
      {scenario && models.length > 0 && (
        <div className="comparison-table-scroll" tabIndex={0} aria-label={`${scenario.short_label} ${locale === "zh" ? "策略比较表，可横向滚动" : "strategy comparison; scroll horizontally"}`}>
          <table className="comparison-table">
            <caption className="sr-only">{title}</caption>
            <thead>
              <tr>
                <th scope="col">{locale === "zh" ? "模型" : "Model"}</th>
                <th scope="col">{locale === "zh" ? "披露程度" : "Disclosure"}</th>
                <th scope="col">{locale === "zh" ? "训练阶段" : "Training stages"}</th>
                <th scope="col">{locale === "zh" ? "数据来源类型" : "Source types"}</th>
                <th scope="col">{locale === "zh" ? "数据引用" : "Data references"}</th>
                <th scope="col">{locale === "zh" ? "规模披露" : "Scale"}</th>
                <th scope="col">{locale === "zh" ? "未知项" : "Unknowns"}</th>
              </tr>
            </thead>
            <tbody>
              {models.map((model) => {
                const profile = model.strategy_profile;
                return (
                  <tr key={model.id}>
                    <th scope="row">
                      <a href={`#strategy-${model.id}`}>{model.name}</a>
                      <small>{model.organization}</small>
                    </th>
                    <td>
                      <span className="comparison-disclosure" data-level={model.data.disclosure_level}>
                        {uiLabel(DISCLOSURE_LABELS, model.data.disclosure_level, locale)}
                      </span>
                    </td>
                    <td>
                      <div className="comparison-terms">
                        {profile.stage_names.map((item, index) => (
                          <span key={`${index}-${item}`}>{uiLabel(STAGE_LABELS, item, locale)}</span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <div className="comparison-terms comparison-sources">
                        {profile.source_types.map((item) => (
                          <span data-undisclosed={item === "undisclosed" || undefined} key={item}>
                            {uiLabel(SOURCE_TYPE_LABELS, item, locale)}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="comparison-ratio">
                      {profile.data_reference_count ? (
                        <div className="comparison-dataset-cell">
                          <a href={`#strategy-datasets-${model.id}`}>
                            <strong>{profile.linked_dataset_count} {locale === "zh" ? "卡" : "cards"} / {profile.data_reference_count} {locale === "zh" ? "引用" : "references"}</strong>
                            <small>{locale === "zh" ? "查看完整引用" : "View all references"}</small>
                          </a>
                          <div className="comparison-dataset-links" aria-label={`${model.name} ${locale === "zh" ? "对应数据集" : "datasets"}`}>
                            {model.data.datasets.slice(0, 2).map((reference, referenceIndex) => {
                              const dataset = reference.catalog_id ? datasetById.get(reference.catalog_id) : undefined;
                              return dataset ? (
                                <button type="button" onClick={() => onOpenDataset(dataset.id)} key={`${model.id}-${reference.role}-${referenceIndex}-${reference.name}`}>
                                  {dataset.name} <span aria-hidden="true">→</span>
                                </button>
                              ) : (
                                <span title={locale === "zh" ? "尚无可打开的数据卡" : "No dataset card available"} key={`${model.id}-${reference.role}-${referenceIndex}-${reference.name}`}>{reference.name}</span>
                              );
                            })}
                            {model.data.datasets.length > 2 && (
                              <a href={`#strategy-datasets-${model.id}`}>+{model.data.datasets.length - 2} {locale === "zh" ? "条" : "more"}</a>
                            )}
                          </div>
                        </div>
                      ) : (
                        <><strong>{locale === "zh" ? "无" : "None"}</strong><small>{locale === "zh" ? "没有数据引用" : "No data references"}</small></>
                      )}
                    </td>
                    <td className="comparison-ratio">
                      <strong>{profile.scale_disclosed_stage_count}/{profile.stage_count}</strong>
                      <small>{locale === "zh" ? "披露阶段 / 全部" : "Disclosed / total"}</small>
                    </td>
                    <td className="comparison-unknowns">
                      <strong>{profile.unknown_count}</strong>
                      <small>{locale === "zh" ? "明确记录" : "Explicitly recorded"}</small>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function StrategyResult({
  model,
  scenarioLabels,
  datasetById,
  onOpenDataset,
}: {
  model: ModelCard;
  scenarioLabels: string[];
  datasetById: Map<string, DatasetCard>;
  onOpenDataset: (datasetId: string) => void;
}) {
  const { locale } = useLocale();
  const disclosed = disclosureScore(model.data.disclosure_level);
  const profile = model.strategy_profile;
  const linkedDatasets = model.linked_dataset_ids
    .map((datasetId) => datasetById.get(datasetId))
    .filter((dataset): dataset is DatasetCard => Boolean(dataset));

  return (
    <article className="strategy-card" id={`strategy-${model.id}`}>
      <header>
        <div>
          <span className="strategy-org">{model.organization}</span>
          <h3>{model.name}</h3>
          <div className="tag-row">
            {scenarioLabels.slice(0, 2).map((item) => (
              <span className="tag tag-scenario" key={item}>{item}</span>
            ))}
            {model.monitoring && <span className="tag tag-monitor">{uiLabel(MONITORING_LABELS, model.monitoring.priority, locale)}</span>}
          </div>
        </div>
        <div className="disclosure-meter" aria-label={`${locale === "zh" ? "披露程度" : "Disclosure"}：${uiLabel(DISCLOSURE_LABELS, model.data.disclosure_level, locale)}`}>
          {[1, 2, 3, 4].map((level) => <span className={level <= disclosed ? "is-on" : ""} key={level} />)}
        </div>
      </header>
      <p className="strategy-lead">{model.data.strategy_summary[0]}</p>
      {linkedDatasets.length > 0 && (
        <nav className="strategy-linked-strip" aria-label={`${model.name} ${locale === "zh" ? "已关联数据集" : "linked datasets"}`}>
          <div className="strategy-linked-label">
            <span>{locale === "zh" ? "已关联数据集" : "Linked datasets"}</span>
            <strong>{linkedDatasets.length} {locale === "zh" ? "张数据卡" : "dataset cards"}</strong>
          </div>
          <div className="strategy-linked-actions">
            {linkedDatasets.map((dataset) => (
              <button type="button" onClick={() => onOpenDataset(dataset.id)} key={dataset.id}>
                {dataset.name} <span aria-hidden="true">→</span>
              </button>
            ))}
          </div>
          <a href={`#strategy-datasets-${model.id}`}>{locale === "zh" ? "完整引用与下载入口" : "All references and downloads"} ↓</a>
        </nav>
      )}
      <div className="pipeline" aria-label={locale === "zh" ? "训练阶段" : "Training stages"}>
        {model.data.stages.map((stage, index) => (
          <div className="pipeline-stage" key={`${model.id}-${index}-${stage.name}`}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <strong>{stage.name}</strong>
            <small>{stage.source_types.join(" + ")}</small>
          </div>
        ))}
      </div>
      <div className="strategy-columns">
        <div>
          <p className="detail-label">{locale === "zh" ? "关键操作" : "Key operations"}</p>
          <div className="operation-row">
            {[...new Set(model.data.stages.flatMap((stage) => stage.operations))].map((item) => <code key={item}>{item}</code>)}
          </div>
        </div>
        <div>
          <p className="detail-label">{locale === "zh" ? "证据边界" : "Evidence boundaries"}</p>
          <p>{model.data.exact_datasets_disclosed ? locale === "zh" ? "公开了具体数据集名称。" : "Specific dataset names are disclosed." : locale === "zh" ? "未公开完整数据集清单。" : "The full dataset inventory is undisclosed."} {model.data.exact_mixture_disclosed ? locale === "zh" ? "混合比例可核验。" : "Mixture ratios are verifiable." : locale === "zh" ? "混合比例仍未知。" : "Mixture ratios remain unknown."}</p>
        </div>
      </div>
      <section className="strategy-datasets" id={`strategy-datasets-${model.id}`} aria-labelledby={`strategy-datasets-title-${model.id}`}>
        <header>
          <div>
            <p className="detail-label" id={`strategy-datasets-title-${model.id}`}>{locale === "zh" ? "关联数据集与访问入口" : "Dataset references and access"}</p>
            <p>{locale === "zh" ? "这里列出模型卡中每一条数据引用。已建数据卡的条目可继续查看详情或直接打开下载、申请入口。" : "Every data reference from the model card appears here. Linked cards open details, downloads, or access requests."}</p>
          </div>
          <strong>{profile.linked_dataset_count} {locale === "zh" ? "卡" : "cards"} / {profile.data_reference_count || 0} {locale === "zh" ? "引用" : "references"}</strong>
        </header>
        {model.data.datasets.length > 0 ? (
          <div className="strategy-dataset-list">
            {model.data.datasets.map((reference, referenceIndex) => {
              const dataset = reference.catalog_id ? datasetById.get(reference.catalog_id) : undefined;
              return (
                <article className="strategy-dataset-row" key={`${model.id}-${reference.role}-${referenceIndex}-${reference.name}`}>
                  <div className="strategy-dataset-name">
                    <strong>{dataset?.name ?? reference.name}</strong>
                    <div>
                      <span>{uiLabel(RELATION_ROLE_LABELS, reference.role, locale)}</span>
                      <span>{uiLabel(DATA_AVAILABILITY_LABELS, reference.availability, locale)}</span>
                      <span>{reference.scale ?? (locale === "zh" ? "规模未披露" : "Scale undisclosed")}</span>
                    </div>
                  </div>
                  <p>{reference.notes}</p>
                  {dataset ? (
                    <div className="strategy-dataset-actions">
                      <button type="button" className="relation-link" onClick={() => onOpenDataset(dataset.id)}>
                        {locale === "zh" ? "查看数据卡" : "View dataset card"} <span aria-hidden="true">→</span>
                      </button>
                      <ExternalLink href={dataset.access.url}>{datasetAccessAction(dataset, locale)}</ExternalLink>
                    </div>
                  ) : (
                    <small className="reference-resolution">
                      {reference.availability === "not-released"
                        ? locale === "zh" ? "发布方尚未公开该数据，暂无下载入口。" : "The publisher has not released this data; no download is available."
                        : reference.availability === "runtime-input"
                          ? locale === "zh" ? "这是每次运行的用户输入，不是可单独下载的固定数据集。" : "This is per-run user input, not a standalone downloadable dataset."
                          : locale === "zh" ? "一手资料未披露可识别的数据集，无法提供下载入口。" : "Primary sources disclose no identifiable dataset or download."}
                    </small>
                  )}
                </article>
              );
            })}
          </div>
        ) : (
          <p className="unknown-copy">{locale === "zh" ? "官方没有公开任何可识别的数据引用，因此暂无可展示的数据卡或下载入口。" : "Official sources disclose no identifiable data references, so no dataset card or download can be shown."}</p>
        )}
      </section>
      <footer>
        <span>{uiLabel(DISCLOSURE_LABELS, model.data.disclosure_level, locale)} / {profile.linked_dataset_count} {locale === "zh" ? "张数据卡" : "dataset cards"} · {profile.data_reference_count || (locale === "zh" ? "无" : "no")} {locale === "zh" ? "条引用" : "references"} / {profile.unknown_count} {locale === "zh" ? "项未知" : "unknowns"}</span>
        <ExternalLink href={model.evidence.technical_report ?? model.evidence.release}>{locale === "zh" ? "查看一手证据" : "View primary evidence"}</ExternalLink>
      </footer>
    </article>
  );
}

export function CatalogExplorer({ catalog }: { catalog: Catalog }) {
  const { locale } = useLocale();
  const [mode, setMode] = useState<Mode>("models");
  const [query, setQuery] = useState("");
  const [modality, setModality] = useState("all");
  const [scenario, setScenario] = useState("all");
  const [expanded, setExpanded] = useState<string | null>("flux-3");

  const scenarioLabels = useMemo(
    () => new Map(catalog.scenarios.map((item) => [item.id, SCENARIO_LABELS[item.id] ? localized(SCENARIO_LABELS[item.id], locale) : item.short_label])),
    [catalog.scenarios, locale],
  );
  const modelById = useMemo(
    () => new Map(catalog.models.map((item) => [item.id, item])),
    [catalog.models],
  );
  const datasetById = useMemo(
    () => new Map(catalog.datasets.map((item) => [item.id, item])),
    [catalog.datasets],
  );
  const recentModel = useMemo(
    () => mostRecentlyVerifiedModel(catalog.models),
    [catalog.models],
  );

  useEffect(() => {
    function restoreCatalogHash() {
      const target = parseCatalogHash(window.location.hash);
      if (!target) return;

      if (target.id === null) {
        setMode(target.mode);
        setQuery("");
        setModality("all");
        setScenario("all");
        setExpanded(null);
        scrollToCatalogTarget(target.elementId);
        return;
      }

      const targetExists = target.mode === "datasets"
        ? datasetById.has(target.id)
        : modelById.has(target.id);
      if (!targetExists) return;

      if (!document.getElementById(target.elementId)) {
        setMode(target.mode);
        setQuery("");
        setModality("all");
        setScenario("all");
      }
      setExpanded(target.mode === "strategies" ? null : target.id);
      scrollToCatalogTarget(target.elementId);
    }

    restoreCatalogHash();
    window.addEventListener("hashchange", restoreCatalogHash);
    window.addEventListener("popstate", restoreCatalogHash);
    return () => {
      window.removeEventListener("hashchange", restoreCatalogHash);
      window.removeEventListener("popstate", restoreCatalogHash);
    };
  }, [datasetById, modelById]);
  const lineageRecords = useMemo(
    () => catalog.relations.flatMap((relation): EnrichedRelation[] => {
      const model = modelById.get(relation.model_id);
      const dataset = datasetById.get(relation.dataset_id);
      return model && dataset ? [{ ...relation, model, dataset }] : [];
    }),
    [catalog.relations, datasetById, modelById],
  );
  const datasetLineageRecords = useMemo(
    () => catalog.dataset_relations.flatMap((relation): EnrichedDatasetLineage[] => {
      const sourceDataset = datasetById.get(relation.source_dataset_id);
      const derivedDataset = datasetById.get(relation.derived_dataset_id);
      return sourceDataset && derivedDataset ? [{ ...relation, sourceDataset, derivedDataset }] : [];
    }),
    [catalog.dataset_relations, datasetById],
  );

  const modelResults = useMemo(() => {
    const search = normalize(query.trim());
    return catalog.models.filter((model) => {
      const inModality = modality === "all" || model.modalities.includes(modality);
      const inScenario = scenario === "all" || model.scenario_ids.includes(scenario);
      const haystack = normalize([
        model.name,
        model.organization,
        ...model.tasks,
        ...model.modalities,
        ...model.data.strategy_summary,
        ...model.data.datasets.map((item) => item.name),
        ...model.data.stages.flatMap((stage) => stage.operations),
        model.monitoring?.priority ?? "",
        model.monitoring ? Object.values(MONITORING_LABELS[model.monitoring.priority]).join(" ") : "",
        model.monitoring ? Object.values(MONITORING_MODE_LABELS[model.monitoring.mode ?? "content-revision"]).join(" ") : "",
      ].join(" "));
      return inModality && inScenario && (!search || haystack.includes(search));
    });
  }, [catalog.models, modality, query, scenario]);

  const datasetResults = useMemo(() => {
    const search = normalize(query.trim());
    return catalog.datasets.filter((dataset) => {
      const inModality = modality === "all" || dataset.modality === modality;
      const inScenario = scenario === "all" || dataset.scenario_ids.includes(scenario);
      const haystack = normalize([
        dataset.name,
        dataset.organization,
        dataset.description,
        dataset.modality,
        ...dataset.tasks,
        ...dataset.annotations.types,
        ...dataset.evidence.used_by,
        dataset.monitoring?.priority ?? "",
        dataset.monitoring ? Object.values(MONITORING_LABELS[dataset.monitoring.priority]).join(" ") : "",
        dataset.monitoring ? Object.values(MONITORING_MODE_LABELS[dataset.monitoring.mode ?? "content-revision"]).join(" ") : "",
        ...dataset.linked_model_ids.map((id) => modelById.get(id)?.name ?? id),
        ...dataset.upstream_dataset_ids.map((id) => datasetById.get(id)?.name ?? id),
        ...dataset.downstream_dataset_ids.map((id) => datasetById.get(id)?.name ?? id),
        ...(dataset.derived_from ?? []).flatMap((item) => [
          item.relationship,
          item.contribution,
          item.notes,
        ]),
      ].join(" "));
      return inModality && inScenario && (!search || haystack.includes(search));
    });
  }, [catalog.datasets, datasetById, modality, modelById, query, scenario]);

  const modelLineageResults = useMemo(() => {
    const search = normalize(query.trim());
    return lineageRecords.filter((relation) => {
      const inModality = modality === "all"
        || relation.model.modalities.includes(modality)
        || relation.dataset.modality === modality;
      const inScenario = scenario === "all"
        || relation.model.scenario_ids.includes(scenario)
        || relation.dataset.scenario_ids.includes(scenario);
      const haystack = normalize([
        relation.model.name,
        relation.model.organization,
        relation.dataset.name,
        relation.dataset.organization,
        relation.reference_name,
        relation.role,
        relation.availability,
        relation.scale ?? "",
        relation.model.monitoring?.priority ?? "",
        relation.model.monitoring ? Object.values(MONITORING_LABELS[relation.model.monitoring.priority]).join(" ") : "",
        relation.dataset.monitoring?.priority ?? "",
        relation.dataset.monitoring ? Object.values(MONITORING_LABELS[relation.dataset.monitoring.priority]).join(" ") : "",
        ...relation.model.tasks,
        ...relation.dataset.tasks,
      ].join(" "));
      return inModality && inScenario && (!search || haystack.includes(search));
    });
  }, [lineageRecords, modality, query, scenario]);

  const datasetLineageResults = useMemo(() => {
    const search = normalize(query.trim());
    return datasetLineageRecords.filter((relation) => {
      const inModality = modality === "all"
        || relation.sourceDataset.modality === modality
        || relation.derivedDataset.modality === modality;
      const inScenario = scenario === "all"
        || relation.sourceDataset.scenario_ids.includes(scenario)
        || relation.derivedDataset.scenario_ids.includes(scenario);
      const haystack = normalize([
        relation.sourceDataset.name,
        relation.sourceDataset.organization,
        relation.derivedDataset.name,
        relation.derivedDataset.organization,
        relation.relationship,
        DATASET_LINEAGE_LABELS[relation.relationship] ? Object.values(DATASET_LINEAGE_LABELS[relation.relationship]).join(" ") : "",
        relation.contribution,
        relation.notes,
        ...relation.sourceDataset.tasks,
        ...relation.derivedDataset.tasks,
      ].join(" "));
      return inModality && inScenario && (!search || haystack.includes(search));
    });
  }, [datasetLineageRecords, modality, query, scenario]);

  const rankingResults = useMemo(() => {
    const search = normalize(query.trim());
    return catalog.rankings.flatMap((board): RankingBoard[] => {
      if (modality !== "all" && modality !== board.modality) return [];
      const entries = board.entries.filter((entry) => !search || normalize([
        board.id,
        board.provider,
        board.label,
        entry.model,
        entry.creator,
        ...entry.components.map((component) => component.name),
        entry.license ?? "",
        entry.open_weights ? "open weights 开放权重" : "closed 闭源",
      ].join(" ")).includes(search));
      return entries.length ? [{ ...board, entries }] : [];
    });
  }, [catalog.rankings, modality, query]);

  const sourcePlatformResults = useMemo(() => {
    const search = normalize(query.trim());
    return catalog.source_platforms.filter((platform) => {
      const inModality = modality === "all" || platform.modalities.includes(modality);
      const inScenario = scenario === "all" || platform.relevant_scenarios.includes(scenario);
      const haystack = normalize([
        platform.name,
        platform.homepage,
        platform.category,
        SOURCE_PLATFORM_CATEGORY_LABELS[platform.category] ? Object.values(SOURCE_PLATFORM_CATEGORY_LABELS[platform.category]).join(" ") : "",
        platform.content_scope,
        platform.data_access.status,
        platform.data_access.interface_name ?? "",
        platform.data_access.scope,
        platform.data_access.requirements,
        platform.monitoring.focus,
        ...platform.modalities,
        ...platform.relevant_scenarios,
        ...platform.relevant_scenarios.map((item) => scenarioLabels.get(item) ?? item),
      ].join(" "));
      return inModality && inScenario && (!search || haystack.includes(search));
    });
  }, [catalog.source_platforms, modality, query, scenario, scenarioLabels]);

  const visibleModalities = mode === "sources"
    ? ["all", "image", "video", "audio", "text"]
    : mode === "datasets"
    ? ["all", "image", "video", "audio", "3d", "preference"]
    : mode === "rankings"
      ? ["all", "image", "video"]
    : mode === "lineage"
      ? ["all", "image", "video", "audio", "3d", "preference", "multimodal", "action"]
    : ["all", "image", "video", "audio", "3d", "multimodal", "action"];
  const visibleCount = mode === "sources"
    ? sourcePlatformResults.length
    : mode === "datasets"
    ? datasetResults.length
    : mode === "rankings"
      ? rankingResults.reduce((count, board) => count + board.entries.length, 0)
    : mode === "lineage"
      ? modelLineageResults.length + datasetLineageResults.length
      : modelResults.length;
  const activeScenarioSource = scenario === "all"
    ? null
    : catalog.scenarios.find((item) => item.id === scenario) ?? null;
  const activeScenario = activeScenarioSource
    ? { ...activeScenarioSource, short_label: scenarioLabels.get(activeScenarioSource.id) ?? activeScenarioSource.short_label }
    : null;
  const exactDatasetModels = catalog.models.filter((item) => item.data.exact_datasets_disclosed).length;
  const openDatasets = catalog.datasets.filter((item) => item.access.status === "open").length;
  const scenarioCounts = useMemo(() => {
    if (mode === "rankings") {
      return Object.fromEntries(catalog.scenarios.map((item) => [item.id, 0]));
    }
    if (mode === "lineage") {
      return Object.fromEntries(catalog.scenarios.map((item) => [
        item.id,
        lineageRecords.filter((relation) => (
          relation.model.scenario_ids.includes(item.id)
          || relation.dataset.scenario_ids.includes(item.id)
        )).length + datasetLineageRecords.filter((relation) => (
          relation.sourceDataset.scenario_ids.includes(item.id)
          || relation.derivedDataset.scenario_ids.includes(item.id)
        )).length,
      ]));
    }
    if (mode === "sources") {
      return Object.fromEntries(catalog.scenarios.map((item) => [
        item.id,
        catalog.source_platforms.filter((entry) => entry.relevant_scenarios.includes(item.id)).length,
      ]));
    }
    const items = mode === "datasets" ? catalog.datasets : catalog.models;
    return Object.fromEntries(catalog.scenarios.map((item) => [
      item.id,
      items.filter((entry) => entry.scenario_ids.includes(item.id)).length,
    ]));
  }, [catalog.datasets, catalog.models, catalog.scenarios, catalog.source_platforms, datasetLineageRecords, lineageRecords, mode]);

  function totalForMode(item: Mode) {
    if (item === "datasets") return catalog.datasets.length;
    if (item === "sources") return catalog.source_platforms.length;
    if (item === "rankings") return catalog.rankings.reduce((count, board) => count + board.entries.length, 0);
    if (item === "lineage") return catalog.relations.length + catalog.dataset_relations.length;
    return catalog.models.length;
  }

  function switchMode(nextMode: Mode) {
    setMode(nextMode);
    setModality("all");
    setExpanded(null);
    window.history.replaceState(null, "", "#explorer");
  }

  function openRelation(targetMode: "models" | "datasets", id: string) {
    setMode(targetMode);
    setQuery("");
    setModality("all");
    setScenario("all");
    setExpanded(id);
    const prefix = targetMode === "models" ? "model" : "dataset";
    const elementId = `${prefix}-${id}`;
    window.history.pushState(null, "", `#${elementId}`);
    scrollToCatalogTarget(elementId);
  }

  return (
    <main>
      <SiteHeader active="catalog" status={`LIVING INDEX · ${formatDate(catalog.last_verified, locale)}`} />

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="kicker">{locale === "zh" ? "生成式 AI 数据情报" : "GENERATIVE AI DATA INTELLIGENCE"}</p>
          <h1>{locale === "zh" ? "追踪模型，" : "Trace models"}<br />{locale === "zh" ? "追到它的" : "back to their "}<span>{locale === "zh" ? "数据源头。" : "data origins."}</span></h1>
          <p className="hero-description">
            {locale === "zh" ? "不止告诉你“有哪些数据集”。这里持续拆解最新 AIGC 模型用了什么数据、怎样清洗与训练，以及官方仍未披露什么。" : "Go beyond dataset lists. See what recent AIGC models use, how data is cleaned and trained, and what official sources still leave undisclosed."}
          </p>
          <div className="hero-actions">
            <button onClick={() => document.querySelector("#explorer")?.scrollIntoView({ behavior: "smooth" })}>
              {locale === "zh" ? "打开目录" : "Open catalog"}
            </button>
          </div>
        </div>
        <aside className="hero-stats" aria-label={locale === "zh" ? "目录统计" : "Catalog statistics"}>
          <div className="stats-topline"><span>INDEX / 2026</span><span>CN / EN</span></div>
          <div className="stat-main"><strong>{catalog.models.length}</strong><span>{locale === "zh" ? <>最新模型<br />及数据策略</> : <>Recent models<br />and data strategies</>}</span></div>
          <div className="stat-grid">
            <div><strong>{catalog.datasets.length}</strong><span>{locale === "zh" ? "结构化数据集" : "Structured datasets"}</span></div>
            <div><strong>{openDatasets}</strong><span>{locale === "zh" ? "公开可访问" : "Publicly accessible"}</span></div>
            <div><strong>{exactDatasetModels}</strong><span>{locale === "zh" ? "披露具体数据" : "Specific data disclosed"}</span></div>
            <div><strong>{catalog.relations.length + catalog.dataset_relations.length}</strong><span>{locale === "zh" ? "模型与数据血缘" : "Model and data lineage"}</span></div>
          </div>
          <div className="stats-note">{locale === "zh" ? "每条结论保留发布日期、核验时间和官方证据。未知不是空白，也是结论。" : "Every conclusion retains release dates, verification time, and official evidence. Unknown is also a finding."}</div>
        </aside>
      </section>

      <section className="signal-strip" aria-label={locale === "zh" ? "最近核验的模型" : "Most recently verified model"}>
        <span className="signal-label">{locale === "zh" ? "最近核验" : "RECENTLY VERIFIED"}</span>
        <span className="signal-date">{locale === "zh" ? "核验" : "Verified"} {formatDate(recentModel.last_verified, locale)}</span>
        <strong>{recentModel.name}</strong>
        <p className="signal-meta">
          <span>{locale === "zh" ? "发布" : "Released"} {formatDate(recentModel.released_at, locale)}</span>
          <span>{uiLabel(DISCLOSURE_LABELS, recentModel.data.disclosure_level, locale)}</span>
          <span>{uiLabel(ACCESS_LABELS, recentModel.access.status, locale)}</span>
        </p>
        <button onClick={() => openRelation("models", recentModel.id)}>
          {locale === "zh" ? "查看模型卡" : "View model card"} ↘
        </button>
      </section>

      <section className="explorer" id="explorer">
        <div className="explorer-heading">
          <div>
            <h2>{locale === "zh" ? "查模型，也查它背后的数据逻辑。" : "Search models—and the data logic behind them."}</h2>
          </div>
          <p>{locale === "zh" ? "目录直接由仓库中的 YAML 数据卡生成；更新事实源，页面随之更新。" : "The catalog is generated directly from repository YAML cards; update the evidence source and the page follows."}</p>
        </div>

        <div className="mode-tabs" role="tablist" aria-label={locale === "zh" ? "目录类型" : "Catalog views"}>
          {(Object.keys(MODE_LABELS) as Mode[]).map((item) => (
            <button
              className={mode === item ? "is-active" : ""}
              key={item}
              onClick={() => switchMode(item)}
              role="tab"
              aria-selected={mode === item}
            >
              <span>{localized(MODE_LABELS[item], locale)}</span>
              <small>{totalForMode(item)}</small>
            </button>
          ))}
        </div>

        {mode !== "rankings" && <div className="scenario-rail" role="group" aria-label={locale === "zh" ? "应用场景筛选" : "Application scenario filter"}>
          <span className="scenario-caption">{locale === "zh" ? "应用场景" : "Scenarios"}</span>
          <div className="scenario-options">
            <button
              className={scenario === "all" ? "is-active" : ""}
              onClick={() => { setScenario("all"); setExpanded(null); }}
              aria-pressed={scenario === "all"}
            >
              <span>{locale === "zh" ? "全部场景" : "All scenarios"}</span>
              <small>{totalForMode(mode)}</small>
            </button>
            {catalog.scenarios.map((item) => (
              <button
                className={scenario === item.id ? "is-active" : ""}
                onClick={() => { setScenario(item.id); setExpanded(null); }}
                aria-pressed={scenario === item.id}
                title={locale === "zh" ? item.description : SCENARIO_DESCRIPTIONS_EN[item.id] ?? item.description}
                key={item.id}
              >
                <span>{scenarioLabels.get(item.id) ?? item.short_label}</span>
                <small>{scenarioCounts[item.id]}</small>
              </button>
            ))}
          </div>
        </div>}

        <div className="search-panel">
          <label className="search-box">
            <span aria-hidden="true">⌕</span>
            <span className="sr-only">{locale === "zh" ? "搜索目录" : "Search catalog"}</span>
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={locale === "zh" ? mode === "datasets"
                ? "搜索数据集、任务、标注类型…" : mode === "sources" ? "搜索来源平台、类别、模态或应用场景…"
                  : mode === "rankings" ? "搜索榜单模型、机构、开放权重…" : mode === "lineage" ? "搜索模型、上游数据、衍生集或关系类型…"
                    : "搜索模型、机构、数据集或训练操作…" : mode === "datasets" ? "Search datasets, tasks, or annotations…"
                : mode === "sources" ? "Search platforms, categories, modalities, or scenarios…" : mode === "rankings" ? "Search ranked models, organizations, or open weights…"
                  : mode === "lineage" ? "Search models, upstream data, derivatives, or relation types…" : "Search models, organizations, datasets, or operations…"}
            />
            {query && <button onClick={() => setQuery("")} aria-label={locale === "zh" ? "清空搜索" : "Clear search"}>×</button>}
          </label>
          <div className="filter-row" aria-label={locale === "zh" ? "模态筛选" : "Modality filter"}>
            {visibleModalities.map((item) => (
              <button className={modality === item ? "is-active" : ""} onClick={() => setModality(item)} key={item}>
                {uiLabel(MODALITY_LABELS, item, locale)}
              </button>
            ))}
          </div>
          <div className="result-count">
            <strong>{visibleCount}</strong> {locale === "zh" ? "条结果" : "results"}
            {mode === "models" && <small>{locale === "zh" ? "发布时间：新 → 旧" : "Release date: new → old"}</small>}
          </div>
        </div>

        <div className="result-list" role="tabpanel">
          {mode === "strategies" && (
            <StrategyMatrix
              models={modelResults}
              scenario={activeScenario}
              datasetById={datasetById}
              onOpenDataset={(id) => openRelation("datasets", id)}
            />
          )}
          {mode === "lineage" && visibleCount > 0 && (
            <LineageOverview
              modelRelations={modelLineageResults}
              datasetRelations={datasetLineageResults}
              onOpenModel={(id) => openRelation("models", id)}
              onOpenDataset={(id) => openRelation("datasets", id)}
            />
          )}
          {mode === "rankings" && visibleCount > 0 && (
            <RankingOverview
              boards={rankingResults}
              modelById={modelById}
              onOpenModel={(id) => openRelation("models", id)}
            />
          )}
          {mode === "sources" && visibleCount > 0 && (
            <SourcePlatformOverview
              platforms={sourcePlatformResults}
              scenarioLabels={scenarioLabels}
            />
          )}
          {mode === "models" && modelResults.map((model) => (
            <ModelResult
              key={model.id}
              model={model}
              scenarioLabels={model.scenario_ids.map((item) => scenarioLabels.get(item) ?? item)}
              expanded={expanded === model.id}
              onToggle={() => setExpanded(expanded === model.id ? null : model.id)}
              onOpenDataset={(id) => openRelation("datasets", id)}
            />
          ))}
          {mode === "datasets" && datasetResults.map((dataset) => (
            <DatasetResult
              key={dataset.id}
              dataset={dataset}
              linkedModels={dataset.linked_model_ids.flatMap((id) => {
                const model = modelById.get(id);
                return model ? [model] : [];
              })}
              upstreamDatasets={dataset.upstream_dataset_ids.flatMap((id) => {
                const source = datasetById.get(id);
                return source ? [source] : [];
              })}
              downstreamDatasets={dataset.downstream_dataset_ids.flatMap((id) => {
                const derived = datasetById.get(id);
                return derived ? [derived] : [];
              })}
              scenarioLabels={dataset.scenario_ids.map((item) => scenarioLabels.get(item) ?? item)}
              expanded={expanded === dataset.id}
              onToggle={() => setExpanded(expanded === dataset.id ? null : dataset.id)}
              onOpenModel={(id) => openRelation("models", id)}
              onOpenDataset={(id) => openRelation("datasets", id)}
            />
          ))}
          {mode === "strategies" && modelResults.map((model) => (
            <StrategyResult
              model={model}
              scenarioLabels={model.scenario_ids.map((item) => scenarioLabels.get(item) ?? item)}
              datasetById={datasetById}
              onOpenDataset={(id) => openRelation("datasets", id)}
              key={model.id}
            />
          ))}
          {visibleCount === 0 && <EmptyState query={query} />}
        </div>
      </section>

      <section className="method-section">
        <div className="method-heading">
          <h2>{locale === "zh" ? "我们把“没说”也写下来。" : "We record what sources do not say."}</h2>
        </div>
        <div className="method-grid">
          <article><span>01</span><h3>{locale === "zh" ? "一手来源优先" : "Primary sources first"}</h3><p>{locale === "zh" ? "官方发布、论文、模型卡和代码仓库交叉核验，不用能力猜训练数据。" : "Cross-check official releases, papers, model cards, and repositories; never infer training data from capabilities."}</p></article>
          <article><span>02</span><h3>{locale === "zh" ? "数据与策略分层" : "Separate data from strategy"}</h3><p>{locale === "zh" ? "区分可下载数据集、未发布语料、合成数据和人类反馈，以及它们所在的训练阶段。" : "Distinguish downloadable datasets, unreleased corpora, synthetic data, human feedback, and their training stages."}</p></article>
          <article><span>03</span><h3>{locale === "zh" ? "权利边界显式化" : "Make rights boundaries explicit"}</h3><p>{locale === "zh" ? "元数据许可不等于媒体可商用；访问方式、商用和再分发分别记录。" : "Metadata licenses do not make media commercially usable; access, commercial use, and redistribution are recorded separately."}</p></article>
          <article><span>04</span><h3>{locale === "zh" ? "持续复核" : "Continuous review"}</h3><p>{locale === "zh" ? "活跃模型 14 天、普通模型 45 天、数据集 90 天触发过期检查。" : "Active models expire after 14 days, standard models after 45, and datasets after 90."}</p></article>
        </div>
      </section>

      <footer className="site-footer">
        <div className="footer-brand">AIGC<span>/</span>DATAHUB</div>
        <p>{locale === "zh" ? "一个持续更新、可复现、对未知诚实的生成式 AI 数据工程索引。" : "A continuously updated, reproducible generative-AI data index that stays honest about unknowns."}</p>
        <div><span>LAST VERIFIED</span><strong>{formatDate(catalog.last_verified, locale)}</strong></div>
        <a href="https://github.com/TobinZuo/AIGCDataHub" target="_blank" rel="noreferrer">CONTRIBUTE ↗</a>
      </footer>
    </main>
  );
}
