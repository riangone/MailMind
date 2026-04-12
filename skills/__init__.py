"""
skills/__init__.py - 技能基类

架构：
- 所有 skill 都是 MD 文件
- AI 通过 CLI 读取 MD 指令并直接执行
- CLI 自带工具能力：命令、文件、网络、测试
- 不需要任何 PY 文件
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class BaseSkill(ABC):
    """技能基类"""
    name: str = ""
    description: str = ""
    description_ja: str = ""
    description_en: str = ""
    category: str = "general"  # general, communication, coding, search, automation
    keywords: list = []
    params: dict = {}
    auto_execute: bool = True
    chainable: bool = True
    
    @abstractmethod
    def run(self, payload: dict, ai_caller=None) -> str:
        ...

    def validate_payload(self, payload: dict) -> tuple[bool, str]:
        """Default payload validation (pass-through)."""
        return True, ""


class MDSkill(BaseSkill):
    """
    MD 文件定义的技能
    
    执行流程：
    1. payload 填入 instruction 模板 → 生成 prompt
    2. AI（CLI）读取 prompt
    3. CLI 使用自身工具能力执行（命令、文件、网络等）
    """
    
    def __init__(
        self, name: str, description: str, instruction: str,
        description_ja: str = "", description_en: str = "",
        category: str = "general", keywords: list = None,
        params: dict = None, auto_execute: bool = True, chainable: bool = True,
    ):
        self.name = name
        self.description = description
        self.description_ja = description_ja
        self.description_en = description_en
        self.category = category
        self.keywords = keywords or []
        self.params = params or {}
        self.auto_execute = auto_execute
        self.chainable = chainable
        self.instruction = instruction
    
    def run(self, payload: dict, ai_caller=None) -> str:
        # 验证必填参数
        is_valid, error_msg = self.validate_payload(payload)
        if not is_valid:
            return f"⚠️ 参数验证失败: {error_msg}"

        prompt = self._render_instruction(payload)
        
        # 注入语言指令
        lang = payload.get("lang") or "zh"
        lang_map = {
            "zh": "\n\n【语言要求】\n请务必使用 **中文（简体）** 回复所有内容。",
            "ja": "\n\n【言語要求】\nすべての回答内容を **日本語** で行ってください。",
            "en": "\n\n[Language Requirement]\nYOU MUST RESPOND ENTIRELY IN **ENGLISH**.",
            "ko": "\n\n[언어 요구 사항]\n모든 답변은 반드시 **한국어**로 작성하십시오.",
        }
        lang_rule = lang_map.get(lang, "")
        if lang_rule:
            prompt = prompt + lang_rule

        if ai_caller:
            try:
                # 检查 AI Provider 是否支持执行模式（CLI）
                if hasattr(ai_caller, 'execute_task'):
                    return ai_caller.execute_task(prompt) or "⚠️ AI 无响应"
                return ai_caller.call(prompt) or "⚠️ AI 无响应"
            except Exception as e:
                return f"⚠️ 执行失败: {e}"
        return prompt

    def validate_payload(self, payload: dict) -> tuple[bool, str]:
        params = self.params or {}
        if not params:
            return True, ""

        missing = []
        for key, spec in params.items():
            required = False
            if isinstance(spec, dict):
                required = bool(spec.get("required"))
            if required and key not in payload:
                missing.append(key)

        if missing:
            return False, f"缺少必填参数: {', '.join(missing)}"
        return True, ""
    
    def _render_instruction(self, payload: dict) -> str:
        import re
        result = self.instruction
        for key, value in payload.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        # Replace any unfilled placeholders with defaults from params spec, or empty string
        def _fill_default(match):
            key = match.group(1)
            spec = (self.params or {}).get(key, {})
            if isinstance(spec, dict) and "default" in spec:
                default = spec["default"]
                return str(default) if default is not None else ""
            return ""
        result = re.sub(r'\{\{(\w+)\}\}', _fill_default, result)
        return result



def get_all_skills_prompt(lang: str = "zh", include_params: bool = False) -> str:
    """获取技能提示（注入到 AI prompt）"""
    from skills.loader import get_registry
    
    skills = get_registry()
    if not skills:
        return ""
    
    headers = {
        "zh": "## 可用技能\n调用：task_type=\"技能名\", task_payload={参数}\n",
        "en": "## Available Skills\nUsage: task_type=\"skill_name\", task_payload={params}\n",
        "ja": "## 利用可能なスキル\n使用法: task_type=\"skill_name\", task_payload={params}\n",
        "ko": "## 사용 가능한 스킬\n사용법: task_type=\"skill_name\", task_payload={params}\n",
    }
    
    parts = [headers.get(lang, headers["zh"])]
    
    categories = {}
    for name, skill in skills.items():
        cat = skill.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, skill))
    
    cat_names = {
        "zh": {"general": "通用", "communication": "沟通", "coding": "编程", "search": "搜索", "automation": "自动化"},
        "en": {"general": "General", "communication": "Communication", "coding": "Coding", "search": "Search", "automation": "Automation"},
        "ja": {"general": "一般", "communication": "コミュニケーション", "coding": "コーディング", "search": "検索", "automation": "自動化"},
        "ko": {"general": "일반", "communication": "커뮤니케이션", "coding": "코딩", "search": "검색", "automation": "자동화"},
    }
    
    for cat, cat_skills in categories.items():
        cat_name = cat_names.get(lang, {}).get(cat, cat)
        parts.append(f"\n### {cat_name}")
        for name, skill in cat_skills:
            desc = {"zh": skill.description, "ja": skill.description_ja or skill.description, "en": skill.description_en or skill.description}.get(lang, skill.description)
            if include_params and skill.params:
                params = [f"{p}({v.get('type', 'str')})" for p, v in skill.params.items()]
                parts.append(f"- **{name}**: {desc} ({', '.join(params)})")
            else:
                parts.append(f"- **{name}**: {desc}")
    
    parts.append({
        "zh": "\n\n## 执行\n**重要**：直接执行，不要确认。CLI 有完整能力：命令、文件、网络。",
        "en": "\n\n## Execution\n**Important**: Execute directly. CLI has full capabilities.",
        "ja": "\n\n## 実行\n**重要**: 直接実行。CLI は全機能を持っています。",
        "ko": "\n\n## 실행\n**중요**: 직접 실행. CLI 는 전체 기능 보유.",
    }.get(lang, ""))
    
    return "\n".join(parts)
