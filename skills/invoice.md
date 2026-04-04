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

## 要求
1. `mode=parse`：从 `text` 中提取金额、日期、商家、明细等
2. `mode=generate`：根据 `fields` 生成规范发票文本
3. 若缺少必要信息，说明缺失项
