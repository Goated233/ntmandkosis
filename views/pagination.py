"""Reusable button pagination view."""
from __future__ import annotations

import discord


class PaginatorView(discord.ui.View):
    """Paginate a list of embeds with Previous/Next buttons."""
    def __init__(self, pages: list[discord.Embed], *, timeout: float = 180) -> None:
        super().__init__(timeout=timeout)
        self.pages = pages
        self.index = 0

    async def update(self, interaction: discord.Interaction) -> None:
        """Refresh the message with the current page."""
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, emoji="◀️")
    async def previous(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Move to the previous page."""
        self.index = (self.index - 1) % len(self.pages)
        await self.update(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, emoji="▶️")
    async def next(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        """Move to the next page."""
        self.index = (self.index + 1) % len(self.pages)
        await self.update(interaction)
