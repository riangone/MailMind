# 测试 Copilot 是否正确理解股市简报任务

## 测试方法

1. 重启守护进程以加载新配置：
   ```bash
   bash manage.sh restart
   ```

2. 发送测试邮件到管理邮箱，主题为：
   ```
   测试股市简报任务
   ```
   
   正文为：
   ```
   每天8点和16点发送中国股市的简报
   ```

3. 检查日志，查看 AI 的原始响应：
   ```bash
   bash manage.sh log
   ```

## 期望的正确响应

Copilot 应该直接输出类似以下的 JSON，**不包含任何对话或询问**：

```json
{
  "subject": "中国股市简报",
  "body": "已创建定时任务，每天 08:00 和 16:00 自动发送中国股市（A股/沪深）简报。",
  "schedule_cron": "0 8,16 * * *",
  "task_type": "stock",
  "task_payload": {
    "query": "中国股市 A股 沪深 主要指数 最新行情",
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

## 错误的响应示例

### ❌ 错误 1：对话式响应
```
我已收到您的请求。根据您的要求，理解如下：
✓ 已理解定时任务配置：每天 08:00 和 16:00 自动发送中国股市行情简报
请明确告诉我您需要执行哪个任务...
```

**问题**：Copilot 在对话而不是直接生成 JSON。

### ❌ 错误 2：使用 ai_job 而不是 stock
```json
{
  "task_type": "ai_job",
  "task_payload": {
    "prompt": "每天8点和16点发送中国股市的简报"
  }
}
```

**问题**：没有识别出这是股市简报任务，应该使用 `stock` 技能。

### ❌ 错误 3：使用 schedule_every 而不是 cron
```json
{
  "schedule_every": "8h",
  "task_type": "stock"
}
```

**问题**：`schedule_every: 8h` 是每8小时一次，而不是每天8点和16点。

## 调试技巧

如果 Copilot 仍然输出对话而不是 JSON，可以尝试：

1. **查看完整 prompt**：在日志中查找 `调用 AI` 相关的行，确认 prompt 是否包含了强制指令。

2. **手动测试 prompt**：
   ```bash
   # 提取完整 prompt 后，手动测试 Copilot
   copilot --yolo -p "你的prompt内容"
   ```

3. **检查 .env 配置**：
   ```bash
   # 确认使用的 AI 后端
   cat .env | grep AI=
   
   # 如果使用的是 copilot，确认 CLI 参数
   grep copilot core/config.py
   ```

4. **添加强制调试日志**：
   在 `email_daemon.py` 的 `call_ai` 函数中，打印完整的 prompt：
   ```python
   log.debug(f"完整 Prompt:\n{prompt}")
   ```

## 预期 cron 任务创建成功标志

在日志中应该看到类似：
```
[Scheduler] ✓ 添加定时任务: 中国股市简报
[Scheduler]   Cron: 0 8,16 * * *
[Scheduler]   Type: stock
```

然后你可以在任务列表中看到它：
```bash
# 查看 SQLite 中的任务
sqlite3 tasks.db "SELECT id, subject, type, cron_expr, status FROM tasks;"
```
