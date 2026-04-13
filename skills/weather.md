---
name: weather
description: 获取指定城市/地区的天气预报
description_ja: 指定した都市・地域の天気予報を取得
description_en: Fetch weather forecast for a specified city or region
category: search
auto_execute: true
chainable: true
keywords:
  - 天气
  - 天气预报
  - weather
  - forecast
  - 気象
  - 天気
  - 気温
  - 날씨
params:
  location:
    type: string
    required: false
    default: Tokyo
    description: 城市或地区名称（默认：Tokyo）
  query:
    type: string
    required: false
    default: ""
    description: 附加查询条件（可选，如"未来7天"、"降雨概率"）
  lang:
    type: string
    required: false
    default: ""
    description: 输出语言（可选）
---

# 天气预报

## 任务
查询并整理 `{{location}}` 的最新天气信息。{{query}}

## 重要约束
1. **禁止探索文件系统**：不要列出目录、不要搜索文件、不要读取项目代码。
2. **禁止创建/修改任务**：不要安排定时任务、不要修改 scheduler 或任务配置。
3. **直接搜索获取天气数据**：使用搜索工具查询最新天气信息。
4. **只输出最终结果**：不输出中间步骤或工具调用过程，只输出最终天气报告。

## 输出要求
1. 先搜索最新天气信息，再生成报告。
2. 输出 Markdown 格式。
3. 至少包含以下部分：
   - 🌤 当前天气（气温、天气状况、湿度、风速）
   - 📅 未来 3 天预报（每天最高/最低气温、天气状况）
   - 💡 简短生活建议（如是否需要带伞、防晒等）
4. 如指定 `lang`，使用目标语言输出。
5. 若无法获取数据，说明原因并提示用户配置 `WEATHER_API_KEY`。
