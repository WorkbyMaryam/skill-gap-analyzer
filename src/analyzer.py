"""High-level pipeline: resume text + JD text -> AnalysisResult."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

from . import keyword_extractor, recommender, resume_insights, scorer
from .skill_extractor import expand_implied, extract_skills
from .text_processing import clean_text, word_count

MIN_WORDS = 15


@dataclass
class AnalysisResult:
    score: float
    label: str
    components: dict
    matching_skills: list[dict]
    missing_skills: list[dict]
    gaps: list[dict]
    strengths: list[dict]
    extra_skills: list[str]
    keywords: list[dict]
    resume_tips: list[str]
    recommendation: str
    jd_skill_count: int
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def analyze(resume_text: str, jd_text: str) -> AnalysisResult:
    resume_text, jd_text = clean_text(resume_text), clean_text(jd_text)
    if word_count(resume_text) < MIN_WORDS:
        raise ValueError("The resume text is too short to analyse. Please provide more content.")
    if word_count(jd_text) < MIN_WORDS:
        raise ValueError("The job description is too short to analyse. Please provide more content.")

    jd = extract_skills(jd_text, weighted=True)
    resume_direct = extract_skills(resume_text)
    resume = expand_implied(resume_direct)
    have = set(resume)

    warnings: list[str] = []
    if not jd:
        warnings.append("No known skills were detected in the job description; the score relies on keywords and text similarity.")

    skill_cov, credits = scorer.skill_coverage(jd, resume)
    keywords = keyword_extractor.extract_keywords(jd_text, {s: m.count for s, m in jd.items()})
    low_resume = resume_text.lower()
    for k in keywords:
        k["in_resume"] = (k["keyword"] in have) if k["is_skill"] else (k["keyword"] in low_resume)
    kw_cov = scorer.keyword_coverage(keywords, resume_text)
    sem = scorer.semantic_similarity(resume_text, jd_text)
    has_kw = sum(1 for k in keywords if not k["is_skill"]) >= 3
    score = scorer.overall_score(skill_cov, kw_cov, sem, bool(jd), has_kw)

    matched, missing = [], {}
    for skill, m in sorted(jd.items(), key=lambda kv: (-kv[1].weight, kv[0])):
        if skill in have:
            r = resume[skill]
            matched.append({"skill": skill, "category": m.category, "importance": m.importance,
                            "jd_mentions": m.count, "resume_mentions": r.count,
                            "implied": r.implied, "implied_by": r.implied_by})
        else:
            missing[skill] = m

    gaps = recommender.build_gaps(missing, have)
    missing_rows = [{"skill": g["skill"], "category": g["category"], "importance": g["importance"],
                     "priority": g["priority"], "transferable_from": g["transferable_from"]} for g in gaps]
    extra = sorted(s for s in resume_direct if s not in jd)
    high_missing = [g["skill"] for g in gaps if g["priority"] == "High"] or [g["skill"] for g in gaps]

    return AnalysisResult(
        score=score, label=scorer.match_label(score),
        components={"skill_coverage": round(skill_cov * 100, 1), "keyword_coverage": round(kw_cov * 100, 1),
                    "text_similarity": round(sem * 100, 1)},
        matching_skills=matched, missing_skills=missing_rows, gaps=gaps,
        strengths=resume_insights.build_strengths(matched, extra, resume_text), extra_skills=extra,
        keywords=keywords, resume_tips=resume_insights.build_resume_tips(resume_text, high_missing),
        recommendation=recommender.build_recommendation(gaps, score),
        jd_skill_count=len(jd), warnings=warnings,
    )
