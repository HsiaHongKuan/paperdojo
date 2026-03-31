---
name: paperdojo
description: Use when implementing or running the PaperDojo workflow — a daily Socratic paper-reading coach that fetches arxiv papers, guides users to solve problems before revealing solutions, and tracks thinking progress over time.
---

# PaperDojo

A daily thinking exercise (思维体操) built on arxiv paper feeds. Instead of passively reading, you see the problem first, try to solve it with an AI coach, then compare with the authors' approach.

## Command Surface

| Command | Role | Notes |
|---|---|---|
| `/feed` | Interactive paper picker → launches `/coach` | Entry point for daily sessions |
| `/coach <arxiv_id>` | Socratic session + auto session report | Works standalone, no `/feed` required |
| `/report` | Historical dashboard (all past sessions) | Reads `.paperdojo/history/` |
| `/setup` | Preferences & MCP config | Optional — smart defaults apply without it |

**`/ideate` is a mode inside `/coach`**, not a standalone command. Type `/ideate` during a session to enter blind brainstorm mode; type it again to return to coached mode.

## `/coach` Session Lifecycle

```
/coach <arxiv_id>
│
├── 1. Read paper via arxiv-latex-mcp
│        Extract → background + problem  (shown to user)
│                → solution              (written to .paperdojo/session.md — NEVER in conversation)
│
├── 2. Socratic loop
│        User explores / proposes
│        ├── asks question    → hint, nudge, navigate related concept
│        ├── types /ideate    → enter blind brainstorm mode
│        │                       agent also loses solution access
│        │                       type /ideate again to exit
│        └── submits answer / "I give up"
│
├── 3. Reveal
│        Read .paperdojo/session.md, compare with user's attempt
│        Discuss differences and key insights
│
└── 4. Session report (automatic)
         - Solve quality rating
         - Reasoning gaps identified
         - Key concepts to revisit
         - Append to .paperdojo/history/YYYY-MM-DD-<arxiv_id>.json
```

**Solution isolation rule:** The solution is written to `.paperdojo/session.md` at step 1 and only re-read at step 3. It must never appear in the conversation context between those two points.

## `/feed` Interactive Picker

1. Fetch today's papers from arxiv using user's configured categories (default: `cs.AI`)
2. Rank by scirate scites if available; fallback to Semantic Scholar citation count or recency + abstract relevance
3. Present papers one by one:

```
[1/5] "Quantum error correction via..."
Authors: X, Y, Z  |  quant-ph  |  ★ 12

The authors tackle the problem of... (2-sentence intro, NO solution hinted)

[s] Start session   [n] Next   [q] Quit
```

4. On `[s]` → immediately launch `/coach <arxiv_id>`
5. Save seen/skipped papers to `.paperdojo/feed_history.json` (no repeats unless reset)

## `/report` — Historical Dashboard

Reads all `.paperdojo/history/*.json` files and generates `.paperdojo/report.html`:

- Activity heatmap (sessions per day/week)
- Solve rate by field (quant-ph, cs.DS, etc.)
- Thinking pattern trends (e.g. "tends to skip constraint formalization")
- Papers solved vs given up
- Top concepts revisited across sessions

Open `report.html` in browser after generation.

## `/setup` — Optional Config

Prompts for and writes `.paperdojo/config.yml`:

```yaml
categories: [cs.AI, quant-ph]     # arxiv categories to follow
keywords: []                        # optional keyword filters
difficulty: medium                  # hint style: gentle / medium / direct
schedule: weekdays                  # daily / weekdays / custom
session_duration: 30                # target minutes
```

If config does not exist, defaults above apply silently.

## Persistence Structure

```
.paperdojo/
├── config.yml                           # user preferences
├── feed_history.json                    # seen/skipped arxiv IDs
├── session.md                           # active session scratch (solution isolated here)
└── history/
    └── YYYY-MM-DD-<arxiv_id>.json       # one record per completed session
```

Add `.paperdojo/` to `.gitignore`.

## Dependencies

- `arxiv-mcp-server` — paper search and metadata
- `arxiv-latex-mcp` — full paper content (required for `/coach`)
- Semantic Scholar API — fallback ranking in `/feed`
- [cryochamber](https://github.com/GiggleLiu/cryochamber) — optional persistent agent scheduling

## Long-term Vision

Run `/ideate` with AI as the student against `/coach` as the examiner — polish adversarially until agents can propose solutions comparable to the paper's without ever seeing it. A step toward automated research ideation benchmarking.
