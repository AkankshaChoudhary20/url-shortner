import pytest

from app.core.exceptions import AliasTakenError, InvalidLinkInputError
from app.services.shortener_service import ShortenerService
from tests.unit.fakes import AlwaysExistsLinkRepository, FakeLinkRepository, future_datetime, past_datetime


@pytest.fixture
def service() -> ShortenerService:
    return ShortenerService(repository=FakeLinkRepository())


async def test_create_link_with_custom_alias(service):
    link = await service.create_link(
        db=None, original_url="https://example.com", custom_alias="my-alias", expires_at=None
    )
    assert link.short_code == "my-alias"
    assert link.is_custom_alias is True


async def test_create_link_with_taken_alias_raises(service):
    await service.create_link(
        db=None, original_url="https://example.com", custom_alias="taken", expires_at=None
    )
    with pytest.raises(AliasTakenError):
        await service.create_link(
            db=None, original_url="https://example.com", custom_alias="taken", expires_at=None
        )


async def test_create_link_without_alias_generates_random_code(service):
    link = await service.create_link(
        db=None, original_url="https://example.com", custom_alias=None, expires_at=None
    )
    assert len(link.short_code) == 7
    assert link.is_custom_alias is False


async def test_create_link_with_past_expiry_raises(service):
    with pytest.raises(InvalidLinkInputError):
        await service.create_link(
            db=None,
            original_url="https://example.com",
            custom_alias=None,
            expires_at=past_datetime(),
        )


async def test_create_link_with_future_expiry_succeeds(service):
    expires_at = future_datetime()
    link = await service.create_link(
        db=None, original_url="https://example.com", custom_alias=None, expires_at=expires_at
    )
    assert link.expires_at == expires_at


async def test_create_link_gives_up_after_max_generation_attempts():
    service = ShortenerService(repository=AlwaysExistsLinkRepository())
    with pytest.raises(InvalidLinkInputError):
        await service.create_link(
            db=None, original_url="https://example.com", custom_alias=None, expires_at=None
        )
