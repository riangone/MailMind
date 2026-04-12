---
name: shell_exec
description: 执行 shell 命令并返回输出
description_ja: シェルコマンドを実行して出力を返す
description_en: Execute shell commands and return output
category: automation
keywords:
  - shell
  - bash
  - 执行命令
  - run command
  - コマンド実行
  - terminal
params:
  command:
    type: string
    required: true
    description: 要执行的 shell 命令
  cwd:
    type: string
    required: false
    description: 工作目录（可选）
---

# Shell 命令执行

## 任务
执行以下 shell 命令并返回输出：

```bash
{{command}}
```

{% if cwd %}
工作目录：`{{cwd}}`
{% endif %}

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件（除非任务明确要求）。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接执行命令**：使用 CLI 能力执行命令。
4. **只输出最终结果**：不输出中间思考过程，只输出命令的输出结果。

## 要求
1. 直接执行命令并返回完整的 stdout 和 stderr 输出
2. 返回退出码（exit code）
3. 如果命令执行失败，说明错误原因
4. **危险命令警告**：以下命令请谨慎执行或确认：
   - `rm -rf /`、`rm -rf /*` 等删除命令
   - `sudo` 提权命令
   - `mkfs`、`dd` 等磁盘格式化命令
   - 网络外连到可疑地址的命令
5. 如涉及敏感操作，请在结果中说明已执行的风险
