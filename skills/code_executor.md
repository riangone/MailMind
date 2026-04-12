---
name: code_executor
description: 编程任务执行器（需求分析、方案与代码输出）
description_ja: コーディングタスク実行（要件整理・方針・コード出力）
description_en: Coding task executor (analyze requirements and output code)
category: coding
auto_execute: true
chainable: true
keywords:
  - code
  - coding
  - executor
  - 编程
params:
  prompt:
    type: string
    required: true
    description: 编程需求或任务描述
  language:
    type: string
    required: false
    description: 目标语言（可选）
---

# 编程任务

## 任务
请完成以下编程需求：

```
{{prompt}}
```

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要查看项目结构。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接编写代码**：根据需求直接输出可执行代码。
4. **只输出最终结果**：不输出中间思考过程，只输出最终代码和必要说明。

## 要求
1. 明确需求理解与方案（简要说明，1-2 句）
2. 输出可执行的代码或伪代码
3. 如指定 `language`，使用目标语言实现
4. 代码应包含必要的注释和错误处理
