#!/usr/bin/env python3
"""Generate a styled HTML session report for a single coached paper."""

import html as html_mod
import json
import sys
from pathlib import Path

BASE = Path(".paperdojo")


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_session_report.py <arxiv_id>")
        sys.exit(1)

    arxiv_id = sys.argv[1]
    history_dir = BASE / "history"

    # Find session file
    session = None
    for f in history_dir.glob(f"*-{arxiv_id}.json"):
        session = json.loads(f.read_text())
        break

    if not session:
        print(f"No coaching session found for {arxiv_id}")
        sys.exit(1)

    # Read interests for context
    interests_path = BASE / "interests.toml"
    interests_text = interests_path.read_text() if interests_path.exists() else ""

    # Read analysis if available
    analysis_path = BASE / "report_analysis.json"
    analysis = json.loads(analysis_path.read_text()) if analysis_path.exists() else {}

    out = BASE / f"session-report-{arxiv_id}.html"
    out.write_text(render_session(session, analysis, interests_text))
    print(f"Session report written to {out}")


def esc(text):
    return html_mod.escape(str(text))


def render_conversation_highlights(conversation):
    """Extract key moments from the conversation."""
    nailed, learned, gaps = [], [], []

    for i, turn in enumerate(conversation):
        content = turn.get("content", "")
        role = turn.get("role", "")

        if role == "user":
            # User insights that were confirmed by coach
            if i + 1 < len(conversation):
                next_turn = conversation[i + 1]
                next_content = next_turn.get("content", "")
                if any(w in next_content.lower() for w in
                       ["confirmed", "right", "correct", "good", "spot-on",
                        "exactly", "matched", "aligned"]):
                    nailed.append(content)

        if role == "coach":
            # Teaching moments
            if "teaching moment" in content.lower() or "explained" in content.lower():
                learned.append(content)
            # Reveals and gaps
            if any(w in content.lower() for w in
                   ["missed", "diverge", "gap", "didn't", "not quite"]):
                gaps.append(content)

    return nailed[:3], learned[:3], gaps[:3]


def render_session(session, analysis, interests_text):
    title = esc(session.get("title", "Unknown"))
    arxiv_id = esc(session.get("arxiv_id", ""))
    date = esc(session.get("date", ""))
    source = esc(session.get("source", ""))
    insight = session.get("insight", session.get("outcome", ""))
    approach = session.get("approach", "")
    conversation = session.get("conversation", [])

    # Derive highlights from conversation
    nailed, learned, gaps = render_conversation_highlights(conversation)

    # Badge colors
    insight_color = "#166534" if insight == "captured" else "#b45309"
    insight_bg = "#f0fdf4" if insight == "captured" else "#fff7ed"
    approach_color = "#166534" if approach == "aligned" else "#b45309"
    approach_bg = "#f0fdf4" if approach == "aligned" else "#fff7ed"

    # Build sections
    nailed_html = "".join(f"<li>{esc(n)}</li>" for n in nailed) if nailed else "<li>No highlights extracted</li>"
    learned_html = "".join(f"<li>{esc(l)}</li>" for l in learned) if learned else "<li>No teaching moments extracted</li>"
    gaps_html = "".join(f"<li>{esc(g)}</li>" for g in gaps) if gaps else "<li>No gaps identified</li>"

    # Conversation timeline
    timeline_html = []
    for turn in conversation:
        role = turn.get("role", "")
        content = esc(turn.get("content", ""))
        if role == "user":
            timeline_html.append(
                f'<div class="turn turn-user">'
                f'<div class="turn-label">You</div>'
                f'<div class="turn-content">{content}</div></div>'
            )
        else:
            timeline_html.append(
                f'<div class="turn turn-coach">'
                f'<div class="turn-label">Coach</div>'
                f'<div class="turn-content">{content}</div></div>'
            )

    # Cross-reference with full analysis for richer content
    best_moments_for_paper = []
    stuck_for_paper = []
    revisit_for_paper = []

    if analysis:
        for key, target in [
            ("best_moments", best_moments_for_paper),
            ("stuck_points", stuck_for_paper),
            ("topics_to_revisit", revisit_for_paper),
        ]:
            text = analysis.get(key, "")
            if text:
                # Extract bullet points mentioning this paper's title or ID
                for line in text.split("\n"):
                    line = line.strip()
                    if line.startswith("- ") and (
                        session.get("title", "NONE").lower()[:30] in line.lower()
                        or session.get("arxiv_id", "NONE") in line
                    ):
                        target.append(line[2:])

    # Use analysis-derived content if available, fall back to conversation extraction
    if best_moments_for_paper:
        nailed_html = "".join(f"<li>{esc(n)}</li>" for n in best_moments_for_paper)
    if stuck_for_paper:
        gaps_html = "".join(f"<li>{esc(g)}</li>" for g in stuck_for_paper)
    if revisit_for_paper:
        revisit_html = "".join(f"<li>{esc(r)}</li>" for r in revisit_for_paper)
    else:
        revisit_html = gaps_html

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Session Report — {title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',-apple-system,sans-serif;background:#f8fafc;color:#334155;line-height:1.6;padding:48px 24px}}
.container{{max-width:840px;margin:0 auto}}
h1{{font-size:24px;font-weight:700;color:#0f172a;margin-bottom:4px;line-height:1.3}}
h2{{font-size:18px;font-weight:600;color:#0f172a;margin-bottom:12px}}
.meta{{color:#64748b;font-size:14px;margin-bottom:24px}}
.meta span{{margin-right:16px}}

.badges{{display:flex;gap:12px;margin-bottom:32px;flex-wrap:wrap}}
.badge{{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:600}}
.badge-label{{color:#64748b;font-weight:400}}

.stats-row{{display:flex;gap:32px;padding:16px 0;border-top:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;margin-bottom:32px;flex-wrap:wrap}}
.stat-val{{font-size:24px;font-weight:700;color:#0f172a}}
.stat-lbl{{font-size:11px;color:#64748b;text-transform:uppercase}}

.card{{border:1px solid;border-radius:8px;padding:16px 20px;margin-bottom:16px}}
.card h2{{margin-bottom:8px}}
.card ul{{font-size:14px;color:#334155;margin:0 0 8px 20px}}
.card li{{margin-bottom:6px;line-height:1.5}}

.timeline{{margin-top:32px;margin-bottom:32px}}
.timeline h2{{margin-bottom:16px}}
.turn{{padding:12px 16px;border-radius:8px;margin-bottom:8px;font-size:14px;line-height:1.5}}
.turn-label{{font-size:11px;font-weight:600;text-transform:uppercase;margin-bottom:4px}}
.turn-user{{background:#eff6ff;border:1px solid #bfdbfe}}
.turn-user .turn-label{{color:#1e40af}}
.turn-coach{{background:#f8fafc;border:1px solid #e2e8f0}}
.turn-coach .turn-label{{color:#64748b}}
.turn-content{{color:#334155}}

.footer{{text-align:center;color:#94a3b8;font-size:12px;margin-top:48px;padding-top:16px;border-top:1px solid #e2e8f0}}
</style>
</head>
<body>
<div class="container">

<h1>{title}</h1>
<div class="meta">
<span>{arxiv_id}</span>
<span>{date}</span>
<span>Source: {source}</span>
</div>

<div class="badges">
<div class="badge" style="background:{insight_bg};color:{insight_color}">
<span class="badge-label">Insight:</span> {esc(insight)}
</div>
<div class="badge" style="background:{approach_bg};color:{approach_color}">
<span class="badge-label">Approach:</span> {esc(approach)}
</div>
</div>

<div class="card" style="background:#f0fdf4;border-color:#bbf7d0">
<h2 style="color:#166534">What You Nailed</h2>
<ul>{nailed_html}</ul>
</div>

<div class="card" style="background:#eff6ff;border-color:#bfdbfe">
<h2 style="color:#1e40af">What You Learned</h2>
<ul>{learned_html}</ul>
</div>

<div class="card" style="background:#fff7ed;border-color:#fed7aa">
<h2 style="color:#9a3412">Gaps to Revisit</h2>
<ul>{revisit_html}</ul>
</div>

<div class="timeline">
<h2>Session Timeline</h2>
{"".join(timeline_html)}
</div>

<div class="footer">
PaperDojo Session Report &middot; Generated from coaching session data
</div>

</div>
</body>
</html>"""


if __name__ == "__main__":
    main()
