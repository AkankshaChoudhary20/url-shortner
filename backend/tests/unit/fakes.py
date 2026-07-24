from datetime import datetime, timedelta, timezone
from itertools import count

from app.db.models.click_event import ClickEvent
from app.db.models.link import Link


class FakeLinkRepository:
    def __init__(self) -> None:
        self._by_code: dict[str, Link] = {}
        self._ids = count(1)

    async def get_by_short_code(self, db, short_code: str) -> Link | None:
        return self._by_code.get(short_code)

    async def exists_by_short_code(self, db, short_code: str) -> bool:
        return short_code in self._by_code

    async def create(
        self, db, *, short_code, original_url, is_custom_alias, expires_at
    ) -> Link:
        link = Link(
            id=next(self._ids),
            short_code=short_code,
            original_url=original_url,
            is_custom_alias=is_custom_alias,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            is_active=True,
            click_count=0,
            last_clicked_at=None,
        )
        self._by_code[short_code] = link
        return link

    async def list_paginated(self, db, *, page: int, page_size: int):
        items = list(self._by_code.values())
        start = (page - 1) * page_size
        return items[start : start + page_size], len(items)

    async def record_click(self, db, link: Link, *, clicked_at: datetime) -> None:
        link.click_count += 1
        link.last_clicked_at = clicked_at


class AlwaysExistsLinkRepository(FakeLinkRepository):
    """Simulates every candidate short code already being taken."""

    async def exists_by_short_code(self, db, short_code: str) -> bool:
        return True


class FakeClickRepository:
    def __init__(self) -> None:
        self._events: list[ClickEvent] = []

    async def create(self, db, *, link_id, clicked_at, referrer, user_agent, ip_hash):
        event = ClickEvent(
            id=len(self._events) + 1,
            link_id=link_id,
            clicked_at=clicked_at,
            referrer=referrer,
            user_agent=user_agent,
            ip_hash=ip_hash,
        )
        self._events.append(event)
        return event

    async def clicks_by_day(self, db, *, link_id, since, until):
        buckets: dict[str, int] = {}
        for event in self._events:
            if event.link_id != link_id:
                continue
            if since and event.clicked_at < since:
                continue
            if until and event.clicked_at > until:
                continue
            day = event.clicked_at.date().isoformat()
            buckets[day] = buckets.get(day, 0) + 1
        return sorted(buckets.items())

    async def count_for_link(self, db, *, link_id):
        return sum(1 for event in self._events if event.link_id == link_id)


def future_datetime(days: int = 1) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def past_datetime(days: int = 1) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)
