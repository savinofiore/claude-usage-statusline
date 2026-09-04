# claude-usage-statusline

A single-file, dependency-free status line for [Claude Code](https://claude.com/claude-code) that shows model, context usage, 5-hour and weekly rate-limit windows, token count and session cost — all on one line.

![demo](demo.png)

```
Sonnet 5  ctx [            ]  0%   5h [██████      ] 26%  3h28m   weekly [████████    ] 44%  16h28m   0 tok  $0.00
```

## Requirements

- Python 3 (stdlib only, no `pip install` needed)
- Claude Code with statusline support

## Install

```bash
curl -fsSL -o ~/.claude/hooks/usage-statusline.py \
  https://raw.githubusercontent.com/savinofiore/claude-usage-statusline/main/usage-statusline.py
chmod +x ~/.claude/hooks/usage-statusline.py
```

Then add this to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/hooks/usage-statusline.py"
  }
}
```

Restart Claude Code (or start a new session) to see it.

## How it works

Claude Code pipes a JSON payload (model info, context window, rate limits, cost) to the statusline command on stdin. The script reads it and prints one ANSI-colored line: bars turn green → yellow → orange → red as each budget fills up.

## License

MIT — see [LICENSE](LICENSE).
