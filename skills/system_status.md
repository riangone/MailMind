---
name: system_status
description: 服务器系统状态监控（CPU/内存/磁盘/网络/关键服务）
description_ja: サーバーのシステム状態モニタリング（CPU/メモリ/ディスク/ネットワーク/主要サービス）
description_en: Server system status monitoring (CPU/Memory/Disk/Network/Key services)
category: automation
auto_execute: true
chainable: false
keywords:
  - 系统状态
  - 系统监控
  - 服务器状态
  - system status
  - server status
  - CPU
  - 内存
  - 磁盘
  - システム状態
  - 서버 상태
params:
  query:
    type: string
    required: false
    default: ""
    description: 自定义监控内容（可选，留空则输出完整状态）
  lang:
    type: string
    required: false
    default: ""
    description: 输出语言（可选）
---

# 系统状态报告

## 任务
获取当前服务器运行状态，生成简洁、结构化的状态报告。

{{query}}

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要读取项目代码。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接执行系统命令获取信息**：使用 CLI 自带的工具能力执行命令。
4. **只输出最终结果**：不输出中间步骤或工具调用过程，只输出最终状态报告。

## 允许执行的系统命令

你可以安全地执行以下命令获取系统信息：

### CPU 信息
```bash
# CPU 使用率和负载
top -bn1 | head -20
# 或
uptime
```

### 内存信息
```bash
# 内存使用情况
free -h
```

### 磁盘信息
```bash
# 磁盘使用情况
df -h
# 磁盘 IO（可选）
iostat -x 1 1 2>/dev/null || echo "iostat 不可用"
```

### 网络信息
```bash
# 网络接口状态
ip addr show
# 网络连通性测试
ping -c 3 -W 2 8.8.8.8 2>/dev/null || echo "ping 不可用或网络不通"
```

### 运行服务/进程
```bash
# 系统运行时间
uptime
# 进程数
ps aux | wc -l
# 关键服务状态（如可用）
systemctl is-active sshd 2>/dev/null || echo "sshd 状态未知"
```

### 系统负载
```bash
# 1/5/15 分钟平均负载
cat /proc/loadavg
```

## 输出要求

1. 依次执行上述命令获取信息，然后生成报告。
2. 输出 Markdown 格式。
3. 至少包含以下部分：

### 📊 系统概览
- 主机名、操作系统
- 运行时间（uptime）
- 系统负载（1/5/15 分钟平均值）

### 🖥️ CPU 状态
- CPU 使用率概况
- 负载情况

### 💾 内存状态
- 总内存、已用、可用、缓存
- 使用率百分比

### 💿 磁盘状态
- 各分区使用率（挂载点、总量、已用、可用、使用率%）
- 标记使用率超过 80% 的分区为 ⚠️

### 🌐 网络状态
- 网络接口 IP 地址
- 外网连通性（ping 结果）

### 🔧 关键服务
- SSH 服务状态
- 其他可检测的关键服务

### 📈 总结与建议
- 当前系统健康状态总结
- 如有异常或资源紧张，给出简要建议（1-2 句）

4. 如指定 `lang`，使用目标语言输出。
5. 如某些命令不可用，跳过该项并标注"不可用"。
