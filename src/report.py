"""Export an AnalysisResult as Markdown or CSV."""
from __future__ import annotations

import csv
import io

from .analyzer import AnalysisResult


def to_markdown(r: AnalysisResult) -> str:
    L = [f"# Skill Gap Analysis", "", f"**Overall Match: {r.score:.0f}%** ({r.label})", ""]
    L += ["| Component | Score |", "|---|---|"]
    L += [f"| {k.replace('_', ' ').title()} | {v:.0f}% |" for k, v in r.components.items()]
    L += ["", "## Matching Skills"]
    L += [f"- ✓ {m['skill']}" + (f" (via {', '.join(m['implied_by'])})" if m["implied"] else "") for m in r.matching_skills] or ["- None"]
    L += ["", "## Missing Skills"]
    L += [f"- ✗ {m['skill']} [{m['priority']} priority]" for m in r.missing_skills] or ["- None"]
    L += ["", "## Top Skill Gaps"]
    L += [f"{g['rank']}. **{g['skill']}** - {g['priority']} priority, ~{g['estimated_time']}. {g['how_to_learn']}" for g in r.gaps[:10]] or ["None"]
    L += ["", "## Recommendation", r.recommendation, "", "## Resume Strengths"]
    L += [f"- **{s['title']}**: {s['detail']}" for s in r.strengths] or ["- None identified"]
    L += ["", "## Job Description Keywords"]
    L += [f"- {k['keyword']} ({'in resume' if k['in_resume'] else 'missing'})" for k in r.keywords]
    L += ["", "## Resume Tips"] + [f"- {t}" for t in r.resume_tips]
    return "\n".join(L) + "\n"


def gaps_to_csv(r: AnalysisResult) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["rank", "skill", "category", "priority", "importance", "jd_mentions", "estimated_time", "how_to_learn"])
    for g in r.gaps:
        w.writerow([g["rank"], g["skill"], g["category"], g["priority"], g["importance"], g["jd_mentions"], g["estimated_time"], g["how_to_learn"]])
    return buf.getvalue()
