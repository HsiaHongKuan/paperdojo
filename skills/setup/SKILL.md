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

### Step 1: Research interests (freeform)

Ask the user what they work on or care about, in their own words. Be warm and a bit humorous — this is a first date with their paper coach. Do NOT list arxiv category codes or assume the user knows them.

### Step 2: Map to arxiv categories

Based on the user's description, suggest relevant arxiv categories. Present as a table with the full category name and a brief reason why it matches. Ask if they want to add or remove any.

### Step 3: Topics and focus (per category)

For each confirmed category, ask what specific topics interest them and what angle they care about. Use **bold** for category names and `code` for arxiv codes to make the output scannable. Illustrate the format with a playful, obviously-not-real example (e.g., topics: "time-traveling qubits", focus: "ones that arrive before they leave"). Focus is optional — don't push if the user doesn't have one.

### Step 4: Coaching preferences

Ask:

> Coaching preferences (defaults in brackets):
> - Difficulty: how aggressive should hints be? [medium] (gentle / medium / direct)
> - Hint style: [socratic] (socratic / nudge / direct)
>
> Press enter to accept defaults, or specify your preferences.

### Step 5: Write config

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

### Step 6: MCP server check

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
