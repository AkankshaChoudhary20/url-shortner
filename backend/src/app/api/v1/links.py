from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import Settings, get_settings
from app.core.security import limiter
from app.schemas.link import ClickBucket, LinkAnalytics, LinkCreate, LinkListResponse, LinkRead
from app.services.analytics_service import analytics_service
from app.services.shortener_service import shortener_service

router = APIRouter(prefix="/links", tags=["links"])


def _to_link_read(link, settings: Settings) -> LinkRead:
    return LinkRead(
        short_code=link.short_code,
        short_url=f"{settings.base_short_url}/{link.short_code}",
        original_url=link.original_url,
        is_custom_alias=link.is_custom_alias,
        created_at=link.created_at,
        expires_at=link.expires_at,
        is_active=link.is_active,
        is_expired=link.is_expired,
        click_count=link.click_count,
        last_clicked_at=link.last_clicked_at,
    )


@router.post("", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_settings().rate_limit_create_link)
async def create_link(
    request: Request,
    payload: LinkCreate,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LinkRead:
    link = await shortener_service.create_link(
        db,
        original_url=payload.original_url,
        custom_alias=payload.custom_alias,
        expires_at=payload.expires_at,
    )
    return _to_link_read(link, settings)


@router.get("", response_model=LinkListResponse)
async def list_links(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LinkListResponse:
    links, total = await shortener_service.list_links(db, page=page, page_size=page_size)
    return LinkListResponse(
        items=[_to_link_read(link, settings) for link in links],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{short_code}", response_model=LinkRead)
async def get_link(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LinkRead:
    link = await shortener_service.get_link_or_raise(db, short_code)
    return _to_link_read(link, settings)


@router.get("/{short_code}/analytics", response_model=LinkAnalytics)
async def get_link_analytics(
    short_code: str,
    since: datetime | None = None,
    until: datetime | None = None,
    db: AsyncSession = Depends(get_db),
) -> LinkAnalytics:
    link = await shortener_service.get_link_or_raise(db, short_code)
    total, buckets = await analytics_service.get_analytics(db, link=link, since=since, until=until)
    return LinkAnalytics(
        short_code=link.short_code,
        total_clicks=total,
        clicks_by_day=[ClickBucket(day=day, clicks=clicks) for day, clicks in buckets],
    )
