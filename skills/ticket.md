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

## 要求
1. `create`：生成清晰的问题描述与复现步骤
2. `list`：按时间倒序列出关键字段
3. `update`：追加更新信息
4. `close`：输出关闭说明
