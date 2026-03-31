---
name: paperdojo
description: Use when implementing or running the PaperDojo workflow — a daily Socratic paper-reading coach that fetches arxiv papers, guides users to solve problems before revealing solutions, and tracks thinking progress over time.
---

# PaperDojo

A daily thinking exercise built on arxiv paper feeds. Instead of passively reading, see the problem first, try to solve it with an AI coach, then compare with the authors' approach.

## Commands

| Command | Skill file | Role |
|---|---|---|
| `/setup` | `setup.md` | Configure interests, coaching preferences, MCP servers. Optional — `/feed` bootstraps itself. |
| `/feed` | `feed.md` | Daily paper browsing with ranked recommendations. Interactive browse → details → coach handoff. |
| `/coach <arxiv_id>` | (not yet implemented) | Socratic coaching session for a specific paper. |
| `/report` | (not yet implemented) | Historical dashboard from past sessions. |

## Persistence

All state lives in `.paperdojo/` (gitignored):

```
.paperdojo/
├── interests.toml          # research interests + coaching preferences
├── session.md              # active /coach scratch (solution isolation)
├── feeds/
│   └── YYYY-MM-DD.json     # per-day feed records
└── history/
    └── YYYY-MM-DD-<id>.json  # per-session coach records
```

## Dependencies

- `arxiv-latex-mcp` — needed for `/feed` details and `/coach`. Installed via `/setup` or just-in-time into `.paperdojo/venv/`.
- arxiv Atom API — used directly via WebFetch for paper search. No MCP needed.
