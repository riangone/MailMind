---
name: github
description: GitHub 操作辅助（生成 issue/PR 说明等）
description_ja: GitHub 操作支援（Issue/PR 文面生成など）
description_en: GitHub helper (issue/PR drafts, summaries)
category: communication
auto_execute: true
chainable: true
keywords:
  - github
  - issue
  - pull request
  - PR
params:
  action:
    type: string
    required: true
    description: 动作（issue/PR/release/summary）
  content:
    type: string
    required: true
    description: 相关内容或变更说明
---

# GitHub 辅助

## 任务
根据 `action` 生成所需的 GitHub 文案或摘要。

## 要求
1. 输出清晰、可直接粘贴使用的文本
2. 重点突出变更与影响
