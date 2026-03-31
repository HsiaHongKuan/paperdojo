# PaperDojo `/coach` Design Spec

## Overview

`/coach <arxiv_id>` — the core Socratic coaching session. The user works through a paper's problem with guided hints before seeing the solution. Works standalone or as a handoff from `/feed`.

## Entry

Two paths:
- **From `/feed`** — user presses `[s]`, hands off to `/coach <arxiv_id>`. May have `[d]` details in context.
- **Direct** — user types `/coach 2603.28349`. No `/feed` required.

## Step 1: Read paper

Main agent reads the paper via `arxiv-latex-mcp` (`get_paper_prompt`). The paper stays in conversation context — the coach needs it for good hints and comparison. Disregard references, appendices, and supplementary material — only the main body matters for coaching.

**Fallback:** If LaTeX source is unavailable, fall back to `arxiv-mcp-server`'s `download_paper` (PDF → markdown). If neither MCP is available, prompt just-in-time install (same as `/feed`).

If coming from `/feed` with `[d]` details viewed, build on that description rather than generating from scratch. Otherwise, generate fresh.

## Step 2: Assess suitability

Before presenting the problem, assess whether the paper is suitable for coaching. A good coaching paper has a clear problem that can be worked through — not every paper qualifies.

**Not suitable:** review articles, pure experimental reports, incremental results with no clear "gap." Tell the user honestly and suggest trying another paper. Don't force a bad session.

**Suitable:** proceed to Step 3.

## Step 3: Present the problem

Three boxes using Unicode box-drawing characters (┌─┐│└─┘) with bold key terms:

- **Background** — what the user needs to know to understand the problem. Calibrated to user's background from `interests.toml` — skip definitions they'd know, include specifics they'd need.
- **Problem** — the precise question or gap. What exactly is unknown, unproven, or unsolved. Include specific setup and constraints.
- **What makes this hard** — why naive approaches fail, what makes this non-trivial.

Detailed enough to start thinking — not a paper summary.

**Solution isolation:** The full paper is in context. The coach must NOT reveal the solution, method names, specific results, or theorem statements from the paper. Guide without spoiling. This is a soft constraint enforced by skill instruction.

## Step 4: Socratic loop

Freeform conversation. Coach behavior driven by `interests.toml` coaching preferences:
- Difficulty: `guided` / `balanced` / `sink-or-swim`
- Hint style: `questioning` / `pointing` / `telling`

Behavior:
- User explores, proposes, asks questions
- Coach gives positive reinforcement when user's thinking touches ideas related to the paper's approach — guiding without revealing
- No formal "submit answer" step — user controls when to see the answer

## Step 5: Reveal

Triggered by user: "show me", "let me compare", "I give up", etc.

Coach presents the paper's approach, discusses differences with the user's thinking, highlights insights.

## Step 6: Save session

Write to `.paperdojo/history/YYYY-MM-DD-<arxiv_id>.json` after the session completes:

```json
{
  "arxiv_id": "2603.28349",
  "title": "The local characterization of global tensor network eigenstates",
  "date": "2026-04-01",
  "source": "feed",
  "outcome": "solved",
  "conversation": [
    {"role": "coach", "content": "..."},
    {"role": "user", "content": "..."}
  ]
}
```

- `source`: `"feed"` (from `/feed` handoff) or `"direct"` (standalone `/coach`)
- `outcome`: `"solved"` (user arrived at solution) or `"revealed"` (user asked to see answer)
- `conversation`: full chat history of the coaching session

## Dependencies

- `arxiv-latex-mcp` — primary method for reading the full paper. Fallback: `arxiv-mcp-server` `download_paper` (PDF → markdown).
- `.paperdojo/interests.toml` — for user background and coaching preferences. If missing, use defaults.
