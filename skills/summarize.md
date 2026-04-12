---
name: summarize
description: 对文本内容进行摘要精简，提取关键要点
description_ja: テキスト内容を要約し、重要なポイントを抽出
description_en: Summarize text and extract key points
category: communication
auto_execute: true
chainable: true
keywords:
  - 摘要
  - summarize
  - summary
  - 要約
  - 요약
params:
  text:
    type: string
    required: true
    description: 要摘要的文本
  lang:
    type: string
    required: false
    description: 摘要语言（可选）
  max_length:
    type: integer
    required: false
    description: 最大字数（可选）
---

# 文本摘要

## 任务
请对以下内容进行摘要，输出简洁要点：

```
{{text}}
```

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要查看项目结构。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接摘要**：根据提供的文本直接生成摘要。
4. **只输出最终结果**：不输出中间思考过程，只输出摘要结果。

## 输出要求
1. 保留关键信息，去除冗余细节
2. 以要点形式输出（推荐 3-7 个要点）
3. 如指定 `lang`，使用目标语言输出
4. 如指定 `max_length`，尽量控制在该长度以内
