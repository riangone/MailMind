---
name: code_executor
description: 编程任务执行器（需求分析、方案与代码输出）
description_ja: コーディングタスク実行（要件整理・方針・コード出力）
description_en: Coding task executor (analyze requirements and output code)
category: coding
auto_execute: true
chainable: true
keywords:
  - code
  - coding
  - executor
  - 编程
params:
  prompt:
    type: string
    required: true
    description: 编程需求或任务描述
  language:
    type: string
    required: false
    description: 目标语言（可选）
---

# 编程任务

## 任务
请完成以下编程需求：

```
{{prompt}}
```

## 要求
1. 明确需求理解与方案
2. 输出可执行的代码或伪代码
3. 如指定 `language`，使用目标语言实现
