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

If yes, create a local venv and install:
```bash
python3 -m venv .paperdojo/venv
.paperdojo/venv/bin/pip install arxiv-latex-mcp
```

Then register via Claude Code CLI:
```bash
claude mcp add -s project arxiv-latex-mcp -- .paperdojo/venv/bin/python -m arxiv_latex_mcp
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
