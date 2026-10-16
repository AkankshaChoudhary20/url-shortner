import re
from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, HttpUrl, TypeAdapter, field_validator

ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,16}$")


class LinkCreate(BaseModel):
    original_url: str = Field(..., max_length=2048)
    custom_alias: str | None = None
    expires_at: datetime | None = None

    @field_validator("original_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("original_url must start with http:// or https://")
        if not urlsplit(value).hostname:
            raise ValueError("original_url must include a hostname")
        TypeAdapter(HttpUrl).validate_python(value)
        return value

    @field_validator("expires_at")
    @classmethod
    def validate_expiration_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("expires_at must include a timezone")
        return value

    @field_validator("custom_alias", mode="before")
    @classmethod
    def validate_alias(cls, value: str | None) -> str | None:
        # An empty string means "no alias" just like an omitted field —
        # clients (including our own frontend) may send either.
        if value is None or value == "":
            return None
        if not isinstance(value, str) or not ALIAS_PATTERN.fullmatch(value):
            raise ValueError("custom_alias must be 3-16 characters: letters, numbers, - or _")
        return value


class LinkRead(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    is_custom_alias: bool
    created_at: datetime
    expires_at: datetime | None
    is_active: bool
    is_expired: bool
    click_count: int
    last_clicked_at: datetime | None

    model_config = {"from_attributes": True}


class LinkListResponse(BaseModel):
    items: list[LinkRead]
    total: int
    page: int
    page_size: int


class ClickBucket(BaseModel):
    day: str
    clicks: int


class LinkAnalytics(BaseModel):
    short_code: str
    total_clicks: int
    clicks_by_day: list[ClickBucket]
