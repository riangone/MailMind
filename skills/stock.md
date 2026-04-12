---
name: stock
description: 生成结构化的股票/股市/股市简报（默认日本市场）
description_ja: 株式市場の構造化ブリーフィング（既定は日本市場）
description_en: Produce a structured stock/market briefing (default: Japan)
category: search
auto_execute: true
chainable: true
keywords:
  - 股票
  - 股市
  - 股市简报
  - 股市简报
  - stock
  - market
  - 日本株
  - 中国股市
  - 中国股票
  - A股
  - 沪深
params:
  query:
    type: string
    required: false
    default: 股市行情 主要指数 最新
    description: 检索主题或市场关键词
  lang:
    type: string
    required: false
    default: ""
    description: 输出语言（可选）
  timeframe:
    type: string
    required: false
    default: 今日
    description: 时间范围（如 今日, 24h, 7d）
---

# 股市简报

## 任务
针对指定市场生成简洁、结构化的股市简报。

主题：`{{query}}`
时间范围：`{{timeframe}}`

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要读取项目代码。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接获取最新市场信息**：以公开来源为主，优先使用最新数据。
4. **只输出最终结果**：不输出中间步骤或工具调用过程，只输出最终简报。

## 输出要求
1. 先检索最新信息，再生成简报。
2. 输出 Markdown 格式。
3. 至少包含以下部分：
   - 市场概况（主要指数：如日经225、TOPIX；上涨/下跌幅度）
   - 热点板块或主题
   - 主要驱动因素（宏观/政策/公司事件）
   - 简短的风险提示或展望（1-2 句）
4. 如指定 `lang`，使用目标语言输出。
5. 若无法获取可靠数据，说明原因并给出替代检索关键词。
