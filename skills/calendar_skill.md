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

动作：`{{action}}`
{% if details %}
详情：`{{details}}`
{% endif %}

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要查看项目结构。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接处理日程**：根据 action 直接处理日历操作。
4. **只输出最终结果**：不输出中间思考过程。

## 输出要求
1. `create`：输出结构化事件信息（时间、地点、参与人、提醒等）
2. `list`：按时间顺序列出事件清单
3. `update`：给出变更摘要和更新后的信息
4. `suggest`：提供可行的替代时间建议
