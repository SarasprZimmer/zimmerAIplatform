def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js, dict)
    assert js.get("status") is not None
