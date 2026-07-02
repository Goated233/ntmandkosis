"""OpenAI-backed neutral relationship guidance service."""
from __future__ import annotations

from openai import AsyncOpenAI

SYSTEM_PROMPT = """You are a neutral relationship assistant for NTM and Kosi. Never take sides. Identify misunderstandings, summarize both viewpoints, ask clarifying questions, recommend fair compromises, encourage direct communication, and never shame either person. You are not a therapist and should encourage professional help for safety or crisis issues."""


class RelationshipAI:
    """Provides AI counseling, appreciation prompts, and mediation summaries."""
    def __init__(self, api_key: str = "") -> None:
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def complete(self, prompt: str) -> str:
        """Generate a neutral response or return a safe offline fallback."""
        if not self.client:
            return (
                "I’m running without an OpenAI key, so here is a gentle structure: describe what happened, "
                "name how each person may have felt, ask one clarifying question, and choose one small compromise."
            )
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.6,
        )
        return response.choices[0].message.content or "I’m here with you, but I could not form a response."

    async def mediate(self, what: str, feeling: str, need: str) -> str:
        """Create a neutral first-pass mediation for a concern."""
        return await self.complete(f"Concern: {what}\nFeeling: {feeling}\nNeed: {need}\nCreate a balanced mediation note.")
