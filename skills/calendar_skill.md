---
name: calendar_skill
description: 日程创建/查询/调整建议
description_ja: カレンダー予定の作成/検索/調整提案
description_en: Create/query calendar events and suggest adjustments
category: automation
auto_execute: true
chainable: true
keywords:
  - calendar
  - 日程
  - 会议
  - カレンダー
params:
  action:
    type: string
    required: true
    description: 动作（create/list/update/suggest）
  details:
    type: string
    required: false
    description: 事件详情（时间、地点、参与人等）
---

# 日程管理

## 任务
根据 `action` 处理日程请求。

## 要求
1. `create`：输出结构化事件信息
2. `list`：按时间顺序列出
3. `update`：给出变更摘要
4. `suggest`：提供可行的替代时间
