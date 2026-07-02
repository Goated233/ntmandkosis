from services.analytics import RelationshipAnalytics
from services.guidance import suggest_memory_tags, validate_text
from utils.embeds import progress_bar


def test_memory_tags_are_suggested():
    assert suggest_memory_tags("We laughed during our movie call") == ["calls", "happy", "movies"]


def test_validation_normalizes_spaces():
    assert validate_text("  hello    love  ") == "hello love"


def test_progress_bar_clamps():
    assert progress_bar(150).endswith("100%")
    assert progress_bar(-5).endswith("0%")


def test_love_language_hint():
    assert RelationshipAnalytics().love_language_hint("let us watch a movie on call") == "Quality time"


def test_catalog_has_50_extra_commands():
    from services.command_catalog import COMMAND_SPECS

    assert len(COMMAND_SPECS) == 50
    assert len({spec.name for spec in COMMAND_SPECS}) == 50
    assert all(spec.example.startswith(",") for spec in COMMAND_SPECS)
