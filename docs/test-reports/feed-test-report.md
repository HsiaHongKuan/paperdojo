# Test Report: /feed

**Date:** 2026-03-31
**Persona:** Raj Patel -- CS PhD student working on GNNs, intermediate Claude Code user
**Profile:** ephemeral (pre-created `.paperdojo/interests.toml` with GNN/reasoning interests)
**Use Case:** Daily curated arxiv feed for GNN/graph learning research
**Expected Outcome:** Browse 5 ranked papers, view details on 1-2, start coaching on one or quit with history saved
**Verdict:** pass (with caveats)
**Critical Issues:** 2

## Flow Completeness

| Phase | Status | Notes |
|-------|--------|-------|
| Step 1: Config Check | Reached (fast path) | interests.toml pre-existed, inline setup skipped |
| Step 1: Inline Setup | Skipped by design | Pre-created config bypassed this branch |
| Step 2: Fetch + Rank | Reached (simulated) | Subagent dispatched, 5 papers returned |
| Step 2: No-papers fallback | Not tested | Would require empty API response |
| Step 3: Browse [n] Next | Exercised 3 times | Papers 1, 2 (after details), 3 |
| Step 3: Browse [d] Details | Exercised 1 time | Paper 2, MCP declined, fallback used |
| Step 3: Browse [s] Coach | Exercised 1 time | Paper 4, triggered handoff to /coach |
| Step 3: Browse [q] Quit | Not exercised | Session ended via [s] handoff instead |
| MCP install prompt | Exercised (declined) | Fallback to abstract analysis worked |
| Post-details re-prompt | Exercised 1 time | Correctly omitted [d] option |

**Decision points exercised:** 6 of maximum 15
**Untested branches:** Config-missing inline setup, [q] quit with summary, MCP install acceptance, subagent returning 0 papers, arxiv API error handling (not specified in skill)

## Interaction Trace

| # | Actor | Action | Notes |
|---|-------|--------|-------|
| 1 | Skill | Reads interests.toml | Found 2 interest categories, proceeds to Step 2 |
| 2 | Skill | Checks .paperdojo/feeds/ | Empty directory, no prior IDs to exclude |
| 3 | Skill | Dispatches fetch subagent | Simulated: 5 papers returned, ranked by relevance |
| 4 | Skill | Presents Paper 1/5 (Topological Expressivity) | Relevance 10/10, Significance 9/10 |
| 5 | Raj | Chooses [n] | "Let me see what else is in the feed first" -- wants full picture before committing |
| 6 | Skill | Records skip, presents Paper 2/5 (Spectral Rewiring) | Relevance 9/10, Significance 8/10 |
| 7 | Raj | Chooses [d] | Wants to compare with Topping et al. 2022 -- typical researcher behavior |
| 8 | Skill | Checks arxiv-latex-mcp availability | Not available, prompts for install |
| 9 | Raj | Declines MCP install [n] | "I'd rather not install stuff right now" |
| 10 | Skill | Provides fallback abstract analysis | 4-paragraph breakdown of problem, approach, significance |
| 11 | Skill | Re-prompts with [n] [s] [q] | Correctly omits [d] since details already viewed |
| 12 | Raj | Chooses [n] | Liked the analysis but continues browsing |
| 13 | Skill | Records skip (details_viewed: true), presents Paper 3/5 (CoG Reasoning) | Relevance 7/10 |
| 14 | Raj | Chooses [n] | "Not directly in my wheelhouse" |
| 15 | Skill | Records skip, presents Paper 4/5 (Universal Approximation) | Relevance 8/10, Significance 9/10 |
| 16 | Raj | Chooses [s] | "This connects to what I'm thinking about for my thesis" |
| 17 | Skill | Records coached, announces handoff to /coach 2603.14209 | Paper 5 never shown, will reappear next run |

## Output Validation

| Expected | Actual | Status |
|----------|--------|--------|
| `.paperdojo/interests.toml` read successfully | Read, 2 interest categories parsed | OK |
| `.paperdojo/feeds/` scanned for seen IDs | Scanned, empty, no exclusions | OK |
| `.paperdojo/feeds/2026-03-31.json` created | Created with correct structure | OK |
| Feed file contains 4 paper records | 4 records: 3 skipped, 1 coached | OK |
| `details_viewed` flags correct | Paper 2 has `true`, others have `false` | OK |
| Paper 5 not recorded (unseen) | Absent from feed file | OK |
| Handoff to `/coach 2603.14209` announced | Announced correctly | OK |
| `.paperdojo/history/` directory exists | Exists but empty (not used by /feed) | OK |

**Feed file final state:**
```json
{
  "date": "2026-03-31",
  "papers": [
    {"arxiv_id": "2603.14821", "title": "Topological Expressivity...", "action": "skipped", "details_viewed": false},
    {"arxiv_id": "2603.15032", "title": "Spectral Rewiring...", "action": "skipped", "details_viewed": true},
    {"arxiv_id": "2603.13467", "title": "Chain-of-Graph Reasoning...", "action": "skipped", "details_viewed": false},
    {"arxiv_id": "2603.14209", "title": "Universal Approximation...", "action": "coached", "details_viewed": false}
  ]
}
```

## Broken References

| Reference | Status | Impact |
|-----------|--------|--------|
| `/coach {arxiv_id}` handoff | Not validated | /coach skill was not tested in this run; if it does not exist or has a different invocation pattern, the handoff fails silently |
| `arxiv-latex-mcp` tool availability check | Ambiguous | The skill says "check if arxiv-latex-mcp is available" but does not specify HOW to check (which tool to probe, what constitutes "available"). The /setup skill is more specific (it says "attempt to use one of its tools") |
| Agent tool for subagent dispatch | Assumed available | The skill assumes the Agent tool exists but does not handle the case where it is unavailable |
| WebFetch tool in subagent | Assumed available | The subagent prompt references WebFetch but there is no fallback if it fails |
| `.paperdojo/history/` directory | Created but never referenced by /feed | The /feed skill never writes to or reads from this directory; it is only relevant to /coach |

## Persona Interview

**1. What was most useful from today?**

> Honestly, the ranking was the best part. I scroll through arxiv listings every morning and it takes me 30-40 minutes to find 2-3 relevant papers. This surfaced 5 papers ranked by relevance to my exact interests in about 30 seconds. The fact that Paper 1 (Topological Expressivity) scored 10/10 on relevance and it genuinely was the most relevant -- that's impressive. Even the lower-ranked ones (CoG at 7/10) were correctly identified as tangential to my core work.

**2. Was there anything confusing or that didn't fit what you needed?**

> The MCP install prompt felt a bit jarring. I'm browsing papers and suddenly I'm asked to install a Python package and register an MCP server? I don't even know what MCP is in this context. The fallback (detailed abstract analysis) was actually quite good though -- maybe that should be the default and MCP should only be suggested during /setup or when you explicitly try to view full paper sections.
>
> Also, when I chose [s] to start coaching, I didn't get a summary of what I'd browsed so far. The skill just jumped straight to /coach. For someone who wants to see all options first (like me), it would be nice to know "you still have 1 unseen paper -- continue browsing or start coaching?"

**3. Were there parts that felt too rushed or too long?**

> The abstract analysis fallback (when I declined MCP) was actually a great length -- 3-4 paragraphs that broke down the problem nicely without spoiling the approach. The paper cards themselves were well-paced: enough info to decide without overwhelming.
>
> What felt too rushed was the transition from [d] -> analysis -> re-prompt. I would have liked a moment to think, maybe a "anything specific you want to know about this paper before moving on?" prompt. The re-prompt came right after the analysis with no breathing room.

**4. Was there anything you wanted to do but couldn't?**

> Three things:
> 1. **Go back.** After seeing Paper 4, I wanted to go back to Paper 1 (which I'd skipped) and start coaching on it instead. There's no [b] Back option.
> 2. **Bookmark.** I wanted to mark Paper 2 as "read later" instead of just skipping it. The only options are skip or coach -- there's no middle ground like "save for later" or "star."
> 3. **Compare.** I wanted to see Papers 1 and 4 side by side since they're both about expressivity of message passing. A compare mode would be amazing.
>
> Also, I couldn't filter or re-sort. What if I want to see only cs.LG papers? Or sort by significance instead of combined score?

**5. Any other thoughts?**

> This is way better than Semantic Scholar alerts, which just email me everything with a keyword match. The ranking feels like it understands what I actually care about, not just keyword overlap. Compared to arxiv-sanity, the interactive browsing is much nicer -- arxiv-sanity gives you a static ranked list, but this feels like a conversation.
>
> One concern: how does the ranking work across runs? If I run /feed again tomorrow, will the same papers show up minus the ones I've seen? The dedup via feed files is good, but what about papers from 3 days ago that I haven't seen yet? Feels like there could be a staleness problem.
>
> Minor thing: the paper card doesn't show the arxiv ID. I sometimes want to quickly look up a paper's ID to share with my advisor. Would be nice to include it in the display.

## Structural Observations

### 1. CRITICAL: Current paper lost on [q] quit
When a user presses [q], the paper currently being viewed is NOT recorded to the feed file. The skill says "the feed record is already up to date" because [n] and [s] append immediately, but the paper being displayed at the time of [q] falls through the cracks. This means:
- The paper will reappear in the next feed run (which may be desirable)
- But there is no record that the user saw it at all (which loses context)
- If the user viewed details ([d]) and then quit, the details_viewed state is also lost

**Recommendation:** On [q], record the current paper with `"action": "abandoned"` or `"action": "seen"` to distinguish from truly unseen papers.

### 2. CRITICAL: No back/bookmark flow for deliberate users
The skill assumes a linear, single-pass browse. Users like Raj who want to see all options first, then decide, are poorly served. The only way to "go back" to a skipped paper is to run /feed again -- but by then the paper is in the exclusion list and will never reappear.

**Recommendation:** Either add a [b] Back option, or at minimum, after all papers are shown, present a summary with the option to revisit any paper for coaching.

### 3. MCP install prompt disrupts browsing flow
Being asked to install software mid-browse is a context switch. The fallback (abstract analysis) is good enough for browsing. MCP should be recommended during /setup or deferred to the coaching session where full paper text is truly needed.

### 4. Missing arxiv ID in paper display
The paper card template in Step 3 does not include the arxiv ID. This is an oversight since the ID is tracked internally and is useful for users who want to look up papers externally.

### 5. No summary on [s] handoff
When [s] triggers a /coach handoff, the user does not receive a feed summary (N browsed, M skipped, K coached). They only get the summary on [q]. Since [s] effectively ends the feed session, the summary should also appear here.

### 6. Subagent prompt lacks error handling guidance
The subagent prompt tells the agent to fetch from the arxiv API but provides no guidance for:
- API rate limiting (arxiv has a 3-second courtesy delay policy)
- Malformed XML responses
- Network failures
- Empty result sets per category (vs globally empty)

### 7. Feed file JSON management is fragile
The skill instructs to read-append-write a JSON file for each action. This pattern is error-prone:
- Concurrent feed sessions could corrupt the file
- A crash mid-write loses the entire file
- JSON append requires parsing the full file each time

An append-only format (JSONL) would be more robust.

### 8. Ambiguity in "date" for feed filename
The skill uses `YYYY-MM-DD.json` but does not specify whether this is the current date, the paper submission date, or the fetch date. In practice it should be the session date, but this should be explicit.

### 9. No category/date shown in paper card
The template shows `{primary_category}` and `{date}` but the subagent output format does not include a `date` field -- it only provides `CATEGORIES`. The skill would need to extract the submission date from the arxiv API response, which the subagent prompt does not request.

## Suggestions

Ordered by impact (highest first):

1. **Add end-of-feed review prompt** -- After all papers are shown (or on [s]/[q]), present a summary table of all papers with their actions and let the user revisit any skipped paper. This addresses the "no going back" problem and serves deliberate users who want to compare before committing. *High impact, moderate effort.*

2. **Record current paper on [q]** -- Add a `"seen"` or `"abandoned"` action for the paper being viewed when the user quits. Prevents data loss and makes dedup behavior predictable. *High impact, low effort.*

3. **Add [b] Bookmark action** -- Add a `"bookmarked"` action that saves the paper for later without starting a coaching session. Bookmarked papers could appear in a separate `/bookmarks` list or at the top of the next feed. *High impact, moderate effort.*

4. **Defer MCP install to /setup or /coach** -- Remove the MCP install prompt from the browse flow. The abstract analysis fallback is sufficient for browsing decisions. Only prompt for MCP when the user starts a coaching session and full paper text is needed. *Medium impact, low effort.*

5. **Show feed summary on [s] handoff** -- Before transitioning to /coach, show the same summary that [q] produces ("N papers browsed, M skipped, K coached"). This gives the user closure on the feed session. *Medium impact, low effort.*

6. **Add arxiv ID to paper display card** -- Include the arxiv ID in the paper card so users can quickly reference or share it. *Low impact, trivial effort.*

7. **Add error handling to subagent prompt** -- Include instructions for handling API failures, rate limits, and empty results. Suggest a retry-with-backoff strategy and a user-facing message for persistent failures. *Medium impact, low effort.*

8. **Switch feed file format to JSONL** -- Use append-only JSON Lines instead of read-modify-write JSON. Each action becomes a single appended line, eliminating parse/rewrite overhead and corruption risk. *Medium impact, moderate effort (requires changes to the reader in Step 2 as well).*

9. **Request submission date in subagent output** -- Add a `DATE:` field to the subagent output format so the paper card can display when the paper was submitted. *Low impact, trivial effort.*

10. **Add re-sort/filter options** -- At the top of the browse loop, offer options to filter by category or re-sort by relevance/significance. This serves power users who process many papers. *Low impact, high effort.*
