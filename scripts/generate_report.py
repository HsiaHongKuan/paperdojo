#!/usr/bin/env python3
"""Generate PaperDojo coaching dashboard as HTML report."""

import html as html_mod
import json
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

BASE = Path(".paperdojo")


def main():
    feeds = load_feeds(BASE / "feeds")
    history = load_history(BASE / "history")
    report_json = BASE / "report.json"
    report_data = json.loads(report_json.read_text()) if report_json.exists() else {}
    analysis = report_data.get("synthesis", {})

    if not feeds and not history:
        print("No data yet. Try /feed or /coach first.")
        sys.exit(0)

    stats = compute_stats(feeds, history)
    activity = compute_activity_map(feeds, history)
    categories = compute_categories(feeds)
    words = compute_word_cloud(feeds, history)
    recent = recent_sessions(history)

    out = BASE / "report.html"
    out.write_text(render(stats, activity, categories, words, recent, analysis))
    print(f"Report written to {out}")


# --- Data loading ---


def load_feeds(feeds_dir):
    papers = []
    if not feeds_dir.exists():
        return papers
    for f in sorted(feeds_dir.glob("*.json")):
        data = json.loads(f.read_text())
        for p in data.get("papers", []):
            p["feed_date"] = data.get("date", f.stem)
            papers.append(p)
    return papers


def load_history(history_dir):
    if not history_dir.exists():
        return []
    return [json.loads(f.read_text()) for f in sorted(history_dir.glob("*.json"))]


# --- Computation ---


def compute_stats(feeds, history):
    coached = len(history)
    insight_captured = sum(1 for s in history if s.get("insight") == "captured")
    approach_aligned = sum(1 for s in history if s.get("approach") == "aligned")
    return {
        "browsed": len(feeds),
        "coached": coached,
        "insight_captured": insight_captured,
        "approach_aligned": approach_aligned,
        "insight_rate": round(insight_captured / coached * 100) if coached else 0,
        "approach_rate": round(approach_aligned / coached * 100) if coached else 0,
    }


def compute_activity_map(feeds, history):
    activity = {}
    for p in feeds:
        d = p.get("feed_date", "")
        if d:
            activity.setdefault(d, {"papers": 0, "coaching": None})
            activity[d]["papers"] += 1
    for s in history:
        d = s.get("date", "")
        if d:
            activity.setdefault(d, {"papers": 0, "coaching": None})
            insight = s.get("insight") == "captured"
            approach = s.get("approach") == "aligned"
            level = "good" if (insight or approach) else "missed"
            if level == "good" or activity[d]["coaching"] != "good":
                activity[d]["coaching"] = level
    return activity


def recent_sessions(history, n=10):
    return sorted(history, key=lambda s: s.get("date", ""), reverse=True)[:n]


def compute_categories(feeds):
    counts = Counter()
    for p in feeds:
        for cat in p.get("categories", []):
            counts[cat] += 1
    return counts.most_common(10)


STOP_WORDS = {
    "a", "an", "the", "of", "in", "for", "and", "on", "to", "with", "by",
    "from", "is", "are", "at", "its", "via", "non", "as", "or",
}


def compute_word_cloud(feeds, history):
    # Only papers the user explored (details viewed or coached)
    titles = [
        p.get("title", "") for p in feeds
        if p.get("details_viewed") or p.get("action") == "coached"
    ]
    titles += [s.get("title", "") for s in history]
    counts = Counter()
    for title in titles:
        for word in re.findall(r"[A-Za-z][-A-Za-z]{2,}", title):
            w = word.lower()
            if w not in STOP_WORDS:
                counts[w] += 1
    return counts.most_common(30)


# --- HTML helpers ---


def esc(text):
    return html_mod.escape(str(text))


def md_to_html(text):
    """Minimal markdown: paragraphs, bold, italic, bullet lists, h3/h4 headers."""
    if not text:
        return ""
    text = re.sub(r"\*\*(.+?)\*\*", r"__B__\1__/B__", text)
    text = re.sub(r"\*(.+?)\*", r"__I__\1__/I__", text)
    text = html_mod.escape(text)
    text = text.replace("__B__", "<strong>").replace("__/B__", "</strong>")
    text = text.replace("__I__", "<em>").replace("__/I__", "</em>")

    result = []
    for para in text.strip().split("\n\n"):
        lines = [l.strip() for l in para.split("\n") if l.strip()]
        if not lines:
            continue
        if lines[0].startswith("### "):
            result.append(f"<h4>{lines[0][4:]}</h4>")
            lines = lines[1:]
            if not lines:
                continue
        if all(l.startswith("- ") for l in lines):
            items = "".join(f"<li>{l[2:]}</li>" for l in lines)
            result.append(f"<ul>{items}</ul>")
        else:
            result.append(f"<p>{' '.join(lines)}</p>")
    return "\n".join(result)


# --- Heatmap ---


def render_heatmap(activity):
    if not activity:
        return '<p class="empty">No activity yet.</p>'

    dates = sorted(activity.keys())
    earliest = date.fromisoformat(dates[0])
    today = date.today()
    start = earliest - timedelta(days=earliest.weekday())
    end = today + timedelta(days=(6 - today.weekday()))
    num_weeks = ((end - start).days + 1) // 7

    cells, months, days = [], [], []
    day_names = ["Mon", "", "Wed", "", "Fri", "", ""]

    for i, name in enumerate(day_names):
        if name:
            days.append(
                f'<div class="hm-day" style="grid-row:{i + 2};grid-column:1">'
                f"{name}</div>"
            )

    prev_month = None
    for w in range(num_weeks):
        for dow in range(7):
            d = start + timedelta(days=w * 7 + dow)
            row = dow + 2
            col = w + 2

            if d > today:
                cells.append(
                    f'<div class="hm-cell" style="grid-row:{row};'
                    f'grid-column:{col};background:transparent"></div>'
                )
                continue

            key = d.isoformat()
            info = activity.get(key, {})
            papers = info.get("papers", 0)
            coaching = info.get("coaching")

            if papers == 0 and not coaching:
                color = "#ebedf0"
            elif papers <= 2:
                color = "#9be9a8"
            elif papers <= 5:
                color = "#40c463"
            else:
                color = "#30a14e"

            if coaching == "good":
                border = "border:2px solid #3b82f6;"
            elif coaching == "missed":
                border = "border:2px solid #e34c26;"
            else:
                border = ""

            tip = f"{key}: {papers} paper{'s' if papers != 1 else ''}"
            if coaching:
                tip += f", coached ({'good' if coaching == 'good' else 'needs work'})"

            cells.append(
                f'<div class="hm-cell" style="grid-row:{row};grid-column:{col};'
                f'background:{color};{border}" title="{tip}"></div>'
            )

        first_day = start + timedelta(days=w * 7)
        m = first_day.strftime("%b")
        if m != prev_month and first_day <= today:
            months.append(
                f'<div class="hm-month" style="grid-row:1;grid-column:{w + 2}">'
                f"{m}</div>"
            )
            prev_month = m

    style = (
        f"grid-template-columns:30px repeat({num_weeks},13px);"
        f"grid-template-rows:20px repeat(7,13px);"
    )
    return (
        f'<div class="heatmap-grid" style="{style}">'
        f'{"".join(months)}{"".join(days)}{"".join(cells)}</div>'
    )


# --- Feed glance ---


def render_glance(analysis):
    glance = analysis.get("at_a_glance")
    if not glance or not isinstance(glance, dict):
        return ""

    parts = []
    # Opening line — casual, reflects activity
    opening = glance.get("opening", "")
    if opening:
        parts.append(
            f'<div class="glance-section">{esc(opening)}</div>'
        )

    labels = [
        ("sharpest", "You're sharpest when:", "section-patterns"),
        ("stretch", "Stretch zone:", "section-growth"),
        ("try_next", "Try next:", "section-revisit"),
    ]
    for key, label, anchor in labels:
        text = glance.get(key, "")
        if text:
            parts.append(
                f'<div class="glance-section">'
                f'<strong>{label}</strong> {esc(text)} '
                f'<a href="#{anchor}" class="see-more">See more \u2192</a>'
                f'</div>'
            )
    if not parts:
        return ""
    return (
        '<div class="glance">'
        '<div class="glance-title">At a Glance</div>'
        f'<div class="glance-sections">{"".join(parts)}</div>'
        '</div>'
    )


# --- Categories bar chart ---


def render_categories(categories):
    if not categories:
        return ""
    max_count = categories[0][1]
    bars = []
    for cat, count in categories:
        pct = round(count / max_count * 100)
        bars.append(
            f'<div class="bar-row">'
            f'<div class="bar-label">{esc(cat)}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div>'
            f'<div class="bar-value">{count}</div></div>'
        )
    return (
        '<div class="chart-card">'
        '<div class="chart-title">Categories</div>'
        f'{"".join(bars)}</div>'
    )


# --- Word cloud ---


def render_word_cloud(words):
    if not words:
        return ""
    max_count = words[0][1]
    spans = []
    for word, count in words:
        size = 10 + round(count / max_count * 16)
        opacity = 0.5 + 0.5 * (count / max_count)
        spans.append(
            f'<span style="font-size:{size}px;opacity:{opacity:.2f}">{esc(word)}</span>'
        )
    return (
        '<div class="word-cloud-card">'
        '<div class="chart-title">Topics You Explore</div>'
        f'<div class="word-cloud">{" ".join(spans)}</div></div>'
    )


# --- Sections ---

SECTIONS = [
    ("coaching_patterns", "Coaching Patterns", "#eff6ff", "#1e40af", "#bfdbfe", "section-patterns"),
    ("thinking_patterns", "Thinking Patterns", "#f0f9ff", "#0c4a6e", "#7dd3fc", "section-thinking"),
    ("best_moments", "Best Moments", "#f0fdf4", "#166534", "#bbf7d0", "section-moments"),
    ("stuck_points", "Growth Areas", "#fff7ed", "#9a3412", "#fed7aa", "section-growth"),
    ("topics_to_revisit", "Topics to Revisit", "#eff6ff", "#1e40af", "#bfdbfe", "section-revisit"),
]


def render_sections(analysis):
    parts = []
    for key, title, bg, fg, border, anchor in SECTIONS:
        content = analysis.get(key)
        if not content:
            continue
        parts.append(
            f'<div id="{anchor}" class="card" style="background:{bg};border-color:{border}">'
            f'<h2 style="color:{fg}">{title}</h2>'
            f'<div class="card-body">{md_to_html(content)}</div></div>'
        )
    return "\n".join(parts)


# --- Recent sessions ---


def render_recent(sessions):
    if not sessions:
        return ""
    rows = []
    for s in sessions:
        insight = s.get("insight", "")
        approach = s.get("approach", "")
        i_cls = "good" if insight == "captured" else "missed"
        a_cls = "good" if approach == "aligned" else "missed"
        rows.append(
            f"<tr><td>{esc(s.get('date', ''))}</td>"
            f"<td>{esc(s.get('title', ''))}</td>"
            f'<td class="outcome {i_cls}">{esc(insight)}</td>'
            f'<td class="outcome {a_cls}">{esc(approach)}</td></tr>'
        )
    return (
        '<h2>Recent Sessions</h2>'
        '<table class="sessions"><thead><tr>'
        "<th>Date</th><th>Paper</th><th>Insight</th><th>Approach</th>"
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )


# --- Full page ---


def render(stats, activity, categories, words, recent, analysis):
    # Date range subtitle
    if activity:
        dates = sorted(activity.keys())
        d0 = date.fromisoformat(dates[0])
        subtitle = f"{d0.strftime('%b %d')} &ndash; {date.today().strftime('%b %d, %Y')}"
    else:
        subtitle = date.today().isoformat()

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>PaperDojo Report</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',-apple-system,sans-serif;background:#f8fafc;color:#334155;line-height:1.6;padding:48px 24px}}
.container{{max-width:840px;margin:0 auto}}
h1{{font-size:28px;font-weight:700;color:#0f172a;margin-bottom:4px}}
h2{{font-size:18px;font-weight:600;color:#0f172a;margin-bottom:12px}}
.subtitle{{color:#64748b;font-size:14px;margin-bottom:32px}}
.stats{{display:flex;gap:32px;padding:16px 0;border-top:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;margin-bottom:32px;flex-wrap:wrap}}
.stat-val{{font-size:24px;font-weight:700;color:#0f172a}}
.stat-lbl{{font-size:11px;color:#64748b;text-transform:uppercase}}
.heatmap-wrap{{background:white;border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin-bottom:32px;overflow-x:auto}}
.heatmap-wrap h2{{font-size:13px;color:#64748b;text-transform:uppercase;margin-bottom:8px}}
.heatmap-grid{{display:grid;gap:3px}}
.hm-cell{{width:13px;height:13px;border-radius:2px;cursor:default}}
.hm-month{{font-size:10px;color:#64748b;line-height:20px}}
.hm-day{{font-size:10px;color:#64748b;line-height:13px;text-align:right;padding-right:4px}}
.legend{{display:flex;align-items:center;gap:4px;margin-top:8px;font-size:11px;color:#64748b}}
.legend-cell{{width:11px;height:11px;border-radius:2px;display:inline-block}}
.card{{border:1px solid;border-radius:8px;padding:16px 20px;margin-bottom:16px}}
.card h2{{margin-bottom:8px}}
.card-body p{{font-size:14px;color:#334155;margin-bottom:8px;line-height:1.6}}
.card-body ul{{font-size:14px;color:#334155;margin:0 0 8px 20px}}
.card-body li{{margin-bottom:4px;line-height:1.5}}
.sessions{{width:100%;border-collapse:collapse;margin-top:8px}}
.sessions th{{font-size:12px;color:#64748b;text-transform:uppercase;text-align:left;padding:8px 12px;border-bottom:2px solid #e2e8f0}}
.sessions td{{font-size:14px;padding:10px 12px;border-bottom:1px solid #f1f5f9}}
.outcome{{font-weight:600;font-size:13px}}
.outcome.good{{color:#166534}}
.outcome.missed{{color:#b45309}}
.empty{{color:#94a3b8;font-size:13px;font-style:italic}}
.charts-row{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:32px}}
.chart-card{{background:white;border:1px solid #e2e8f0;border-radius:8px;padding:16px}}
.chart-title{{font-size:13px;font-weight:600;color:#64748b;text-transform:uppercase;margin-bottom:12px}}
.bar-row{{display:flex;align-items:center;margin-bottom:6px}}
.bar-label{{width:120px;font-size:12px;color:#475569;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.bar-track{{flex:1;height:6px;background:#f1f5f9;border-radius:3px;margin:0 8px}}
.bar-fill{{height:100%;border-radius:3px;background:#6366f1}}
.bar-value{{width:28px;font-size:12px;font-weight:500;color:#64748b;text-align:right}}
.word-cloud{{line-height:2;padding:8px 0}}
.word-cloud-card{{background:white;border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin-bottom:16px}}
.word-cloud span{{display:inline-block;margin:2px 6px;color:#334155;font-weight:500}}
.glance{{background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);border:1px solid #f59e0b;border-radius:12px;padding:20px 24px;margin-bottom:32px}}
.glance-title{{font-size:16px;font-weight:700;color:#92400e;margin-bottom:16px}}
.glance-sections{{display:flex;flex-direction:column;gap:12px}}
.glance-section{{font-size:14px;color:#78350f;line-height:1.6}}
.glance-section strong{{color:#92400e}}
.see-more{{color:#b45309;text-decoration:none;font-size:13px;white-space:nowrap}}
.see-more:hover{{text-decoration:underline}}
</style>
</head>
<body>
<div class="container">
<h1>PaperDojo Report</h1>
<p class="subtitle">{subtitle}</p>

{render_glance(analysis)}

<div class="stats">
<div><div class="stat-val">{stats['browsed']}</div><div class="stat-lbl">Papers Browsed</div></div>
<div><div class="stat-val">{stats['coached']}</div><div class="stat-lbl">Coached</div></div>
<div><div class="stat-val">{stats['insight_rate']}%</div><div class="stat-lbl">Insight Rate</div></div>
<div><div class="stat-val">{stats['approach_rate']}%</div><div class="stat-lbl">Approach Rate</div></div>
</div>

<div class="heatmap-wrap">
<h2>Activity</h2>
{render_heatmap(activity)}
<div class="legend">
<span>Less</span>
<div class="legend-cell" style="background:#ebedf0"></div>
<div class="legend-cell" style="background:#9be9a8"></div>
<div class="legend-cell" style="background:#40c463"></div>
<div class="legend-cell" style="background:#30a14e"></div>
<span>More</span>
<span style="margin-left:12px"></span>
<div class="legend-cell" style="background:#9be9a8;border:2px solid #e34c26"></div>
<span>Miss</span>
<div class="legend-cell" style="background:#9be9a8;border:2px solid #3b82f6"></div>
<span>Hit</span>
</div>
</div>

{render_word_cloud(words)}

<div class="charts-row">
{render_categories(categories)}
</div>

{render_sections(analysis)}
{render_recent(recent)}
</div>
</body>
</html>"""


if __name__ == "__main__":
    main()
