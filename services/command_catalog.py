"""Catalog of extra relationship assistant commands.

Each command is intentionally small, useful, and production-safe: commands either
save structured relationship data, show a guided prompt, or display tracked data.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RelationshipCommandSpec:
    """Definition for a generated relationship command."""

    name: str
    category: str
    description: str
    example: str
    action: str
    collection: str = "trackers"
    kind: str = "note"


COMMAND_SPECS: tuple[RelationshipCommandSpec, ...] = (
    RelationshipCommandSpec("gratitude", "Daily care", "Save one thing you appreciate about your partner.", ",gratitude I love how patient you were today", "save", "gratitude", "gratitude"),
    RelationshipCommandSpec("affirm", "Daily care", "Save a sweet affirmation.", ",affirm You are loved even on hard days", "save", "affirmations", "affirmation"),
    RelationshipCommandSpec("reassure", "Daily care", "Get a reassurance message to send your partner.", ",reassure", "prompt"),
    RelationshipCommandSpec("goodmorning", "Daily care", "Generate a good morning message idea.", ",goodmorning", "prompt"),
    RelationshipCommandSpec("goodnight", "Daily care", "Generate a good night message idea.", ",goodnight", "prompt"),
    RelationshipCommandSpec("missyou", "Daily care", "Save or generate an I-miss-you note.", ",missyou I miss your voice", "save", "notes", "miss_you"),
    RelationshipCommandSpec("comfort", "Daily care", "Get a comforting response idea.", ",comfort", "prompt"),
    RelationshipCommandSpec("apology", "Conflict care", "Draft a gentle apology without blame.", ",apology I was short earlier", "ai"),
    RelationshipCommandSpec("repair", "Conflict care", "Create a repair plan after tension.", ",repair We argued about texting back", "ai"),
    RelationshipCommandSpec("clarify", "Conflict care", "Turn a confusing issue into clarifying questions.", ",clarify She seemed distant", "ai"),
    RelationshipCommandSpec("compromise", "Conflict care", "Suggest fair compromises for a disagreement.", ",compromise Time zones make calls hard", "ai"),
    RelationshipCommandSpec("boundaries", "Conflict care", "Save or discuss a healthy boundary.", ",boundaries No yelling during conflict", "save", "boundaries", "boundary"),
    RelationshipCommandSpec("trigger", "Conflict care", "Track a trigger so you can handle it gently next time.", ",trigger late replies make me anxious", "save", "triggers", "trigger"),
    RelationshipCommandSpec("need", "Conflict care", "Save a relationship need clearly.", ",need I need reassurance after arguments", "save", "needs", "need"),
    RelationshipCommandSpec("listen", "Conflict care", "Get an active-listening checklist.", ",listen", "prompt"),
    RelationshipCommandSpec("cooldown", "Conflict care", "Start a calm-down plan before responding.", ",cooldown", "prompt"),
    RelationshipCommandSpec("forgive", "Conflict care", "Save a forgiveness reflection.", ",forgive I want to let go of yesterday", "save", "reflections", "forgiveness"),
    RelationshipCommandSpec("dateidea", "Fun", "Generate a long-distance date idea.", ",dateidea", "ai"),
    RelationshipCommandSpec("truth", "Fun", "Generate a soft truth question.", ",truth", "prompt"),
    RelationshipCommandSpec("dare", "Fun", "Generate a cute safe dare.", ",dare", "prompt"),
    RelationshipCommandSpec("question", "Fun", "Generate a connection question.", ",question", "prompt"),
    RelationshipCommandSpec("wouldyourather", "Fun", "Generate a relationship would-you-rather.", ",wouldyourather", "prompt"),
    RelationshipCommandSpec("playlist", "Fun", "Save a song for your shared playlist.", ",playlist Those Eyes - New West", "save", "playlist", "song"),
    RelationshipCommandSpec("song", "Fun", "Save a song that reminds you of them.", ",song Best Part", "save", "playlist", "song"),
    RelationshipCommandSpec("movie", "Trackers", "Add a movie to watch together.", ",movie Your Name", "tracker", "trackers", "movie"),
    RelationshipCommandSpec("game", "Trackers", "Add a game to play together.", ",game Minecraft", "tracker", "trackers", "game"),
    RelationshipCommandSpec("book", "Trackers", "Add a book/story to read together.", ",book The Little Prince", "tracker", "trackers", "reading"),
    RelationshipCommandSpec("anime", "Trackers", "Add an anime/show to watch together.", ",anime Horimiya", "tracker", "trackers", "movie"),
    RelationshipCommandSpec("wishlist", "Trackers", "Save a wishlist item.", ",wishlist matching bracelets", "save", "wishlist", "wishlist"),
    RelationshipCommandSpec("giftidea", "Trackers", "Save a gift idea.", ",giftidea handwritten letter", "save", "gifts", "gift"),
    RelationshipCommandSpec("bucket", "Trackers", "Add a shared bucket-list item.", ",bucket meet at the airport", "tracker", "trackers", "bucket"),
    RelationshipCommandSpec("promise", "Trackers", "Save a promise you want tracked.", ",promise call before sleeping on Fridays", "tracker", "trackers", "promise"),
    RelationshipCommandSpec("visit", "Trackers", "Save a visit plan/countdown note.", ",visit December winter break", "tracker", "trackers", "visit"),
    RelationshipCommandSpec("milestone", "Memories", "Save a relationship milestone.", ",milestone first 100-day streak", "save", "achievements", "milestone"),
    RelationshipCommandSpec("achievement", "Memories", "Save an achievement together.", ",achievement solved our first big argument kindly", "save", "achievements", "achievement"),
    RelationshipCommandSpec("insidejoke", "Memories", "Save an inside joke.", ",insidejoke the penguin voice", "save", "inside_jokes", "inside_joke"),
    RelationshipCommandSpec("favorite", "Memories", "Save one of your partner's favorites.", ",favorite Kosi likes purple flowers", "save", "favorites", "favorite"),
    RelationshipCommandSpec("dream", "Future", "Save a future dream.", ",dream apartment with a cozy gaming room", "save", "dreams", "dream"),
    RelationshipCommandSpec("plan", "Future", "Save a plan.", ",plan call Sunday at 8", "save", "plans", "plan"),
    RelationshipCommandSpec("countdown", "Future", "Save something you are counting down to.", ",countdown next visit", "save", "countdowns", "countdown"),
    RelationshipCommandSpec("journal", "Reflection", "Save a private mood-linked journal note.", ",journal I felt calmer after our call", "save", "journals", "journal"),
    RelationshipCommandSpec("moodnote", "Reflection", "Save a mood note.", ",moodnote anxious but hopeful", "save", "mood_notes", "mood"),
    RelationshipCommandSpec("lesson", "Reflection", "Save a lesson from a hard moment.", ",lesson ask before assuming", "save", "lessons", "lesson"),
    RelationshipCommandSpec("pattern", "Reflection", "Track a recurring communication pattern.", ",pattern we argue more when tired", "save", "patterns", "pattern"),
    RelationshipCommandSpec("streak", "Stats", "Show the current tracking streak summary.", ",streak", "stats"),
    RelationshipCommandSpec("communication", "Stats", "Show communication statistics.", ",communication", "stats"),
    RelationshipCommandSpec("lovelanguage", "Stats", "Analyze a note for likely love language.", ",lovelanguage I love when you spend time with me", "love"),
    RelationshipCommandSpec("randommemory", "Memories", "Show a recent positive memory.", ",randommemory", "recent", "memories", "memory"),
    RelationshipCommandSpec("review", "Weekly review", "Generate a weekly relationship review prompt.", ",review", "ai"),
    RelationshipCommandSpec("weekly", "Weekly review", "Alias-style weekly reflection prompt.", ",weekly", "ai"),
)
