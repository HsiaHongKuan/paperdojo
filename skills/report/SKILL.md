---
name: report
description: Historical dashboard of PaperDojo coaching sessions — generates an HTML report with GitHub-style heatmap, stats, coaching patterns, and research insights.
---

# /report — Coaching Dashboard

## Step 1: Collect data

Read all files in `.paperdojo/feeds/` and `.paperdojo/history/`. Also read `.paperdojo/interests.toml` for context.

If no feed or history files exist, tell the user there's nothing to report yet — try `/feed` or `/coach` first.

## Step 2: Analyze coaching conversations

If history files exist, dispatch a subagent to analyze the coaching conversations:

```
description: "Analyze coaching history"
prompt: |
  Analyze the user's PaperDojo coaching history and produce insights.

  ## User's interests

  <interests>
  {paste interests.toml contents}
  </interests>

  ## Coaching sessions

  {paste all history JSON files — full conversation for each}

  ## Instructions

  Produce a JSON object with these keys. Be specific — reference actual papers and moments. Keep each section concise (2-4 bullet points in markdown).

  - "at_a_glance": 2-3 sentence warm summary of the coaching journey so far.
  - "coaching_patterns": How the user approaches problems. Reasoning styles, solve rate trend.
  - "best_moments": Moments where the user's thinking was strong or novel. Reference paper titles.
  - "stuck_points": Recurring patterns where the user gets stuck. Frame as growth areas, not failures.
  - "topics_to_revisit": Based on missed insights, divergent approaches, and hints needed, suggest concepts to revisit.
  - "research_directions": Themes emerging across sessions. Connections between papers.

  Return ONLY the JSON object. No commentary.
```

Write the subagent's output to `.paperdojo/report_analysis.json`.

If no history files exist, skip this step (the report will show stats, heatmap, and word cloud without narrative sections).

## Step 3: Generate report

Run the report generator:

```bash
python3 scripts/generate_report.py
```

This reads feeds, history, and analysis data, then writes `.paperdojo/report.html`.

## Step 4: Open

```bash
open .paperdojo/report.html   # macOS
xdg-open .paperdojo/report.html   # Linux
```

Report: "Dashboard written to `.paperdojo/report.html` and opened in your browser."
