"""Warm, consistent Discord embed helpers."""
from __future__ import annotations

from typing import Iterable

try:
    import discord
except ModuleNotFoundError:  # allows pure utility tests without discord.py installed
    discord = None  # type: ignore

BLUSH = 0xF6A6C8
LAVENDER = 0xB8A6F6
MINT = 0xA6F6D2
ERROR = 0xF28B82


def warm_embed(title: str, description: str = "", *, color: int = BLUSH):
    """Create a soft relationship-themed embed."""
    if discord is None:
        raise RuntimeError("discord.py is required for embeds.")
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="NTM & Kosi Relationship Assistant • gentle, private, neutral")
    return embed


def error_embed(message: str):
    """Create a kind error embed with a next step."""
    return warm_embed("Let’s fix that together", f"{message}\n\nTry `,help` or open `,relationship`.", color=ERROR)


def progress_bar(percent: int, *, width: int = 12) -> str:
    """Render a compact text progress bar."""
    percent = max(0, min(100, int(percent)))
    filled = round(width * percent / 100)
    return "▓" * filled + "░" * (width - filled) + f" {percent}%"


def bullet_list(items: Iterable[str], *, empty: str = "Nothing here yet.") -> str:
    """Format a list for embeds without overflowing."""
    values = [f"• {item}" for item in items]
    return "\n".join(values) if values else empty
