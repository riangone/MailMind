import os
import shutil

# ═══════════════════════════════════════════════════════════════
#  邮箱配置
# ═══════════════════════════════════════════════════════════════

MAILBOXES = {
    "126": {
        "address":         os.environ.get("MAIL_126_ADDRESS", ""),
        "password":        os.environ.get("MAIL_126_PASSWORD", ""),
        "imap_server":     "imap.126.com",
        "imap_port":       993,
        "smtp_server":     "smtp.126.com",
        "smtp_port":       465,
        "smtp_ssl":        True,
        "imap_id":         True,
        "auth":            "password",
        "allowed_senders": [s.strip() for s in os.environ.get("MAIL_126_ALLOWED", "").split(",") if s.strip()],
        "spam_folder":     os.environ.get("MAIL_126_SPAM_FOLDER", "Junk"),
    },
    "163": {
        "address":         os.environ.get("MAIL_163_ADDRESS", ""),
        "password":        os.environ.get("MAIL_163_PASSWORD", ""),
        "imap_server":     "imap.163.com",
        "imap_port":       993,
        "smtp_server":     "smtp.163.com",
        "smtp_port":       465,
        "smtp_ssl":        True,
        "imap_id":         True,
        "auth":            "password",
        "allowed_senders": [s.strip() for s in os.environ.get("MAIL_163_ALLOWED", "").split(",") if s.strip()],
        "spam_folder":     os.environ.get("MAIL_163_SPAM_FOLDER", "Junk"),
    },
    "qq": {
        "address":         os.environ.get("MAIL_QQ_ADDRESS", ""),
        "password":        os.environ.get("MAIL_QQ_PASSWORD", ""),
        "imap_server":     "imap.qq.com",
        "imap_port":       993,
        "smtp_server":     "smtp.qq.com",
        "smtp_port":       465,
        "smtp_ssl":        True,
        "imap_id":         False,
        "auth":            "password",
        "allowed_senders": [s.strip() for s in os.environ.get("MAIL_QQ_ALLOWED", "").split(",") if s.strip()],
        "spam_folder":     os.environ.get("MAIL_QQ_SPAM_FOLDER", "Junk"),
    },
    "gmail": {
        "address":         os.environ.get("MAIL_GMAIL_ADDRESS", ""),
        "password":        os.environ.get("MAIL_GMAIL_PASSWORD", ""),
        "imap_server":     "imap.gmail.com",
        "imap_port":       993,
        "smtp_server":     "smtp.gmail.com",
        "smtp_port":       465,
        "smtp_ssl":        True,
        "imap_id":         False,
        "auth":            os.environ.get("MAIL_GMAIL_AUTH", "oauth_google"),
        "oauth_token_file": os.path.join(os.path.dirname(__file__), "..", "token_gmail.json"),
        "oauth_creds_file": os.path.join(os.path.dirname(__file__), "..", "credentials_gmail.json"),
        "allowed_senders": [s.strip() for s in os.environ.get("MAIL_GMAIL_ALLOWED", "").split(",") if s.strip()],
        "spam_folder":     os.environ.get("MAIL_GMAIL_SPAM_FOLDER", "[Gmail]/Spam"),
    },
    "outlook": {
        "address":         os.environ.get("MAIL_OUTLOOK_ADDRESS", ""),
        "imap_server":     "outlook.office365.com",
        "imap_port":       993,
        "smtp_server":     "smtp.office365.com",
        "smtp_port":       587,
        "smtp_ssl":        False,
        "imap_id":         False,
        "auth":            "oauth_microsoft",
        "oauth_token_file": os.path.join(os.path.dirname(__file__), "..", "token_outlook.json"),
        "oauth_client_id":  os.environ.get("OUTLOOK_CLIENT_ID", ""),
        "allowed_senders": [s.strip() for s in os.environ.get("MAIL_OUTLOOK_ALLOWED", "").split(",") if s.strip()],
        "spam_folder":     os.environ.get("MAIL_OUTLOOK_SPAM_FOLDER", "Junk"),
    },
    "icloud": {
        "address":         os.environ.get("MAIL_ICLOUD_ADDRESS", ""),
        "password":        os.environ.get("MAIL_ICLOUD_PASSWORD", ""),  # App-specific password
        "imap_server":     "imap.mail.me.com",
        "imap_port":       993,
        "smtp_server":     "smtp.mail.me.com",
        "smtp_port":       587,
        "smtp_ssl":        False,
        "imap_id":         False,
        "auth":            "password",
        "allowed_senders": [s.strip() for s in os.environ.get("MAIL_ICLOUD_ALLOWED", "").split(",") if s.strip()],
        "spam_folder":     os.environ.get("MAIL_ICLOUD_SPAM_FOLDER", "Junk"),
    },
    "proton": {
        "address":         os.environ.get("MAIL_PROTON_ADDRESS", ""),
        "password":        os.environ.get("MAIL_PROTON_PASSWORD", ""),  # Bridge password
        "imap_server":     "127.0.0.1",
        "imap_port":       1143,
        "smtp_server":     "127.0.0.1",
        "smtp_port":       1025,
        "smtp_ssl":        False,
        "imap_id":         False,
        "auth":            "password",
        "allowed_senders": [s.strip() for s in os.environ.get("MAIL_PROTON_ALLOWED", "").split(",") if s.strip()],
        "spam_folder":     os.environ.get("MAIL_PROTON_SPAM_FOLDER", "Spam"),
    },
    "custom": {
        "address":         os.environ.get("MAIL_CUSTOM_ADDRESS", ""),
        "password":        os.environ.get("MAIL_CUSTOM_PASSWORD", ""),
        "imap_server":     os.environ.get("MAIL_CUSTOM_IMAP_SERVER", ""),
        "imap_port":       int(os.environ.get("MAIL_CUSTOM_IMAP_PORT", "993")),
        "smtp_server":     os.environ.get("MAIL_CUSTOM_SMTP_SERVER", ""),
        "smtp_port":       int(os.environ.get("MAIL_CUSTOM_SMTP_PORT", "465")),
        "smtp_ssl":        os.environ.get("MAIL_CUSTOM_SMTP_SSL", "true").lower() == "true",
        "imap_id":         False,
        "auth":            "password",
        "allowed_senders": [s.strip() for s in os.environ.get("MAIL_CUSTOM_ALLOWED", "").split(",") if s.strip()],
        "spam_folder":     os.environ.get("MAIL_CUSTOM_SPAM_FOLDER", ""),
    },
}

# ═══════════════════════════════════════════════════════════════
#  AI 配置
# ═══════════════════════════════════════════════════════════════

def _copilot_cmd() -> str:
    """查找 GitHub Copilot CLI 可执行文件路径"""
    env_cmd = os.environ.get("COPILOT_CMD", "")
    if env_cmd:
        return env_cmd
    bundled = os.path.expanduser(
        "~/.vscode-server/data/User/globalStorage/github.copilot-chat/copilotCli/copilot"
    )
    if os.path.isfile(bundled):
        return bundled
    return "copilot"


AI_BACKENDS = {
    "claude":      {"type": "cli", "cmd": os.environ.get("CLAUDE_CMD", "claude"), "args": ["--print"]},
    "codex":       {"type": "cli", "cmd": os.environ.get("CODEX_CMD",  "codex"),  "args": ["exec", "--skip-git-repo-check"]},
    "gemini":      {"type": "cli", "cmd": os.environ.get("GEMINI_CMD", "gemini"), "args": ["-p"]},
    "qwen":        {"type": "cli", "cmd": os.environ.get("QWEN_CMD",   "qwen"),   "args": ["--prompt", "--web-search-default", "--yolo"], "native_web_search": True},
    "anthropic":   {"type": "api_anthropic", "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),  "model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")},
    "openai":      {"type": "api_openai",    "api_key": os.environ.get("OPENAI_API_KEY", ""),     "model": os.environ.get("OPENAI_MODEL",     "gpt-4o"),            "url": "https://api.openai.com/v1/chat/completions"},
    "gemini-api":  {"type": "api_gemini",    "api_key": os.environ.get("GEMINI_API_KEY", ""),     "model": os.environ.get("GEMINI_MODEL",     "gemini-3-flash-preview")},
    "qwen-api":    {"type": "api_qwen",      "api_key": os.environ.get("QWEN_API_KEY", ""),       "model": os.environ.get("QWEN_MODEL",       "qwen-max")},
    "deepseek":    {"type": "api_openai",    "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),   "model": os.environ.get("DEEPSEEK_MODEL",    "deepseek-chat"),     "url": "https://api.deepseek.com/v1/chat/completions"},
    "copilot":     {"type": "cli_copilot",   "cmd": _copilot_cmd()},
}

# ────────────────────────────────────────────────────────────────
#  Web Search / Weather / News 配置
# ────────────────────────────────────────────────────────────────

WEB_SEARCH_ENABLED = os.environ.get("WEB_SEARCH", "false").lower() == "true"
WEB_SEARCH_ENGINE = os.environ.get("WEB_SEARCH_ENGINE", "google")
SEARCH_RESULTS_COUNT = int(os.environ.get("SEARCH_RESULTS_COUNT", "5"))
WEB_SEARCH_TIMEOUT = int(os.environ.get("WEB_SEARCH_TIMEOUT", "10"))
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
WEATHER_DEFAULT_LOCATION = os.environ.get("WEATHER_DEFAULT_LOCATION", "Tokyo")
NEWS_DEFAULT_QUERY = os.environ.get("NEWS_DEFAULT_QUERY", "technology OR AI")

POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "60"))
DEFAULT_TASK_AI = os.environ.get("TASK_DEFAULT_AI", "")

# ────────────────────────────────────────────────────────────────
#  Prompts
# ────────────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """\
你正在通过邮件接收用户指令。以下是用户发来的邮件，请执行其中的任务。

{instruction}

请严格按以下 JSON 格式回复，不要输出任何其他内容：
{{"subject": "根据回复内容拟定的简短邮件标题",
  "body": "回复正文内容",
  "schedule_at": "可选：触发时间(ISO格式或相对秒数)",
  "schedule_every": "可选：重复间隔(秒或5m/2h)",
  "schedule_until": "可选：截止时间(ISO格式)",
  "attachments": [{{"filename": "文件名.txt", "content": "文件内容"}}],
  "task_type": "可选：email|ai_job|weather|news|web_search|report|system_status",
  "task_payload": {{"可选": "任务参数，如 location/query/prompt 等"}},
  "output": {{"email": true, "archive": true, "archive_dir": "reports"}}
}}

说明：
- 当用户要求获取“OS状态”、“CPU使用率”、“内存使用情况”或“磁盘空间”等系统信息时，请务必设置 task_type="system_status"。
- 只有当用户明确要求“日报”、“总结报告”或“综合信息”时，才使用 task_type="report"。
- schedule_at: 仅当用户要求定时提醒/发送时使用（例如 "2026-03-13T10:00:00" 或 "3600" 表示1小时后）。若即时回复则省略。
- schedule_every: 当用户要求“每 X 分钟/小时”等重复提醒时填写（例如 "5m"、"300"）。
- schedule_until: 重复提醒的截止时间（例如 "2026-03-13T18:00:00"），与 schedule_every 配合使用。
- attachments 为可选字段，附件内容为纯文本。"""
