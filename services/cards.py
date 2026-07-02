"""Consistent Pillow image card generation."""
from __future__ import annotations

from io import BytesIO
from typing import Iterable

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # Pillow is optional in tests/imports
    Image = ImageDraw = ImageFont = None  # type: ignore


class CardRenderer:
    """Renders warm relationship image cards for profiles, memories, and stats."""
    def render(self, title: str, lines: Iterable[str]) -> BytesIO:
        """Return a PNG image buffer using the shared card style."""
        if Image is None:
            raise RuntimeError("Pillow is required for image cards.")
        image = Image.new("RGB", (900, 520), "#fff5fa")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((28, 28, 872, 492), radius=36, fill="#ffe1ef", outline="#f6a6c8", width=4)
        font_big = ImageFont.load_default(size=42)
        font = ImageFont.load_default(size=26)
        draw.text((70, 70), f"❤ {title}", fill="#7a3158", font=font_big)
        y = 150
        for line in lines:
            draw.text((80, y), f"• {line}", fill="#44283a", font=font)
            y += 46
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
