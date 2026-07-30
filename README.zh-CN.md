# AIGCDataHub

[English](README.md) · [简体中文](README.zh-CN.md)

![AIGCDataHub — 从模型追到数据](site/public/og.png)

**从生成式 AI 模型，一路追到它的数据源头。** AIGCDataHub 是一个持续维护、
证据优先的多模态模型与数据目录，记录训练阶段、数据策略、访问条件、许可边界、
模型—数据集关系以及官方仍未披露的信息。

[![目录校验](https://img.shields.io/github/actions/workflow/status/TobinZuo/AIGCDataHub/validate.yml?branch=master&label=%E7%9B%AE%E5%BD%95%E6%A0%A1%E9%AA%8C)](https://github.com/TobinZuo/AIGCDataHub/actions/workflows/validate.yml)
[![许可证](https://img.shields.io/github/license/TobinZuo/AIGCDataHub)](LICENSE)
[![Stars](https://img.shields.io/github/stars/TobinZuo/AIGCDataHub?style=flat&label=stars)](https://github.com/TobinZuo/AIGCDataHub/stargazers)

**[打开在线目录](https://tobinzuo.github.io/AIGCDataHub/)** ·
**[查看最近更新](https://tobinzuo.github.io/AIGCDataHub/changelog/)** ·
**[查找可下载数据集](DATASET_ACCESS_INDEX.md)** ·
**[查看模型—数据关系](MODEL_DATASET_INDEX.md)**

<!-- BEGIN PROJECT METRICS -->
| 模型 | 数据集 | 模型与数据关系 | 数据集衍生关系 | 公开可访问 | 最新核验 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 93 | 122 | 135 | 29 | 53 | 2026-07-30 |
<!-- END PROJECT METRICS -->

> [!NOTE]
> 这不是另一个 Awesome List。每张卡都保留发布日期和核验日期，区分训练、
> 微调、偏好、评估、继承和运行时数据；官方没有披露的信息会明确写成
> “未披露”，不会根据模型能力反推训练数据。

## 它解决什么问题

| 你想知道 | AIGCDataHub 提供 |
|---|---|
| 模型究竟点名了哪些数据？ | 有一手来源支持的训练、微调、偏好、评估和继承数据引用。 |
| 数据能否下载或申请？ | 直接下载、浏览、申请、API、未发布或不可用状态。 |
| 数据经过了什么处理？ | 官方披露的过滤、去重、重标注、合成和偏好优化方法。 |
| 哪些信息仍然未知？ | 未披露的来源、权利、配比、规模和训练阶段。 |
| 最近发生了什么变化？ | 每日一手来源监控、人工核验记录和可追溯 Git 历史。 |

## 推荐入口

- [数据集下载与访问索引](DATASET_ACCESS_INDEX.md)：每张数据卡的下载、浏览、
  申请或不可用说明。
- [模型—数据集关系索引](MODEL_DATASET_INDEX.md)：训练、微调、偏好、评估和
  继承数据的双向关系。
- [模型卡](models/)与[数据卡](catalog/)：生成页面和所有索引的 YAML 事实源。
- [来源平台索引](SOURCE_PLATFORM_INDEX.md)：区分网站/API/合作接口与真正可下载
  的数据集。
- [更新记录](updates/)：每次接受、更新、证据不足或超出范围的候选及其一手来源。

## 60 秒使用数据

站点数据会生成一个受版本控制的 JSON 快照。下面的命令可直接查询 ID-V2V
模型及其数据引用：

```bash
curl -sL https://raw.githubusercontent.com/TobinZuo/AIGCDataHub/master/site/app/catalog-data.json \
  | jq '.models[] | select(.id == "id-v2v") | {name, released_at, access, datasets: .data.datasets}'
```

用于可复现实验时，请固定具体 commit 或 Release，不要直接依赖持续变化的
`master`。

## 覆盖范围

- 生图、生视频、图像/视频编辑；
- 数字人、口型同步、视频翻译与配音；
- 虚拟试衣、电商条件生成；
- 音视频联合生成、3D 和统一多模态；
- 数据获取、过滤、去重、重标注、合成、偏好优化、许可、隐私和来源治理。

纯文本大语言模型语料不在当前范围内。

## 参与贡献

小而可核验的贡献比大批未经审阅的链接更有价值。你可以：

- 提交新的模型或数据集一手来源；
- 修正访问状态、许可、规模或训练阶段；
- 补齐模型与数据集关系；
- 报告失效链接或过期信息；
- 改善中英文说明、查询示例和数据导出。

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，并使用模型或数据集 Issue 表单。

如果这个项目帮你节省了检索和核验时间，可以点一个 Star 作为支持；如果希望
收到版本通知，请使用 GitHub 的 Watch / Releases 订阅。

## 许可边界

仓库代码和原创文档使用 Apache-2.0。各数据集保留自己的条款；“公开可下载”
不等于其底层媒体可以用于训练、商业用途或再分发。本项目是工程参考，不构成
法律意见。
