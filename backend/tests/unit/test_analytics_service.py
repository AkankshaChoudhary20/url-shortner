from app.services.analytics_service import hash_ip


def test_hash_ip_returns_none_for_missing_ip():
    assert hash_ip(None) is None
    assert hash_ip("") is None


def test_hash_ip_is_deterministic_and_not_the_raw_ip():
    hashed = hash_ip("203.0.113.5")
    assert hashed != "203.0.113.5"
    assert hashed == hash_ip("203.0.113.5")


def test_hash_ip_differs_for_different_ips():
    assert hash_ip("203.0.113.5") != hash_ip("203.0.113.6")
