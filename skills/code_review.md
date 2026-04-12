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

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要查看项目结构。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接审查代码**：根据提供的代码直接进行分析。
4. **只输出最终结果**：不输出中间思考过程，只输出审查结果。

## 输出要求
1. 指出潜在 Bug、边界问题与安全隐患（按严重程度排序）
2. 提出可执行的改进建议（附带代码示例）
3. 如指定 `language`，针对该语言给出更具体建议
4. 输出格式清晰，使用 Markdown 的代码块和引用
