"""Production entrypoint for the NTM & Kosi relationship assistant bot."""
from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

from cogs.admin import AdminCog
from cogs.extended import ExtendedRelationshipCommands
from cogs.help import HelpCog
from cogs.relationship import RelationshipCog
from config import get_settings
from database.client import MongoService
from database.repository import RelationshipRepository
from database.sqlite_repository import SQLiteRelationshipRepository
from events.reminders import ReminderEvents
from services.ai import RelationshipAI
from utils.embeds import error_embed
from utils.logging import configure_logging

LOGGER = logging.getLogger(__name__)


class RelationshipBot(commands.Bot):
    """Discord bot wired with the configured database, AI services, and cogs."""
    def __init__(self) -> None:
        self.settings = get_settings()
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=self.settings.command_prefix, intents=intents, help_command=None, owner_ids=self.settings.owner_ids)
        self.mongo: MongoService | None = None
        if self.settings.normalized_database_backend == "mongodb":
            self.mongo = MongoService(self.settings.mongodb_uri, self.settings.mongodb_db)
            self.repo = RelationshipRepository(self.mongo.db)
            LOGGER.info("Using MongoDB repository", extra={"database": self.settings.mongodb_db})
        else:
            self.repo = SQLiteRelationshipRepository(self.settings.sqlite_path)
            LOGGER.info("Using SQLite repository", extra={"sqlite_path": self.settings.sqlite_path})
        self.ai = RelationshipAI(self.settings.openai_api_key)

    async def setup_hook(self) -> None:
        """Initialize database indexes and register cogs."""
        await self.repo.ensure_indexes()
        await self.add_cog(RelationshipCog(self, self.repo, self.ai, self.settings))
        await self.add_cog(AdminCog(self, self.repo))
        await self.add_cog(HelpCog(self))
        await self.add_cog(ExtendedRelationshipCommands(self, self.repo, self.ai, self.settings))
        await self.add_cog(ReminderEvents(self))
        LOGGER.info("Relationship bot setup complete")

    async def close(self) -> None:
        """Cleanly close Discord and database resources."""
        if self.mongo is not None:
            self.mongo.close()
        elif hasattr(self.repo, "close"):
            self.repo.close()
        await super().close()

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Send friendly, actionable errors for command failures."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(embed=error_embed("I don’t know that command yet. Open the guided hub with `,relationship`."))
            return
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            await ctx.send(embed=error_embed("That command needs a little more information. Check `,help` for examples."))
            return
        LOGGER.exception("Command failed", exc_info=error)
        await ctx.send(embed=error_embed("Something went wrong, but I logged it so it can be fixed."))


async def main() -> None:
    """Run the bot from environment configuration."""
    settings = get_settings()
    configure_logging(settings.log_level)
    if not settings.discord_token:
        raise RuntimeError("DISCORD_TOKEN is required to run the bot.")
    async with RelationshipBot() as bot:
        await bot.start(settings.discord_token)


if __name__ == "__main__":
    asyncio.run(main())
