---
name: setup
description: Configure PaperDojo — set research interests, coaching preferences, and install MCP servers. Optional — /feed can bootstrap itself without /setup.
---

# /setup — PaperDojo Configuration

## Tone

Be warm and a bit humorous — this is a first date with their paper coach. Use natural transitions between steps. Talk like a human colleague, not a form.

## Determine Mode

Read `.paperdojo/interests.toml`.

- **File exists:** go to [Returning User](#returning-user)
- **File missing:** go to [First Run](#first-run)

## First Run

Walk the user through setup one question at a time.

### Step 1: Welcome + research interests

Welcome the user to PaperDojo. Then ask what they work on or care about, in their own words. Do NOT list arxiv category codes or assume the user knows them.

### Step 2: Map to arxiv categories

Based on the user's description, suggest relevant arxiv categories. Present as a table with the full category name and a brief reason why it matches. Ask if they want to add or remove any.

### Step 3: Topics and focus

Ask about specific topics and focus **once** — not per-category. The user's interests often span multiple categories. Only ask per-category if their interests are clearly distinct across categories (e.g., quantum computing AND graph algorithms are different enough to warrant separate questions).

Use **bold** for category names and `code` for arxiv codes to make the output scannable. Illustrate the format with a playful, obviously-not-real example (e.g., topics: "time-traveling qubits", focus: "ones that arrive before they leave"). Focus is optional — don't push if the user doesn't have one.

When writing `interests.toml`, shared topics go under each relevant category.

### Step 4: Coaching preferences

Transition naturally — e.g., "Now, as your intellectual sparring partner..."

Present each option with a brief explanation of what it means in practice:

- **Difficulty** (how much you struggle before getting help):
  - guided — frequent hints, won't let you stare at a wall for long
  - balanced (default) — hints when you're stuck, but room to think first
  - sink-or-swim — minimal hand-holding, you struggle until you ask

- **Hint style** (how help is delivered):
  - questioning (default) — answers your questions with questions
  - pointing — points a direction without spelling it out
  - telling — tells you the relevant concept or technique

Let the user pick or accept defaults.

### Step 5: Write config

Create `.paperdojo/` directory structure and write `interests.toml`:

```toml
[user]
background = "<what the user said about themselves, if anything>"

[coaching]
difficulty = "<user_choice>"
hint_style = "<user_choice>"

[interests.<category>]
topics = [<user_topics>]
focus = "<user_focus>"
```

Only include the `[user]` section if the user mentioned their background during the conversation. Do not ask for it — just persist what was naturally shared.

Use the Write tool to create `.paperdojo/interests.toml`.
Use Bash to create directories: `mkdir -p .paperdojo/feeds .paperdojo/history`

### Step 6: MCP server check

Check if `arxiv-latex-mcp` is available by attempting to use one of its tools.

- **Available:** report "arxiv-latex-mcp is ready."
- **Not available:** ask the user:

> arxiv-latex-mcp is needed for viewing paper details and coaching sessions. Install now? [y/n]

If yes, create a local venv and install both MCP servers:
```bash
python3 -m venv .paperdojo/venv
.paperdojo/venv/bin/pip install arxiv-latex-mcp arxiv-mcp-server
```

Then register via Claude Code CLI:
```bash
claude mcp add -s project arxiv-latex-mcp -- .paperdojo/venv/bin/python -m arxiv_latex_mcp
claude mcp add -s project arxiv-mcp-server -- .paperdojo/venv/bin/python -m arxiv_mcp_server
```

Present a config summary table (categories, topics, focus, coaching style), then close as a coach welcoming a new student — introduce what PaperDojo is about (daily thinking exercises, not passive reading), what they can do next (`/feed` to browse today's papers), and set the tone for the coaching relationship. Both structured info and warm words.

## Returning User

### Step 1: Present current config

Read `.paperdojo/interests.toml` and present it as a formatted table.

### Step 2: Ask for updates

Ask if they want to change anything — add/remove categories, update topics/focus, change coaching preferences, or check MCP status.

If the user wants changes, walk through them interactively. After each change, update `interests.toml` and re-present the table.

### Step 3: MCP check

Same as First Run Step 6.
