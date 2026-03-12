# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MailMind is an email-to-AI bridge daemon. Users send emails with instructions; the daemon polls via IMAP, passes the instruction to an AI backend, and replies via SMTP.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install requests
# Optional for Gmail OAuth:
pip install google-auth google-auth-oauthlib google-auth-httplib2
# Optional for Outlook OAuth:
pip install msal
```

## Running

```bash
# Daemon lifecycle (recommended)
bash manage.sh start | stop | restart | status | log

# Direct invocation
python3 email_daemon.py --mailbox gmail --ai claude
python3 email_daemon.py --mailbox 126 --ai anthropic
python3 email_daemon.py --list                        # Show config status
python3 email_daemon.py --mailbox gmail --auth        # One-time OAuth flow
```

## Architecture

Everything lives in two files:

- **`email_daemon.py`** — the core daemon (~576 lines)
- **`manage.sh`** — wrapper for background process/systemd lifecycle + all configuration

### Configuration model

All credentials and settings are injected via environment variables. `manage.sh` (lines 7–57) is where these are set before invoking the daemon. There are no config files — just env vars.

### Key data structures in `email_daemon.py`

- **`MAILBOX_CONFIG`** (line ~29) — dict of mailbox presets keyed by name (`126`, `163`, `qq`, `gmail`, `outlook`), each with IMAP/SMTP servers, ports, auth type, and env var names to read credentials from.
- **`AI_CONFIG`** (line ~99) — dict of AI backend presets keyed by name, each with `type` (`cli` or `api`), command/URL, and model.

### Main loop flow

```
fetch_unread_emails() → process_email() → call_ai() → send_reply()
```

- IMAP polling every `POLL_INTERVAL` seconds (default 60)
- Per-mailbox sender whitelist checked before processing
- AI response expected as JSON `{"subject": "...", "body": "..."}` (prompt is hardcoded in Chinese, lines ~118–124)
- Processed email IDs tracked in-memory to prevent duplicate handling

### Adding a new mailbox or AI backend

Add an entry to `MAILBOX_CONFIG` or `AI_CONFIG` in `email_daemon.py` — the rest of the logic is generic and routes by config.

### Auth types

| Mailbox | Auth |
|---------|------|
| 126, 163, qq | password (app password via env var) |
| gmail | `oauth_google` (browser flow) or `password` |
| outlook | `oauth_microsoft` (device code flow) |

OAuth tokens are cached as `token_<mailbox>.json` (gitignored).

## Systemd

```bash
bash manage.sh install    # Install and enable service
bash manage.sh uninstall  # Remove service
```

The template `email-daemon.service` targets user `ubuntu` at `/home/ubuntu/ws/ccmail` — adjust before installing.
