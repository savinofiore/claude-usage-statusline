#!/usr/bin/env python3
"""SessionStart hook: wire this plugin's statusline into ~/.claude/settings.json.

Idempotent — no-ops if our statusline is already configured, and never
overwrites a statusLine that belongs to someone else.
"""
import json
import os
import sys
from pathlib import Path

MARKER = "usage-statusline.py"


def settings_path():
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))
    return Path(config_dir) / "settings.json"


def load_settings(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def existing_command(settings):
    line = settings.get("statusLine")
    if not line:
        return ""
    return line if isinstance(line, str) else line.get("command", "")


def main():
    path = settings_path()
    settings = load_settings(path)
    if settings is None:
        print(f"claude-usage-statusline: {path} is not valid JSON — skipping. "
              "Add statusLine manually, see README.")
        return

    current = existing_command(settings)
    if MARKER in current:
        return

    if current:
        print("claude-usage-statusline: existing statusLine detected — not overriding. "
              "See README to add the badge manually.")
        return

    script = Path(__file__).resolve().parent.parent / "hooks" / "usage-statusline.py"
    settings["statusLine"] = {"type": "command", "command": f'python3 "{script}"'}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n")
    print("claude-usage-statusline: statusline installed — restart Claude Code to see it.")


if __name__ == "__main__":
    main()
