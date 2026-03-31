# PaperDojo `/setup` + `/feed` Design Spec

## Overview

Two skills for the PaperDojo plugin: `/setup` (optional pre-configuration) and `/feed` (daily paper browsing with ranked recommendations). Both persist state to `.paperdojo/` and work together — `/feed` can bootstrap itself without `/setup`, but `/setup` provides a smoother first-run experience.

## Persistence Structure

```
.paperdojo/
├── interests.toml                    # interests + coaching prefs
├── session.md                        # active /coach scratch (temporary)
├── feeds/
│   └── 2026-03-31.json              # per-day feed record
└── history/
    └── 2026-03-31-2603.12345.json   # per-session coach record
```

### `interests.toml`

```toml
[coaching]
difficulty = "medium"        # gentle / medium / direct
hint_style = "socratic"      # socratic / nudge / direct

[interests.quant-ph]
topics = ["quantum error correction", "topological codes"]
focus = "new code constructions and threshold results"

[interests."cs.DS"]
topics = ["graph algorithms", "approximation"]
focus = "sublinear time algorithms"
```

Structured interests enable LLM-based relevance scoring — `focus` tells the subagent what aspect of a topic the user cares about, which flat keywords cannot express.

### Feed record (`feeds/YYYY-MM-DD.json`)

```json
{
  "date": "2026-03-31",
  "papers": [
    {"arxiv_id": "2603.12345", "title": "...", "action": "coached", "details_viewed": true},
    {"arxiv_id": "2603.12346", "title": "...", "action": "skipped", "details_viewed": false},
    {"arxiv_id": "2603.12347", "title": "...", "action": "skipped", "details_viewed": true}
  ]
}
```

Arxiv ID is the universal key across feeds, coach sessions, and the arxiv API. Feed records serve double duty: "no repeats" mechanism and data source for `/report`.

Multiple `/feed` runs per day append to the same day's record and exclude already-seen papers.

## `/setup` Skill

Interactive, one-question-at-a-time. Not a gate — purely a convenience.

### First run (no `interests.toml`)

1. Ask user's research field/categories (present arxiv category list for reference)
2. For each category: ask topics and focus (freeform)
3. Ask coaching preferences (difficulty, hint style) — offer defaults
4. Write `interests.toml`
5. Check if `arxiv-latex-mcp` is installed; if not, ask to install
6. Create `.paperdojo/` directory structure (`feeds/`, `history/`)

### Returning user (`interests.toml` exists)

1. Read `interests.toml`, present as a table
2. Ask: "Want to update anything?" — if yes, ask which section, edit interactively
3. Check MCP server status

## `/feed` Skill

### Step 1: Config check

Read `interests.toml`. If missing or empty, ask for categories + topics inline (same questions as `/setup` steps 1-2), persist, then continue. No redirect to `/setup`.

### Step 2: Fetch + rank (subagent)

Dispatch a subagent with:
- User's interests from `interests.toml`
- Past feed records from `feeds/` (arxiv IDs to exclude)

The subagent:
- Queries the arxiv Atom API (`export.arxiv.org/api/query`) per category via `WebFetch`
- Scores each paper on two axes:
  - **Niche relevance** — how well it matches the user's specific topics + focus
  - **Field significance** — detected via abstract language, cross-listings, and the LLM's own knowledge of the field (no hardcoded author lists)
- Returns top 5-10 papers ranked by combined score

Fetch up to 20 papers per category, score and return top 5-10.

No MCP servers needed for this step.

### Step 3: Interactive browse (main agent)

Present papers one at a time:

```
[1/7] "Quantum error correction via..."
Authors: X, Y, Z  |  quant-ph  |  2026-03-31

Abstract: ...

[d] Details  [n] Next  [s] Start /coach  [q] Quit
```

Each action immediately appends to `feeds/YYYY-MM-DD.json` — no batch save, so abrupt exits don't lose state.

Actions:
- `[n]` — append as `skipped`, show next paper
- `[d]` — does NOT record an action (it's a peek, not a decision). Dispatch details subagent to fetch intro section via `arxiv-latex-mcp`. Subagent extracts problem/motivation and truncates at any "we show/propose/prove" statements to avoid solution leakage. Present the result, then re-prompt with `[n] Next  [s] Start /coach  [q] Quit` (no `[d]`). If MCP not installed, ask to install just-in-time.
- `[s]` — append as `coached`, hand off to `/coach <arxiv_id>` (conversation transitions, no return to `/feed`). Unseen papers are not recorded and will reappear next `/feed` run.
- `[q]` — done (record already up to date)

## Subagent Contracts

### Feed ranking subagent

```
Input:
  interests  — parsed content of interests.toml
  exclude    — list of arxiv IDs from past feeds

Output:
  papers     — list of {arxiv_id, title, authors, abstract, categories,
                relevance_score, significance_note}
               ranked by combined score, max 10
```

Uses `WebFetch` to query the arxiv Atom API. The LLM scores relevance against interests and uses its own knowledge for field significance.

### Details subagent

```
Input:
  arxiv_id

Output:
  problem_description — extracted from intro section, solution-free
```

Uses `arxiv-latex-mcp`'s `get_paper_section` to fetch the introduction. Summarizes the problem and motivation without hinting at the solution.

## MCP Handling

`arxiv-latex-mcp` is the only MCP dependency.

- **Not needed for:** `/setup`, `/feed` browse (titles + abstracts)
- **Needed for:** `/feed` `[d]` details, `/coach`
- **Detection:** check if the MCP server is available in the current session
- **Just-in-time install:** when needed and missing, ask "arxiv-latex-mcp is required. Install now? [y/n]" — install, then continue. User stays in flow.
- **`/setup` pre-installs** so the user won't be interrupted later

## Skill File Structure

```
.claude/skills/paperdojo/
├── SKILL.md      # main skill (overview/router, existing, to be updated)
├── setup.md      # /setup interaction flow
└── feed.md       # /feed interaction flow
```

`SKILL.md` remains the overview. `setup.md` and `feed.md` contain the full interaction flow for each command.

## Edge Cases

- **Empty results:** If no papers match the user's interests today, ask the user what they'd like to do (broaden search, try different categories, etc.) — no hardcoded fallback.
- **Concurrent `/feed` sessions:** Not supported. Running two `/feed` sessions simultaneously may corrupt the feed record. Don't optimize for this.
- **Solution leakage in details:** The details subagent is instructed to extract problem/motivation only and truncate at solution-hinting language ("we show", "we propose", "we prove"). Soft guarantee — best effort, not cryptographic isolation.
