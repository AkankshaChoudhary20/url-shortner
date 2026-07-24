from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.logging import get_logger, request_id_ctx

logger = get_logger("app.exceptions")


class AppException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "INTERNAL_ERROR"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AliasTakenError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "ALIAS_TAKEN"


class LinkNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "LINK_NOT_FOUND"


class LinkExpiredError(AppException):
    status_code = status.HTTP_410_GONE
    code = "LINK_EXPIRED"


class InvalidLinkInputError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "INVALID_INPUT"


def _envelope(code: str, message: str, details: dict | None = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "request_id": request_id_ctx.get(),
        }
    }


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning("app_exception", code=exc.code, message=exc.message, path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(exc.code, exc.message, exc.details),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = jsonable_encoder(exc.errors())
    logger.warning("validation_error", errors=errors, path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=_envelope("VALIDATION_ERROR", "Request validation failed", {"errors": errors}),
    )


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    logger.warning("rate_limit_exceeded", path=request.url.path, detail=str(exc.detail))
    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=_envelope("RATE_LIMITED", "Rate limit exceeded, please slow down", {"limit": str(exc.detail)}),
    )
    response.headers["Retry-After"] = "60"
    return response


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_envelope("INTERNAL_ERROR", "An unexpected error occurred"),
    )
