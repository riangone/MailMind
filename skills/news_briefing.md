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

## 要求
1. 先搜索最新信息，再生成简报
2. 输出格式为 Markdown
3. 每条新闻包含：标题、来源、要点（1-2 句）
4. 如指定 `lang`，使用目标语言输出
5. 若无结果，说明原因并给出替代建议关键词
