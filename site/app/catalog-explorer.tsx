"use client";

import { useMemo, useState } from "react";

type Mode = "models" | "datasets" | "sources" | "rankings" | "lineage" | "strategies";

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

const MODE_LABELS: Record<Mode, string> = {
  models: "模型 · 发布时间↓",
  datasets: "最新数据集",
  sources: "来源平台",
  rankings: "行业排行榜",
  lineage: "关系图谱",
  strategies: "数据策略",
};

const RANKING_LABELS: Record<string, string> = {
  "text-to-image": "文生图",
  "image-editing": "图片编辑",
  "text-to-video": "文生视频",
  "image-to-video": "图生视频",
  "video-editing": "视频编辑",
  "arena-text-to-image": "Arena 文生图",
  "arena-image-edit": "Arena 图片编辑",
  "arena-text-to-video": "Arena 文生视频",
  "arena-image-to-video": "Arena 图生视频",
  "arena-video-edit": "Arena 视频编辑",
};

const MODALITY_LABELS: Record<string, string> = {
  all: "全部模态",
  image: "图像",
  video: "视频",
  audio: "音频",
  text: "文本 / 元数据",
  action: "具身 / Action",
  multimodal: "多模态",
  preference: "偏好数据",
  "3d": "3D",
};

const SOURCE_PLATFORM_CATEGORY_LABELS: Record<string, string> = {
  "video-platform": "视频平台",
  "streaming-and-studio": "流媒体与影视",
  "stock-media": "素材平台",
  ecommerce: "电商平台",
};

const SOURCE_PLATFORM_ACCESS_LABELS: Record<string, string> = {
  "documented-api": "公开文档 API",
  "partner-api": "合作方 API",
  "partner-portal": "合作方门户",
  "licensed-service": "授权服务",
  "not-cataloged": "尚未确认接口",
};

const DISCLOSURE_LABELS: Record<string, string> = {
  full: "完整披露",
  partial: "部分披露",
  "high-level": "仅高层策略",
  undisclosed: "未披露",
};

const MONITORING_LABELS: Record<string, string> = {
  critical: "核心监控",
  high: "重点监控",
  standard: "常规监控",
};

const MONITORING_MODE_LABELS: Record<string, string> = {
  "content-revision": "内容版本监控",
  availability: "可用性监控",
};

const STAGE_LABELS: Record<string, string> = {
  pretraining: "预训练",
  midtraining: "持续训练",
  "fine-tuning": "微调",
  preference: "偏好对齐",
  distillation: "蒸馏",
  "action-adaptation": "动作适配",
};

const SOURCE_TYPE_LABELS: Record<string, string> = {
  undisclosed: "未披露",
  "public-web": "公开网络",
  "public-dataset": "公开数据集",
  licensed: "授权数据",
  proprietary: "自有数据",
  synthetic: "合成数据",
  "human-feedback": "人类反馈",
  "robot-demonstration": "机器人示范",
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

const RELATION_ROLE_LABELS: Record<string, string> = {
  pretraining: "预训练",
  "fine-tuning": "微调",
  preference: "偏好对齐",
  evaluation: "评测",
  distillation: "蒸馏",
};

const DATA_AVAILABILITY_LABELS: Record<string, string> = {
  public: "公开数据",
  gated: "受限访问",
  "not-released": "尚未发布",
  undisclosed: "未披露",
};

const DATASET_LINEAGE_LABELS: Record<string, string> = {
  "source-component": "来源组成",
  "filtered-subset": "筛选子集",
  "annotation-derivative": "标注衍生",
  "benchmark-derivative": "评测衍生",
  "transformed-derivative": "转换衍生",
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

function taxonomyLabel(value: string, labels: Record<string, string>) {
  return labels[value] ?? value.replaceAll("-", " ");
}

function datasetAccessAction(dataset: DatasetCard) {
  const labels: Record<string, string> = {
    hosted: dataset.access.status === "gated" ? "登录并获取数据" : "下载 / 浏览数据文件",
    urls: "获取源 URL 与下载工具",
    metadata: "获取元数据与工具",
    request: "申请数据访问",
    none: "查看不可用说明",
  };
  return labels[dataset.access.type] ?? "查看数据访问入口";
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
      <p>试试缩短“{query || "当前条件"}”，或切换到全部场景和全部模态。</p>
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
  const namedDatasets = model.data.datasets.filter((item) => item.catalog_id);

  return (
    <article id={`model-${model.id}`} className={`result-card model-card ${expanded ? "is-expanded" : ""}`}>
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
            {scenarioLabels.slice(0, 2).map((item) => (
              <span className="tag tag-scenario" key={item}>{item}</span>
            ))}
            {model.modalities.slice(0, 4).map((item) => (
              <span className="tag" key={item}>{MODALITY_LABELS[item] ?? item}</span>
            ))}
            {model.ranking_positions.slice(0, 2).map((item) => (
              <span className="tag tag-ranking" key={`${item.ranking_id}-${item.rank}`}>
                {RANKING_LABELS[item.ranking_id] ?? item.ranking_id} #{item.rank}{item.component_count > 1 ? " · 组合" : ""}
              </span>
            ))}
            {model.monitoring && <span className="tag tag-monitor">{MONITORING_LABELS[model.monitoring.priority]}</span>}
          </div>
        </div>
        <div className="card-metrics">
          <div>
            <span className="metric-label">数据披露</span>
            <strong>{DISCLOSURE_LABELS[model.data.disclosure_level]}</strong>
          </div>
          <div>
            <span className="metric-label">目录关联</span>
            <strong>{model.data.datasets.length ? `${namedDatasets.length}/${model.data.datasets.length}` : "无"}</strong>
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
              {model.data.stages.map((stage, index) => (
                <div className="stage" key={`${model.id}-${index}-${stage.name}`}>
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
                    <span>{item.role} · {DATA_AVAILABILITY_LABELS[item.availability] ?? item.availability} · {item.scale ?? "规模未披露"}</span>
                    <p>{item.notes}</p>
                    {item.catalog_id && (
                      <button className="relation-link" onClick={() => onOpenDataset(item.catalog_id!)}>
                        打开数据卡 <span aria-hidden="true">→</span>
                      </button>
                    )}
                    {!item.catalog_id && (
                      <small className="reference-resolution">
                        {item.availability === "not-released"
                          ? "没有数据卡：发布方尚未发布该语料。"
                          : "没有数据卡：一手资料没有披露可识别的数据集。"}
                      </small>
                    )}
                  </div>
                ))}
              </div>
            ) : <p className="unknown-copy">官方没有公开任何可识别的数据集名称。</p>}
            {namedDatasets.length > 0 && (
              <p className="linked-note">其中 {namedDatasets.length} 个已与本目录数据卡建立关联。</p>
            )}
            {model.monitoring && (
              <p className="linked-note">模型更新：{MONITORING_MODE_LABELS[model.monitoring.mode ?? "content-revision"]} / {MONITORING_LABELS[model.monitoring.priority]}。监控源变化时进入每周复核队列。</p>
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
              {model.monitoring && <ExternalLink href={model.monitoring.source_url}>版本监控源</ExternalLink>}
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
  const datasetLineageCount = upstreamDatasets.length + downstreamDatasets.length;
  return (
    <article id={`dataset-${dataset.id}`} className={`result-card dataset-card ${expanded ? "is-expanded" : ""}`}>
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
            {scenarioLabels.slice(0, 2).map((item) => (
              <span className="tag tag-scenario" key={item}>{item}</span>
            ))}
            <span className="tag">{MODALITY_LABELS[dataset.modality] ?? dataset.modality}</span>
            {dataset.tasks.slice(0, 2).map((item) => <span className="tag" key={item}>{item}</span>)}
            {dataset.monitoring && <span className="tag tag-monitor">{MONITORING_LABELS[dataset.monitoring.priority]}</span>}
            {linkedModels.length > 0 && <span className="tag tag-relation">{linkedModels.length} 个模型关联</span>}
            {datasetLineageCount > 0 && <span className="tag tag-lineage">{datasetLineageCount} 条数据血缘</span>}
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
          <section className="access-panel">
            <p className="detail-label">数据获取入口</p>
            <ExternalLink href={dataset.access.url}>{datasetAccessAction(dataset)}</ExternalLink>
            <p>{dataset.access.notes}</p>
          </section>
          <section>
            <p className="detail-label">数据与标注</p>
            <dl className="fact-grid">
              <div><dt>标注来源</dt><dd>{dataset.annotations.source}</dd></div>
              <div><dt>标注类型</dt><dd>{dataset.annotations.types.join(" · ")}</dd></div>
              <div><dt>处理格式</dt><dd>{dataset.processing.recommended_format}</dd></div>
              <div><dt>账号要求</dt><dd>{dataset.access.requires_account ? "需要" : "不需要"}</dd></div>
              <div><dt>首次发布</dt><dd>{formatDate(dataset.released_at)}</dd></div>
              <div><dt>最近核验</dt><dd>{formatDate(dataset.last_verified)}</dd></div>
              {dataset.monitoring && (
                <div>
                  <dt>更新监控</dt>
                  <dd>{MONITORING_MODE_LABELS[dataset.monitoring.mode ?? "content-revision"]} / {MONITORING_LABELS[dataset.monitoring.priority]}</dd>
                </div>
              )}
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
          {(linkedModels.length > 0
            || upstreamDatasets.length > 0
            || downstreamDatasets.length > 0
            || dataset.evidence.used_by.length > 0) && (
            <section className="relation-panel">
              <p className="detail-label">模型关系与数据血缘</p>
              {linkedModels.length > 0 && (
                <div className="relation-list relation-group">
                  <span className="relation-group-label">关联模型</span>
                  {linkedModels.map((model) => (
                    <button className="relation-link" onClick={() => onOpenModel(model.id)} key={model.id}>
                      <span>{model.name}</span><small>{model.data.datasets.find((item) => item.catalog_id === dataset.id)?.role ?? "关联"}</small><b aria-hidden="true">→</b>
                    </button>
                  ))}
                </div>
              )}
              {upstreamDatasets.length > 0 && (
                <div className="relation-list relation-group">
                  <span className="relation-group-label">上游数据集</span>
                  {upstreamDatasets.map((source) => {
                    const lineage = dataset.derived_from?.find((item) => item.catalog_id === source.id);
                    return (
                      <button className="relation-link" onClick={() => onOpenDataset(source.id)} key={source.id}>
                        <span>{source.name}</span>
                        <small>{taxonomyLabel(lineage?.relationship ?? "", DATASET_LINEAGE_LABELS)}</small>
                        <b aria-hidden="true">↑</b>
                      </button>
                    );
                  })}
                </div>
              )}
              {downstreamDatasets.length > 0 && (
                <div className="relation-list relation-group">
                  <span className="relation-group-label">下游衍生数据集</span>
                  {downstreamDatasets.map((derived) => (
                    <button className="relation-link" onClick={() => onOpenDataset(derived.id)} key={derived.id}>
                      <span>{derived.name}</span>
                      <small>{taxonomyLabel(
                        derived.derived_from?.find((item) => item.catalog_id === dataset.id)?.relationship ?? "",
                        DATASET_LINEAGE_LABELS,
                      )}</small>
                      <b aria-hidden="true">↓</b>
                    </button>
                  ))}
                </div>
              )}
              {dataset.evidence.used_by.length > 0 && (
                <p className="editorial-relation">
                  上游资料提及：{dataset.evidence.used_by.join("、")}。目录内反向链接只由模型卡的 <code>catalog_id</code> 自动生成。
                </p>
              )}
            </section>
          )}
          <section className="unknown-panel">
            <p className="detail-label">已知限制</p>
            <ul>
              {dataset.quality.known_limitations.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </section>
          <footer className="detail-footer">
            <span>{dataset.access.notes}</span>
            <nav aria-label={`${dataset.name} 来源`}>
              <ExternalLink href={dataset.access.url}>{datasetAccessAction(dataset)}</ExternalLink>
              <ExternalLink href={dataset.evidence.homepage}>项目主页</ExternalLink>
              {dataset.release_date_source !== dataset.evidence.homepage && (
                <ExternalLink href={dataset.release_date_source}>发布日期证据</ExternalLink>
              )}
              {dataset.evidence.paper && dataset.evidence.paper !== dataset.release_date_source && (
                <ExternalLink href={dataset.evidence.paper}>论文</ExternalLink>
              )}
              {dataset.monitoring && <ExternalLink href={dataset.monitoring.source_url}>版本监控源</ExternalLink>}
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
          <h3 id="lineage-title">从上游数据，一路追到衍生集和模型。</h3>
          <p>模型关系来自模型卡的 <code>catalog_id</code>；数据血缘来自子数据集的 <code>derived_from</code>。两类边都保留原始证据边界。</p>
        </div>
        <dl>
          <div><dt>当前关系</dt><dd>{relationCount}</dd></div>
          <div><dt>关联模型</dt><dd>{modelCount}</dd></div>
          <div><dt>关联数据集</dt><dd>{datasetCount}</dd></div>
        </dl>
      </header>
      {modelRelations.length > 0 && (
        <section className="lineage-section">
          <div className="lineage-section-heading"><span>MODEL → DATASET</span><strong>模型使用了哪些数据</strong></div>
          <div className="lineage-grid">
            {modelRelations.map((relation) => (
              <article className="lineage-row" key={`${relation.model_id}-${relation.dataset_id}-${relation.role}`}>
                <button
                  className="lineage-entity lineage-model"
                  onClick={() => onOpenModel(relation.model_id)}
                  aria-label={`打开模型 ${relation.model.name}`}
                >
                  <span>M</span>
                  <strong>{relation.model.name}</strong>
                  <small>{relation.model.organization}</small>
                  {relation.model.monitoring && <small>{MONITORING_LABELS[relation.model.monitoring.priority]}</small>}
                </button>
                <div className="lineage-edge">
                  <strong>{taxonomyLabel(relation.role, RELATION_ROLE_LABELS)}</strong>
                  <span>{taxonomyLabel(relation.availability, DATA_AVAILABILITY_LABELS)}</span>
                  <small>{relation.scale ?? "规模未披露"}</small>
                </div>
                <button
                  className="lineage-entity lineage-dataset"
                  onClick={() => onOpenDataset(relation.dataset_id)}
                  aria-label={`打开数据集 ${relation.dataset.name}`}
                >
                  <span>D</span>
                  <strong>{relation.dataset.name}</strong>
                  <small>
                    {MODALITY_LABELS[relation.dataset.modality] ?? relation.dataset.modality} · {ACCESS_LABELS[relation.dataset.access.status] ?? relation.dataset.access.status}
                    {relation.dataset.monitoring ? ` · ${MONITORING_LABELS[relation.dataset.monitoring.priority]}` : ""}
                  </small>
                </button>
              </article>
            ))}
          </div>
        </section>
      )}
      {datasetRelations.length > 0 && (
        <section className="lineage-section">
          <div className="lineage-section-heading"><span>DATASET → DATASET</span><strong>上游数据如何形成衍生集</strong></div>
          <div className="lineage-grid">
            {datasetRelations.map((relation) => (
              <article className="lineage-row" key={`${relation.source_dataset_id}-${relation.derived_dataset_id}`}>
                <button
                  className="lineage-entity lineage-dataset"
                  onClick={() => onOpenDataset(relation.source_dataset_id)}
                  aria-label={`打开上游数据集 ${relation.sourceDataset.name}`}
                >
                  <span>D</span>
                  <strong>{relation.sourceDataset.name}</strong>
                  <small>上游 · {MODALITY_LABELS[relation.sourceDataset.modality] ?? relation.sourceDataset.modality}</small>
                </button>
                <div className="lineage-edge lineage-edge-dataset">
                  <strong>{taxonomyLabel(relation.relationship, DATASET_LINEAGE_LABELS)}</strong>
                  <span>{relation.contribution}</span>
                  <small>已核验派生关系</small>
                </div>
                <button
                  className="lineage-entity lineage-derived"
                  onClick={() => onOpenDataset(relation.derived_dataset_id)}
                  aria-label={`打开衍生数据集 ${relation.derivedDataset.name}`}
                >
                  <span>D′</span>
                  <strong>{relation.derivedDataset.name}</strong>
                  <small>
                    衍生 · {ACCESS_LABELS[relation.derivedDataset.access.status] ?? relation.derivedDataset.access.status}
                    {relation.derivedDataset.monitoring ? ` · ${MONITORING_LABELS[relation.derivedDataset.monitoring.priority]}` : ""}
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
          <h3 id="ranking-title">头部模型不是凭印象补录，而是跟着榜单持续复核。</h3>
          <p>每周同步 Artificial Analysis、Arena 与 AVGen-Bench 的生成媒体榜单。成员或名次变化进入复核队列，分数的小幅波动不单独提醒。</p>
        </div>
        <dl>
          <div><dt>榜单</dt><dd>{boards.length}</dd></div>
          <div><dt>监控席位</dt><dd>{monitored}</dd></div>
          <div><dt>席位映射</dt><dd>{cataloged}/{monitored}</dd></div>
          <div><dt>组件关系</dt><dd>{catalogedComponents}/{componentCount}</dd></div>
        </dl>
      </header>
      <div className="ranking-boards">
        {boards.map((board) => (
          <article className="ranking-board" key={board.id}>
            <header>
              <div><span>{board.provider.toUpperCase()}</span><h4>{board.label}</h4></div>
              <ExternalLink href={board.source_url}>榜单原页</ExternalLink>
            </header>
            <ol>
              {board.entries.map((entry) => (
                <li key={`${board.id}-${entry.rank}-${entry.model}`}>
                  <strong className="ranking-rank">{String(entry.rank).padStart(2, "0")}</strong>
                  <div>
                    <b>{entry.model}</b>
                    <span>{entry.creator} · {entry.released ? `${board.date_label} ${entry.released}` : "发布日期未列"}</span>
                    {entry.components.length > 1 && <small>组合管线: {entry.components.length} 个组件模型</small>}
                  </div>
                  <div className="ranking-score"><strong>{Number.isInteger(entry.score) ? entry.score : entry.score.toFixed(1)}</strong><span>{board.score_label}</span></div>
                  <span className={`ranking-access ${entry.open_weights ? "is-open" : ""}`}>
                    {entry.open_weights ? entry.license || "开放权重" : entry.license || "闭源 / 服务"}
                  </span>
                  <div className="ranking-model-links" aria-label={`${entry.model} 组件模型`}>
                    {entry.components.map((component) => {
                      const model = component.model_id ? modelById.get(component.model_id) : undefined;
                      return model ? (
                        <button
                          type="button"
                          title={`打开 ${model.name} 模型卡`}
                          onClick={() => onOpenModel(model.id)}
                          key={`${entry.rank}-${component.name}`}
                        >
                          <strong>{entry.components.length > 1 ? component.name : "模型卡"}</strong>
                          <small>{model.strategy_profile.linked_dataset_count}/{model.strategy_profile.data_reference_count} 数据卡</small>
                        </button>
                      ) : (
                        <small key={`${entry.rank}-${component.name}`}>{component.name}: 待建卡</small>
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
          <h3 id="source-platform-title">把网站来源和可下载数据集分开管理。</h3>
          <p>这些条目是候选内容来源，不是数据集下载入口，也不代表已经获得抓取、训练、商用或再分发许可。</p>
        </div>
        <dl>
          <div><dt>候选平台</dt><dd>{platforms.length}</dd></div>
          <div><dt>已登记接口</dt><dd>{interfaceCount}</dd></div>
          <div><dt>重点监控</dt><dd>{highPriorityCount}</dd></div>
        </dl>
      </header>
      <div className="source-platform-groups">
        {categories.map((category) => {
          const entries = platforms.filter((item) => item.category === category);
          if (entries.length === 0) return null;
          return (
            <article className="source-platform-group" key={category}>
              <header>
                <h4>{SOURCE_PLATFORM_CATEGORY_LABELS[category] ?? category}</h4>
                <span>{entries.length}</span>
              </header>
              <div className="source-platform-list">
                {entries.map((platform) => (
                  <section className="source-platform-item" key={platform.id}>
                    <div className="source-platform-name">
                      <ExternalLink href={platform.homepage}>{platform.name}</ExternalLink>
                      <span>{formatDate(platform.last_reviewed)} 复核</span>
                    </div>
                    <p>{platform.content_scope}</p>
                    <div className="source-platform-access">
                      <span>{SOURCE_PLATFORM_ACCESS_LABELS[platform.data_access.status] ?? platform.data_access.status}</span>
                      {platform.data_access.interface_url && platform.data_access.interface_name ? (
                        <ExternalLink href={platform.data_access.interface_url}>
                          {platform.data_access.interface_name}
                        </ExternalLink>
                      ) : (
                        <strong>仅登记官方站点</strong>
                      )}
                    </div>
                    <p className="source-platform-scope">可访问范围：{platform.data_access.scope}</p>
                    <p className="source-platform-requirements">准入条件：{platform.data_access.requirements}</p>
                    <div className="tag-row">
                      {platform.modalities.map((item) => (
                        <span className="tag" key={item}>{MODALITY_LABELS[item] ?? item}</span>
                      ))}
                      {platform.relevant_scenarios.map((item) => (
                        <span className="tag tag-scenario" key={item}>{scenarioLabels.get(item) ?? item}</span>
                      ))}
                    </div>
                    <footer>
                      <span>来源平台，不是数据集</span>
                      <strong>{platform.monitoring.priority === "high" ? "重点监控" : "标准监控"} · 权利需逐源审核</strong>
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
  const title = scenario
    ? `${scenario.short_label}：同场景数据策略对比`
    : "同场景数据策略对比";

  return (
    <section className="strategy-comparison" aria-labelledby="strategy-comparison-title">
      <header>
        <div>
          <p className="comparison-kicker">COMPARE / SOURCE-BOUND</p>
          <h3 id="strategy-comparison-title">{title}</h3>
        </div>
        <p>只比较一手资料明确披露的字段，不补全未知项，也不做综合评分。</p>
      </header>
      {!scenario && (
        <div className="comparison-prompt">
          <strong>先选择一个应用场景</strong>
          <span>生图、生视频、数字人、视频翻译与 Try-On 将在各自场景内比较。</span>
        </div>
      )}
      {scenario && models.length === 0 && (
        <div className="comparison-prompt">
          <strong>当前条件下没有可比较模型</strong>
          <span>可清空搜索词或切换模态后重试。</span>
        </div>
      )}
      {scenario && models.length > 0 && (
        <div className="comparison-table-scroll" tabIndex={0} aria-label={`${scenario.short_label}策略比较表，可横向滚动`}>
          <table className="comparison-table">
            <caption className="sr-only">{title}</caption>
            <thead>
              <tr>
                <th scope="col">模型</th>
                <th scope="col">披露程度</th>
                <th scope="col">训练阶段</th>
                <th scope="col">数据来源类型</th>
                <th scope="col">数据引用</th>
                <th scope="col">规模披露</th>
                <th scope="col">未知项</th>
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
                        {DISCLOSURE_LABELS[model.data.disclosure_level]}
                      </span>
                    </td>
                    <td>
                      <div className="comparison-terms">
                        {profile.stage_names.map((item, index) => (
                          <span key={`${index}-${item}`}>{taxonomyLabel(item, STAGE_LABELS)}</span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <div className="comparison-terms comparison-sources">
                        {profile.source_types.map((item) => (
                          <span data-undisclosed={item === "undisclosed" || undefined} key={item}>
                            {taxonomyLabel(item, SOURCE_TYPE_LABELS)}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="comparison-ratio">
                      {profile.data_reference_count ? (
                        <div className="comparison-dataset-cell">
                          <a href={`#strategy-datasets-${model.id}`}>
                            <strong>{profile.linked_dataset_count}/{profile.data_reference_count}</strong>
                            <small>查看完整引用</small>
                          </a>
                          <div className="comparison-dataset-links" aria-label={`${model.name} 对应数据集`}>
                            {model.data.datasets.slice(0, 2).map((reference) => {
                              const dataset = reference.catalog_id ? datasetById.get(reference.catalog_id) : undefined;
                              return dataset ? (
                                <button type="button" onClick={() => onOpenDataset(dataset.id)} key={`${model.id}-${reference.name}`}>
                                  {dataset.name} <span aria-hidden="true">→</span>
                                </button>
                              ) : (
                                <span title="尚无可打开的数据卡" key={`${model.id}-${reference.name}`}>{reference.name}</span>
                              );
                            })}
                            {model.data.datasets.length > 2 && (
                              <a href={`#strategy-datasets-${model.id}`}>+{model.data.datasets.length - 2} 条</a>
                            )}
                          </div>
                        </div>
                      ) : (
                        <><strong>无</strong><small>没有数据引用</small></>
                      )}
                    </td>
                    <td className="comparison-ratio">
                      <strong>{profile.scale_disclosed_stage_count}/{profile.stage_count}</strong>
                      <small>披露阶段 / 全部</small>
                    </td>
                    <td className="comparison-unknowns">
                      <strong>{profile.unknown_count}</strong>
                      <small>明确记录</small>
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
  const disclosed = disclosureScore(model.data.disclosure_level);
  const profile = model.strategy_profile;

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
            {model.monitoring && <span className="tag tag-monitor">{MONITORING_LABELS[model.monitoring.priority]}</span>}
          </div>
        </div>
        <div className="disclosure-meter" aria-label={`披露程度：${DISCLOSURE_LABELS[model.data.disclosure_level]}`}>
          {[1, 2, 3, 4].map((level) => <span className={level <= disclosed ? "is-on" : ""} key={level} />)}
        </div>
      </header>
      <p className="strategy-lead">{model.data.strategy_summary[0]}</p>
      <div className="pipeline" aria-label="训练阶段">
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
      <section className="strategy-datasets" id={`strategy-datasets-${model.id}`} aria-labelledby={`strategy-datasets-title-${model.id}`}>
        <header>
          <div>
            <p className="detail-label" id={`strategy-datasets-title-${model.id}`}>关联数据集与访问入口</p>
            <p>这里列出模型卡中每一条数据引用。已建数据卡的条目可继续查看详情或直接打开下载、申请入口。</p>
          </div>
          <strong>{profile.linked_dataset_count}/{profile.data_reference_count || 0}</strong>
        </header>
        {model.data.datasets.length > 0 ? (
          <div className="strategy-dataset-list">
            {model.data.datasets.map((reference) => {
              const dataset = reference.catalog_id ? datasetById.get(reference.catalog_id) : undefined;
              return (
                <article className="strategy-dataset-row" key={`${model.id}-${reference.name}`}>
                  <div className="strategy-dataset-name">
                    <strong>{dataset?.name ?? reference.name}</strong>
                    <div>
                      <span>{RELATION_ROLE_LABELS[reference.role] ?? reference.role}</span>
                      <span>{DATA_AVAILABILITY_LABELS[reference.availability] ?? reference.availability}</span>
                      <span>{reference.scale ?? "规模未披露"}</span>
                    </div>
                  </div>
                  <p>{reference.notes}</p>
                  {dataset ? (
                    <div className="strategy-dataset-actions">
                      <button type="button" className="relation-link" onClick={() => onOpenDataset(dataset.id)}>
                        查看数据卡 <span aria-hidden="true">→</span>
                      </button>
                      <ExternalLink href={dataset.access.url}>{datasetAccessAction(dataset)}</ExternalLink>
                    </div>
                  ) : (
                    <small className="reference-resolution">
                      {reference.availability === "not-released"
                        ? "发布方尚未公开该数据，暂无下载入口。"
                        : "一手资料未披露可识别的数据集，无法提供下载入口。"}
                    </small>
                  )}
                </article>
              );
            })}
          </div>
        ) : (
          <p className="unknown-copy">官方没有公开任何可识别的数据引用，因此暂无可展示的数据卡或下载入口。</p>
        )}
      </section>
      <footer>
        <span>{DISCLOSURE_LABELS[model.data.disclosure_level]} / {profile.linked_dataset_count}/{profile.data_reference_count || "无"} 数据卡关联 / {profile.unknown_count} 项未知</span>
        <ExternalLink href={model.evidence.technical_report ?? model.evidence.release}>查看一手证据</ExternalLink>
      </footer>
    </article>
  );
}

export function CatalogExplorer({ catalog }: { catalog: Catalog }) {
  const [mode, setMode] = useState<Mode>("models");
  const [query, setQuery] = useState("");
  const [modality, setModality] = useState("all");
  const [scenario, setScenario] = useState("all");
  const [expanded, setExpanded] = useState<string | null>("flux-3");

  const scenarioLabels = useMemo(
    () => new Map(catalog.scenarios.map((item) => [item.id, item.short_label])),
    [catalog.scenarios],
  );
  const modelById = useMemo(
    () => new Map(catalog.models.map((item) => [item.id, item])),
    [catalog.models],
  );
  const datasetById = useMemo(
    () => new Map(catalog.datasets.map((item) => [item.id, item])),
    [catalog.datasets],
  );
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
        model.monitoring ? MONITORING_LABELS[model.monitoring.priority] : "",
        model.monitoring ? MONITORING_MODE_LABELS[model.monitoring.mode ?? "content-revision"] : "",
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
        dataset.monitoring ? MONITORING_LABELS[dataset.monitoring.priority] : "",
        dataset.monitoring ? MONITORING_MODE_LABELS[dataset.monitoring.mode ?? "content-revision"] : "",
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
        relation.model.monitoring ? MONITORING_LABELS[relation.model.monitoring.priority] : "",
        relation.dataset.monitoring?.priority ?? "",
        relation.dataset.monitoring ? MONITORING_LABELS[relation.dataset.monitoring.priority] : "",
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
        DATASET_LINEAGE_LABELS[relation.relationship] ?? "",
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
        SOURCE_PLATFORM_CATEGORY_LABELS[platform.category] ?? "",
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
  const activeScenario = scenario === "all"
    ? null
    : catalog.scenarios.find((item) => item.id === scenario) ?? null;
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
  }

  function openRelation(targetMode: "models" | "datasets", id: string) {
    setMode(targetMode);
    setQuery("");
    setModality("all");
    setScenario("all");
    setExpanded(id);
    const prefix = targetMode === "models" ? "model" : "dataset";
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        document.getElementById(`${prefix}-${id}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
      });
    });
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
          <p className="kicker">生成式 AI 数据情报</p>
          <h1>追踪模型，<br />追到它的<span>数据源头。</span></h1>
          <p className="hero-description">
            不止告诉你“有哪些数据集”。这里持续拆解最新 AIGC 模型用了什么数据、怎样清洗与训练，以及官方仍未披露什么。
          </p>
          <div className="hero-actions">
            <button onClick={() => document.querySelector("#explorer")?.scrollIntoView({ behavior: "smooth" })}>
              打开目录
            </button>
          </div>
        </div>
        <aside className="hero-stats" aria-label="目录统计">
          <div className="stats-topline"><span>INDEX / 2026</span><span>CN / EN</span></div>
          <div className="stat-main"><strong>{catalog.models.length}</strong><span>最新模型<br />及数据策略</span></div>
          <div className="stat-grid">
            <div><strong>{catalog.datasets.length}</strong><span>结构化数据集</span></div>
            <div><strong>{openDatasets}</strong><span>公开可访问</span></div>
            <div><strong>{exactDatasetModels}</strong><span>披露具体数据</span></div>
            <div><strong>{catalog.relations.length + catalog.dataset_relations.length}</strong><span>模型与数据血缘</span></div>
          </div>
          <div className="stats-note">每条结论保留发布日期、核验时间和官方证据。未知不是空白，也是结论。</div>
        </aside>
      </section>

      <section className="signal-strip" aria-label="最新追踪信号">
        <span className="signal-label">LATEST SIGNAL</span>
        <span className="signal-date">{formatDate(catalog.models[0].released_at)}</span>
        <strong>{catalog.models[0].name}</strong>
        <p>{catalog.models[0].data.strategy_summary[0]}</p>
        <button onClick={() => openRelation("models", catalog.models[0].id)}>
          查看拆解 ↘
        </button>
      </section>

      <section className="explorer" id="explorer">
        <div className="explorer-heading">
          <div>
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
              <small>{totalForMode(item)}</small>
            </button>
          ))}
        </div>

        {mode !== "rankings" && <div className="scenario-rail" role="group" aria-label="应用场景筛选">
          <span className="scenario-caption">应用场景</span>
          <div className="scenario-options">
            <button
              className={scenario === "all" ? "is-active" : ""}
              onClick={() => { setScenario("all"); setExpanded(null); }}
              aria-pressed={scenario === "all"}
            >
              <span>全部场景</span>
              <small>{totalForMode(mode)}</small>
            </button>
            {catalog.scenarios.map((item) => (
              <button
                className={scenario === item.id ? "is-active" : ""}
                onClick={() => { setScenario(item.id); setExpanded(null); }}
                aria-pressed={scenario === item.id}
                title={item.description}
                key={item.id}
              >
                <span>{item.short_label}</span>
                <small>{scenarioCounts[item.id]}</small>
              </button>
            ))}
          </div>
        </div>}

        <div className="search-panel">
          <label className="search-box">
            <span aria-hidden="true">⌕</span>
            <span className="sr-only">搜索目录</span>
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={mode === "datasets"
                ? "搜索数据集、任务、标注类型…"
                : mode === "sources"
                  ? "搜索来源平台、类别、模态或应用场景…"
                : mode === "rankings"
                  ? "搜索榜单模型、机构、开放权重…"
                : mode === "lineage"
                  ? "搜索模型、上游数据、衍生集或关系类型…"
                  : "搜索模型、机构、数据集或训练操作…"}
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
          <div className="result-count">
            <strong>{visibleCount}</strong> 条结果
            {mode === "models" && <small>发布时间：新 → 旧</small>}
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
