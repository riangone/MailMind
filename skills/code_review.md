---
name: code_review
description: 对代码进行审查，指出潜在问题并给出建议
description_ja: コードレビュー（潜在的な問題の指摘と提案）
description_en: Review code and point out potential issues with suggestions
category: coding
auto_execute: true
chainable: true
keywords:
  - code_review
  - review
  - 代码审查
  - レビュー
params:
  code:
    type: string
    required: true
    description: 需要审查的代码
  language:
    type: string
    required: false
    description: 编程语言（可选）
---

# 代码审查

## 任务
请审查以下代码：

```
{{code}}
```

## 要求
1. 指出潜在 Bug、边界问题与安全隐患
2. 提出可执行的改进建议
3. 如指定 `language`，针对该语言给出更具体建议
