---
name: feed
description: Daily arxiv paper feed — fetches and ranks papers by relevance to your research interests, with interactive browsing and optional deep-dive into paper details.
---

# /feed — Daily Paper Feed

## Step 1: Config Check

Read `.paperdojo/interests.toml`.

**If missing or has no `[interests.*]` sections:** run a lightweight inline setup (same interactive style as `/setup`, skip coaching preferences — use defaults):

1. Ask what they work on or care about, in their own words. Be warm and humorous — they came for papers, not a form.
2. Map their description to arxiv categories. Present as a table with full names and why each matches. Let them adjust.
3. Ask about topics and focus once (not per-category — interests often span multiple categories). Show a playful non-real example for the format. Focus is optional.
4. Write `.paperdojo/interests.toml` with defaults for `[coaching]`. Create directories: `mkdir -p .paperdojo/feeds .paperdojo/history`

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

For each paper, display:

```
[{index}/{total}] "{title}"
Authors: {authors}  |  {primary_category}  |  {date}

{abstract}

[d] Details  [n] Next  [s] Start /coach  [q] Quit
```

### On `[n]` (Next)

Immediately append to `.paperdojo/feeds/YYYY-MM-DD.json`:

```json
{"arxiv_id": "<id>", "title": "<title>", "action": "skipped", "details_viewed": false}
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

  From the returned content, find the introduction (may be labeled "Introduction", "I. Introduction", or use inline markers like "Introduction.---"). Extract:
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
