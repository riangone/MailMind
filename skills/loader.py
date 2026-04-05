"""
skills/loader.py - 技能加载器

所有 skill 都是 MD 文件。
AI 通过 CLI 直接执行，不需要 PY 文件。
"""

import os
import re
from typing import Optional
from skills import BaseSkill, MDSkill
from utils.logger import log

_registry: dict = {}
_loaded = False


def _parse_yaml_frontmatter(text: str) -> dict:
    """解析 YAML front matter（简化版，支持嵌套字典/列表）"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', text, re.DOTALL)
    if not match:
        return {}, text

    yaml_str = match.group(1)
    body = match.group(2).strip()

    def _parse_scalar(raw: str):
        v = raw.strip()
        if not v:
            return ""
        if v.startswith('[') and v.endswith(']'):
            items = [x.strip().strip('"').strip("'") for x in v[1:-1].split(',') if x.strip()]
            return items
        if v.startswith('{') and v.endswith('}'):
            inner = {}
            for item in v[1:-1].split(','):
                if ':' in item:
                    ik, _, iv = item.partition(':')
                    inner[ik.strip()] = iv.strip().strip('"').strip("'")
            return inner
        low = v.lower()
        if low in ('true', 'yes'):
            return True
        if low in ('false', 'no'):
            return False
        if v.isdigit():
            try:
                return int(v)
            except Exception:
                return v
        return v.strip('"').strip("'")

    meta: dict = {}
    # stack entries: (indent_level, container, pending_key)
    stack = [(-1, meta, None)]

    for raw_line in yaml_str.splitlines():
        if not raw_line.strip():
            continue
        # Expand tabs to keep indentation consistent
        line = raw_line.expandtabs(2)
        indent = len(line) - len(line.lstrip(' '))
        stripped = line.strip()

        # Find current container based on indent
        while stack and indent < stack[-1][0]:
            stack.pop()
        if not stack:
            stack = [(-1, meta, None)]

        parent_indent, parent_container, pending_key = stack[-1]

        # If parent is waiting for a nested container, create it now
        if pending_key is not None and indent > parent_indent:
            new_container = [] if stripped.startswith('- ') else {}
            if isinstance(parent_container, dict):
                parent_container[pending_key] = new_container
            stack[-1] = (parent_indent, parent_container, None)
            stack.append((indent, new_container, None))
            parent_container = new_container
            parent_indent = indent

        if stripped.startswith('- '):
            item_raw = stripped[2:].strip()
            if isinstance(parent_container, list):
                parent_container.append(_parse_scalar(item_raw))
            elif isinstance(parent_container, dict):
                # Try to append to the last pending key if it exists
                if stack[-1][2]:
                    key = stack[-1][2]
                    parent_container[key] = parent_container.get(key, [])
                    if isinstance(parent_container[key], list):
                        parent_container[key].append(_parse_scalar(item_raw))
            continue

        if ':' not in stripped:
            continue
        key, _, value = stripped.partition(':')
        key = key.strip()
        value = value.strip()

        if not value:
            # Defer container type (dict/list) to next indented line
            stack[-1] = (parent_indent, parent_container, key)
            continue

        if isinstance(parent_container, dict):
            parent_container[key] = _parse_scalar(value)

    # Resolve any dangling pending keys as empty dicts
    for indent, container, pending_key in stack:
        if pending_key and isinstance(container, dict) and pending_key not in container:
            container[pending_key] = {}

    return meta, body


def load_all_skills() -> dict:
    """加载所有 MD 技能文件"""
    global _registry, _loaded
    skills = {}
    skills_dir = os.path.dirname(__file__)
    
    for fname in sorted(os.listdir(skills_dir)):
        if not fname.endswith('.md'):
            continue
        
        skill_name = fname[:-3]
        fpath = os.path.join(skills_dir, fname)
        
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            meta, body = _parse_yaml_frontmatter(content)
            
            if not meta or 'name' not in meta:
                continue
            
            # 解析 params（如果有）
            params = meta.get('params', {})
            if isinstance(params, str):
                params = {}
            
            skill = MDSkill(
                name=meta.get('name', skill_name),
                description=meta.get('description', ''),
                instruction=body,
                description_ja=meta.get('description_ja', ''),
                description_en=meta.get('description_en', ''),
                category=meta.get('category', 'general'),
                keywords=meta.get('keywords', []),
                params=params,
                auto_execute=meta.get('auto_execute', True),
                chainable=meta.get('chainable', True),
            )
            
            if skill.name:
                skills[skill.name] = skill
                log.debug(f"[Skills] ✓ 加载: {skill.name}")
        except Exception as e:
            log.warning(f"[Skills] ✗ 加载失败 {fname}: {e}")
    
    _registry = skills
    _loaded = True
    log.info(f"[Skills] 已加载 {len(skills)} 个技能 (全部 MD 文件)")
    return skills


def get_registry() -> dict:
    if not _loaded:
        load_all_skills()
    return _registry


def get_skill(name: str) -> Optional[MDSkill]:
    return get_registry().get(name)


def reload_skills() -> dict:
    global _loaded
    _loaded = False
    return load_all_skills()


def get_skills_hint(lang: str = "zh") -> str:
    """获取技能列表提示"""
    skills = get_registry()
    if not skills:
        return ""
    
    if lang == "ja":
        lines = ["利用可能なスキル:"]
        for name, sk in skills.items():
            desc = sk.description_ja or sk.description_en or sk.description
            lines.append(f"  {name}: {desc}")
    elif lang == "en":
        lines = ["Available skills:"]
        for name, sk in skills.items():
            lines.append(f"  {name}: {sk.description_en or sk.description}")
    else:
        lines = ["可用技能："]
        for name, sk in skills.items():
            lines.append(f"  {name}: {sk.description}")
    
    return "\n".join(lines)
