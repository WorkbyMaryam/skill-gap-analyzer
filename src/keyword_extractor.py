"""Extract relevant keywords / key phrases from a job description."""
from __future__ import annotations

import re

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer

from .skills_db import SKILLS

# Generic job-post filler that carries no skill signal.
_FILLER = {
    "experience", "work", "working", "team", "teams", "ability", "able", "looking", "role", "candidate",
    "candidates", "years", "year", "strong", "skills", "skill", "company", "job", "position", "required",
    "requirements", "preferred", "responsibilities", "responsibility", "including", "include", "etc",
    "knowledge", "understanding", "excellent", "good", "great", "join", "opportunity", "will", "can",
    "new", "use", "using", "used", "make", "help", "ensure", "support", "related", "relevant", "plus",
    "environment", "business", "across", "within", "well", "best", "like", "need", "needs", "must",
    "have", "has", "based", "high", "level", "highly", "key", "various", "multiple", "day", "ideal",
    "seeking", "hiring", "apply", "benefits", "salary", "equal", "employer", "degree", "bachelor",
    "master", "field", "demonstrated", "proven", "minimum", "preferred", "nice", "bonus", "proficiency",
    "proficient", "familiarity", "hands", "solid", "build", "building", "develop", "developing",
    "hands-on", "non-technical", "growing", "clearly", "clear", "communicate", "non", "technical", "teams", "stakeholders",
}
_STOP = set(ENGLISH_STOP_WORDS) | _FILLER


def _analyzer(text: str) -> list[str]:
    tokens = re.findall(r"[a-z][a-z+#./-]{1,}", text.lower())
    return [t.strip(".-/") for t in tokens]


def extract_keywords(jd_text: str, skill_counts: dict[str, int], top_n: int = 20) -> list[dict]:
    """Return ranked keywords: [{"keyword", "count", "is_skill"}].

    Detected skills always rank first (they matter most); remaining slots are filled with
    domain n-grams (1-2 words) ranked by frequency, bigrams boosted, with filler removed.
    """
    skill_names = set(skill_counts)
    skill_lower = {s.lower() for s in skill_names}
    for name in skill_names:                      # also exclude every alias of detected skills
        skill_lower.update(SKILLS[name]["aliases"])
    vec = CountVectorizer(analyzer="word", tokenizer=_analyzer, preprocessor=None, lowercase=False,
                          token_pattern=None, ngram_range=(1, 2), stop_words=None)
    try:
        # n-grams must not span line breaks or punctuation, so fit on clauses and sum counts
        clauses = [c for c in re.split(r"[\n.;,:()]", jd_text.lower()) if c.strip()]
        counts = vec.fit_transform(clauses).sum(axis=0)
    except ValueError:
        return []
    terms = vec.get_feature_names_out()
    freq = [int(x) for x in counts.A1]
    min_unigram = 2 if len(jd_text.split()) > 120 else 1

    scored = []
    for term, c in zip(terms, freq):
        words = term.split()
        if any(w in _STOP or len(w) < 3 or w.isdigit() or w.endswith('ly') for w in words):
            continue
        if term in skill_lower or any(len(s) > 3 and (term in s or s in term) for s in skill_lower):
            continue
        if len(words) == 1 and c < min_unigram:
            continue
        if len(words) == 2 and c < 1:
            continue
        scored.append((c * (1.5 if len(words) == 2 else 1.0), term, int(c)))
    scored.sort(key=lambda x: (-x[0], x[1]))

    chosen: list[tuple[str, int]] = []
    for _, term, c in scored:
        if any(term in kept for kept, _ in chosen if len(kept.split()) > len(term.split())):
            continue        # unigram already covered by a chosen bigram
        chosen.append((term, c))

    skill_rows = [{"keyword": s, "count": skill_counts[s], "is_skill": True}
                  for s in sorted(skill_names, key=lambda k: (-skill_counts[k], k))]
    extra = [{"keyword": t, "count": c, "is_skill": False} for t, c in chosen]
    n_extra = min(len(extra), max(6, top_n - len(skill_rows)))
    return skill_rows[: top_n - n_extra] + extra[:n_extra]
