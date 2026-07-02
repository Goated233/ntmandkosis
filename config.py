"""Runtime configuration for the private relationship assistant bot."""
from __future__ import annotations

from functools import lru_cache
from typing import Set

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings with safe defaults for local tests."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    discord_token: str = Field(default="", alias="DISCORD_TOKEN")
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_db: str = Field(default="relationship_bot", alias="MONGODB_DB")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    command_prefix: str = Field(default=",", alias="COMMAND_PREFIX")
    owner_ids_raw: str = Field(default="1417262684990083142", alias="OWNER_IDS")
    partner_one_id: int = Field(default=1417262684990083142, alias="PARTNER_ONE_ID")
    partner_two_id: int = Field(default=1516247373716787363, alias="PARTNER_TWO_ID")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def owner_ids(self) -> Set[int]:
        """Return configured bot owner IDs."""
        return {int(value.strip()) for value in self.owner_ids_raw.split(",") if value.strip().isdigit()}

    @property
    def partner_ids(self) -> Set[int]:
        """Return the two allowed partner IDs for this personal bot."""
        return {self.partner_one_id, self.partner_two_id}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once per process."""
    return Settings()
