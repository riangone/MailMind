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

动作：`{{action}}`

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要查看项目结构。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接生成文案**：使用 CLI 能力生成内容。
4. **只输出最终结果**：不输出中间思考过程。

## 输出要求
1. 输出清晰、可直接粘贴使用的文本
2. 重点突出变更与影响
3. 格式规范，包含必要的 Markdown 元素（如适用）
