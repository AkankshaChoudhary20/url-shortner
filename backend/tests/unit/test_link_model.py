from datetime import datetime, timedelta, timezone

from app.db.models.link import Link


def _make_link(**overrides) -> Link:
    defaults = dict(
        id=1,
        short_code="abc1234",
        original_url="https://example.com",
        is_custom_alias=False,
        created_at=datetime.now(timezone.utc),
        expires_at=None,
        is_active=True,
        click_count=0,
        last_clicked_at=None,
    )
    defaults.update(overrides)
    return Link(**defaults)


def test_link_without_expiry_is_never_expired():
    link = _make_link(expires_at=None)
    assert link.is_expired is False


def test_link_with_future_expiry_is_not_expired():
    link = _make_link(expires_at=datetime.now(timezone.utc) + timedelta(days=1))
    assert link.is_expired is False


def test_link_with_past_expiry_is_expired():
    link = _make_link(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))
    assert link.is_expired is True
