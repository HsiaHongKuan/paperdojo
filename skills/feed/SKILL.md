---
name: feed
description: Daily arxiv paper feed — fetches and ranks papers by relevance to your research interests, with interactive browsing and optional deep-dive into paper details.
---

# /feed — Daily Paper Feed

## Entry

- `/feed` — browse today's ranked paper feed (default flow, starts at Step 1).
- `/feed <arxiv_id>` — look up a specific paper. Skips fetch+rank, goes straight to that paper.

## Lookup Mode

When an arxiv ID is provided (e.g., `/feed 2603.12345`):

1. **Config check** — same as Step 1 below. Interests are needed for calibrating details.

2. **Fetch paper metadata** — dispatch a subagent:

   ```
   description: "Fetch arxiv paper metadata"
   prompt: |
     Fetch metadata for arxiv paper {arxiv_id} using WebFetch:

     URL: `https://export.arxiv.org/api/query?id_list={arxiv_id}`

     Parse the Atom XML. Extract: arxiv ID, title, authors, abstract, categories.

     Return in this format:

     ARXIV_ID: <id>
     TITLE: <title>
     AUTHORS: <authors>
     ABSTRACT: <abstract>
     CATEGORIES: <categories>

     Do not interact with the user.
   ```

3. **Check for existing session** — read `.paperdojo/history/` for any file matching `*-{arxiv_id}.json`. If a coaching session exists, add `[r] Session report` to the actions.

4. **Present the paper** — same format as Step 3 browse, with interest-matching terms bolded:

   ```
   "{title}"
   {arxiv_id}  |  {authors}  |  {primary_category}

   {abstract with interest-matching terms bolded}

   [d] Details  [s] Start /coach  [r] Session report  [q] Done
   ```

   Omit `[r]` if no coaching session exists for this paper.

5. **Handle actions:**
   - `[d]` — same as Step 3's `[d]` Details.
   - `[s]` — record as `"action": "coached"` in feed file, hand off to `/coach {arxiv_id}`.
   - `[r]` — generate a single-paper session report (see [Session Report](#session-report) below).
   - `[q]` — record as `"action": "seen"` in feed file, done.

   After `[d]`, re-prompt without `[d]`. After `[r]`, re-prompt with remaining actions.

Record the paper in `.paperdojo/feeds/YYYY-MM-DD.json` same as the browse flow.

---

## Session Report

Generate the HTML session report by running `scripts/generate_session_report.py` — same as `/coach` does at the end of a session:

```bash
python3 scripts/generate_session_report.py {arxiv_id}
open .paperdojo/session-report-{arxiv_id}.html   # macOS
```

Report: "Session report opened in your browser."

---

## Step 1: Config Check

Read `.paperdojo/interests.toml`.

**If missing or has no `[interests.*]` sections:** run a lightweight inline setup. Walk through each step one at a time — wait for the user's reply before moving to the next step. Skip coaching preferences (use defaults).

1. **Research area** — Tell the user you need to know their research area to find relevant papers. Ask them to describe what they work on or care about, in their own words — e.g., "I study topological phases in condensed matter" or "I work on LLM reasoning and alignment." Be warm and humorous — they came for papers, not a form.

2. **Confirm arxiv categories** — Based on their description, map to arxiv categories. Present as a table with the category code, full name, and why it matches. Explicitly ask: "Want to add or remove any of these?"

3. **Topics and focus** — Explain that topics are specific keywords used to rank papers within their categories, and focus is an optional narrower lens. Give a concrete, playful example: e.g., topics: `["time-traveling qubits", "retrocausal entanglement"]`, focus: `"ones that arrive before they leave"`. Ask: "What specific topics should I prioritize? And optionally, any particular focus or angle?" Make clear that focus is optional.

4. **Write config** — Write `.paperdojo/interests.toml` with defaults for `[coaching]`. Distribute topics to categories where they naturally belong — don't copy all topics to all categories. Create directories: `mkdir -p .paperdojo/feeds .paperdojo/history`. Confirm to the user: "Config saved — fetching your first feed now."

Then continue to Step 2.

**If exists and has interests:** continue to Step 2.

## Step 2: Fetch + Rank

Read `.paperdojo/interests.toml` to get the user's interests.

Read all files in `.paperdojo/feeds/` to collect previously seen arxiv IDs (all `arxiv_id` values from all feed records). These must be excluded from results.

### Fetch papers

Two tiers depending on what's available:

**Fast path (arxiv-mcp-server installed):** Call `search_papers` MCP tool directly from the main agent:
- `categories`: list of categories from interests (e.g. `["quant-ph", "cond-mat.str-el"]`)
- `sort_by`: `"date"`
- `max_results`: 30

This returns structured JSON — no XML parsing needed.

**Fallback (no MCP):** Dispatch a subagent to fetch via WebFetch in a single request:

```
description: "Fetch arxiv papers"
prompt: |
  Fetch recent papers from the arxiv API in a SINGLE request combining all categories with OR. Use WebFetch:

  URL: `https://export.arxiv.org/api/query?search_query=cat:{cat1}+OR+cat:{cat2}+OR+cat:{cat3}&sortBy=submittedDate&sortOrder=descending&max_results=30`

  Categories: {list categories here}

  Parse the Atom XML response. Extract for each paper: arxiv ID (just the ID part, e.g., "2603.12345"), title, authors, abstract, categories.

  Return results in this format (one per block, separated by ---):

  ARXIV_ID: <id>
  TITLE: <title>
  AUTHORS: <authors>
  ABSTRACT: <abstract>
  CATEGORIES: <categories>
  ---

  Do not score or rank. Just fetch and extract. Do not interact with the user.
```

### Rank papers

After fetching (either path), remove previously seen arxiv IDs, then dispatch a ranking subagent:

```
description: "Rank arxiv papers by relevance"
prompt: |
  You are a paper ranking agent. Score and rank these papers by relevance to the user's research interests.

  ## User's interests

  <interests>
  {paste the full contents of interests.toml here}
  </interests>

  ## Papers to rank

  {paste the fetched papers here}

  ## Instructions

  1. Score each paper on two axes:
     - **Niche relevance** (0-10): how well it matches the user's specific topics and focus
     - **Field significance** (0-10): based on abstract language (strong claims, broad impact), cross-listing in multiple categories, and your knowledge of the field (major groups, trending directions)

  2. Rank by combined score. Return the top 5-10 papers.

  3. Return in this exact format (one per block, separated by ---):

     ARXIV_ID: <id>
     TITLE: <title>
     AUTHORS: <authors>
     ABSTRACT: <abstract>
     CATEGORIES: <categories>
     ---

     Papers must be in ranked order (best first). Do not include scores in the output.

  Do not interact with the user. Just score, rank, and return.
```

Parse the subagent's response to extract the ranked paper list. The scores are for internal ranking only — do NOT show them to the user.

If the subagent returns no papers, ask the user what they'd like to do. Do not provide hardcoded fallback suggestions.

## Step 3: Interactive Browse

Present papers one at a time. Track a `details_viewed` flag per paper, initially `false`.

For each paper, display with **bold** highlighting on key terms that match the user's interests (from `interests.toml` topics):

```
[{index}/{total}] "{title}"
{arxiv_id}  |  {authors}  |  {primary_category}  |  {date}

{abstract with interest-matching terms bolded}

[d] Details  [n] Next  [s] Start /coach  [r] Session report  [q] Quit
```

Only show `[r]` if a coaching session exists for the current paper (check `.paperdojo/history/` for `*-{arxiv_id}.json`).

### On `[n]` (Next)

Immediately append to `.paperdojo/feeds/YYYY-MM-DD.json`:

```json
{"arxiv_id": "<id>", "title": "<title>", "categories": ["<cat1>", "<cat2>"], "action": "skipped", "details_viewed": false}
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

If yes, install via local venv:
```bash
python3 -m venv .paperdojo/venv
.paperdojo/venv/bin/pip install arxiv-latex-mcp
claude mcp add -s project arxiv-latex-mcp -- .paperdojo/venv/bin/python -m arxiv_latex_mcp
```

If the user declines, fall back to presenting a more detailed abstract analysis.

If available (or after install), dispatch a details subagent:

```
description: "Fetch paper intro details"
prompt: |
  Fetch the full content of arxiv paper {arxiv_id} using the arxiv-latex-mcp tool `get_paper_prompt`. Use ONE call — do not use list_paper_sections or get_paper_section.

  The user's background: {paste [user] section from interests.toml, or "not specified"}

  From the returned content, find the introduction and problem setup (may be labeled "Introduction", "I. Introduction", or use inline markers like "Introduction.---"). Extract a SOLVABLE PROBLEM STATEMENT — not a paper summary, but enough context for someone to start forming their own approach. Include:
  - The specific setup and constraints (e.g., what system, what regime, finite or infinite, what assumptions)
  - The precise question or gap: what exactly is unknown, unproven, or unsolved
  - Why naive approaches fail or why this is non-trivial
  - Any key prior results that frame the problem

  Calibrate the level of detail to the user's background — skip definitions they'd know, but include specifics they'd need to think about the problem.

  CRITICAL: Do NOT include anything about the authors' solution or approach. Truncate at any "we show", "we propose", "we prove", "in this paper, we", "our approach", "our method", or similar solution-hinting language.

  Return a thorough overview — this is the user's main window into the paper before deciding to coach. Be detailed and precise, not terse. Adapt to the paper's nature:
  - If the paper has a clear problem/gap: cover the setting in detail, the specific gap, why it's hard (what makes naive approaches fail), what's known so far, and key prior results
  - If not (review, experimental report, benchmark): cover the context, what they do, key findings, and significance

  Each bullet point should be a full sentence or two, not a fragment.
```

Present the subagent's output in a Unicode box titled "Overview" using box-drawing characters (┌─┐│└─┘). Bold key terms. Use bullet points for structure:

```
┌─ Overview ────────────────────────────────────────
│
│ - ...detailed point...
│ - ...detailed point...
│ - ...detailed point...
│
└────────────────────────────────────────────────────
```

Then re-prompt with:

```
[n] Next  [s] Start /coach  [q] Quit
```

(No `[d]` — details already viewed.)

### On `[r]` (Session report)

Generate the session report for this paper (see [Session Report](#session-report) above). After displaying the report, re-prompt with the current paper's remaining actions (exclude `[r]` since it was just shown).

### On `[s]` (Start /coach)

Immediately append to `.paperdojo/feeds/YYYY-MM-DD.json`:

```json
{"arxiv_id": "<id>", "title": "<title>", "categories": ["<cat1>", "<cat2>"], "action": "coached", "details_viewed": <true|false>}
```

(Same file read-append-write as `[n]`.)

Report the feed summary (same as `[q]`), then announce:

> Starting coaching session for "{title}" ({arxiv_id})...

Hand off to `/coach {arxiv_id}`. The conversation transitions to the coaching flow.

### On `[q]` (Quit)

Record the currently displayed paper (if any) as `"action": "seen"` — the user saw it but made no decision.

Report:

> Feed session complete. {N} papers browsed, {M} skipped, {K} coached.

Done.
