"""
Weather Skill — 天气查询

支持多种执行方式：
1. AI Skill 模式：通过 ai.skills 执行（优先）
2. 传统模式：直接调用 fetch_weather_data + AI 整理（向后兼容）
"""

from skills import BaseSkill
from ai.skills import execute_ai_skill, fetch_weather_via_api, format_weather_result
from tasks.registry import pick_task_ai
from ai.providers import get_ai_provider
from core.config import WEATHER_DEFAULT_LOCATION, PROMPT_LANG


class WeatherSkill(BaseSkill):
    name = "weather"
    description = "天气查询与播报"
    description_ja = "天気情報の取得と配信"
    description_en = "Weather lookup and broadcast"
    keywords = ["天气", "weather", "天気", "날씨", "气温", "预报"]

    def run(self, payload: dict, ai_caller=None) -> str:
        loc = payload.get("location") or WEATHER_DEFAULT_LOCATION
        lang = payload.get("lang", PROMPT_LANG)
        
        # 1. 优先使用 AI Skill 模式（支持 MCP/WeatherAPI）
        result = execute_ai_skill("weather", {"location": loc}, lang)
        if result:
            return result
        
        # 2. 回退到传统模式：直接调用 API + AI 整理
        weather_data = fetch_weather_via_api(loc)
        ai_name, backend = pick_task_ai(payload)
        ai = ai_caller or get_ai_provider(ai_name, backend)
        
        if weather_data:
            prompt = f"以下是 {loc} 的实时天气数据，请用自然语言整理成简洁的天气播报：\n\n{format_weather_result(weather_data, lang)}"
        else:
            prompt = f"请搜索并告诉我现在 {loc} 的天气情况，包括温度和天气现象。"
        
        return ai.call(prompt) or "⚠️ 天气信息获取失败。"


SKILL = WeatherSkill()
