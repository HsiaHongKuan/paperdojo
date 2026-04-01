# Test Report: /setup

**Date:** 2026-03-31
**Persona:** Dr. Mei Chen -- condensed matter physicist, beginner with Claude Code
**Profile:** ephemeral
**Use Case:** First-time setup for daily cond-mat/quant-ph paper digest
**Expected Outcome:** A working interests.toml with physics categories and default coaching preferences
**Verdict:** pass
**Critical Issues:** 1

## Flow Completeness

| Phase | Status | Notes |
|---|---|---|
| Mode determination | reached | No existing `interests.toml` -- correctly routed to First Run |
| Step 1: Welcome + interests | reached | User provided free-text research description |
| Step 2: Map to arxiv categories | reached | 4 categories suggested, user removed 1, added 1 |
| Step 3: Topics and focus | reached | User gave 6 topics and 1 focus string |
| Step 4: Coaching preferences | reached | User chose sink-or-swim + questioning (default) |
| Step 5: Write config | reached | `interests.toml` written, directories created |
| Step 6: MCP server check | reached | Simulated install (user chose y) |
| Returning User path | skipped | Not applicable for first-run persona |

**Decision points exercised:** 6 of 6 (first-run path)
**Untested branches:**
- Returning User flow (requires pre-existing `interests.toml`)
- User declining MCP install (choosing `n` at Step 6)
- Per-category topic splitting (when interests are "clearly distinct across categories")
- User providing no focus (focus is optional but persona provided one)
- User providing no background (the `[user]` section is conditional)

## Interaction Trace

| # | Step | Skill Action | Persona Response | Decision |
|---|---|---|---|---|
| 1 | Welcome | Asked what user works on in plain language | Described topological superconductors, Majorana fermions, quantum information overlap. Mentioned skepticism about AI. | Free-text interests provided |
| 2 | Category mapping | Suggested 4 categories in table format with reasons | Dropped `cond-mat.str-el` (too broad), added `cond-mat.mtrl-sci` (experimental topological materials). Kept `supr-con`, `mes-hall`, `quant-ph`. | 1 removed, 1 added, 2 confirmed |
| 3 | Topics + focus | Asked for topics and optional focus across all categories | Gave 6 topics (Majorana fermions, topological superconductors, topological quantum computing, anyonic braiding, vortex bound states, Kitaev chain) and focus "theoretical predictions and signatures of non-Abelian anyons" | Topics + focus provided |
| 4 | Coaching: difficulty | Presented 3 options with explanations | Chose "sink-or-swim" -- experienced physicist, does not want hand-holding | Non-default choice |
| 5 | Coaching: hint style | Presented 3 options with explanations | Accepted default "questioning" -- likes Socratic approach | Default accepted |
| 6 | MCP install | Reported arxiv-latex-mcp not available, asked to install | Said yes -- valued ability to read math/equations in papers | Chose y |

## Output Validation

### Expected files
| File/Directory | Expected | Actual | Status |
|---|---|---|---|
| `.paperdojo/interests.toml` | Created with user, coaching, and interests sections | Created at `/tmp/paperdojo-test-setup/.paperdojo/interests.toml` | PASS |
| `.paperdojo/feeds/` | Empty directory created | Created | PASS |
| `.paperdojo/history/` | Empty directory created | Created | PASS |
| `.paperdojo/venv/` | Created during MCP install | Simulated (not actually created) | SIMULATED |

### interests.toml content validation
| Field | Expected | Actual | Status |
|---|---|---|---|
| `[user].background` | Present (user shared background naturally) | "Condensed matter physicist, five years postdoc, works on topological superconductors" | PASS |
| `[coaching].difficulty` | "sink-or-swim" | "sink-or-swim" | PASS |
| `[coaching].hint_style` | "questioning" | "questioning" | PASS |
| `[interests.cond-mat.supr-con]` | Present with relevant topics | Present with 4 topics + focus | PASS |
| `[interests.cond-mat.mes-hall]` | Present with relevant topics | Present with 4 topics + focus | PASS |
| `[interests.quant-ph]` | Present with relevant topics | Present with 3 topics + focus | PASS |
| `[interests.cond-mat.mtrl-sci]` | Present with relevant topics | Present with 2 topics + focus | PASS |

### TOML key format issue (CRITICAL)
The category keys use dotted notation: `[interests.cond-mat.supr-con]`. In TOML, dots in keys denote nested tables. This means `cond-mat` is interpreted as a parent table containing `supr-con`, `mes-hall`, and `mtrl-sci` as sub-tables. The key `quant-ph` would be a separate sibling of `cond-mat` under `interests`. This is actually well-formed TOML and correctly represents the arxiv hierarchy, but any code parsing this file must be aware that `interests` is a deeply nested structure, not a flat map of category codes to config. If the intent is for category codes to be flat string keys, the keys should be quoted: `[interests."cond-mat.supr-con"]`.

## Broken References

| Reference | Location | Status |
|---|---|---|
| `arxiv-latex-mcp` package | Step 6 -- `pip install arxiv-latex-mcp` | Cannot verify -- package may not exist on PyPI. The `.mcp.json` references it but no installation validation is possible. |
| `claude mcp add` CLI command | Step 6 -- MCP registration | Depends on Claude Code CLI being installed. No fallback if `claude` binary is not in PATH. |
| `/feed` skill | Mentioned in final summary ("Try `/feed`") | Exists at `skills/feed/SKILL.md` (confirmed in project structure). |
| `/coach` skill | Referenced in CLAUDE.md as "not yet implemented" | Not tested but not referenced by `/setup`. No issue. |

## Persona Interview

**Q1: What was most useful from today?**
> The category mapping was genuinely helpful. I appreciated that it didn't just dump a list of arxiv codes at me -- it explained why each category was relevant. The table format was easy to scan. And the fact that I could just describe my research in plain language and get sensible suggestions was nice.

**Q2: Was there anything confusing or that didn't fit what you needed?**
> The topics/focus distinction was a bit unclear at first. I wasn't sure if "focus" was supposed to be different from "topics" or just a more specific version. The playful example helped, but I think a real example from, say, quantum computing or condensed matter would have been more clarifying than "time-traveling qubits." Also, I noticed the TOML file has dots in the category keys like `cond-mat.supr-con` -- I wonder if that could cause parsing issues since dots are sometimes treated as nested keys in TOML. That's a technical concern though.

**Q3: Were there parts that felt too rushed or too long?**
> The coaching preferences felt a bit abrupt as a transition. One moment we're talking about arxiv categories and the next we're configuring coaching difficulty. I didn't fully understand what "coaching session" means in practice until the MCP step mentioned looking at papers together. It would help to have a brief explanation of what coaching sessions actually look like before asking me to configure preferences for them.

**Q4: Was there anything you wanted to do but couldn't?**
> I wanted to set different topics per category -- my interests in `quant-ph` are somewhat different from my interests in `cond-mat.supr-con`. The skill asked for topics once globally, which is fine as a default, but I would have liked the option to refine per-category. Also, I would have liked to preview what a daily feed or coaching session looks like before committing to preferences. It's hard to configure something you haven't seen yet.

**Q5: Any other thoughts?**
> The tone was good -- not too corporate, not too casual. I was skeptical coming in, but the setup process itself was painless. My real test will be whether `/feed` actually surfaces relevant papers and doesn't just give me the top 10 from each category sorted by download count. Also, the MCP installation step -- I'm glad it asked first rather than just installing things, but I have no idea what a "venv" is or what "MCP" stands for. For someone who's not a software engineer, a one-line explanation of what's being installed and why would go a long way.

## Structural Observations

### 1. TOML dotted-key ambiguity (CRITICAL)
The SKILL.md template uses `[interests.<category>]` as the section format. Arxiv category codes contain dots (e.g., `cond-mat.supr-con`). In TOML, `[interests.cond-mat.supr-con]` creates a three-level nested structure: `interests` -> `cond-mat` -> `supr-con`. This works but means categories without dots (like `quant-ph`) are at a different nesting depth than hyphenated sub-categories. Any downstream consumer (e.g., `/feed`) must handle this asymmetry. Using quoted keys like `[interests."cond-mat.supr-con"]` would keep categories as flat keys and be less error-prone.

### 2. No validation of generated TOML
The skill writes the file but never validates that it parses correctly. A malformed file (e.g., from special characters in user input) would silently break downstream skills.

### 3. Coaching preferences lack context
The skill presents coaching options before the user has experienced a coaching session. The persona found this confusing. Consider either: (a) deferring coaching config to the first `/coach` session, or (b) adding a 1-2 sentence preview of what a coaching session looks like before presenting options.

### 4. MCP install has no error handling
If `pip install` fails (network issues, Python version incompatibility, package doesn't exist), the skill has no fallback. It should catch failures and suggest manual installation or skipping.

### 5. MCP explanation assumes technical knowledge
Terms like "MCP server," "venv," and "register via CLI" are opaque to non-developer users. The skill's tone section says "talk like a human colleague" but the MCP step reads like a sysadmin runbook.

### 6. No undo or reset mechanism
If the user makes a mistake during setup, there's no way to restart from scratch within the skill. The returning-user flow allows edits but doesn't offer a "start over" option.

### 7. Shared topics heuristic is underspecified
Step 3 says to ask per-category "if their interests are clearly distinct across categories" but provides no guidance on how to determine this. In practice, an LLM will need to make a judgment call, which may vary between sessions.

### 8. The `[user]` section conditional is good design
The instruction to only include `[user].background` if naturally shared (rather than asking for it) is a thoughtful UX choice that reduces the interview feel.

## Suggestions

Ordered by impact:

1. **Quote TOML category keys** -- Change the template from `[interests.<category>]` to `[interests."<category>"]` to avoid the dotted-key nesting issue. This is the most likely source of downstream bugs. *(HIGH IMPACT, LOW EFFORT)*

2. **Add a 1-sentence coaching preview** -- Before presenting coaching options, briefly describe what a coaching session looks like: "When you do a coaching session with `/coach`, I'll present a paper's problem statement and guide you through solving it before revealing the authors' approach." This gives users context for their preference choices. *(HIGH IMPACT, LOW EFFORT)*

3. **Explain MCP in plain language** -- Replace or supplement the technical MCP explanation with something like: "This installs a small helper program that lets me read the full LaTeX source of papers -- equations, proofs, and all -- instead of just abstracts." Only mention venv/MCP/CLI if the user asks. *(MEDIUM IMPACT, LOW EFFORT)*

4. **Add TOML validation after write** -- After writing `interests.toml`, parse it back and confirm it's valid. If it fails, show the error and offer to fix it. *(MEDIUM IMPACT, LOW EFFORT)*

5. **Add error handling for MCP install** -- Wrap the pip install and claude mcp add steps in error handling. On failure, explain what went wrong and offer alternatives (skip for now, manual install instructions). *(MEDIUM IMPACT, MEDIUM EFFORT)*

6. **Offer per-category topic refinement** -- After collecting global topics, ask "Want to refine topics for any specific category?" This respects the current quick flow while giving power users an escape hatch. *(LOW IMPACT, LOW EFFORT)*

7. **Add a "start over" option for returning users** -- In the returning-user flow, offer a "Reset and start fresh" option alongside edit-in-place. *(LOW IMPACT, LOW EFFORT)*

8. **Clarify topics vs. focus distinction** -- Consider using a domain-relevant example instead of the playful one, or add a brief explanation like "Topics are WHAT you track; focus is HOW you filter -- your angle or lens on those topics." *(LOW IMPACT, LOW EFFORT)*
