---
name: twitter-workflow-ops
description: Run and troubleshoot the twitter-workflow project safely (config checks, dry-run execution, login/cookie checks, telegram delivery checks).
---

# Twitter Workflow Ops

Use this skill when operating this repository's workflow scripts (`main.py`, `login_twitter.py`, `get_chat_id.py`).

## Quick procedure

1. Validate local configuration and required env vars.
2. Run dry-run first.
3. If dry-run is healthy, run production mode.
4. If Telegram delivery fails, run chat-id diagnostics.

## Commands

- Validate env/config: `python scripts/check_env_and_config.py`
- Dry-run (visible): `python main.py --visible --dry-run`
- Get telegram chat ids: `python get_chat_id.py`
- Twitter login refresh: `python login_twitter.py`

## Safety defaults

- Prefer `--dry-run` before any real send.
- Prefer low volume parameters first (`-n 1` / stricter filters).
- Never hardcode API keys in tracked files.
