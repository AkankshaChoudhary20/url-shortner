from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.link import Link


class LinkRepository:
    async def get_by_short_code(self, db: AsyncSession, short_code: str) -> Link | None:
        result = await db.execute(select(Link).where(Link.short_code == short_code))
        return result.scalar_one_or_none()

    async def exists_by_short_code(self, db: AsyncSession, short_code: str) -> bool:
        result = await db.execute(select(Link.id).where(Link.short_code == short_code))
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        db: AsyncSession,
        *,
        short_code: str,
        original_url: str,
        is_custom_alias: bool,
        expires_at: datetime | None,
    ) -> Link:
        link = Link(
            short_code=short_code,
            original_url=original_url,
            is_custom_alias=is_custom_alias,
            expires_at=expires_at,
        )
        db.add(link)
        await db.flush()
        await db.refresh(link)
        return link

    async def list_paginated(
        self, db: AsyncSession, *, page: int, page_size: int
    ) -> tuple[list[Link], int]:
        total_result = await db.execute(select(func.count()).select_from(Link))
        total = total_result.scalar_one()

        result = await db.execute(
            select(Link)
            .order_by(Link.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def record_click(self, db: AsyncSession, link: Link, *, clicked_at: datetime) -> None:
        link.click_count += 1
        link.last_clicked_at = clicked_at
        db.add(link)
        await db.flush()


link_repository = LinkRepository()
