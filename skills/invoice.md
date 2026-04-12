---
name: invoice
description: 发票/账单解析或生成
description_ja: 請求書の解析または生成
description_en: Parse or generate invoices
category: automation
auto_execute: true
chainable: true
keywords:
  - invoice
  - 发票
  - 账单
  - 請求書
params:
  mode:
    type: string
    required: true
    description: 模式（parse 或 generate）
  text:
    type: string
    required: false
    description: 发票文本（parse 用）
  schema:
    type: string
    required: false
    description: 期望输出结构（parse 用，可选）
  fields:
    type: string
    required: false
    description: 生成发票所需字段（generate 用）
---

# 发票处理

## 任务
根据 `mode` 执行发票解析或生成。

模式：`{{mode}}`

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要查看项目结构。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接处理发票**：根据 mode 直接处理文本或生成内容。
4. **只输出最终结果**：不输出中间思考过程。

## 输出要求
1. `mode=parse`：从文本中提取金额、日期、商家、明细等信息，输出结构化结果
2. `mode=generate`：根据字段生成规范化发票文本
3. 若缺少必要信息，说明缺失项
4. 输出格式清晰、可读性强
