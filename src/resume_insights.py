"""Resume strengths and improvement tips."""
from __future__ import annotations

import re
from collections import defaultdict

from .skill_extractor import SkillMention
from .text_processing import word_count

_SECTION_PATTERNS = {
    "Experience": r"\b(work )?experience\b|\bemployment\b|\bwork history\b",
    "Education": r"\beducation\b|\bb\.?sc\b|\bm\.?sc\b|\bbachelor|\bmaster|\bdegree\b|\buniversity\b",
    "Projects": r"\bprojects?\b",
    "Certifications": r"\bcertifications?\b|\bcertified\b|\bcertificate\b",
    "Skills": r"\bskills\b|\btechnical skills\b|\btools\b",
}
_METRIC_RE = re.compile(r"(\d+(\.\d+)?\s?(%|percent|x\b|k\b|m\b|million|billion))|[$€£]\s?\d|\b\d{2,}\b\s+(users|customers|records|rows|clients|models|reports|dashboards)", re.I)
_ACTION_VERBS = {"built", "developed", "designed", "led", "created", "implemented", "automated", "improved", "reduced",
                 "increased", "analyzed", "analysed", "delivered", "optimized", "optimised", "deployed", "launched",
                 "managed", "engineered", "streamlined", "migrated", "forecasted", "generated"}


def detect_sections(resume_text: str) -> dict[str, bool]:
    return {name: bool(re.search(p, resume_text, re.I)) for name, p in _SECTION_PATTERNS.items()}


def count_metrics(resume_text: str) -> int:
    return sum(1 for line in resume_text.split("\n") if _METRIC_RE.search(line))


def count_action_verbs(resume_text: str) -> int:
    words = re.findall(r"[a-z]+", resume_text.lower())
    return len({w for w in words if w in _ACTION_VERBS})


def build_strengths(matched: list[dict], extra_skills: list[str], resume_text: str) -> list[dict]:
    """Return [{"title", "detail"}] strengths in priority order."""
    strengths: list[dict] = []
    must = [m["skill"] for m in matched if m["importance"] == "required" and not m["implied"]]
    if must:
        strengths.append({"title": "Meets key requirements",
                          "detail": "Your resume evidences must-have skills: " + ", ".join(must[:8]) + "."})
    by_cat = defaultdict(list)
    for m in matched:
        by_cat[m["category"]].append(m["skill"])
    if by_cat:
        top_cat, skills = max(by_cat.items(), key=lambda kv: len(kv[1]))
        if len(skills) >= 2:
            strengths.append({"title": f"Strong {top_cat} coverage",
                              "detail": f"{len(skills)} relevant skills align here: {', '.join(skills[:6])}."})
    strong_evidence = [m["skill"] for m in matched if m["resume_mentions"] >= 3]
    if strong_evidence:
        strengths.append({"title": "Repeated, well-evidenced skills",
                          "detail": "Mentioned several times in your resume: " + ", ".join(strong_evidence[:6]) + "."})
    metrics = count_metrics(resume_text)
    if metrics >= 3:
        strengths.append({"title": "Quantified achievements",
                          "detail": f"About {metrics} lines contain measurable results - recruiters value this."})
    verbs = count_action_verbs(resume_text)
    if verbs >= 4:
        strengths.append({"title": "Action-oriented language",
                          "detail": f"You use {verbs} distinct strong action verbs (built, automated, improved...)."})
    if extra_skills:
        strengths.append({"title": "Extra value beyond the JD",
                          "detail": "Additional skills the employer didn't list but may value: " + ", ".join(extra_skills[:8]) + "."})
    sections = detect_sections(resume_text)
    if sections.get("Projects") and sections.get("Experience"):
        strengths.append({"title": "Balanced resume structure",
                          "detail": "Both experience and projects are present, which shows applied skills."})
    return strengths


def build_resume_tips(resume_text: str, missing_high: list[str]) -> list[str]:
    tips: list[str] = []
    wc = word_count(resume_text)
    if wc < 150:
        tips.append("Your resume text is very short - add detail on projects, tools used and outcomes.")
    elif wc > 1200:
        tips.append("Your resume is long - tighten it to the most relevant 1-2 pages for this role.")
    if count_metrics(resume_text) < 3:
        tips.append("Add measurable results (e.g. 'reduced reporting time by 30%') to at least 3 bullet points.")
    sections = detect_sections(resume_text)
    if not sections.get("Projects"):
        tips.append("Add a Projects section showing real work with the tools this job asks for.")
    if not sections.get("Skills"):
        tips.append("Add a dedicated Skills section so applicant-tracking systems find your keywords quickly.")
    if not sections.get("Certifications") and missing_high:
        tips.append("A short certification or course in a missing skill signals initiative to recruiters.")
    if count_action_verbs(resume_text) < 3:
        tips.append("Start bullets with strong action verbs (built, automated, analysed, delivered).")
    if missing_high:
        tips.append("If you have genuinely used " + ", ".join(missing_high[:3]) + ", name it explicitly in your resume.")
    return tips
