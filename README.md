# PaperDojo

**Don't read papers. Solve them.**

See the problem, spar with an AI coach, then compare with the authors' approach.

PaperDojo delivers a daily feed of arxiv papers matched to your interests and turns them into **thinking exercises**. You work through the core problem with a Socratic coach, then compare with the authors' approach.

## Install

```bash
claude plugin add --from github HsiaHongKuan/paperdojo
```

## Get started

Run `/setup` to configure your research interests and coaching style. Then `/feed` to browse today's papers — press `[s]` on one to spar. Or jump straight in with `/coach 2603.12345` if you already have a paper. Run `/report` to see your thinking patterns and progress.

## Skills

| Skill | Description |
|---|---|
| `/setup` | Configure research interests, coaching preferences, MCP servers |
| `/feed` | Daily paper browsing with ranked recommendations |
| `/coach` | Socratic coaching session — work through a paper's problem with guided hints |
| `/report` | HTML dashboard — heatmap, stats, thinking patterns, coaching insights |

## Dependencies

- **arxiv-latex-mcp** — Reads full paper LaTeX source (equations, proofs, everything). Installed automatically via `/setup`.
- **arxiv Atom API** — Paper search. No setup needed.

## Project structure

```
skills/              Skill definitions (one directory per skill)
scripts/             Report generator
docs/schema.md       Shared data formats for feed/coach/report pipeline
.claude-plugin/      Plugin and marketplace metadata
.paperdojo/          Local user state (gitignored)
```

## License

MIT
