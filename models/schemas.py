"""Pydantic schemas for relationship data persisted in MongoDB."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RelationshipBase(BaseModel):
    """Base document carrying timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(RelationshipBase):
    """A Discord user known to the relationship bot."""
    user_id: int
    display_name: str


class Couple(RelationshipBase):
    """The configured relationship between NTM and Kosi."""
    partner_one_id: int
    partner_two_id: int
    status: Literal["pending", "active"] = "active"


class Memory(RelationshipBase):
    """A positive shared memory with suggested tags."""
    author_id: int
    text: str = Field(min_length=3, max_length=1200)
    tags: list[str] = Field(default_factory=list)


class Complaint(RelationshipBase):
    """A guided concern submitted for neutral mediation."""
    author_id: int
    other_id: int
    what_happened: str = Field(min_length=5, max_length=1200)
    feeling: str = Field(min_length=2, max_length=500)
    need: str = Field(min_length=2, max_length=500)
    status: str = "open"
    ai_summary: str = ""


class CheckIn(RelationshipBase):
    """A daily emotional check-in."""
    author_id: int
    mood: int = Field(ge=1, le=10)
    energy: int = Field(ge=1, le=10)
    note: str = Field(default="", max_length=800)


class Goal(RelationshipBase):
    """A shared relationship goal with progress."""
    title: str = Field(min_length=2, max_length=120)
    progress: int = Field(default=0, ge=0, le=100)
    owner_id: int | None = None


class TrackerItem(RelationshipBase):
    """A shared movie, game, reading, bucket-list, promise, or visit item."""
    kind: Literal["bucket", "promise", "visit", "movie", "game", "reading"]
    title: str = Field(min_length=2, max_length=140)
    status: str = "planned"
    notes: str = Field(default="", max_length=800)


class Settings(RelationshipBase):
    """Server-specific configuration."""
    guild_id: int
    logging_channel_id: int | None = None


class Journal(RelationshipBase):
    """Private journal entry linked to mood for correlation."""
    author_id: int
    mood: int = Field(ge=1, le=10)
    text: str = Field(min_length=3, max_length=1500)


class Achievement(RelationshipBase):
    """Relationship milestone or achievement."""
    title: str
    description: str = ""


class Quote(RelationshipBase):
    """Saved quote or affirmation."""
    text: str
    author_id: int | None = None


class Promise(TrackerItem):
    """A promise item specialized from tracker data."""
    kind: Literal["promise"] = "promise"


class Reminder(TrackerItem):
    """A reminder item for future delivery."""
    kind: Literal["bucket"] = "bucket"
    remind_at: datetime | None = None


class Visit(TrackerItem):
    """Online relationship visit countdown."""
    kind: Literal["visit"] = "visit"
    visit_at: datetime | None = None


class Wishlist(TrackerItem):
    """Shared wishlist item."""
    kind: Literal["bucket"] = "bucket"


class Gift(TrackerItem):
    """Gift idea item."""
    kind: Literal["bucket"] = "bucket"


class AIMemory(RelationshipBase):
    """Stored AI context memory."""
    key: str
    value: str


class ConversationSummary(RelationshipBase):
    """Neutral summary of a mediated conversation."""
    complaint_id: str
    summary: str
