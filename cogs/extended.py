"""Generated useful relationship commands from the command catalog."""
from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from typing import Any

from discord.ext import commands

from config import Settings
from database.repository import RelationshipRepository
from services.ai import RelationshipAI
from services.analytics import RelationshipAnalytics
from services.command_catalog import COMMAND_SPECS, RelationshipCommandSpec
from services.guidance import validate_text
from utils.embeds import bullet_list, error_embed, warm_embed

LOGGER = logging.getLogger(__name__)

PROMPTS: dict[str, str] = {
    "reassure": "Try: ‘I love you, I’m here, and one hard moment doesn’t erase us.’",
    "goodmorning": "Try: ‘Good morning love. I hope today is gentle to you. I’m proud of you already.’",
    "goodnight": "Try: ‘Sleep well, my love. Whatever happened today, I’m still choosing us tomorrow.’",
    "comfort": "First validate the feeling, then offer one concrete support: listen, call, space, or reassurance.",
    "listen": "Listen checklist: repeat what you heard, ask if you got it right, validate the feeling, then ask what they need.",
    "cooldown": "Take 20 minutes, drink water, write the feeling without sending it, then return with one clear need.",
    "truth": "Truth: What is one small thing I do that makes you feel loved?",
    "dare": "Dare: Send a 20-second voice note saying three things you appreciate.",
    "question": "Connection question: What moment made you feel closest to me this week?",
    "wouldyourather": "Would you rather have a surprise movie night or a planned deep-talk call?",
}


class ExtendedRelationshipCommands(commands.Cog):
    """Registers 50 useful relationship commands without duplicating handlers."""

    def __init__(self, bot: commands.Bot, repo: RelationshipRepository, ai: RelationshipAI, settings: Settings) -> None:
        self.bot = bot
        self.repo = repo
        self.ai = ai
        self.settings = settings
        self.analytics = RelationshipAnalytics()
        self._registered: list[str] = []

    async def cog_load(self) -> None:
        """Attach generated commands when the cog loads."""
        for spec in COMMAND_SPECS:
            if self.bot.get_command(spec.name):
                continue
            command = commands.Command(self._make_callback(spec), name=spec.name, help=spec.description, usage=spec.example)
            self.bot.add_command(command)
            self._registered.append(spec.name)
        LOGGER.info("Registered %s extended relationship commands", len(self._registered))

    async def cog_unload(self) -> None:
        """Remove generated commands when the cog unloads."""
        for name in self._registered:
            self.bot.remove_command(name)

    def _make_callback(self, spec: RelationshipCommandSpec) -> Callable[..., Coroutine[Any, Any, None]]:
        """Build a command callback for one catalog spec."""
        async def callback(ctx: commands.Context, *, text: str = "") -> None:
            if not await self._allowed(ctx):
                return
            if spec.action in {"save", "tracker"}:
                await self._save(ctx, spec, text)
            elif spec.action == "prompt":
                await ctx.send(embed=warm_embed(spec.description, PROMPTS.get(spec.name, "Try one small, kind action today.")))
            elif spec.action == "ai":
                await self._ai(ctx, spec, text)
            elif spec.action == "stats":
                await self._stats(ctx, spec)
            elif spec.action == "love":
                await self._love(ctx, text)
            elif spec.action == "recent":
                await self._recent(ctx, spec)
            else:
                await ctx.send(embed=error_embed("This command is not configured correctly yet."))
        callback.__name__ = f"generated_{spec.name}"
        callback.__doc__ = spec.description
        return callback

    async def _allowed(self, ctx: commands.Context) -> bool:
        """Return whether the caller may use this private bot."""
        allowed = ctx.author.id in self.settings.partner_ids or ctx.author.id in self.settings.owner_ids
        if not allowed:
            await ctx.send(embed=error_embed("This is a private bot for NTM and Kosi."))
        return allowed

    async def _save(self, ctx: commands.Context, spec: RelationshipCommandSpec, text: str) -> None:
        """Save a structured note or tracker entry."""
        if not text:
            await ctx.send(embed=error_embed(f"Please include what to save. Example: `{spec.example}`"))
            return
        cleaned = validate_text(text, minimum=2, maximum=1000)
        document = {"author_id": ctx.author.id, "kind": spec.kind, "title": cleaned, "text": cleaned, "status": "planned"}
        await self.repo.create(spec.collection, document)
        await ctx.send(embed=warm_embed("Saved", f"Saved **{spec.category}** item: {cleaned}"))
        if ctx.guild:
            await self.repo.log_event(self.bot, ctx.guild.id, f"{spec.name} saved", f"{ctx.author} saved: {cleaned[:200]}")

    async def _ai(self, ctx: commands.Context, spec: RelationshipCommandSpec, text: str) -> None:
        """Generate a neutral AI response for a command."""
        prompt = text or spec.description
        async with ctx.typing():
            response = await self.ai.complete(f"Command: {spec.name}\nUser text: {prompt}\nRespond warmly, briefly, and neutrally.")
        await ctx.send(embed=warm_embed(spec.description, response))

    async def _stats(self, ctx: commands.Context, spec: RelationshipCommandSpec) -> None:
        """Display relationship stats for generated stat commands."""
        stats = await self.repo.stats()
        await ctx.send(embed=warm_embed(spec.description, bullet_list(f"{name}: {count}" for name, count in stats.items())))

    async def _love(self, ctx: commands.Context, text: str) -> None:
        """Analyze love-language hints from user text."""
        if not text:
            await ctx.send(embed=error_embed("Add a sentence to analyze. Example: `,lovelanguage I feel loved when we call`."))
            return
        await ctx.send(embed=warm_embed("Love language hint", self.analytics.love_language_hint(text)))

    async def _recent(self, ctx: commands.Context, spec: RelationshipCommandSpec) -> None:
        """Show recent items from a collection."""
        docs = await self.repo.recent(spec.collection, limit=5)
        lines = [doc.get("text") or doc.get("title") or "Saved item" for doc in docs]
        await ctx.send(embed=warm_embed(spec.description, bullet_list(lines)))
