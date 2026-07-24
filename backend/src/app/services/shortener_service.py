from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AliasTakenError,
    InvalidLinkInputError,
    LinkExpiredError,
    LinkNotFoundError,
)
from app.core.logging import get_logger
from app.db.models.link import Link
from app.repositories.link_repository import LinkRepository, link_repository
from app.utils.code_generator import generate_short_code

logger = get_logger("app.services.shortener")

MAX_GENERATION_ATTEMPTS = 5


class ShortenerService:
    def __init__(self, repository: LinkRepository = link_repository) -> None:
        self.repository = repository

    async def create_link(
        self,
        db: AsyncSession,
        *,
        original_url: str,
        custom_alias: str | None,
        expires_at: datetime | None,
    ) -> Link:
        if expires_at is not None and expires_at <= datetime.now(timezone.utc):
            raise InvalidLinkInputError("expires_at must be in the future")

        if custom_alias:
            if await self.repository.exists_by_short_code(db, custom_alias):
                raise AliasTakenError(f"Alias '{custom_alias}' is already taken")
            return await self.repository.create(
                db,
                short_code=custom_alias,
                original_url=original_url,
                is_custom_alias=True,
                expires_at=expires_at,
            )

        for _ in range(MAX_GENERATION_ATTEMPTS):
            candidate = generate_short_code()
            if not await self.repository.exists_by_short_code(db, candidate):
                return await self.repository.create(
                    db,
                    short_code=candidate,
                    original_url=original_url,
                    is_custom_alias=False,
                    expires_at=expires_at,
                )

        logger.error("short_code_generation_exhausted")
        raise InvalidLinkInputError("Could not generate a unique short code, please retry")

    async def get_link_or_raise(self, db: AsyncSession, short_code: str) -> Link:
        link = await self.repository.get_by_short_code(db, short_code)
        if link is None:
            raise LinkNotFoundError(f"Link '{short_code}' not found")
        return link

    async def resolve_for_redirect(self, db: AsyncSession, short_code: str) -> Link:
        link = await self.get_link_or_raise(db, short_code)
        if not link.is_active or link.is_expired:
            raise LinkExpiredError(f"Link '{short_code}' is no longer active")
        return link

    async def list_links(self, db: AsyncSession, *, page: int, page_size: int):
        return await self.repository.list_paginated(db, page=page, page_size=page_size)


shortener_service = ShortenerService()
