---
name: web_search
description: 网页搜索并整理结构化摘要
description_ja: ウェブ検索して構造化サマリーを生成
description_en: Search the web and produce a structured summary
category: search
auto_execute: true
chainable: true
keywords:
  - 搜索
  - 网页搜索
  - web search
  - search
  - 検索
  - ウェブ検索
  - 검색
  - 查询
  - 最新
params:
  query:
    type: string
    required: true
    description: 搜索关键词或问题
  num_results:
    type: integer
    required: false
    default: 5
    description: 参考结果数量（默认 5）
  lang:
    type: string
    required: false
    default: ""
    description: 输出语言（可选）
---

# 网页搜索

## 任务
针对以下查询，搜索网页并整理出结构化摘要。

查询：`{{query}}`
参考结果数：`{{num_results}}`

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要读取项目代码。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接搜索互联网**：使用搜索工具获取最新信息。
4. **只输出最终结果**：不输出中间步骤或工具调用过程，只输出最终摘要。

## 输出要求
1. 先执行搜索，再整理摘要。
2. 输出 Markdown 格式。
3. 结构建议：
   - 🔍 搜索摘要（2-3 句核心结论）
   - 📌 关键要点（3-5 条）
   - 🔗 主要来源（列出域名或标题）
4. 如指定 `lang`，使用目标语言输出。
5. 若搜索结果不足，说明原因并建议替代关键词。
