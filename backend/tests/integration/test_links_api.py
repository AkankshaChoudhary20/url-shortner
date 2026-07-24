from datetime import datetime, timedelta, timezone


async def test_create_link_happy_path(client):
    response = await client.post("/api/v1/links", json={"original_url": "https://example.com"})
    assert response.status_code == 201
    body = response.json()
    assert len(body["short_code"]) == 7
    assert body["original_url"] == "https://example.com"
    assert body["click_count"] == 0


async def test_create_link_with_custom_alias(client):
    response = await client.post(
        "/api/v1/links", json={"original_url": "https://example.com", "custom_alias": "abc-alias"}
    )
    assert response.status_code == 201
    assert response.json()["short_code"] == "abc-alias"


async def test_create_link_with_empty_string_alias_is_treated_as_no_alias(client):
    # A frontend that clears an optional field may send "" rather than
    # omitting the key entirely — this should behave the same as no alias,
    # not trip the 3-16 character length check.
    response = await client.post(
        "/api/v1/links", json={"original_url": "https://example.com", "custom_alias": ""}
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body["short_code"]) == 7
    assert body["is_custom_alias"] is False


async def test_create_link_with_taken_alias_returns_409(client):
    await client.post(
        "/api/v1/links", json={"original_url": "https://example.com", "custom_alias": "dup-alias"}
    )
    response = await client.post(
        "/api/v1/links", json={"original_url": "https://example.com", "custom_alias": "dup-alias"}
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ALIAS_TAKEN"


async def test_create_link_with_invalid_url_returns_422(client):
    response = await client.post("/api/v1/links", json={"original_url": "not-a-url"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_create_link_with_past_expiry_returns_422(client):
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    response = await client.post(
        "/api/v1/links", json={"original_url": "https://example.com", "expires_at": past}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_INPUT"


async def test_get_link_not_found_returns_404(client):
    response = await client.get("/api/v1/links/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "LINK_NOT_FOUND"


async def test_list_links_paginated(client):
    for i in range(3):
        await client.post("/api/v1/links", json={"original_url": f"https://example.com/{i}"})

    response = await client.get("/api/v1/links", params={"page": 1, "page_size": 2})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["total"] >= 3
    assert body["page"] == 1
    assert body["page_size"] == 2


async def test_redirect_happy_path_increments_click_count(client):
    create_resp = await client.post(
        "/api/v1/links", json={"original_url": "https://example.com/target", "custom_alias": "redir1"}
    )
    short_code = create_resp.json()["short_code"]

    redirect_resp = await client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_resp.status_code == 302
    assert redirect_resp.headers["location"] == "https://example.com/target"

    detail_resp = await client.get(f"/api/v1/links/{short_code}")
    assert detail_resp.json()["click_count"] == 1
    assert detail_resp.json()["last_clicked_at"] is not None


async def test_redirect_missing_link_returns_404(client):
    response = await client.get("/nope-does-not-exist", follow_redirects=False)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "LINK_NOT_FOUND"


async def test_redirect_expired_link_returns_410(client):
    future = (datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat()
    create_resp = await client.post(
        "/api/v1/links",
        json={
            "original_url": "https://example.com/expiring",
            "custom_alias": "willexpire",
            "expires_at": future,
        },
    )
    assert create_resp.status_code == 201

    import asyncio

    await asyncio.sleep(1.5)

    response = await client.get("/willexpire", follow_redirects=False)
    assert response.status_code == 410
    assert response.json()["error"]["code"] == "LINK_EXPIRED"


async def test_analytics_endpoint_after_multiple_clicks(client):
    create_resp = await client.post(
        "/api/v1/links", json={"original_url": "https://example.com/a", "custom_alias": "analytics1"}
    )
    short_code = create_resp.json()["short_code"]

    for _ in range(3):
        await client.get(f"/{short_code}", follow_redirects=False)

    response = await client.get(f"/api/v1/links/{short_code}/analytics")
    assert response.status_code == 200
    body = response.json()
    assert body["total_clicks"] == 3
    assert sum(bucket["clicks"] for bucket in body["clicks_by_day"]) == 3
