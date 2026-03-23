# Mail Stats Dashboard — Implementation Notes

## Overview

The mail stats dashboard (`/tabs/stats`) was added to track email processing history.
It reads from the `mail_stats` table in `tasks.db` and displays:

- KPI cards: total processed, today's count, success rate, average AI response time
- 7-day bar chart (success vs error breakdown per day)
- Recent 10 records table

## Components

| File | Role |
|------|------|
| `tasks/scheduler.py` | `mail_stats` table creation + `record_stat()` method |
| `email_daemon.py` | Calls `scheduler.record_stat()` after each AI call (success or error) |
| `webui/server.py` | `get_mail_stats()` aggregation function + `/tabs/stats` route |
| `webui/templates/partials/tab_stats.html` | Jinja2 template for the stats tab |
| `webui/static/style.css` | `.stats-*` CSS classes for cards and bar chart |

## DB Schema

`mail_stats` table (in `tasks.db`):

```sql
CREATE TABLE mail_stats (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ts      REAL NOT NULL,       -- Unix timestamp (local time)
    mailbox TEXT,                -- mailbox name key (e.g. "gmail")
    status  TEXT,                -- "success" or "error"
    ai_ms   INTEGER,             -- AI response time in milliseconds
    subject TEXT                 -- email subject (truncated to 100 chars)
);
CREATE INDEX idx_stats_ts ON mail_stats (ts);
```

## Bug Fixed: Timezone offset in day boundary calculation

### Problem

The original `get_mail_stats()` used `now % 86400` to compute midnight boundaries:

```python
# WRONG — UTC-based, off by local UTC offset hours
today_start = now - (now % day)
day_start = day_ts - (day_ts % day)
```

Since `time.time()` returns seconds since the Unix epoch (UTC), `now % 86400` gives
the number of seconds elapsed since 00:00 UTC — not local midnight. For a UTC+9
timezone this produces a boundary 9 hours into the local day, causing "today"
to miss all emails sent between 00:00 and 09:00 local time, and the 7-day bar
chart to misattribute emails near midnight.

### Fix

Replaced the modulo calculation with proper local datetime arithmetic:

```python
# CORRECT — uses local midnight
local_now = datetime.now()
today_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

# For 7-day chart:
day_dt = local_now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
day_start = day_dt.timestamp()
day_end = (day_dt + timedelta(days=1)).timestamp()
```

`datetime.now()` returns the current local time, so `.replace(hour=0, ...)` gives
the correct local midnight regardless of the system timezone.

## Skills Test Panel

The skills tab now includes an inline test panel for each skill. Clicking "Test"
expands a JSON payload editor; clicking "Run" calls `POST /api/skills/{name}/test`
and displays the result inline. The endpoint is auth-protected.

## Notes

- `record_stat()` is wrapped in a try/except so a DB failure never breaks email delivery.
- `get_mail_stats()` returns `{}` if `tasks.db` does not exist or the `mail_stats`
  table is missing — the template handles this gracefully by showing an empty-state message.
- The `mail_stats` table is created automatically by `TaskScheduler._init_db()` on
  first startup; no manual migration is required.
