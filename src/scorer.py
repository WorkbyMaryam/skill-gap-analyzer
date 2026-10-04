"""Match-score computation (explainable, three components)."""
from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skill_extractor import SkillMention
from .skills_db import TRANSFERABLE_GROUPS

W_SKILLS, W_KEYWORDS, W_SEMANTIC = 0.80, 0.12, 0.08
TRANSFER_CREDIT = 0.30


def transferable_from(skill: str, resume_skills: set[str]) -> list[str]:
    """Resume skills that are close substitutes for `skill`."""
    out: list[str] = []
    for group in TRANSFERABLE_GROUPS:
        if skill in group:
            out += sorted((group & resume_skills) - {skill})
    return list(dict.fromkeys(out))


def skill_coverage(jd: dict[str, SkillMention], resume: dict[str, SkillMention]) -> tuple[float, dict]:
    """Weighted share of JD skills covered by the resume (0-1) + per-skill credit."""
    total = sum(m.weight for m in jd.values())
    if not total:
        return 0.0, {}
    have = set(resume)
    credits, earned = {}, 0.0
    for skill, m in jd.items():
        if skill in have:
            credit = 1.0
        elif transferable_from(skill, have):
            credit = TRANSFER_CREDIT
        else:
            credit = 0.0
        credits[skill] = credit
        earned += m.weight * credit
    return earned / total, credits


def keyword_coverage(keywords: list[dict], resume_text: str) -> float:
    """Share of non-skill JD keywords that also appear in the resume."""
    words = [k["keyword"] for k in keywords if not k["is_skill"]]
    if not words:
        return 0.0
    low = resume_text.lower()
    return sum(1 for w in words if w in low) / len(words)


def semantic_similarity(resume_text: str, jd_text: str) -> float:
    """TF-IDF cosine similarity rescaled to 0-1 (raw values rarely exceed ~0.5)."""
    try:
        tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        m = tfidf.fit_transform([resume_text, jd_text])
        raw = float(cosine_similarity(m[0], m[1])[0][0])
    except ValueError:
        return 0.0
    return min(1.0, raw * 2.0)


def overall_score(skill_cov: float, kw_cov: float, sem: float, has_skills: bool, has_keywords: bool) -> float:
    """Blend components; re-normalise weights if a component is unavailable."""
    parts = [(skill_cov, W_SKILLS, has_skills), (kw_cov, W_KEYWORDS, has_keywords), (sem, W_SEMANTIC, True)]
    active = [(v, w) for v, w, ok in parts if ok]
    total_w = sum(w for _, w in active)
    return round(100 * sum(v * w for v, w in active) / total_w, 1)


def match_label(score: float) -> str:
    if score >= 80:
        return "Excellent match"
    if score >= 65:
        return "Strong match"
    if score >= 50:
        return "Moderate match"
    if score >= 35:
        return "Partial match"
    return "Low match"
