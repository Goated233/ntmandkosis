"""Polished help and command discovery."""
from __future__ import annotations

from collections import defaultdict

from discord.ext import commands

from services.command_catalog import COMMAND_SPECS
from utils.embeds import warm_embed
from views.pagination import PaginatorView


class HelpCog(commands.Cog):
    """Custom warm help pages with explanations and examples."""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context, category: str = "") -> None:
        """Show discoverable command categories and concrete examples."""
        pages = self._build_pages()
        if category:
            wanted = category.lower().replace("-", " ")
            pages = [page for page in pages if wanted in (page.title or "").lower()] or pages
        await ctx.send(embed=pages[0], view=PaginatorView(pages) if len(pages) > 1 else None)

    def _build_pages(self) -> list:
        """Build paginated help embeds from the command catalog."""
        intro = warm_embed("Relationship Bot Help", "Use `,setup` once in your server to set the log channel, then `,relationship` for the guided hub.")
        intro.add_field(name="How commands work", value="Most commands accept natural text. If a command needs AI, the bot shows typing while it thinks. If a command saves data, it stores it in MongoDB for stats, lists, and cards.", inline=False)
        intro.add_field(name="Core examples", value="`,checkin 8 6 missed you today`\n`,complain`\n`,memory our first movie night`\n`,goal 40 plan our visit`\n`,card`", inline=False)
        pages = [intro]
        grouped: dict[str, list[str]] = defaultdict(list)
        for spec in COMMAND_SPECS:
            grouped[spec.category].append(f"`{spec.example}` — {spec.description}")
        for category, lines in grouped.items():
            embed = warm_embed(f"Help: {category}", "\n".join(lines[:10]))
            if len(lines) > 10:
                embed.add_field(name="More", value="\n".join(lines[10:20]), inline=False)
            pages.append(embed)
        admin = warm_embed("Help: Setup & logs", "`,setup` — configure the current server and channel as the log channel.\n`,setlog` — move logs to the current channel.\n`,backup` — owner-only JSON backup preview.")
        pages.append(admin)
        return pages


async def setup(bot: commands.Bot) -> None:
    """Load the help cog without external dependencies."""
    await bot.add_cog(HelpCog(bot))
