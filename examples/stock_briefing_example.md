# 股市简报任务示例

## 用户指令示例

**指令**：`每天8点和16点发送中国股市的简报`

## Copilot 应该如何理解

当 Copilot 收到这个指令时，应该生成如下的 JSON 响应：

```json
{
  "subject": "中国股市简报",
  "body": "将定时生成中国股市（A股/沪深）的简报，包含主要指数涨跌、热点板块、驱动因素等。",
  "schedule_cron": "0 8,16 * * *",
  "task_type": "stock",
  "task_payload": {
    "query": "中国股市 A股 沪深 主要指数",
    "lang": "zh",
    "timeframe": "最新"
  },
  "output": {
    "email": true,
    "archive": true,
    "archive_dir": "reports"
  }
}
```

## 字段说明

| 字段 | 值 | 说明 |
|------|-----|------|
| `subject` | "中国股市简报" | 简短描述性标题 |
| `body` | 说明文字 | 告知用户任务已创建 |
| `schedule_cron` | "0 8,16 * * *" | **关键**：使用 cron 表达式实现每天8点和16点两个时间点执行 |
| `task_type` | "stock" | **关键**：必须使用 `stock` 技能类型，而不是 "ai_job" 或其他 |
| `task_payload.query` | "中国股市 A股 沪深 主要指数" | 指定关注中国股市 |
| `task_payload.lang` | "zh" | 输出语言为中文 |
| `task_payload.timeframe` | "最新" | 获取最新行情 |
| `output` | {...} | 邮件发送+归档到 reports 目录 |

## Cron 表达式说明

- `0 8,16 * * *` = 每天 8:00 和 16:00 各执行一次
- `0 9 * * *` = 每天 9:00 执行一次
- `0 9 * * 1-5` = 工作日每天 9:00 执行
- `0 */2 * * *` = 每 2 小时执行一次

## 常见错误

### ❌ 错误示例 1：误解为技能任务

```json
{
  "task_type": "ai_job",
  "task_payload": {
    "prompt": "每天8点和16点发送中国股市的简报"
  }
}
```

**问题**：没有识别出这是定时任务，也没有使用 `stock` 技能。

### ❌ 错误示例 2：使用 schedule_every 而不是 cron

```json
{
  "schedule_every": "8h",
  "task_type": "stock"
}
```

**问题**：`schedule_every` 只能实现固定间隔，无法实现"8点和16点"这种特定时间点。

### ❌ 错误示例 3：没有指定 query

```json
{
  "task_type": "stock",
  "task_payload": {}
}
```

**问题**：没有指定市场，会使用默认的日本股市，而不是中国股市。

## 正确的任务执行流程

1. 用户发送邮件：`每天8点和16点发送中国股市的简报`
2. Copilot 解析指令，生成上述 JSON
3. 系统创建定时任务，保存到 SQLite
4. 每天 8:00 和 16:00，系统自动执行：
   - 调用 `stock` 技能
   - 使用 `task_payload.query` 搜索中国股市最新信息
   - 生成结构化简报
   - 通过邮件发送给用户
   - 归档到 `reports/` 目录

## 如何测试

发送邮件到你的管理邮箱：

```
每天8点和16点发送中国股市的简报，包括上证综指、深证成指、创业板指的主要涨跌情况。
```

你应该收到类似的 JSON 响应，并创建一个 cron 定时任务。
