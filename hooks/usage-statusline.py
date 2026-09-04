#!/usr/bin/env python3
"""Claude Code statusline: model, context, 5h and weekly rate-limit bars.

Reads the statusline JSON payload on stdin and prints one ANSI-colored line:
  Opus 5 (1M context) ctx [====   ] 5%  5h [=      ] 5% 3h29m  weekly [==  ] 15% 1d12h  $0.35

Wire it up in settings.json:
  "statusLine": { "type": "command", "command": "python3 ~/.claude/hooks/usage-statusline.py" }
"""
import json
import sys
import time

BAR_WIDTH = 12
PARTIAL_BLOCKS = " ▏▎▍▌▋▊▉"
RESET = "\033[0m"
BOLD_WHITE = "\033[1;38;5;255m"
LABEL = "\033[38;5;245m"
EMPTY_TRACK = "\033[38;5;238m"
COST_STYLE = "\033[38;5;81m"
GREEN, YELLOW, ORANGE, RED = "\033[38;5;114m", "\033[38;5;185m", "\033[38;5;215m", "\033[38;5;203m"


def color_for(percent):
    """Green under half, then warmer as the budget runs out."""
    if percent >= 90:
        return RED
    if percent >= 75:
        return ORANGE
    if percent >= 50:
        return YELLOW
    return GREEN


def render_bar(percent, color):
    """Bracketed bar with sub-cell precision, e.g. [███▍        ]."""
    cells = max(0.0, min(100.0, percent)) / 100 * BAR_WIDTH
    filled = min(int(cells), BAR_WIDTH)
    fraction = int((cells - filled) * (len(PARTIAL_BLOCKS) - 1)) if filled < BAR_WIDTH else 0
    partial = PARTIAL_BLOCKS[fraction].strip() or ("▏" if 0 < percent and not filled else "")
    track = "░" * (BAR_WIDTH - filled - len(partial))
    return f"{LABEL}[{color}{'█' * filled}{partial}{EMPTY_TRACK}{track}{LABEL}]{RESET}"


def format_countdown(resets_at):
    """Epoch seconds -> compact time-left string, or '' when unknown/past."""
    if not resets_at:
        return ""
    left = int(resets_at - time.time())
    if left <= 0:
        return ""
    days, hours, minutes = left // 86400, left % 86400 // 3600, left % 3600 // 60
    if days:
        return f"{days}d{hours}h"
    return f"{hours}h{minutes:02d}m" if hours else f"{minutes}m"


def render_gauge(label, percent, resets_at=None):
    """One labelled bar segment: name, bar, percentage and optional countdown."""
    color = color_for(percent)
    countdown = format_countdown(resets_at)
    tail = f" {LABEL}{countdown}{RESET}" if countdown else ""
    return f"{LABEL}{label}{RESET} {render_bar(percent, color)} {color}{percent:.0f}%{RESET}{tail}"


def context_percent(payload):
    window = payload.get("context_window") or {}
    if window.get("used_percentage") is not None:
        return float(window["used_percentage"])
    size = window.get("context_window_size") or 0
    return float(window.get("total_input_tokens", 0)) / size * 100 if size else 0.0


def format_cost(payload):
    """Session spend so far, e.g. $0.35 — sub-cent runs collapse to $0.00."""
    spent = (payload.get("cost") or {}).get("total_cost_usd") or 0
    return f"${spent:.2f}"


def format_tokens(payload):
    """Token count backing the context bar, e.g. 15.5k tok / 1.2M tok."""
    window = payload.get("context_window") or {}
    total = float(window.get("total_input_tokens", 0)) + float(window.get("total_output_tokens", 0))
    if total >= 1_000_000:
        return f"{total / 1_000_000:.1f}M tok"
    if total >= 1_000:
        return f"{total / 1_000:.1f}k tok"
    return f"{int(total)} tok"


def build_segments(payload):
    segments = [f"{BOLD_WHITE}{payload.get('model', {}).get('display_name', 'claude')}{RESET}"]
    segments.append(render_gauge("ctx", context_percent(payload)))
    limits = payload.get("rate_limits") or {}
    for key, label in (("five_hour", "5h"), ("seven_day", "weekly")):
        window = limits.get(key)
        if window:
            segments.append(render_gauge(label, float(window.get("used_percentage", 0)), window.get("resets_at")))
    segments.append(f"{LABEL}{format_tokens(payload)}{RESET}")
    segments.append(f"{COST_STYLE}{format_cost(payload)}{RESET}")
    return segments


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    sys.stdout.write("  ".join(build_segments(payload)))


if __name__ == "__main__":
    main()
