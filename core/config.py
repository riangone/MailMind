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
    # CLI 方式
    "claude":      {"type": "cli",           "cmd": os.environ.get("CLAUDE_CMD", "claude"), "args": ["--print"],                                                              "label": "Claude CLI",       "env_key": None},
    "codex":       {"type": "cli",           "cmd": os.environ.get("CODEX_CMD",  "codex"),  "args": ["exec", "--skip-git-repo-check"],                                        "label": "Codex CLI",        "env_key": None},
    "gemini":      {"type": "cli",           "cmd": os.environ.get("GEMINI_CMD", "gemini"), "args": ["-p"],                                                                   "label": "Gemini CLI",       "env_key": None},
    "qwen":        {"type": "cli",           "cmd": os.environ.get("QWEN_CMD",   "qwen"),   "args": ["--prompt", "--web-search-default", "--yolo"], "native_web_search": True, "label": "Qwen CLI",         "env_key": None},
    "copilot":     {"type": "cli_copilot",   "cmd": _copilot_cmd(),                                                                                                           "label": "GitHub Copilot",   "env_key": "GITHUB_COPILOT_TOKEN"},

    # API 方式 - 国际模型
    "anthropic":   {"type": "api_anthropic", "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),  "model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),                                                      "label": "Anthropic Claude",  "env_key": "ANTHROPIC_API_KEY"},
    "openai":      {"type": "api_openai",    "api_key": os.environ.get("OPENAI_API_KEY", ""),     "model": os.environ.get("OPENAI_MODEL",     "gpt-4o"),            "url": "https://api.openai.com/v1/chat/completions",          "label": "OpenAI (gpt-4o)",   "env_key": "OPENAI_API_KEY"},
    "gemini-api":  {"type": "api_gemini",    "api_key": os.environ.get("GEMINI_API_KEY", ""),     "model": os.environ.get("GEMINI_MODEL",     "gemini-3-flash-preview"),                                                 "label": "Gemini API",        "env_key": "GEMINI_API_KEY"},
    "deepseek":    {"type": "api_openai",    "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),   "model": os.environ.get("DEEPSEEK_MODEL",    "deepseek-chat"),     "url": "https://api.deepseek.com/v1/chat/completions",        "label": "DeepSeek",          "env_key": "DEEPSEEK_API_KEY"},
    "groq":        {"type": "api_openai",    "api_key": os.environ.get("GROQ_API_KEY", ""),       "model": os.environ.get("GROQ_MODEL",         "llama-3.3-70b-versatile"), "url": "https://api.groq.com/openai/v1/chat/completions",  "label": "Groq (Llama)",      "env_key": "GROQ_API_KEY"},
    "perplexity":  {"type": "api_openai",    "api_key": os.environ.get("PERPLEXITY_API_KEY", ""), "model": os.environ.get("PERPLEXITY_MODEL",   "sonar-pro"),             "url": "https://api.perplexity.ai/chat/completions",      "label": "Perplexity",        "env_key": "PERPLEXITY_API_KEY"},
    "cohere":      {"type": "api_cohere",    "api_key": os.environ.get("COHERE_API_KEY", ""),     "model": os.environ.get("COHERE_MODEL",       "command-r-plus"),                                                        "label": "Cohere",            "env_key": "COHERE_API_KEY"},

    # API 方式 - 中国模型
    "qwen-api":    {"type": "api_qwen",      "api_key": os.environ.get("QWEN_API_KEY", ""),       "model": os.environ.get("QWEN_MODEL",       "qwen-max"),                                                               "label": "通义千问 (Qwen)",    "env_key": "QWEN_API_KEY"},
    "moonshot":    {"type": "api_openai",    "api_key": os.environ.get("MOONSHOT_API_KEY", ""),   "model": os.environ.get("MOONSHOT_MODEL",   "moonshot-v1-8k"),      "url": "https://api.moonshot.cn/v1/chat/completions",        "label": "月之暗面 Kimi",      "env_key": "MOONSHOT_API_KEY"},
    "glm":         {"type": "api_openai",    "api_key": os.environ.get("GLM_API_KEY", ""),        "model": os.environ.get("GLM_MODEL",        "glm-4"),               "url": "https://open.bigmodel.cn/api/paas/v4/chat/completions", "label": "智谱 GLM",          "env_key": "GLM_API_KEY"},
    "spark":       {"type": "api_spark",     "api_key": os.environ.get("SPARK_API_KEY", ""),      "model": os.environ.get("SPARK_MODEL",      "4.0Ultra"),                                                               "label": "讯飞星火",           "env_key": "SPARK_API_KEY"},
    "ernie":       {"type": "api_ernie",     "api_key": os.environ.get("ERNIE_API_KEY", ""),      "model": os.environ.get("ERNIE_MODEL",      "ernie-4.0-8k"),                                                           "label": "百度文心一言",        "env_key": "ERNIE_API_KEY"},
    "yi":          {"type": "api_openai",    "api_key": os.environ.get("YI_API_KEY", ""),         "model": os.environ.get("YI_MODEL",         "yi-lightning"),        "url": "https://api.lingyiwanwu.com/v1/chat/completions",     "label": "零一万物 Yi",        "env_key": "YI_API_KEY"},
}

# ────────────────────────────────────────────────────────────────
#  Web Search / Weather / News 配置
# ────────────────────────────────────────────────────────────────

WEB_SEARCH_ENABLED = os.environ.get("WEB_SEARCH", "false").lower() == "true"
WEB_SEARCH_ENGINE = os.environ.get("WEB_SEARCH_ENGINE", "google")
SEARCH_RESULTS_COUNT = int(os.environ.get("SEARCH_RESULTS_COUNT", "5"))
WEB_SEARCH_TIMEOUT = int(os.environ.get("WEB_SEARCH_TIMEOUT", "10"))
BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
WEATHER_DEFAULT_LOCATION = os.environ.get("WEATHER_DEFAULT_LOCATION", "Tokyo")
NEWS_DEFAULT_QUERY = os.environ.get("NEWS_DEFAULT_QUERY", "technology OR AI")

POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "60"))
DEFAULT_TASK_AI = os.environ.get("TASK_DEFAULT_AI", "")
ATTACHMENT_MAX_SIZE_MB = int(os.environ.get("ATTACHMENT_MAX_SIZE_MB", "10"))
AI_CONCURRENCY = int(os.environ.get("AI_CONCURRENCY", "3"))
CONTEXT_MAX_DEPTH = int(os.environ.get("CONTEXT_MAX_DEPTH", "5"))

# ────────────────────────────────────────────────────────────────
#  Prompts
# ────────────────────────────────────────────────────────────────

_PROMPT_TEMPLATES = {
    "zh": """\
你正在通过邮件接收用户指令。以下是用户发来的邮件，请执行其中的任务。

{{instruction}}

请严格按以下 JSON 格式回复，不要输出任何其他内容：
{{"subject": "根据回复内容拟定的简短邮件标题",
  "body": "回复正文内容",
  "schedule_at": "可选：触发时间(ISO格式或相对秒数)",
  "schedule_every": "可选：重复间隔(秒或5m/2h)",
  "schedule_cron": "可选：cron表达式(例: 0 9 * * 1-5)",
  "schedule_until": "可选：截止时间(ISO格式)",
  "attachments": [{{"filename": "文件名.txt", "content": "文件内容"}}],
  "task_type": "可选：email|ai_job|weather|news|web_search|report|system_status",
  "task_payload": {{"可选": "任务参数，如 location/query/prompt 等"}},
  "output": {{"email": true, "archive": true, "archive_dir": "reports"}}
}}

说明：
- 当用户要求获取"OS状态"、"CPU使用率"、"内存使用情况"或"磁盘空间"等系统信息时，请务必设置 task_type="system_status"。
- 只有当用户明确要求"日报"、"总结报告"或"综合信息"时，才使用 task_type="report"。
- schedule_at: 仅当用户要求定时提醒/发送时使用（例如 "2026-03-13T10:00:00" 或 "3600" 表示1小时后）。若即时回复则省略。
- schedule_every: 当用户要求"每 X 分钟/小时"等重复提醒时填写（例如 "5m"、"300"）。
- schedule_cron: 使用 cron 表达式进行高级定时调度（例如平日早9点 → "0 9 * * 1-5"，每小时 → "0 * * * *"）。
- schedule_until: 重复提醒的截止时间（例如 "2026-03-13T18:00:00"），与 schedule_every/schedule_cron 配合使用。
- attachments 为可选字段，附件内容为纯文本。""",

    "ja": """\
あなたはメールでユーザーの指示を受け取っています。以下のメールを読み、タスクを実行してください。

{{instruction}}

以下のJSON形式で厳密に回答してください。他のテキストは出力しないでください：
{{"subject": "返信メールの件名",
  "body": "返信本文",
  "schedule_at": "任意：実行時刻（ISO形式または相対秒数）",
  "schedule_every": "任意：繰り返し間隔（秒または5m/2h）",
  "schedule_cron": "任意：cron式（例: 0 9 * * 1-5）",
  "schedule_until": "任意：終了時刻（ISO形式）",
  "attachments": [{{"filename": "ファイル名.txt", "content": "ファイル内容"}}],
  "task_type": "任意：email|ai_job|weather|news|web_search|report|system_status",
  "task_payload": {{"location": "...", "query": "...", "prompt": "..."}},
  "output": {{"email": true, "archive": true, "archive_dir": "reports"}}
}}

説明：
- CPU・メモリ・ディスクなどシステム情報のリクエストには task_type="system_status" を設定してください。
- 日報・週報・総合レポートの場合のみ task_type="report" を使用してください。
- schedule_at: ユーザーが特定の時刻を指定した場合のみ使用（例: "2026-03-13T10:00:00" または "3600" で1時間後）。
- schedule_every: 「毎X分/時間」など繰り返しの場合に使用（例: "5m"、"2h"）。
- schedule_cron: cron式による高度なスケジューリング（例: 平日9時毎日 → "0 9 * * 1-5"）。
- schedule_until: 繰り返しの終了時刻（schedule_every/schedule_cronと組み合わせて使用）。
- attachments は任意フィールドで、テキストコンテンツのみ対応。""",

    "en": """\
You are receiving user instructions via email. Please read the email below and execute the requested task.

{{instruction}}

Reply strictly in the following JSON format with no other text:
{{"subject": "Short email subject for the reply",
  "body": "Reply body content",
  "schedule_at": "Optional: trigger time (ISO format or relative seconds)",
  "schedule_every": "Optional: repeat interval (seconds or 5m/2h)",
  "schedule_cron": "Optional: cron expression (e.g. 0 9 * * 1-5)",
  "schedule_until": "Optional: end time (ISO format)",
  "attachments": [{{"filename": "file.txt", "content": "file content"}}],
  "task_type": "Optional: email|ai_job|weather|news|web_search|report|system_status",
  "task_payload": {{"location": "...", "query": "...", "prompt": "..."}},
  "output": {{"email": true, "archive": true, "archive_dir": "reports"}}
}}

Notes:
- Set task_type="system_status" for system info requests (CPU usage, memory, disk space).
- Use task_type="report" only for daily/weekly reports or summaries.
- schedule_at: only when user requests a specific time (e.g. "2026-03-13T10:00:00" or "3600" for 1 hour later).
- schedule_every: for recurring tasks (e.g. "every 5 minutes" → "5m", "every 2 hours" → "2h").
- schedule_cron: for advanced scheduling using cron syntax (e.g. weekdays at 9 AM → "0 9 * * 1-5").
- schedule_until: end time for recurring tasks, used with schedule_every or schedule_cron.
- attachments: optional, text content only.""",
}

def _load_prompt_template() -> str:
    custom_file = os.environ.get("PROMPT_TEMPLATE_FILE", "")
    if custom_file and os.path.isfile(custom_file):
        with open(custom_file, "r", encoding="utf-8") as f:
            tmpl = f.read()
        # Ensure {instruction} placeholder exists
        if "{instruction}" not in tmpl and "{{instruction}}" in tmpl:
            tmpl = tmpl.replace("{{instruction}}", "{instruction}")
        return tmpl
    lang = os.environ.get("PROMPT_LANG", "zh").lower()
    tmpl = _PROMPT_TEMPLATES.get(lang, _PROMPT_TEMPLATES["zh"])
    # Convert {{instruction}} → {instruction} for .format() compatibility
    return tmpl.replace("{{instruction}}", "{instruction}")

PROMPT_TEMPLATE = _load_prompt_template()
