import pytest

from services.cards import CardRenderer, Image


@pytest.mark.skipif(Image is None, reason="Pillow is not installed")
def test_card_renderer_outputs_png():
    data = CardRenderer().render("Test", ["One", "Two"]).getvalue()
    assert data.startswith(b"\x89PNG")
