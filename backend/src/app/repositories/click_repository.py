from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.click_event import ClickEvent


class ClickRepository:
    async def create(
        self,
        db: AsyncSession,
        *,
        link_id: int,
        clicked_at: datetime,
        referrer: str | None,
        user_agent: str | None,
        ip_hash: str | None,
    ) -> ClickEvent:
        event = ClickEvent(
            link_id=link_id,
            clicked_at=clicked_at,
            referrer=referrer,
            user_agent=user_agent,
            ip_hash=ip_hash,
        )
        db.add(event)
        await db.flush()
        return event

    async def clicks_by_day(
        self, db: AsyncSession, *, link_id: int, since: datetime | None, until: datetime | None
    ) -> list[tuple[str, int]]:
        stmt = select(
            func.to_char(ClickEvent.clicked_at, "YYYY-MM-DD").label("day"),
            func.count().label("clicks"),
        ).where(ClickEvent.link_id == link_id)

        if since is not None:
            stmt = stmt.where(ClickEvent.clicked_at >= since)
        if until is not None:
            stmt = stmt.where(ClickEvent.clicked_at <= until)

        stmt = stmt.group_by("day").order_by("day")
        result = await db.execute(stmt)
        return [(row.day, row.clicks) for row in result.all()]

    async def count_for_link(self, db: AsyncSession, *, link_id: int) -> int:
        result = await db.execute(
            select(func.count()).select_from(ClickEvent).where(ClickEvent.link_id == link_id)
        )
        return result.scalar_one()


click_repository = ClickRepository()
