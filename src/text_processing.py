"""Text cleaning helpers."""
from __future__ import annotations

import re
import unicodedata

_BULLETS = "•●▪■◦‣∙·●○◆►➢➔✓✔"
_BULLET_RE = re.compile(f"[{re.escape(_BULLETS)}]")


def clean_text(text: str) -> str:
    """Normalise unicode, bullets and whitespace while preserving line breaks."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _BULLET_RE.sub("-", text)
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)           # zero-width chars
    text = re.sub(r"[^\S\n]+", " ", text)                              # collapse spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.strip() for line in text.split("\n")).strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))
