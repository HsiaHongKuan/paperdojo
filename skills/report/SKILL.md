---
name: report
description: Historical dashboard of PaperDojo coaching sessions — generates an HTML report with GitHub-style heatmap, stats, coaching patterns, and research insights.
---

# /report — Coaching Dashboard

## Step 1: Collect data

Read all files in `.paperdojo/feeds/` and `.paperdojo/history/`. Also read `.paperdojo/interests.toml` for context.

If no feed or history files exist, tell the user there's nothing to report yet — try `/feed` or `/coach` first.

## Step 2: Analyze coaching conversations

If no history files exist, skip this step — write `{"extractions": {}, "synthesis": {}}` to `.paperdojo/report.json`.

### Incremental caching

Read `.paperdojo/report.json` if it exists. Compare session IDs in `extractions` against files in `.paperdojo/history/`.

- **No new sessions:** skip to Step 3 — reuse existing `report.json`.
- **New sessions:** run Stage 1 only for the new ones, then re-run Stage 2 with all extractions.

### Stage 1: Per-session extraction

Dispatch one subagent per **new** coaching session in parallel. Each subagent receives `interests.toml` and one session file:

```
description: "Extract patterns from {paper_title}"
prompt: |
  Extract thinking patterns from this PaperDojo coaching session.

  ## User's interests
  <interests>
  {paste interests.toml contents}
  </interests>

  ## Session
  {paste one history JSON file}

  ## Instructions

  Return a JSON object:
  - "trigger_reactions": array of {trigger, reaction, name} — reasoning moves the user made. Name each with a verb phrase (e.g., "Kill the boring explanation first"). Only include genuine patterns, not routine steps.
  - "key_moment": the single most impressive or revealing moment — one sentence.
  - "stuck_on": what the user struggled with, if anything — one sentence. Null if none.
  - "insight": "captured" or "missed"
  - "approach": "aligned" or "divergent"

  Return ONLY the JSON object. No commentary.
```

Append the new extractions to the `extractions` dict in `report.json`, keyed by session ID (e.g., `"2026-03-28-2603.19247"`).

### Stage 2: Synthesis

Dispatch one subagent with **all** extractions (cached + new), plus `interests.toml` and activity metadata (dates active, gaps, session count):

```
description: "Synthesize coaching analysis"
prompt: |
  Synthesize a coaching analysis from individual session extractions.

  ## User's interests
  <interests>
  {paste interests.toml contents}
  </interests>

  ## Activity metadata
  Sessions: {count}, Dates: {date list}, Gaps: {any gaps > 2 days}

  ## Per-session extractions
  {paste all extractions, labeled by paper title and date}

  ## Instructions

  Produce a JSON object with these keys. Find cross-session patterns — a pattern must appear in 2+ sessions to be included. Be specific, reference actual papers.

  - "at_a_glance": object with four fields, written in a warm coach voice:
    - "opening": a casual 1-2 sentence greeting that reflects the user's recent activity pattern (streak, consistency, gaps) and overall performance. Be warm and encouraging — like a coach wrapping up the week. Examples: "5 sessions this week — nice streak! You're sharpest on the experimental transport papers." / "Welcome back! It's been a few days — ready for some sparring?"
    - "sharpest": 1-2 sentences on when the user's thinking is strongest. Link to deeper section.
    - "stretch": 1-2 sentences on growth areas, framed as a coach's gentle nudge. Constructive, not critical.
    - "try_next": 1 sentence directional nudge — point a direction without prescribing a specific paper or problem. Concrete suggestions go in "topics_to_revisit".
  - "coaching_patterns": markdown, 3-4 bullets on reasoning style across sessions.
  - "thinking_patterns": markdown with 3-4 named trigger→reaction patterns. Each as:
    ### Pattern: <verb phrase>
    **Trigger:** what situation triggers this
    **Reaction:** what the user does
    **Example:** concrete example from a specific paper
  - "best_moments": markdown, 3-4 bullets referencing specific papers.
  - "stuck_points": markdown, 2-3 bullets framed as growth areas.
  - "topics_to_revisit": markdown, 2-3 bullets.

  Return ONLY the JSON object. No commentary.
```

Write the final `report.json` with both `extractions` and `synthesis`:

```json
{
  "extractions": {
    "<session-id>": { ... },
    ...
  },
  "synthesis": {
    "at_a_glance": { ... },
    "coaching_patterns": "...",
    ...
  }
}
```

## Step 3: Generate report

```bash
python3 scripts/generate_report.py
```

The script reads `.paperdojo/report.json`, feeds, and history, then writes `.paperdojo/report.html`.

## Step 4: Open

```bash
open .paperdojo/report.html   # macOS
xdg-open .paperdojo/report.html   # Linux
```

Report: "Dashboard written to `.paperdojo/report.html` and opened in your browser."
