from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = {}
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
