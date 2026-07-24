async def test_create_link_rate_limit_returns_429(client):
    responses = [
        await client.post("/api/v1/links", json={"original_url": f"https://example.com/rl{i}"})
        for i in range(15)
    ]

    statuses = [r.status_code for r in responses]
    assert 429 in statuses, f"expected a 429 among {statuses}"

    rejected = next(r for r in responses if r.status_code == 429)
    assert rejected.json()["error"]["code"] == "RATE_LIMITED"
