---
name: news_briefing
description: 生成统一格式的新闻简报
description_ja: 統一フォーマットのニュースブリーフィングを生成
description_en: Generate a unified-format news briefing
category: search
auto_execute: true
chainable: true
keywords:
  - 新闻
  - news
  - briefing
  - 简报
  - ニュース
params:
  query:
    type: string
    required: true
    description: 新闻主题或关键词
  num_results:
    type: integer
    required: false
    default: 5
    description: 结果数量（默认 5）
  lang:
    type: string
    required: false
    default: ""
    description: 输出语言（可选）
  timeframe:
    type: string
    required: false
    default: 最新
    description: 时间范围（如 24h, 7d；默认最新）
---

# 新闻简报

## 任务
围绕主题生成简洁、结构化的新闻简报。

主题：`{{query}}`
数量：`{{num_results}}`
时间范围：`{{timeframe}}`

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要读取项目代码。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接获取最新信息**：使用搜索工具获取最新新闻和资讯。
4. **只输出最终结果**：不输出中间步骤或工具调用过程，只输出最终简报。

## 输出要求
1. 先搜索最新信息，再生成简报
2. 输出格式为 Markdown
3. 结构建议：
   - 📰 标题与来源（1-2 句要点）
   - 📌 核心要点摘要
   - 🔗 相关背景或延伸（可选）
4. 如指定 `lang`，使用目标语言输出
5. 若无结果，说明原因并给出替代建议关键词
