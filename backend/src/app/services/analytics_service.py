import hashlib
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.link import Link
from app.repositories.click_repository import ClickRepository, click_repository
from app.repositories.link_repository import LinkRepository, link_repository


def hash_ip(ip_address: str | None) -> str | None:
    if not ip_address:
        return None
    return hashlib.sha256(ip_address.encode()).hexdigest()


class AnalyticsService:
    def __init__(
        self,
        click_repo: ClickRepository = click_repository,
        link_repo: LinkRepository = link_repository,
    ) -> None:
        self.click_repo = click_repo
        self.link_repo = link_repo

    async def record_click(
        self,
        db: AsyncSession,
        *,
        link: Link,
        referrer: str | None,
        user_agent: str | None,
        ip_address: str | None,
    ) -> None:
        clicked_at = datetime.now(timezone.utc)
        await self.click_repo.create(
            db,
            link_id=link.id,
            clicked_at=clicked_at,
            referrer=referrer,
            user_agent=user_agent,
            ip_hash=hash_ip(ip_address),
        )
        await self.link_repo.record_click(db, link, clicked_at=clicked_at)
        await db.commit()

    async def get_analytics(
        self,
        db: AsyncSession,
        *,
        link: Link,
        since: datetime | None,
        until: datetime | None,
    ) -> tuple[int, list[tuple[str, int]]]:
        total = await self.click_repo.count_for_link(db, link_id=link.id)
        buckets = await self.click_repo.clicks_by_day(db, link_id=link.id, since=since, until=until)
        return total, buckets


analytics_service = AnalyticsService()
