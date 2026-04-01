# PaperDojo

**Don't read papers. Solve them.**

See the problem, spar with an AI coach, then compare with the authors' approach.

PaperDojo delivers a daily feed of arxiv papers matched to your interests and turns them into **thinking exercises**. You work through the core problem with a Socratic coach, then compare with the authors' approach.

## Install

```bash
/plugin marketplace add HsiaHongKuan/paperdojo
/plugin install paperdojo@paperdojo
```

## Get started

Run `/setup` to tell PaperDojo what you're into. Then `/feed` to browse today's papers — when one catches your eye, press `[s]` or type `/coach` to start sparring. You can also jump in directly with `/coach 2603.12345` if you already have a paper.

After a few sessions, run `/report` to see what's working and where to stretch — it surfaces your reasoning patterns, spots gaps in methodology or formalism, and suggests what to revisit.

## Dependencies

- **arxiv-latex-mcp** — Reads full paper LaTeX source (equations, proofs, everything). Installed automatically via `/setup`.
- **arxiv Atom API** — Paper search. No setup needed.

## License

MIT
