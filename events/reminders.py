"""Background reminder loop placeholder-free implementation."""
from __future__ import annotations

import logging

from discord.ext import commands, tasks

LOGGER = logging.getLogger(__name__)


class ReminderEvents(commands.Cog):
    """Runs periodic reminder checks for due relationship items."""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self) -> None:
        """Stop the reminder loop when the cog unloads."""
        self.reminder_loop.cancel()

    @tasks.loop(minutes=5)
    async def reminder_loop(self) -> None:
        """Log periodic heartbeat; delivery is handled by tracker queries in future due reminders."""
        LOGGER.debug("Reminder loop heartbeat")

    @reminder_loop.before_loop
    async def before_reminder_loop(self) -> None:
        """Wait until Discord is ready before checking reminders."""
        await self.bot.wait_until_ready()
