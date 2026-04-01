<p align="center">
  <img src="logo.svg" width="300" alt="PaperDojo logo">
</p>

# PaperDojo

**Don't read papers. Solve them.**

See the problem, spar with an AI coach, then compare with the authors' approach.

PaperDojo delivers a daily feed of arxiv papers matched to your interests and turns them into **thinking exercises**. You work through the core problem with a Socratic coach, then compare with the authors' approach.

## Quick start (Claude Code)

```bash
/plugin marketplace add HsiaHongKuan/paperdojo
/plugin install paperdojo@paperdojo
```

For Codex and OpenCode, see [Other platforms](#other-platforms).



Run `/setup` to tell PaperDojo what you're into. Then `/feed` to browse today's papers — when one catches your eye, press `[s]` or type `/coach` to start sparring. You can also jump in directly with `/coach 2603.12345` if you already have a paper.

After a few sessions, run `/report` to see what's working and where to stretch — it surfaces your reasoning patterns, spots gaps in methodology or formalism, and suggests what to revisit.

## Dependencies

- **arxiv-latex-mcp** — Reads full paper LaTeX source (equations, proofs, everything). Installed automatically via `/setup`.
- **arxiv Atom API** — Paper search. No setup needed.

## Other platforms

### Codex

Tell Codex:

```
Fetch and follow instructions from https://raw.githubusercontent.com/HsiaHongKuan/paperdojo/refs/heads/main/.codex/INSTALL.md
```

### OpenCode

Tell OpenCode:

```
Fetch and follow instructions from https://raw.githubusercontent.com/HsiaHongKuan/paperdojo/refs/heads/main/.opencode/INSTALL.md
```

### Updating

```bash
# Codex
cd ~/.codex/paperdojo && git pull

# OpenCode
cd ~/.config/opencode/paperdojo && git pull
```

For Claude Code, use the plugin marketplace update workflow.

## License

MIT
