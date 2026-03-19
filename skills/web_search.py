"""
Web Search Skill — 网页搜索

支持多种执行方式：
1. AI Skill 模式：通过 ai.skills 执行（优先，支持 MCP/本地搜索）
2. 传统模式：直接调用 web_search（向后兼容）
"""

from skills import BaseSkill
from ai.skills import execute_ai_skill, call_mcp_tool_wrapper
from utils.search import web_search, format_search_results
from core.config import WEB_SEARCH_ENGINE, SEARCH_RESULTS_COUNT, PROMPT_LANG


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = "网页搜索"
    description_ja = "ウェブ検索"
    description_en = "Web search"
    keywords = ["搜索", "检索", "search", "検索", "검색", "查找"]

    def run(self, payload: dict, ai_caller=None) -> str:
        q = payload.get("query") or ""
        if not q:
            return "⚠️ 请在 task_payload 中提供 query 字段。"
        
        count = payload.get("count", SEARCH_RESULTS_COUNT)
        engine = payload.get("engine", WEB_SEARCH_ENGINE)
        lang = payload.get("lang", PROMPT_LANG)
        
        # 1. 尝试 MCP 搜索工具（如果配置了）
        mcp_result = call_mcp_tool_wrapper("search", "search", {"query": q})
        if mcp_result and not mcp_result.startswith("⚠️"):
            return mcp_result
        
        # 2. 使用本地 web_search
        results = web_search(q, count, engine)
        return format_search_results(results) if results else "没有找到结果。"


SKILL = WebSearchSkill()
