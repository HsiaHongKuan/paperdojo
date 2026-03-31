# PaperDojo

A skill-based plugin for AI coding assistants. Daily thinking exercise built on arxiv paper feeds — see the problem first, try to solve it with an AI coach, then compare with the authors' approach.

## Skills

| Skill | Description |
|---|---|
| `/setup` | Configure research interests, coaching preferences, MCP servers |
| `/feed` | Daily paper browsing with ranked recommendations |
| `/coach` | Socratic coaching session for a specific paper (not yet implemented) |
| `/report` | Historical dashboard from past sessions (not yet implemented) |

## Key Files

- `skills/` — skill definitions (one directory per skill, each with SKILL.md)
- `.claude-plugin/plugin.json` — marketplace plugin metadata
- `.mcp.json` — project-scoped MCP server config (arxiv-latex-mcp)
- `.paperdojo/` — local user state (gitignored): interests, feed history, coach sessions

## Dependencies

- `arxiv-latex-mcp` — MCP server for reading paper LaTeX source. Installed into `.paperdojo/venv/` via `/setup` or just-in-time.
- arxiv Atom API — used directly via WebFetch for paper search.

## Installation

### Claude Code
```bash
claude plugin add --from github HsiaHongKuan/paperdojo
```
