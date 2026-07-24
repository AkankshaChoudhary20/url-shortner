import pytest
from pydantic import ValidationError

from app.schemas.link import LinkCreate


def test_link_create_with_no_alias():
    link = LinkCreate(original_url="https://example.com")
    assert link.custom_alias is None


def test_link_create_with_empty_string_alias_normalizes_to_none():
    link = LinkCreate(original_url="https://example.com", custom_alias="")
    assert link.custom_alias is None


def test_link_create_with_valid_alias():
    link = LinkCreate(original_url="https://example.com", custom_alias="my-alias")
    assert link.custom_alias == "my-alias"


def test_link_create_with_too_short_alias_raises():
    with pytest.raises(ValidationError):
        LinkCreate(original_url="https://example.com", custom_alias="ab")


def test_link_create_with_invalid_url_scheme_raises():
    with pytest.raises(ValidationError):
        LinkCreate(original_url="ftp://example.com")
