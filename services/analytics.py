"""Relationship analytics calculations."""
from __future__ import annotations

from utils.embeds import progress_bar


class RelationshipAnalytics:
    """Builds human-friendly stats and progress summaries."""
    def goal_line(self, title: str, progress: int) -> str:
        """Format a goal with a progress bar."""
        return f"{title}: {progress_bar(progress)}"

    def love_language_hint(self, text: str) -> str:
        """Infer a likely love-language category from text."""
        lowered = text.lower()
        if any(word in lowered for word in ["gift", "present", "surprise"]):
            return "Receiving gifts"
        if any(word in lowered for word in ["help", "support", "do", "done"]):
            return "Acts of service"
        if any(word in lowered for word in ["call", "time", "movie", "game"]):
            return "Quality time"
        if any(word in lowered for word in ["hug", "cuddle", "touch"]):
            return "Physical touch"
        return "Words of affirmation"
