"""Validation, tag suggestions, and UX text helpers."""
from __future__ import annotations

KEYWORDS = {
    "call": "calls", "voice": "calls", "movie": "movies", "game": "games", "laugh": "happy",
    "miss": "long-distance", "visit": "visits", "gift": "gifts", "date": "dates", "comfort": "support",
}


def validate_text(value: str, *, minimum: int = 2, maximum: int = 1200) -> str:
    """Validate and normalize user-submitted text."""
    cleaned = " ".join(value.strip().split())
    if len(cleaned) < minimum:
        raise ValueError(f"Please write at least {minimum} characters so I understand you.")
    if len(cleaned) > maximum:
        raise ValueError(f"Please keep this under {maximum} characters.")
    return cleaned


def suggest_memory_tags(text: str) -> list[str]:
    """Suggest warm memory tags from natural language."""
    lowered = text.lower()
    tags = [tag for word, tag in KEYWORDS.items() if word in lowered]
    return sorted(set(tags or ["memory"]))[:5]
