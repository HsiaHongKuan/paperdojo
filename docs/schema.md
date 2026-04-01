# PaperDojo Data Schema

Shared data formats flowing between `/feed`, `/coach`, and `/report`.

## Feed record — `.paperdojo/feeds/YYYY-MM-DD.json`

Written by `/feed`. Read by `/report`.

```json
{
  "date": "YYYY-MM-DD",
  "papers": [
    {
      "arxiv_id": "2603.12345",
      "title": "Paper title",
      "categories": ["cond-mat.mes-hall", "cond-mat.str-el"],
      "action": "skipped | coached | seen",
      "details_viewed": false
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `arxiv_id` | string | Arxiv paper ID (e.g., `"2603.12345"`) |
| `title` | string | Paper title |
| `categories` | string[] | Arxiv categories |
| `action` | string | `"skipped"` (user pressed [n]), `"coached"` (user pressed [s]), `"seen"` (user pressed [q] while viewing) |
| `details_viewed` | bool | Whether the user pressed [d] to view details |

## Coaching session — `.paperdojo/history/YYYY-MM-DD-<arxiv_id>.json`

Written by `/coach`. Read by `/report`.

```json
{
  "arxiv_id": "2603.12345",
  "title": "Paper title",
  "date": "YYYY-MM-DD",
  "source": "feed | direct",
  "insight": "captured | missed",
  "approach": "aligned | divergent",
  "conversation": [
    {"role": "coach", "content": "..."},
    {"role": "user", "content": "..."}
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `source` | string | `"feed"` if handed off from `/feed`, `"direct"` if user ran `/coach` directly |
| `insight` | string | `"captured"` if user identified the core conceptual insight, `"missed"` otherwise |
| `approach` | string | `"aligned"` if user proposed the right method/technique, `"divergent"` otherwise |
| `conversation` | object[] | Reconstructed coaching conversation |

## Report data — `.paperdojo/report.json`

Written by `/report` analysis step. Read by `scripts/generate_report.py`.

```json
{
  "extractions": {
    "<session-id>": {
      "trigger_reactions": [
        {"name": "verb phrase", "trigger": "...", "reaction": "..."}
      ],
      "key_moment": "one sentence",
      "stuck_on": "one sentence or null",
      "insight": "captured | missed",
      "approach": "aligned | divergent"
    }
  },
  "synthesis": {
    "at_a_glance": {
      "opening": "casual coach greeting",
      "sharpest": "strength highlight",
      "stretch": "growth nudge",
      "try_next": "directional suggestion"
    },
    "coaching_patterns": "markdown",
    "thinking_patterns": "markdown",
    "best_moments": "markdown",
    "stuck_points": "markdown",
    "topics_to_revisit": "markdown"
  }
}
```

Session ID format: `YYYY-MM-DD-<arxiv_id>` (matches history filename without `.json`).

## User config — `.paperdojo/interests.toml`

Written by `/setup` or `/feed` inline setup. Read by all skills.

```toml
[user]
background = "optional, only if naturally shared"

[coaching]
difficulty = "guided | balanced | sink-or-swim"
hint_style = "questioning | pointing | telling"

[interests."<arxiv-category>"]
topics = ["topic1", "topic2"]
focus = "optional focus description"
```
