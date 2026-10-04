"""Skill extraction with boundary-safe matching and JD importance weighting."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

from .skills_db import CASE_SENSITIVE_ALIASES, IMPLIES, SKILLS

WEIGHT_REQUIRED = 2.0
WEIGHT_NORMAL = 1.0
WEIGHT_PREFERRED = 0.5
REPEAT_BONUS = 0.25     # per extra mention
REPEAT_BONUS_CAP = 4

_REQUIRED_CUES = re.compile(
    r"\b(must[- ]have|must|required|requirements?|mandatory|essential|proficien\w*|expert\w*|"
    r"strong|solid|extensive|minimum|hands[- ]on|advanced|qualifications?|what you(?:'|’)?ll need|"
    r"what we(?:'|’)?re looking for|you have|you bring)\b", re.I)
_PREFERRED_CUES = re.compile(
    r"\b(preferred|nice[- ]to[- ]have|bonus|a plus|is a plus|desirable|good to have|advantage|"
    r"optional|beneficial|familiarity|exposure to|ideally|not required)\b|\bplus\b", re.I)


@dataclass
class SkillMention:
    skill: str
    category: str
    count: int = 0
    weight: float = WEIGHT_NORMAL
    importance: str = "standard"          # required | standard | preferred
    implied: bool = False                 # resume only: credited via another skill
    implied_by: list[str] = field(default_factory=list)


@lru_cache(maxsize=1)
def _compiled_patterns() -> dict:
    """Pre-compile one case-insensitive and one case-sensitive regex per skill."""
    left, right = r"(?<![A-Za-z0-9+#])", r"(?![A-Za-z0-9+#])(?!\.[A-Za-z0-9])"
    patterns = {}
    for skill, meta in SKILLS.items():
        loose, strict = [], []
        for alias in sorted(meta["aliases"], key=len, reverse=True):
            if alias in CASE_SENSITIVE_ALIASES or alias.lower() in CASE_SENSITIVE_ALIASES:
                strict += [re.escape(v) for v in {alias.capitalize(), alias.upper()}]
            else:
                loose.append(re.escape(alias))
        loose_re = re.compile(f"{left}(?:{'|'.join(loose)}){right}", re.I) if loose else None
        strict_re = re.compile(f"{left}(?:{'|'.join(strict)}){right}") if strict else None
        patterns[skill] = (loose_re, strict_re)
    return patterns


def _count_in(line: str, skill: str) -> int:
    loose_re, strict_re = _compiled_patterns()[skill]
    n = len(loose_re.findall(line)) if loose_re else 0
    n += len(strict_re.findall(line)) if strict_re else 0
    return n


def _line_importance(clause: str, section: str | None) -> str:
    if _PREFERRED_CUES.search(clause):
        return "preferred"
    if _REQUIRED_CUES.search(clause):
        return "required"
    return section or "standard"


def _header_section(line: str) -> tuple[bool, str | None]:
    """Detect a section header and the importance it sets for following lines."""
    stripped = line.strip().lstrip("#*- ").rstrip()
    is_header = bool(stripped) and len(stripped) <= 70 and (stripped.endswith(":") or line.lstrip().startswith("#") or stripped.isupper())
    if not is_header:
        return False, None
    if _PREFERRED_CUES.search(stripped):
        return True, "preferred"
    if _REQUIRED_CUES.search(stripped):
        return True, "required"
    return True, "standard"


def extract_skills(text: str, *, weighted: bool = False) -> dict[str, SkillMention]:
    """Find all known skills in `text`.

    With weighted=True (job descriptions) each skill gets an importance weight from
    surrounding cues ("must have", "nice to have", section headers) and repetition.
    """
    found: dict[str, SkillMention] = {}
    section: str | None = None
    levels: dict[str, list[str]] = {}

    for line in text.split("\n"):
        if not line.strip():
            continue
        is_header, new_section = _header_section(line)
        has_items = is_header and ":" in line and line.split(":", 1)[1].strip()
        if is_header and not has_items:
            section = None if new_section == "standard" else new_section
            continue
        if is_header and has_items:                       # "Nice to have: Docker, AWS"
            section_for_line = None if new_section == "standard" else new_section
        else:
            section_for_line = section
        for clause in re.split(r"(?<=[.;!?])\s+", line):
            importance = _line_importance(clause, section_for_line)
            for skill, meta in SKILLS.items():
                n = _count_in(clause, skill)
                if not n:
                    continue
                m = found.setdefault(skill, SkillMention(skill, meta["category"]))
                m.count += n
                levels.setdefault(skill, []).extend([importance] * n)

    if weighted:
        for skill, m in found.items():
            lv = levels[skill]
            m.importance = "required" if "required" in lv else ("standard" if "standard" in lv else "preferred")
            base = {"required": WEIGHT_REQUIRED, "standard": WEIGHT_NORMAL, "preferred": WEIGHT_PREFERRED}[m.importance]
            m.weight = base + REPEAT_BONUS * min(m.count - 1, REPEAT_BONUS_CAP)
    return found


def expand_implied(found: dict[str, SkillMention]) -> dict[str, SkillMention]:
    """Add skills that are proven by other skills (e.g. Pandas -> Python)."""
    expanded = dict(found)
    for skill in list(found):
        for implied in IMPLIES.get(skill, []):
            if implied in expanded:
                continue
            expanded[implied] = SkillMention(implied, SKILLS[implied]["category"], count=0,
                                             implied=True, implied_by=[skill])
        for implied in IMPLIES.get(skill, []):
            if expanded[implied].implied and skill not in expanded[implied].implied_by:
                expanded[implied].implied_by.append(skill)
    return expanded
