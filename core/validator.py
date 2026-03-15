import os
import logging
from typing import List, Dict

log = logging.getLogger("mailmind")

def validate_config(mailboxes: Dict, ai_backends: Dict) -> bool:
    """验证配置的完整性"""
    success = True
    
    # 验证邮箱
    active_mailboxes = []
    for name, mb in mailboxes.items():
        if mb.get("address"):
            active_mailboxes.append(name)
            # 基础验证
            if not mb.get("imap_server") or not mb.get("smtp_server"):
                log.warning(f"邮箱 '{name}' 配置缺失服务器信息")
                success = False
    
    if not active_mailboxes:
        log.warning("未检测到配置了 address 的有效邮箱")
        # success = False # 允许空配置启动，可能是为了 list
        
    # 验证 AI
    active_ai = []
    for name, ai in ai_backends.items():
        t = ai.get("type")
        if t == "cli":
            if os.path.isfile(ai.get("cmd", "")) or shutil.which(ai.get("cmd", "")):
                active_ai.append(name)
        elif t.startswith("api_"):
            if ai.get("api_key"):
                active_ai.append(name)
                
    if not active_ai:
        log.warning("未检测到有效的 AI 后端（CLI 或 API Key）")
        # success = False
        
    return success

import shutil
