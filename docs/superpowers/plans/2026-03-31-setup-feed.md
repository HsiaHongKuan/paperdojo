# `/setup` + `/feed` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `/setup` and `/feed` as Claude Code skill files that guide the LLM through interactive paper configuration and daily arxiv paper browsing.

**Architecture:** Two skill files (`setup.md`, `feed.md`) under `.claude/skills/paperdojo/`, plus an updated `SKILL.md` router. Skills are LLM instruction documents — no application code. Persistence uses `.paperdojo/interests.toml` and `.paperdojo/feeds/*.json`. Paper fetching uses the arxiv Atom API via `WebFetch`; details use `arxiv-latex-mcp` via subagent.

**Tech Stack:** Claude Code skills (markdown), arxiv Atom API, `arxiv-latex-mcp` MCP server (optional)

---

### Task 1: Write `setup.md` skill file

**Files:**
- Create: `.claude/skills/paperdojo/setup.md`

- [ ] **Step 1: Write the skill file**

Create `.claude/skills/paperdojo/setup.md` with the following content:

```markdown
---
name: setup
description: Configure PaperDojo — set research interests, coaching preferences, and install MCP servers. Optional — /feed can bootstrap itself without /setup.
---

# /setup — PaperDojo Configuration

## Determine Mode

Read `.paperdojo/interests.toml`.

- **File exists:** go to [Returning User](#returning-user)
- **File missing:** go to [First Run](#first-run)

## First Run

Walk the user through setup one question at a time.

### Step 1: Research categories

Ask the user which arxiv categories they follow. Present common examples for reference:

```
Common arxiv categories:
  Physics: quant-ph, cond-mat, hep-th, gr-qc
  CS: cs.AI, cs.DS, cs.LG, cs.CL, cs.CC
  Math: math.CO, math-ph, math.QA
  Other: stat.ML, eess.SP

Full list: https://arxiv.org/category_taxonomy

What arxiv categories are you interested in?
```

### Step 2: Topics and focus (per category)

For each category the user provided, ask:

> For **[category]**: what specific topics are you interested in, and what's your focus? (e.g., topics: "quantum error correction, topological codes", focus: "new code constructions and threshold results")

The user can answer both in one message or separately. If they give only topics without a focus, that's fine — focus is optional.

### Step 3: Coaching preferences

Ask:

> Coaching preferences (defaults in brackets):
> - Difficulty: how aggressive should hints be? [medium] (gentle / medium / direct)
> - Hint style: [socratic] (socratic / nudge / direct)
>
> Press enter to accept defaults, or specify your preferences.

### Step 4: Write config

Create `.paperdojo/` directory structure and write `interests.toml`:

```toml
[coaching]
difficulty = "<user_choice>"
hint_style = "<user_choice>"

[interests.<category>]
topics = [<user_topics>]
focus = "<user_focus>"
```

Use the Write tool to create `.paperdojo/interests.toml`.
Use Bash to create directories: `mkdir -p .paperdojo/feeds .paperdojo/history`

### Step 5: MCP server check

Check if `arxiv-latex-mcp` is available by attempting to use one of its tools.

- **Available:** report "arxiv-latex-mcp is ready."
- **Not available:** ask the user:

> arxiv-latex-mcp is needed for viewing paper details and coaching sessions. Install now? [y/n]

If yes, run:
```bash
npx -y @anthropic-ai/claude-code mcp add arxiv-latex-mcp -- npx -y arxiv-latex-mcp
```

Report setup complete. Summarize what was configured.

## Returning User

### Step 1: Present current config

Read `.paperdojo/interests.toml` and present it as a formatted table:

```
Current PaperDojo configuration:

Coaching: difficulty=medium, hint_style=socratic

Interests:
  quant-ph
    Topics: quantum error correction, topological codes
    Focus: new code constructions and threshold results
  cs.DS
    Topics: graph algorithms, approximation
    Focus: sublinear time algorithms
```

### Step 2: Ask for updates

> Want to update anything? You can:
> - Add/remove a category
> - Update topics or focus for a category
> - Change coaching preferences
> - Check MCP server status
>
> Or type "done" if everything looks good.

If the user wants changes, walk through them interactively. After each change, update `interests.toml` and re-present the table.

### Step 3: MCP check

Same as First Run Step 5.
```

- [ ] **Step 2: Verify the skill loads**

Run `/setup` in Claude Code in this project. Verify:
- The skill is listed in available skills
- Invoking it starts the interactive setup flow

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/paperdojo/setup.md
git commit -m "Add /setup skill — interactive PaperDojo configuration"
```

---

### Task 2: Write `feed.md` skill file

**Files:**
- Create: `.claude/skills/paperdojo/feed.md`

- [ ] **Step 1: Write the skill file**

Create `.claude/skills/paperdojo/feed.md` with the following content:

```markdown
---
name: feed
description: Daily arxiv paper feed — fetches and ranks papers by relevance to your research interests, with interactive browsing and optional deep-dive into paper details.
---

# /feed — Daily Paper Feed

## Step 1: Config Check

Read `.paperdojo/interests.toml`.

**If missing or has no `[interests.*]` sections:** ask the user inline:

> What arxiv categories are you interested in? (e.g., quant-ph, cs.AI, cs.DS)

Then for each category:

> For **[category]**: what specific topics and focus? (e.g., topics: "quantum error correction", focus: "threshold results")

Write `.paperdojo/interests.toml` with the answers (use defaults for `[coaching]` section). Create directories: `mkdir -p .paperdojo/feeds .paperdojo/history`

Then continue to Step 2.

**If exists and has interests:** continue to Step 2.

## Step 2: Fetch + Rank (Subagent)

Read `.paperdojo/interests.toml` to get the user's interests.

Read all files in `.paperdojo/feeds/` to collect previously seen arxiv IDs (all `arxiv_id` values from all feed records). These must be excluded from results.

Dispatch a subagent with the Agent tool:

```
prompt: |
  You are a paper ranking agent. Your job is to fetch recent arxiv papers and rank them by relevance to the user's research interests.

  ## User's interests

  <interests>
  {paste the full contents of interests.toml here}
  </interests>

  ## Previously seen papers (exclude these)

  {list of arxiv IDs to exclude, or "none" if empty}

  ## Instructions

  1. For each category in the user's interests, fetch recent papers from the arxiv API using WebFetch:

     URL: `https://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results=20`

  2. Parse the Atom XML response. Extract for each paper: arxiv ID (from <id> tag — extract just the ID part, e.g., "2603.12345"), title, authors, abstract, categories.

  3. Remove any papers whose arxiv ID is in the exclusion list.

  4. Score each remaining paper on two axes:
     - **Niche relevance** (0-10): how well it matches the user's specific topics and focus for its category
     - **Field significance** (0-10): based on abstract language (strong claims, broad impact), cross-listing in multiple categories, and your knowledge of the field (major groups, trending directions)

  5. Rank by combined score. Return the top 5-10 papers.

  6. Report results in this exact format (one paper per block, separated by ---):

     ```
     ARXIV_ID: <id>
     TITLE: <title>
     AUTHORS: <authors>
     ABSTRACT: <abstract>
     CATEGORIES: <categories>
     RELEVANCE: <score>/10
     SIGNIFICANCE: <score>/10 — <brief note why>
     ---
     ```

  Do not interact with the user. Just fetch, score, and return results.
```

Parse the subagent's response to extract the ranked paper list.

If the subagent returns no papers, ask the user what they'd like to do (e.g., broaden categories, try different keywords). Do not provide hardcoded suggestions.

## Step 3: Interactive Browse

Present papers one at a time. Track a `details_viewed` flag per paper, initially `false`.

For each paper, display:

```
[{index}/{total}] "{title}"
Authors: {authors}  |  {primary_category}  |  {date}
Relevance: {relevance}/10  |  Significance: {significance}/10 — {note}

{abstract}

[d] Details  [n] Next  [s] Start /coach  [q] Quit
```

### On `[n]` (Next)

Immediately append to `.paperdojo/feeds/YYYY-MM-DD.json`:

```json
{"arxiv_id": "<id>", "title": "<title>", "action": "skipped", "details_viewed": <true|false>}
```

If the feed file doesn't exist yet, create it with structure:
```json
{
  "date": "YYYY-MM-DD",
  "papers": [<the entry above>]
}
```

If it exists, read it, append to the `papers` array, write back.

Show the next paper. If no more papers, report that all papers have been browsed.

### On `[d]` (Details)

Set `details_viewed = true` for this paper. Do NOT append to the feed record yet — `[d]` is a peek, not a decision.

Check if `arxiv-latex-mcp` is available. If not, ask:

> arxiv-latex-mcp is needed to fetch paper details. Install now? [y/n]

If the user declines, fall back to presenting a more detailed abstract analysis.

If available (or after install), dispatch a details subagent:

```
prompt: |
  Fetch the introduction section of arxiv paper {arxiv_id} using the arxiv-latex-mcp tools.

  Use `get_paper_section` or `list_paper_sections` + `get_paper_section` to find and retrieve the introduction.

  From the introduction, extract:
  - The problem being studied and its motivation
  - Key background concepts needed to understand the problem
  - What makes this problem hard or important

  CRITICAL: Do NOT include anything about the authors' solution or approach. Truncate at any "we show", "we propose", "we prove", "in this paper, we", "our approach", "our method", or similar solution-hinting language.

  Return a concise problem description (3-5 paragraphs).
```

Present the subagent's output, then re-prompt with:

```
[n] Next  [s] Start /coach  [q] Quit
```

(No `[d]` — details already viewed.)

### On `[s]` (Start /coach)

Immediately append to `.paperdojo/feeds/YYYY-MM-DD.json`:

```json
{"arxiv_id": "<id>", "title": "<title>", "action": "coached", "details_viewed": <true|false>}
```

(Same file read-append-write as `[n]`.)

Then announce:

> Starting coaching session for "{title}" ({arxiv_id})...

Hand off to `/coach {arxiv_id}`. The conversation transitions to the coaching flow. Unseen papers are not recorded and will reappear in the next `/feed` run.

### On `[q]` (Quit)

The feed record is already up to date (each action appends immediately). Report:

> Feed session complete. {N} papers browsed, {M} skipped, {K} coached.

Done.
```

- [ ] **Step 2: Verify the skill loads**

Run `/feed` in Claude Code in this project. Verify:
- The skill is listed in available skills
- Invoking it starts the config check / fetch flow

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/paperdojo/feed.md
git commit -m "Add /feed skill — daily arxiv paper browsing with ranked recommendations"
```

---

### Task 3: Update `SKILL.md` router

**Files:**
- Modify: `.claude/skills/paperdojo/SKILL.md`

- [ ] **Step 1: Update SKILL.md**

Replace the full content of `.claude/skills/paperdojo/SKILL.md` with:

```markdown
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

- `arxiv-latex-mcp` — needed for `/feed` details and `/coach`. Installed via `/setup` or just-in-time when needed.
- arxiv Atom API — used directly via WebFetch for paper search. No MCP needed.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/paperdojo/SKILL.md
git commit -m "Update SKILL.md — add command table and reference new skill files"
```

---

### Task 4: End-to-end test

- [ ] **Step 1: Test /setup first-run flow**

Run `/setup` with no `.paperdojo/` directory. Walk through:
1. Provide categories (e.g., `quant-ph, cs.DS`)
2. Provide topics and focus for each
3. Accept default coaching preferences
4. Verify `.paperdojo/interests.toml` was created correctly
5. Verify `.paperdojo/feeds/` and `.paperdojo/history/` directories exist

- [ ] **Step 2: Test /setup returning-user flow**

Run `/setup` again. Verify:
1. Current config is presented as a table
2. Can update a category's topics
3. Changes are persisted to `interests.toml`

- [ ] **Step 3: Test /feed flow**

Run `/feed`. Verify:
1. Reads interests from `interests.toml`
2. Subagent fetches and ranks papers
3. Papers are presented one at a time with `[d]/[n]/[s]/[q]` options
4. `[n]` appends to feed record and shows next paper
5. `[d]` fetches details (or asks to install MCP), then re-prompts without `[d]`
6. `[q]` exits cleanly
7. Feed record in `.paperdojo/feeds/YYYY-MM-DD.json` has correct entries with `details_viewed` flags

- [ ] **Step 4: Test /feed no-config bootstrap**

Delete `.paperdojo/interests.toml`. Run `/feed`. Verify it asks for interests inline, persists them, then continues to fetch papers.
