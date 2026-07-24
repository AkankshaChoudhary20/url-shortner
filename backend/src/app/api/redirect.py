from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.deps import get_db
from app.core.logging import get_logger
from app.services.analytics_service import analytics_service
from app.services.shortener_service import shortener_service

router = APIRouter(tags=["redirect"])
logger = get_logger("app.api.redirect")


@router.get("/{short_code}")
async def redirect_short_link(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    link = await shortener_service.resolve_for_redirect(db, short_code)

    # FastAPI guarantees a yield-dependency's post-yield cleanup (get_db's
    # commit/close) runs after background tasks complete, so it's safe to
    # reuse the request-scoped session here instead of opening a new one.
    # This also keeps click logging subject to the same get_db dependency
    # override used in tests.
    background_tasks.add_task(
        analytics_service.record_click,
        db,
        link=link,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    logger.info("redirect", short_code=short_code)
    return RedirectResponse(url=link.original_url, status_code=status.HTTP_302_FOUND)
