#!/usr/bin/env python3
import json
import os
from pathlib import Path

required_env = ["VOLC_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
missing = [k for k in required_env if not os.getenv(k)]

config_path = Path("config.json")
config_ok = config_path.exists()
config_error = None
if config_ok:
    try:
        json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        config_error = str(exc)
        config_ok = False

print("[check] env")
for k in required_env:
    print(f"- {k}: {'ok' if os.getenv(k) else 'missing'}")

print("[check] config.json")
if not config_path.exists():
    print("- missing")
elif config_ok:
    print("- ok")
else:
    print(f"- invalid: {config_error}")

if missing or not config_ok:
    raise SystemExit(1)
