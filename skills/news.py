"""
News Skill — 新闻搜索与摘要

支持多种执行方式：
1. AI Skill 模式：通过 ai.skills 执行（优先，支持 NewsAPI/网页搜索）
2. 传统模式：直接调用 web_search + AI 整理（向后兼容）
"""

from skills import BaseSkill
from ai.skills import execute_ai_skill, fetch_news_via_search, format_news_result
from tasks.registry import pick_task_ai
from ai.providers import get_ai_provider
from core.config import SEARCH_RESULTS_COUNT, PROMPT_LANG


class NewsSkill(BaseSkill):
    name = "news"
    description = "新闻搜索与摘要"
    description_ja = "ニュース検索と要約"
    description_en = "News search and summarization"
    keywords = ["新闻", "新闻摘要", "news", "ニュース", "뉴스", "资讯"]

    def run(self, payload: dict, ai_caller=None) -> str:
        q = payload.get("query") or "最新的新闻"
        lang = payload.get("lang", PROMPT_LANG)
        
        # 1. 优先使用 AI Skill 模式（支持 NewsAPI/网页搜索）
        result = execute_ai_skill("news", {"query": q}, lang)
        if result:
            return result
        
        # 2. 回退到传统模式：web_search + AI 整理
        ai_name, backend = pick_task_ai(payload)
        ai = ai_caller or get_ai_provider(ai_name, backend)
        
        # 如果 AI 支持 native_web_search，直接让 AI 搜索
        if backend.get("native_web_search"):
            prompt = f"请搜索并总结关于以下主题的最新新闻：{q}。重要提示：必须在回复中包含每条新闻的原始链接（URL），不要删减链接信息。"
            return ai.call(prompt) or "⚠️ 新闻获取失败。"
        
        # 否则使用本地 web_search
        results = fetch_news_via_search(q, SEARCH_RESULTS_COUNT)
        if results:
            search_ctx = format_news_result(results, lang)
            prompt = f"以下是关于「{q}」的网络搜索结果，请将其整理为新闻摘要，按重要性排列，保留并完整显示每条的原始链接（URL）。\n\n{search_ctx}"
        else:
            prompt = f"请搜索并总结关于以下主题的最新新闻：{q}。重要提示：必须在回复中包含每条新闻的原始链接（URL），不要删减链接信息。"
        
        return ai.call(prompt) or "⚠️ 新闻获取失败。"


SKILL = NewsSkill()
