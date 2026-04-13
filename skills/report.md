---
name: report
description: 生成综合日报（天气 + 新闻 + 市场 + 系统状态）
description_ja: 総合日次レポートを生成（天気・ニュース・マーケット・システム）
description_en: Generate a comprehensive daily report (weather, news, market, system)
category: automation
auto_execute: true
chainable: true
keywords:
  - 日报
  - 报告
  - report
  - 日次レポート
  - 综合报告
  - 일보
  - daily report
  - 汇报
params:
  topics:
    type: string
    required: false
    default: 天气,新闻,股市
    description: 报告涵盖的主题，逗号分隔（如：天气,新闻,股市,系统状态）
  location:
    type: string
    required: false
    default: Tokyo
    description: 天气查询地点（默认 Tokyo）
  query:
    type: string
    required: false
    default: ""
    description: 新闻或搜索的附加关键词（可选）
  lang:
    type: string
    required: false
    default: ""
    description: 输出语言（可选）
---

# 综合日报

## 任务
生成一份包含以下主题的综合日报：`{{topics}}`

天气地点：`{{location}}`
附加关键词：`{{query}}`

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要读取项目代码。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **搜索最新信息**：对于每个主题，使用搜索工具获取最新数据。
4. **只输出最终结果**：不输出中间步骤或工具调用过程，只输出最终日报。

## 报告结构

根据 `topics` 参数，按需包含以下各节：

### 🌤 天气（若 topics 包含"天气"）
- 当前天气状况、气温、湿度
- 今明两天预报
- 简短生活提示（是否带伞等）

### 📰 新闻（若 topics 包含"新闻"）
- 今日热点新闻 3-5 条（标题 + 1 句要点）
- 附加关键词相关新闻（如指定）

### 📈 股市（若 topics 包含"股市"或"market"）
- 主要指数表现（日经、标普、沪深等）
- 热点板块和驱动因素（1-2 句）

### 🖥️ 系统状态（若 topics 包含"系统状态"或"system"）
- CPU、内存、磁盘使用率概况
- 是否有异常警告

### 📌 今日摘要
- 2-3 句综合今日重点

## 输出要求
1. 仅包含 topics 中指定的板块。
2. 输出 Markdown 格式，各节用 `---` 分隔。
3. 简洁为主，每节不超过 200 字。
4. 如指定 `lang`，使用目标语言输出。
