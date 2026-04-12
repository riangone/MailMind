---
name: ticket
description: 工单创建/查询/更新
description_ja: チケットの作成/検索/更新
description_en: Create/query/update support tickets
category: automation
auto_execute: true
chainable: true
keywords:
  - ticket
  - 工单
  - issue
  - チケット
params:
  action:
    type: string
    required: true
    description: 动作（create/list/update/close）
  title:
    type: string
    required: false
    description: 工单标题（create）
  body:
    type: string
    required: false
    description: 工单内容（create/update）
  ticket_id:
    type: string
    required: false
    description: 工单 ID（update/close）
---

# 工单管理

## 任务
根据 `action` 处理工单请求。

动作：`{{action}}`
{% if title %}标题：`{{title}}`{% endif %}
{% if body %}内容：`{{body}}`{% endif %}
{% if ticket_id %}工单 ID：`{{ticket_id}}`{% endif %}

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要查看项目结构。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接处理工单**：根据 action 直接处理工单操作。
4. **只输出最终结果**：不输出中间思考过程。

## 输出要求
1. `create`：生成清晰的问题描述与复现步骤（标题、环境、期望行为、实际行为）
2. `list`：按时间倒序列出关键字段（ID、标题、状态、优先级、创建时间）
3. `update`：追加更新信息，给出变更摘要
4. `close`：输出关闭说明（原因、解决方式）
