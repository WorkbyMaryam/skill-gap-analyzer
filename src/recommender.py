"""Turn skill gaps into prioritised, actionable recommendations."""
from __future__ import annotations

from .scorer import transferable_from
from .skill_extractor import SkillMention
from .skills_db import CATEGORY_LEARNING, IMPLIES, SKILL_TIPS


def priority_for(m: SkillMention) -> str:
    if m.importance == "required" or m.weight >= 2.0:
        return "High"
    if m.importance == "preferred" and m.weight < 1.0:
        return "Low"
    return "Medium"


def build_gaps(missing: dict[str, SkillMention], resume_skills: set[str]) -> list[dict]:
    """Return missing skills sorted by priority, with learning guidance."""
    order = {"High": 0, "Medium": 1, "Low": 2}
    gaps = []
    for skill, m in missing.items():
        eta, generic = CATEGORY_LEARNING.get(m.category, ("2-4 weeks", "Study the fundamentals and build a small project."))
        similar = transferable_from(skill, resume_skills)
        if similar:
            eta = "1-2 weeks"          # head start from a similar tool
        gaps.append({
            "skill": skill, "category": m.category, "priority": priority_for(m), "importance": m.importance,
            "jd_mentions": m.count, "weight": round(m.weight, 2), "transferable_from": similar,
            "estimated_time": eta, "how_to_learn": SKILL_TIPS.get(skill, generic),
        })
    gaps = _bundle_redundant(gaps)
    gaps.sort(key=lambda g: (order[g["priority"]], -g["weight"], g["skill"]))
    for i, g in enumerate(gaps, 1):
        g["rank"] = i
    return gaps


def _bundle_redundant(gaps: list[dict]) -> list[dict]:
    """Fold a gap into a more advanced missing skill of the same category that already implies it
    (e.g. 'Excel' is covered when learning 'Advanced Excel'), so the list has no duplicates."""
    by_name = {g["skill"]: g for g in gaps}
    folded = set()
    for g in gaps:
        for implied in IMPLIES.get(g["skill"], []):
            other = by_name.get(implied)
            if other and other["category"] == g["category"] and implied not in folded:
                folded.add(implied)
                g["also_covers"] = g.get("also_covers", []) + [implied]
                if other["priority"] == "High":
                    g["priority"] = "High"
                g["weight"] = max(g["weight"], other["weight"])
    return [g for g in gaps if g["skill"] not in folded]


def _join(items: list[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def build_recommendation(gaps: list[dict], score: float) -> str:
    if not gaps:
        return "You cover every skill this job description lists. Focus on tailoring your resume wording and quantifying results."
    top = [g["skill"] for g in gaps[:3]]
    text = f"Focus on {_join(top)} fundamentals to improve your suitability for this role."
    quick = [g["skill"] for g in gaps if g["transferable_from"]][:2]
    if quick:
        text += f" Quick win: {_join(quick)} should be fast to pick up thanks to your related experience."
    if score >= 65:
        text += " You are already a strong candidate - highlight your matching skills prominently."
    elif score < 40:
        text += " Consider whether a closer-fit role or a short upskilling plan would help first."
    return text
