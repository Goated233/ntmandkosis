"""Owner/admin commands for setup, backup, and logging configuration."""
from __future__ import annotations

import json

from discord.ext import commands

from database.repository import RelationshipRepository
from utils.embeds import warm_embed


class AdminCog(commands.Cog):
    """Private owner tools for the relationship bot."""
    def __init__(self, bot: commands.Bot, repo: RelationshipRepository) -> None:
        self.bot = bot
        self.repo = repo

    @commands.command(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def setup_server(self, ctx: commands.Context) -> None:
        """Configure the current server and channel as the relationship log channel."""
        if ctx.guild is None:
            await ctx.send("Use `,setup` inside the server where you want logs configured.")
            return
        await self.repo.set_logging_channel(ctx.guild.id, ctx.channel.id)
        embed = warm_embed("Relationship bot setup complete", f"This server is connected. I’ll use {ctx.channel.mention} as the log channel.")
        embed.add_field(name="Next steps", value="Use `,relationship` for the guided hub, `,help` for examples, and `,setlog` later if you want a different log channel.", inline=False)
        await ctx.send(embed=embed)
        await self.repo.log_event(self.bot, ctx.guild.id, "Setup completed", f"Configured by {ctx.author} in #{ctx.channel}.")

    @commands.command(name="backup")
    @commands.is_owner()
    async def backup(self, ctx: commands.Context) -> None:
        """Export recent relationship data as JSON text."""
        data = {name: await self.repo.recent(name, limit=100) for name in ["memories", "complaints", "checkins", "goals", "trackers", "journals", "gratitude", "affirmations"]}
        safe = json.dumps(data, default=str, indent=2)[:1900]
        await ctx.send(embed=warm_embed("Backup preview", f"```json\n{safe}\n```"))

    @commands.command(name="setlog")
    @commands.has_permissions(manage_guild=True)
    async def setlog(self, ctx: commands.Context) -> None:
        """Set the current channel as the relationship bot log channel."""
        if ctx.guild is None:
            await ctx.send("This command must be used in a server.")
            return
        await self.repo.set_logging_channel(ctx.guild.id, ctx.channel.id)
        await ctx.send(embed=warm_embed("Logging configured", f"I’ll log important bot events in {ctx.channel.mention}."))
        await self.repo.log_event(self.bot, ctx.guild.id, "Log channel changed", f"New log channel: #{ctx.channel}")
