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

## 要求
1. 保留关键信息，去除冗余细节
2. 以要点形式输出
3. 如指定 `lang`，使用目标语言输出
4. 如指定 `max_length`，尽量控制在该长度以内
