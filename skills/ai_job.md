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

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要查看项目结构。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接执行任务**：根据任务要求搜索/分析/处理信息。
4. **只输出最终结果**：不输出中间步骤或工具调用过程。

## 要求
1. 直接输出结果
2. 如指定 `lang`，使用目标语言输出
