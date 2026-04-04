---
name: ai_job
description: 通用 AI 任务执行（分析/生成/解释/改写等）
description_ja: 汎用 AI タスク実行（分析/生成/説明/書き換え）
description_en: General AI task execution (analyze/generate/explain/rewrite)
category: general
auto_execute: true
chainable: true
keywords:
  - ai_job
  - 分析
  - 生成
  - 改写
  - explain
params:
  prompt:
    type: string
    required: true
    description: 任务描述或输入内容
  lang:
    type: string
    required: false
    description: 输出语言（可选）
---

# 通用 AI 任务

## 任务
请完成以下任务：

```
{{prompt}}
```

## 要求
1. 直接输出结果
2. 如指定 `lang`，使用目标语言输出
