"""Guided relationship assistant commands and views."""
from __future__ import annotations

import discord
from discord.ext import commands

from config import Settings
from database.repository import RelationshipRepository
from services.ai import RelationshipAI
from services.analytics import RelationshipAnalytics
from services.cards import CardRenderer
from services.guidance import suggest_memory_tags, validate_text
from utils.embeds import bullet_list, error_embed, warm_embed


class RelationshipCog(commands.Cog):
    """Personal relationship assistant for NTM and Kosi across DMs and servers."""
    def __init__(self, bot: commands.Bot, repo: RelationshipRepository, ai: RelationshipAI, settings: Settings) -> None:
        self.bot = bot
        self.repo = repo
        self.ai = ai
        self.settings = settings
        self.analytics = RelationshipAnalytics()
        self.cards = CardRenderer()

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Restrict personal relationship commands to the configured couple and owners."""
        allowed = ctx.author.id in self.settings.partner_ids or ctx.author.id in self.settings.owner_ids
        if not allowed:
            await ctx.send(embed=error_embed("This is a private bot for NTM and Kosi."))
        return allowed

    @commands.command(name="relationship", aliases=["hub", "home"])
    async def relationship(self, ctx: commands.Context) -> None:
        """Open the guided relationship hub."""
        embed = warm_embed("Your Relationship Hub", "Choose a gentle action below, or use `,help` to discover every feature.")
        embed.add_field(name="Guided flows", value="Daily check-in • Concern mediation • Memories • Shared trackers", inline=False)
        await ctx.send(embed=embed, view=RelationshipHubView(self))

    @commands.command(name="checkin")
    async def checkin(self, ctx: commands.Context, mood: int | None = None, energy: int | None = None, *, note: str = "") -> None:
        """Log a daily check-in, or open the guided modal when no values are provided."""
        if mood is None or energy is None:
            await ctx.send(embed=warm_embed("Daily check-in", "Use the button to share your mood privately and gently."), view=CheckInStartView(self))
            return
        if not 1 <= mood <= 10 or not 1 <= energy <= 10:
            await ctx.send(embed=error_embed("Mood and energy must be from 1 to 10."))
            return
        await self.repo.create("checkins", {"author_id": ctx.author.id, "mood": mood, "energy": energy, "note": validate_text(note or "No note", minimum=2, maximum=800)})
        await ctx.send(embed=warm_embed("Check-in saved", f"Mood: **{mood}/10**\nEnergy: **{energy}/10**\nThank you for being honest."))
        if ctx.guild:
            await self.repo.log_event(self.bot, ctx.guild.id, "Check-in saved", f"{ctx.author} logged mood {mood}/10 and energy {energy}/10.")

    @commands.command(name="complain", aliases=["concern", "mediate"])
    async def complain(self, ctx: commands.Context) -> None:
        """Start a guided, neutral complaint mediation workflow."""
        await ctx.send(embed=warm_embed("Guided concern", "Press the button and I’ll collect the concern safely with a modal."), view=ComplaintStartView(self))

    @commands.command(name="memory")
    async def memory(self, ctx: commands.Context, *, text: str = "") -> None:
        """Save a memory with automatic tags."""
        if not text:
            await ctx.send(embed=warm_embed("Save a memory", "Use `,memory we laughed during our movie call` or the hub button."))
            return
        text = validate_text(text, minimum=3, maximum=1200)
        tags = suggest_memory_tags(text)
        await self.repo.create("memories", {"author_id": ctx.author.id, "text": text, "tags": tags})
        await ctx.send(embed=warm_embed("Memory saved", f"{text}\n\nTags: `{', '.join(tags)}`"))
        if ctx.guild:
            await self.repo.log_event(self.bot, ctx.guild.id, "Memory saved", f"{ctx.author} saved a memory with tags: {', '.join(tags)}.")

    @commands.command(name="add")
    async def add_tracker(self, ctx: commands.Context, kind: str, *, title: str) -> None:
        """Add bucket, promise, visit, movie, game, or reading tracker items."""
        if kind not in {"bucket", "promise", "visit", "movie", "game", "reading"}:
            await ctx.send(embed=error_embed("Kind must be bucket, promise, visit, movie, game, or reading."))
            return
        await self.repo.create("trackers", {"kind": kind, "title": validate_text(title, minimum=2, maximum=140), "status": "planned"})
        await ctx.send(embed=warm_embed("Shared item added", f"Added **{title}** to `{kind}`."))
        if ctx.guild:
            await self.repo.log_event(self.bot, ctx.guild.id, "Shared item added", f"{ctx.author} added {kind}: {title}.")

    @commands.command(name="goal")
    async def goal(self, ctx: commands.Context, progress: int, *, title: str) -> None:
        """Add a relationship goal with a progress bar."""
        if not 0 <= progress <= 100:
            await ctx.send(embed=error_embed("Goal progress must be between 0 and 100."))
            return
        await self.repo.create("goals", {"title": validate_text(title, minimum=2, maximum=120), "progress": progress, "owner_id": ctx.author.id})
        await ctx.send(embed=warm_embed("Goal saved", self.analytics.goal_line(title, progress)))

    @commands.command(name="list")
    async def list_items(self, ctx: commands.Context, collection: str = "memories") -> None:
        """Show recent memories, goals, concerns, check-ins, or tracker items."""
        mapping = {"memories": "memories", "goals": "goals", "concerns": "complaints", "checkins": "checkins", "trackers": "trackers"}
        if collection not in mapping:
            await ctx.send(embed=error_embed("Choose memories, goals, concerns, checkins, or trackers."))
            return
        docs = await self.repo.recent(mapping[collection], limit=10)
        lines = [doc.get("text") or doc.get("title") or doc.get("what_happened") or f"Mood {doc.get('mood')}/10" for doc in docs]
        await ctx.send(embed=warm_embed(f"Recent {collection}", bullet_list(lines)))

    @commands.command(name="stats")
    async def stats(self, ctx: commands.Context) -> None:
        """Show relationship communication statistics."""
        stats = await self.repo.stats()
        embed = warm_embed("Relationship stats", "A soft snapshot of how much you two have been tracking together.")
        for name, count in stats.items():
            embed.add_field(name=name.title(), value=str(count), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="card")
    async def card(self, ctx: commands.Context) -> None:
        """Generate a relationship profile image card."""
        stats = await self.repo.stats()
        buffer = self.cards.render("NTM & Kosi", [f"{name.title()}: {count}" for name, count in stats.items()])
        await ctx.send(file=discord.File(buffer, filename="relationship-card.png"))

    @commands.command(name="appreciate")
    async def appreciate(self, ctx: commands.Context) -> None:
        """Generate an AI appreciation prompt."""
        async with ctx.typing():
            text = await self.ai.complete("Give one sweet, specific appreciation prompt for an online couple named NTM and Kosi.")
        await ctx.send(embed=warm_embed("Appreciation prompt", text))


class RelationshipHubView(discord.ui.View):
    """Buttons that expose the main guided workflows."""
    def __init__(self, cog: RelationshipCog) -> None:
        super().__init__(timeout=300)
        self.cog = cog

    @discord.ui.button(label="Daily check-in", style=discord.ButtonStyle.primary, emoji="💗")
    async def checkin(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.send_modal(CheckInModal(self.cog))

    @discord.ui.button(label="Share concern", style=discord.ButtonStyle.danger, emoji="🕊️")
    async def concern(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.send_modal(ComplaintModal(self.cog))

    @discord.ui.button(label="Save memory", style=discord.ButtonStyle.success, emoji="📸")
    async def memory(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.send_modal(MemoryModal(self.cog))


class CheckInStartView(discord.ui.View):
    """Single-button entry to the daily check-in modal."""
    def __init__(self, cog: RelationshipCog) -> None:
        super().__init__(timeout=180); self.cog = cog
    @discord.ui.button(label="Open check-in", style=discord.ButtonStyle.primary)
    async def open(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.send_modal(CheckInModal(self.cog))


class ComplaintStartView(CheckInStartView):
    """Single-button entry to the concern modal."""
    @discord.ui.button(label="Open concern form", style=discord.ButtonStyle.danger)
    async def concern_open(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.send_modal(ComplaintModal(self.cog))


class CheckInModal(discord.ui.Modal, title="Daily check-in"):
    """Modal for daily mood and energy tracking."""
    mood = discord.ui.TextInput(label="Mood 1-10", max_length=2)
    energy = discord.ui.TextInput(label="Energy 1-10", max_length=2)
    note = discord.ui.TextInput(label="Anything you want remembered?", style=discord.TextStyle.paragraph, required=False, max_length=800)
    def __init__(self, cog: RelationshipCog) -> None:
        super().__init__(); self.cog = cog
    async def on_submit(self, interaction: discord.Interaction) -> None:
        mood, energy = int(str(self.mood)), int(str(self.energy))
        await self.cog.repo.create("checkins", {"author_id": interaction.user.id, "mood": mood, "energy": energy, "note": str(self.note)})
        await interaction.response.send_message(embed=warm_embed("Check-in saved", "Thank you for sharing honestly."), ephemeral=True)


class MemoryModal(discord.ui.Modal, title="Save a memory"):
    """Modal for memory capture with automatic tags."""
    text = discord.ui.TextInput(label="What happened?", style=discord.TextStyle.paragraph, max_length=1200)
    def __init__(self, cog: RelationshipCog) -> None:
        super().__init__(); self.cog = cog
    async def on_submit(self, interaction: discord.Interaction) -> None:
        tags = suggest_memory_tags(str(self.text))
        await self.cog.repo.create("memories", {"author_id": interaction.user.id, "text": str(self.text), "tags": tags})
        await interaction.response.send_message(embed=warm_embed("Memory saved", f"Tags: `{', '.join(tags)}`"), ephemeral=True)


class ComplaintModal(discord.ui.Modal, title="Share a concern"):
    """Modal that starts neutral complaint mediation."""
    what = discord.ui.TextInput(label="What happened?", style=discord.TextStyle.paragraph, max_length=1200)
    feeling = discord.ui.TextInput(label="How did it make you feel?", max_length=500)
    need = discord.ui.TextInput(label="What do you need next?", max_length=500)
    def __init__(self, cog: RelationshipCog) -> None:
        super().__init__(); self.cog = cog
    async def on_submit(self, interaction: discord.Interaction) -> None:
        other = next(iter(self.cog.settings.partner_ids - {interaction.user.id}), interaction.user.id)
        await interaction.response.defer(ephemeral=True, thinking=True)
        summary = await self.cog.ai.mediate(str(self.what), str(self.feeling), str(self.need))
        await self.cog.repo.create("complaints", {"author_id": interaction.user.id, "other_id": other, "what_happened": str(self.what), "feeling": str(self.feeling), "need": str(self.need), "ai_summary": summary, "status": "open"})
        await interaction.followup.send(embed=warm_embed("Concern saved", summary), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """discord.py extension hook intentionally unused; bot.py injects dependencies."""
    return None
